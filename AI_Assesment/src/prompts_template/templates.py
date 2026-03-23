"""Centralized prompt templates for all agents.

This file contains all prompts used by the deliberation agents as user message.
Prompts are clearly visible and separated from orchestration logic.
"""

# =============================================================================
# PROPOSER PROMPTS
# =============================================================================

PROPOSER_INITIAL_MESSAGE = """## Feature Request to Analyze

"{feature_request}"

## Your Task (Round 1)

Produce an initial structured proposal for this feature request. Include:
1. Proposed scope (what's included and excluded)
2. Assumptions you are making (surface the implicit!)
3. Success criteria (measurable)

Remember: Be concrete enough to be challenged. Surface hidden assumptions.

Respond with valid JSON only."""


PROPOSER_RESPONSE_MESSAGE = """## Round {round_number} - Respond to Critic's Challenges

The Critic has raised the following challenges to your proposal:

{challenges_text}

## Your Task

For each challenge, you must either:
- **DEFEND**: Maintain your position with specific reasoning
- **REVISE**: Adjust your proposal based on the valid point
- **CONCEDE**: Acknowledge this should be an open question

Update your proposal accordingly. Remember: Don't cave on everything - defend positions unless given a convincing reason to change.

Respond with valid JSON only."""


PROPOSER_RETRY_MESSAGE = """Your response was not valid JSON. Please respond with ONLY valid JSON matching the specified format. No markdown, no explanations."""


# =============================================================================
# CRITIC PROMPTS
# =============================================================================

CRITIC_REVIEW_MESSAGE = """## Round {round_number} - Review Proposer's Response

The Proposer has submitted the following:

{proposal_json}

## Your Task

1. Identify specific weaknesses, gaps, or risks in the proposal
2. Challenge assumptions that seem unfounded
3. Probe for missing constraints or edge cases

{satisfaction_instruction}

Remember: Be specific in your challenges. "This is too vague" is not sufficient.

Respond with valid JSON only."""


CRITIC_CAN_SIGNAL_SATISFACTION = """If the proposal is now robust enough, you MAY signal satisfaction. But do not signal satisfaction just to end the conversation - only if genuinely satisfied."""


CRITIC_CANNOT_SIGNAL_SATISFACTION = """You CANNOT signal satisfaction this round (minimum rounds not met). Focus on strengthening the proposal."""


CRITIC_RETRY_MESSAGE = """Your response was not valid JSON. Please respond with ONLY valid JSON matching the specified format. No markdown, no explanations."""


# =============================================================================
# SUMMARIZER PROMPTS
# =============================================================================

SUMMARIZER_MESSAGE = """## Generate Decision Document

Based on the complete deliberation trace below, produce a final decision document.

### Feature Request
"{feature_request}"

### Deliberation Trace
{deliberation_trace}

### Final Proposer Position
{final_proposer}

### Final Critic Position
{final_critic}

### Termination Reason
{termination_reason}

## Your Task

Synthesize the deliberation into a structured decision document containing:
1. **Agreed Scope** - What the feature will and will not include
2. **Surfaced Assumptions** - What was assumed, challenged, or accepted
3. **Open Questions** - What remains unresolved and requires human input
4. **Key Tensions** - Major disagreements that emerged

Be objective. Capture the real tension from the dialogue, not a generic summary.

Respond with valid JSON only."""


SUMMARIZER_RETRY_MESSAGE = """Your response was not valid JSON. Please respond with ONLY valid JSON matching the specified format. No markdown, no explanations."""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_proposer_initial(feature_request: str) -> str:
    """Format the initial proposer message."""
    return PROPOSER_INITIAL_MESSAGE.format(feature_request=feature_request)


def format_proposer_response(round_number: int, challenges_text: str) -> str:
    """Format the proposer response message."""
    return PROPOSER_RESPONSE_MESSAGE.format(
        round_number=round_number,
        challenges_text=challenges_text,
    )


def format_critic_review(
    round_number: int,
    proposal_json: str,
    can_signal_satisfaction: bool,
) -> str:
    """Format the critic review message."""
    satisfaction_instruction = (
        CRITIC_CAN_SIGNAL_SATISFACTION if can_signal_satisfaction
        else CRITIC_CANNOT_SIGNAL_SATISFACTION
    )
    return CRITIC_REVIEW_MESSAGE.format(
        round_number=round_number,
        proposal_json=proposal_json,
        satisfaction_instruction=satisfaction_instruction,
    )


def format_summarizer_message(
    feature_request: str,
    deliberation_trace: str,
    final_proposer: str,
    final_critic: str,
    termination_reason: str,
) -> str:
    """Format the summarizer message."""
    return SUMMARIZER_MESSAGE.format(
        feature_request=feature_request,
        deliberation_trace=deliberation_trace,
        final_proposer=final_proposer,
        final_critic=final_critic,
        termination_reason=termination_reason,
    )