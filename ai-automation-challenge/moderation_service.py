import json
from typing import Dict, List, Tuple

from models import (
    ModerationDecision,
    ModerationRequest,
    ModerationResult,
    ProviderAssessment,
    ThresholdConfig,
    ViolationType,
)
from mock_clients import MockAnthropicClient, MockOpenAIClient


class ModerationService:
    """
    Content moderation service with a review lane for borderline content.

    Flow:
    - Run a first-pass moderation classifier
    - Apply tunable thresholds to produce allow/review/block
    - Use a secondary model for contextual analysis on ambiguous content
    - Return detailed reasoning, scores, and provider assessments
    """

    CATEGORY_MAP = {
        "hate": ViolationType.HATE_SPEECH,
        "violence": ViolationType.VIOLENCE,
        "sexual": ViolationType.ADULT_CONTENT,
        "spam": ViolationType.SPAM,
    }

    def __init__(self, openai_key: str, anthropic_key: str):
        self.openai_client = MockOpenAIClient(api_key=openai_key)
        self.anthropic_client = MockAnthropicClient(api_key=anthropic_key)
        self.thresholds = ThresholdConfig(
            allow_below=0.30,
            review_above=0.30,
            block_above=0.80,
        )
        self.category_review_thresholds = {
            ViolationType.HATE_SPEECH: 0.25,
            ViolationType.VIOLENCE: 0.35,
            ViolationType.ADULT_CONTENT: 0.35,
            ViolationType.SPAM: 0.30,
        }

    async def moderate_content(self, request: ModerationRequest) -> ModerationResult:
        """Moderate content using a first-pass classifier and contextual review."""
        response = await self.openai_client.moderations.create(input=request.content)
        result = response.results[0]

        category_scores = self._extract_scores(result.category_scores)
        primary_violation, max_score = self._get_primary_violation(category_scores)
        triggered_categories = self._get_triggered_categories(category_scores)
        decision = self._decision_from_scores(primary_violation, max_score)
        assessments = [
            ProviderAssessment(
                provider="openai",
                confidence=max_score,
                violation_type=primary_violation,
                reasoning=self._build_primary_reasoning(primary_violation, max_score, triggered_categories),
                recommends_human_review=decision == ModerationDecision.REVIEW,
            )
        ]

        final_decision = decision
        final_violation = primary_violation
        final_reasoning = self._build_final_reasoning(
            decision=decision,
            violation_type=primary_violation,
            confidence=max_score,
            triggered_categories=triggered_categories,
        )

        if self._should_run_secondary_review(decision, primary_violation):
            secondary_assessment = await self._get_secondary_assessment(
                request.content,
                primary_violation,
                max_score,
                triggered_categories,
            )
            assessments.append(secondary_assessment)

            if secondary_assessment.recommends_human_review:
                final_decision = ModerationDecision.REVIEW
            elif secondary_assessment.violation_type == ViolationType.NONE and decision == ModerationDecision.REVIEW:
                final_decision = ModerationDecision.ALLOW
            else:
                final_decision = decision

            if secondary_assessment.violation_type != ViolationType.NONE:
                final_violation = secondary_assessment.violation_type

            final_reasoning = self._merge_reasoning(
                primary_reasoning=final_reasoning,
                secondary_reasoning=secondary_assessment.reasoning,
                final_decision=final_decision,
            )

        return ModerationResult(
            decision=final_decision,
            is_safe=final_decision != ModerationDecision.BLOCK,
            confidence=max_score,
            violation_type=final_violation if final_decision != ModerationDecision.ALLOW else ViolationType.NONE,
            reasoning=final_reasoning,
            provider="multi-stage" if len(assessments) > 1 else "openai",
            requires_human_review=final_decision == ModerationDecision.REVIEW,
            triggered_categories=triggered_categories,
            category_scores=category_scores,
            thresholds=self.thresholds,
            provider_assessments=assessments,
        )

    def _extract_scores(self, score_obj) -> Dict[str, float]:
        return {
            "hate": score_obj.hate,
            "violence": score_obj.violence,
            "sexual": score_obj.sexual,
            "spam": score_obj.spam,
        }

    def _get_primary_violation(self, category_scores: Dict[str, float]) -> Tuple[ViolationType, float]:
        max_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[max_category]
        violation = self.CATEGORY_MAP.get(max_category, ViolationType.NONE)
        return violation, max_score

    def _get_triggered_categories(self, category_scores: Dict[str, float]) -> List[ViolationType]:
        categories: List[ViolationType] = []
        for category_name, score in category_scores.items():
            violation = self.CATEGORY_MAP[category_name]
            threshold = self.category_review_thresholds[violation]
            if score >= threshold:
                categories.append(violation)
        return categories

    def _decision_from_scores(self, primary_violation: ViolationType, max_score: float) -> ModerationDecision:
        if primary_violation == ViolationType.NONE or max_score < self.thresholds.review_above:
            return ModerationDecision.ALLOW
        if max_score >= self.thresholds.block_above:
            return ModerationDecision.BLOCK
        return ModerationDecision.REVIEW

    def _should_run_secondary_review(
        self,
        decision: ModerationDecision,
        primary_violation: ViolationType,
    ) -> bool:
        return decision == ModerationDecision.REVIEW or primary_violation in {
            ViolationType.HATE_SPEECH,
            ViolationType.SPAM,
        }

    async def _get_secondary_assessment(
        self,
        content: str,
        primary_violation: ViolationType,
        confidence: float,
        triggered_categories: List[ViolationType],
    ) -> ProviderAssessment:
        prompt = (
            "Review this moderation decision for context sensitivity. "
            f"Content: {content}\n"
            f"Primary violation: {primary_violation.value}\n"
            f"Primary confidence: {confidence}\n"
            f"Triggered categories: {[category.value for category in triggered_categories]}\n"
            "Return JSON with is_safe, confidence, violation_type, reasoning, "
            "requires_human_review, and context_notes."
        )
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        payload = json.loads(response.content[0].text)
        violation = ViolationType(payload.get("violation_type", "none"))

        return ProviderAssessment(
            provider="anthropic",
            confidence=payload.get("confidence", confidence),
            violation_type=violation,
            reasoning=payload.get("reasoning", "Secondary contextual review completed."),
            recommends_human_review=payload.get("requires_human_review", False),
        )

    def _build_primary_reasoning(
        self,
        violation_type: ViolationType,
        confidence: float,
        triggered_categories: List[ViolationType],
    ) -> str:
        if violation_type == ViolationType.NONE:
            return "Primary classifier found no category above the review threshold."

        category_list = ", ".join(category.value for category in triggered_categories) or violation_type.value
        return (
            f"Primary classifier scored the content highest for {violation_type.value} "
            f"at {confidence:.2f}. Categories at or above review sensitivity: {category_list}."
        )

    def _build_final_reasoning(
        self,
        decision: ModerationDecision,
        violation_type: ViolationType,
        confidence: float,
        triggered_categories: List[ViolationType],
    ) -> str:
        if decision == ModerationDecision.ALLOW:
            return "Content is allowed because no category score crossed the review threshold."
        if decision == ModerationDecision.BLOCK:
            return (
                f"Content is blocked because {violation_type.value} reached {confidence:.2f}, "
                f"which exceeds the block threshold of {self.thresholds.block_above:.2f}."
            )

        category_list = ", ".join(category.value for category in triggered_categories) or violation_type.value
        return (
            f"Content is routed to review because {violation_type.value} reached {confidence:.2f}. "
            f"Triggered categories: {category_list}. This is above the review threshold but below the block threshold."
        )

    def _merge_reasoning(
        self,
        primary_reasoning: str,
        secondary_reasoning: str,
        final_decision: ModerationDecision,
    ) -> str:
        if final_decision == ModerationDecision.ALLOW:
            decision_summary = "Secondary review found enough context to allow the content."
        elif final_decision == ModerationDecision.BLOCK:
            decision_summary = "Secondary review supported keeping the content blocked."
        else:
            decision_summary = "Secondary review recommends sending the content to human review."

        return f"{primary_reasoning} {secondary_reasoning} {decision_summary}"
