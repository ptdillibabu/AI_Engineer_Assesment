"""Critic agent implementation."""

import json
from typing import Optional

from .base import BaseAgent
from ..models.messages import CriticResponse, ProposerResponse
from ..llm.client import LLMClient
from ..prompts_template import format_critic_review, CRITIC_RETRY_MESSAGE


class Critic(BaseAgent):
    """The Critic agent challenges proposals and signals completion."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_path: Optional[str] = None,
        system_context: str = "",
    ):
        super().__init__(llm_client, prompt_path, system_context)
    
    def _default_prompt_path(self) -> str:
        return "prompts/critic.md"
    
    def respond(
        self,
        proposal: ProposerResponse,
        round_number: int,
        can_signal_satisfaction: bool = False,
    ) -> CriticResponse:
        """Review a proposal and generate challenges."""
        
        system_prompt = self._build_system_prompt()
        
        # Build user message using centralized template
        proposal_json = json.dumps(proposal.to_dict(), indent=2)
        user_message = format_critic_review(
            round_number=round_number,
            proposal_json=proposal_json,
            can_signal_satisfaction=can_signal_satisfaction,
        )
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Call LLM
        response_text = self.llm.chat(
            system_prompt=system_prompt,
            messages=self.conversation_history,
        )
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        # Parse response
        try:
            response_data = self._parse_json_response(response_text)
            response = CriticResponse.from_dict(response_data, round_number)
            response.raw_response = response_text
            return response
        except (json.JSONDecodeError, KeyError):
            # Retry once
            self.conversation_history.append({"role": "user", "content": CRITIC_RETRY_MESSAGE})
            
            response_text = self.llm.chat(
                system_prompt=system_prompt,
                messages=self.conversation_history,
            )
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            response_data = self._parse_json_response(response_text)
            response = CriticResponse.from_dict(response_data, round_number)
            response.raw_response = response_text
            return response
    
    def _parse_json_response(self, text: str) -> dict:
        """Extract and parse JSON from response text."""
        text = text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())