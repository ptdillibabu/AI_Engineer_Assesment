"""Proposer agent implementation."""

import json
from typing import Optional

from .base import BaseAgent
from ..models.messages import ProposerResponse, Challenge
from ..llm.client import LLMClient
from ..prompts_template import (
    format_proposer_initial,
    format_proposer_response,
    PROPOSER_RETRY_MESSAGE,
)


class Proposer(BaseAgent):
    """The Proposer agent interprets requests and defends proposals."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_path: Optional[str] = None,
        system_context: str = "",
    ):
        super().__init__(llm_client, prompt_path, system_context)
    
    def _default_prompt_path(self) -> str:
        return "prompts/proposer.md"
    
    def respond(
        self,
        feature_request: str,
        round_number: int,
        previous_challenges: list[Challenge] = None,
    ) -> ProposerResponse:
        """Generate a proposal or respond to challenges."""
        
        system_prompt = self._build_system_prompt()
        
        # Build user message based on round
        if round_number == 1:
            user_message = format_proposer_initial(feature_request)
        else:
            challenges_text = "\n".join([
                f"- **{c.id}** [{c.category.value}]: {c.description}"
                for c in previous_challenges
            ])
            user_message = format_proposer_response(round_number, challenges_text)
        
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
            response = ProposerResponse.from_dict(response_data, round_number)
            response.raw_response = response_text
            return response
        except (json.JSONDecodeError, KeyError) as e:
            # Retry once with a nudge
            self.conversation_history.append({"role": "user", "content": PROPOSER_RETRY_MESSAGE})
            
            response_text = self.llm.chat(
                system_prompt=system_prompt,
                messages=self.conversation_history,
            )
            self.conversation_history.append({"role": "assistant", "content": response_text})           
            response_data = self._parse_json_response(response_text)
            response = ProposerResponse.from_dict(response_data, round_number)
            response.raw_response = response_text
            return response
    
    def _parse_json_response(self, text: str) -> dict:
        """Extract and parse JSON from response text."""
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        return json.loads(text)