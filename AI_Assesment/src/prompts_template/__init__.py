"""Prompt templates module."""

from .templates import (
    # Proposer
    PROPOSER_INITIAL_MESSAGE,
    PROPOSER_RESPONSE_MESSAGE,
    PROPOSER_RETRY_MESSAGE,
    format_proposer_initial,
    format_proposer_response,
    
    # Critic
    CRITIC_REVIEW_MESSAGE,
    CRITIC_CAN_SIGNAL_SATISFACTION,
    CRITIC_CANNOT_SIGNAL_SATISFACTION,
    CRITIC_RETRY_MESSAGE,
    format_critic_review,
    
    # Summarizer
    SUMMARIZER_MESSAGE,
    SUMMARIZER_RETRY_MESSAGE,
    format_summarizer_message,
)

__all__ = [
    "PROPOSER_INITIAL_MESSAGE",
    "PROPOSER_RESPONSE_MESSAGE", 
    "PROPOSER_RETRY_MESSAGE",
    "format_proposer_initial",
    "format_proposer_response",
    "CRITIC_REVIEW_MESSAGE",
    "CRITIC_CAN_SIGNAL_SATISFACTION",
    "CRITIC_CANNOT_SIGNAL_SATISFACTION",
    "CRITIC_RETRY_MESSAGE",
    "format_critic_review",
    "SUMMARIZER_MESSAGE",
    "SUMMARIZER_RETRY_MESSAGE",
    "format_summarizer_message",
]