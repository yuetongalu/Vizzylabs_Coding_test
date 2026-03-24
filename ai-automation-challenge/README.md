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

## My Approach

This challenge is not mainly about making the code run. The code already runs. The real task is to improve a moderation system that is functional but not reliable enough for real business use.

My approach was to separate technical correctness from product correctness. I first looked for the gap between what the system currently does and what the business actually needs. In this case, the gap was clear: the moderation flow was too binary, not explainable enough, and not flexible enough to handle the tension between Creator Success, Trust and Safety, and Legal.

## My Problem-Solving Methodology

I followed a simple workflow:

1. Identify the real problem.
   I first ask whether the system solves the business problem, not just whether it runs.

2. Diagnose before changing code.
   I review the codebase to find architectural gaps, weak logic, dead paths, and missing capabilities.

3. Use AI as a senior engineer partner.
   I use AI to review the code, challenge assumptions, and accelerate analysis, but I keep the product judgment and prioritization human-led.

4. Implement the highest-impact changes first.
   In a time-limited exercise, I focus on the changes that most directly improve decision quality and reduce risk.

5. Verify with edge cases.
   I check how the system behaves on ambiguous and high-risk examples, not just a happy path.

## Why I Prompted AI This Way

My first prompt asked AI to inspect the code and explain what problems it recognized before doing any implementation. I did that on purpose. I did not want AI to jump straight into writing code without understanding the system.

I wanted AI to behave like a senior engineer in a code review: read the code first, explain the risks, identify what is missing, and help me decide what to fix. That was important here because the challenge was not a simple bug-fix task. The service already returned responses, but it was still failing the business in meaningful ways.

That first diagnosis helped surface the main issues:

- the moderation flow trusted a simple binary result too much
- there was no review path for borderline content
- the output was not explainable enough
- part of the available AI logic was unused
- some score-handling logic was incomplete

After that, I gave a more directed implementation prompt:

> So right now, I saw the problem is some part of the code is unused, and the result only trust a really simply binary moderation decision. So Lets enable the part unused, and also make sure:
> 1. Add a review channel, for content being hestitate to post, let get it into review channel.
> 2. Add more detailed in the simple discription tagging of the code, and make it explainable.
> 3. Finished the problem you recognized and debug it. (time limited)

That prompt was based on the diagnosis, not on guesswork.

I chose those instructions for three reasons:

- The code review showed that some useful logic already existed but was not being used, so enabling it was a high-value change.
- The business requirements showed that a binary allow-or-block decision was too rigid, so a review channel was needed for uncertain cases.
- Legal and Trust and Safety needed clearer reasoning, so explainability had to become part of the output.

Because the exercise was time-limited, I focused the prompt on practical, high-impact improvements instead of asking AI to redesign the entire system.

## Problems I Identified

- The moderation flow relied too heavily on a simple binary provider flag.
- The system had no review lane for borderline content.
- The response was not detailed enough to explain moderation decisions.
- A second AI client existed in the codebase but was not being used.
- The score-processing path was incomplete and needed debugging.

## Changes I Made

- Added a multi-stage moderation flow in `moderation_service.py`
- Introduced three outcomes: `allow`, `review`, and `block`
- Added threshold-based decision logic instead of trusting only a binary model result
- Enabled the unused Anthropic client as a secondary reviewer for ambiguous or sensitive cases
- Expanded the response model in `models.py` to include decision details, category scores, triggered categories, threshold settings, provider assessments, and review flags
- Improved the secondary reviewer in `mock_clients.py` so it returns more context-aware reasoning
- Fixed the score extraction logic so category scores are explicitly evaluated

## Why These Changes Solve the Problem

These changes make the moderation system more useful in practice.

The review channel creates a middle path for uncertain content, which helps reduce false positives without simply becoming less strict. The threshold-based logic makes the system more tunable, which is important when different moderation categories need different levels of sensitivity. The richer response model improves transparency by showing what the system detected, why it made a decision, and which model contributed to that decision.

Using the secondary reviewer also improves context handling. Cases like cooking, fitness, or medical language can now be reconsidered with more nuance, while subtle harmful content like supplement scams or coded hate speech can be escalated instead of being missed.

## Verification

I validated the solution by checking representative edge cases instead of relying on a single happy-path example.

The cases I focused on were:

- cooking content that can look violent out of context
- fitness content that can be misread as adult content
- supplement scam language that should not be missed
- borderline hate speech that needs escalation
- clearly unsafe violent content
- clearly safe everyday content

That matters because moderation systems should be judged by how they handle ambiguity, trade-offs, and edge cases, not only by whether an endpoint returns a response.

## Screen Recording Link
https://drive.google.com/file/d/1jtuHGHXOqQzyf8pG65KS9YohqYbMp7X9/view?usp=drive_link
