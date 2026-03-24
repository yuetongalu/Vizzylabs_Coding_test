# AI Automation Engineer Challenge

**Time Limit:** 15 minutes
**Position:** AI Automation Engineer

---

## Scenario

You've joined Vizzy Labs and inherited a content moderation service. The service is **functional** - it runs, accepts requests, and returns results.

However, the business has concerns...

---

## The Situation

**From the Creator Success Team (via Slack):**
> "We're getting ~50 support tickets/week from creators whose content is incorrectly flagged. One cooking video was flagged as 'violence' (chopping vegetables). A fitness creator got flagged for 'adult content' (shirtless workout). Creators are threatening to leave the platform."

**From Trust & Safety (in a meeting):**
> "We had a video promoting dangerous supplements reach 100K views before we caught it. Our moderation also missed some borderline hate speech last month. We need to be MORE aggressive, not less."

**From your Engineering Manager:**
> "Both teams are right. We also have no visibility into WHY decisions are made. When Legal asks 'why was this flagged?', we can't answer. We need the system to be more transparent and tunable."

---

## Your Task

**You have 15 minutes.** The interviewer is your stakeholder - ask them questions.

We want to see:

1. **How do you approach this problem?**
   - These requirements conflict. How do you think about the trade-offs?
   - What questions would you ask? What data would you want?

2. **What do you propose?**
   - There's no single "right" answer
   - We want to understand YOUR reasoning

3. **Implement something**
   - Once you've decided what to do, build it
   - AI can help you code, but YOU must decide what to code

---

## Current System

```bash
cd ai-automation-challenge
pip install -r requirements.txt
uvicorn main:app --reload
```

Test it:
```bash
curl -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{"content": "Check out my cooking tutorial!", "creator_id": "chef123"}'
```

The system works. It returns moderation results. The question is whether it's doing the RIGHT thing.

---

## Files

All files are functional. Modify whatever you think needs changing.

| File | Description |
|------|-------------|
| `main.py` | FastAPI application |
| `moderation_service.py` | Core moderation logic |
| `models.py` | Data models |
| `mock_clients.py` | Simulates AI APIs (realistic behavior) |

---

## Important

**We are NOT looking for:**
- Bug fixes (the code runs fine)
- A "perfect" solution (none exists)
- Impressive code (simple is better)

**We ARE looking for:**
- How you think about conflicting requirements
- Your ability to make decisions with incomplete information
- Whether you can direct AI tools vs being directed by them
- Your reasoning and trade-off analysis

---

## Hints for the Interviewer (Candidate: Ignore This)

*If candidate asks good questions, share relevant context. If they dive straight into code without understanding the problem, that's a signal.*

---

## My Problem-Solving Workflow

My workflow starts with identifying the actual product and system problem before making code changes. In this challenge, the moderation service was functional, but the business problem was that it was too simplistic for real-world moderation. It produced a basic binary decision, lacked explainability, and did not handle conflicting goals between creator experience and trust and safety.

After identifying the problem, I diagnose it like a code review. I used AI as a senior engineer partner to inspect the codebase, point out architectural weaknesses, and surface hidden issues such as unused components, missing review flows, weak explainability, and logic that looked configurable but was not actually connected to the decision path. I treat AI as a reviewer and collaborator, not as the decision-maker. The goal is to use AI to accelerate diagnosis while keeping the reasoning and prioritization human-led.

Once the problems were clear, I solved them with AI assistance by focusing on the highest-value improvements first. Instead of trying to perfect the whole system, I changed the moderation flow so it could support review decisions, clearer reasoning, and more context-aware handling of borderline content. After the implementation, I double-check the solution against other cases such as cooking, fitness, supplement scams, coded hate speech, clear violence, and safe content. That verification step is important because moderation quality depends on how the system behaves across edge cases, not just on whether the code runs.

## Why I Chose This Workflow

I chose this workflow because this challenge is not mainly about writing code quickly. It is about making a good engineering decision under conflicting business requirements. If I start coding too early, I risk improving the wrong thing. By first identifying the problem, then diagnosing it through a code-review mindset, and only then implementing targeted changes, I can focus on solving the business risk instead of only changing syntax or structure.

Using AI in this way also reflects how I like to work in practice. AI is most useful when it helps me review assumptions, identify gaps, and accelerate implementation, but the product judgment still comes from me. That is especially important in moderation systems, where the trade-offs affect creators, safety teams, and legal stakeholders.

## Problems I Identified

- The moderation flow trusted a simple binary provider flag instead of making a transparent, tunable decision.
- The service had no review channel for borderline content.
- The response was not explainable enough for legal, trust and safety, or creator support use cases.
- A secondary AI client already existed in the codebase but was unused.
- The score handling logic was incomplete and included a bug in how category scores were processed.

## Changes I Made

- Added a multi-stage moderation flow in `moderation_service.py`.
- Introduced three moderation outcomes: `allow`, `review`, and `block`.
- Added threshold-based decision logic instead of relying only on a provider's binary flag.
- Enabled the previously unused Anthropic client as a secondary reviewer for ambiguous or sensitive cases.
- Expanded the response model in `models.py` to include decision type, category scores, triggered categories, threshold settings, provider assessments, and review requirements.
- Improved the mock secondary reviewer in `mock_clients.py` so it returns more context-aware reasoning for moderation edge cases.
- Fixed the score extraction logic so category scores are explicitly read and evaluated instead of being treated as a directly iterable object.

## How These Changes Solve the Problem

These changes make the system better aligned with the business requirements. The review channel reduces the risk of over-blocking legitimate content, because borderline cases can now be escalated instead of being automatically blocked. The threshold-based logic makes the moderation system more tunable, which is important when different categories need different sensitivity levels. The expanded response structure improves transparency by showing what the system saw, why it made the decision, and which model contributed to the outcome.

Enabling the secondary reviewer also improves context handling. False-positive cases such as cooking, fitness, or medical content can now be reconsidered with more nuance, while subtle harmful cases such as supplement scams or coded hate speech can be escalated for review instead of silently passing through. In other words, the system is no longer only functional; it is closer to being operationally useful.

## Verification Mindset

I verified the changes by checking representative edge cases rather than relying on one happy-path example. The cases I focused on were:

- Cooking content that can look violent out of context
- Fitness content that can be misread as adult content
- Supplement scam language that should not be missed
- Borderline hate speech that needs escalation
- Clear policy-violating violent content
- Clearly safe everyday content

This matters because a moderation system should be evaluated by how it handles ambiguity and trade-offs, not only by whether the endpoint returns a response.
