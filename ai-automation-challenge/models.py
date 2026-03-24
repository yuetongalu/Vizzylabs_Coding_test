from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum

class ViolationType(str, Enum):
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    SPAM = "spam"
    NONE = "none"

class ModerationDecision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"

class ModerationRequest(BaseModel):
    """Request model for content moderation"""
    content: str = Field(..., min_length=1)
    creator_id: str
    video_id: Optional[str] = None

class ThresholdConfig(BaseModel):
    """Thresholds used to interpret model scores."""
    allow_below: float = Field(..., ge=0.0, le=1.0)
    review_above: float = Field(..., ge=0.0, le=1.0)
    block_above: float = Field(..., ge=0.0, le=1.0)

class ProviderAssessment(BaseModel):
    """Provider-specific assessment for transparency."""
    provider: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    violation_type: ViolationType
    reasoning: str
    recommends_human_review: bool = False

class ModerationResult(BaseModel):
    """Structured moderation decision with explainability details."""
    decision: ModerationDecision
    is_safe: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    violation_type: ViolationType
    reasoning: str
    provider: str
    requires_human_review: bool = False
    triggered_categories: List[ViolationType] = Field(default_factory=list)
    category_scores: Dict[str, float] = Field(default_factory=dict)
    thresholds: ThresholdConfig
    provider_assessments: List[ProviderAssessment] = Field(default_factory=list)

class ModerationResponse(BaseModel):
    """API response model"""
    video_id: Optional[str]
    moderation: ModerationResult
    processing_time_ms: float
