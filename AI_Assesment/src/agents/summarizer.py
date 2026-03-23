"""Summarizer agent implementation."""

import json
from typing import Optional

from .base import BaseAgent
from ..models.messages import ProposerResponse, CriticResponse
from ..models.decision_document import (
    DecisionDocument, ScopeItem, AssumptionResult, OpenQuestion
)
from ..llm.client import LLMClient
from ..prompts_template import format_summarizer_message, SUMMARIZER_RETRY_MESSAGE


class Summarizer(BaseAgent):
    """The Summarizer agent synthesizes deliberation into a decision document."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_path: Optional[str] = None,
        system_context: str = "",
    ):
        super().__init__(llm_client, prompt_path, system_context)
    
    def _default_prompt_path(self) -> str:
        return "prompts/summarizer.md"
    
    def respond(
        self,
        feature_request: str,
        deliberation_trace: list[dict],
        final_proposer: ProposerResponse,
        final_critic: CriticResponse,
        termination_reason: str,
    ) -> DecisionDocument:
        """Synthesize the deliberation into a decision document."""
        
        system_prompt = self._build_system_prompt()
        
        # Build trace text
        trace_text = self._format_trace(deliberation_trace)
        
        # Build the synthesis request using centralized template
        user_message = format_summarizer_message(
            feature_request=feature_request,
            deliberation_trace=trace_text,
            final_proposer=json.dumps(final_proposer.to_dict(), indent=2),
            final_critic=json.dumps(final_critic.to_dict(), indent=2),
            termination_reason=termination_reason,
        )
        
        # Call LLM
        response_text = self.llm.chat(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        
        # Parse and build decision document
        try:
            response_data = self._parse_json_response(response_text)
            return self._build_decision_document(
                feature_request,
                response_data,
                deliberation_trace,
                final_proposer,
                final_critic,
                termination_reason,
            )
        except (json.JSONDecodeError, KeyError):
            # Retry once
            retry_response = self.llm.chat(
                system_prompt=system_prompt,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response_text},
                    {"role": "user", "content": SUMMARIZER_RETRY_MESSAGE},
                ],
            )
            
            try:
                response_data = self._parse_json_response(retry_response)
                return self._build_decision_document(
                    feature_request,
                    response_data,
                    deliberation_trace,
                    final_proposer,
                    final_critic,
                    termination_reason,
                )
            except (json.JSONDecodeError, KeyError):
                # Fallback: build from final state without summarizer
                return self._build_fallback_document(
                    feature_request,
                    deliberation_trace,
                    final_proposer,
                    final_critic,
                    termination_reason,
                )
    
    def _format_trace(self, trace: list[dict]) -> str:
        """Format deliberation trace for the prompt."""
        trace_text = ""
        for entry in trace:
            round_num = entry.get("round", "?")
            agent = entry.get("agent", "unknown")
            content = json.dumps(entry.get("content", {}), indent=2)
            trace_text += f"\n### Round {round_num} - {agent.upper()}\n```json\n{content}\n```\n"
        return trace_text

    def _parse_json_response(self, text: str) -> dict:
        """Extract and parse JSON from response text."""
        text = text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        return json.loads(text)
    
    def _build_decision_document(
        self,
        feature_request: str,
        summary_data: dict,
        trace: list[dict],
        final_proposer: ProposerResponse,
        final_critic: CriticResponse,
        termination_reason: str,
    ) -> DecisionDocument:
        """Build DecisionDocument from summarizer output."""
        
        # Parse scope
        agreed_scope = summary_data.get("agreed_scope", {})
        included = [
            ScopeItem(item=s["item"], rationale=s.get("rationale", ""))
            for s in agreed_scope.get("included", [])
        ]
        excluded = [
            ScopeItem(item=s["item"], rationale=s.get("rationale", ""))
            for s in agreed_scope.get("excluded", [])
        ]
        
        # Parse assumptions
        assumptions = [
            AssumptionResult(
                assumption=a["assumption"],
                challenged=a.get("challenged", False),
                resolution=a.get("resolution", "ACCEPTED"),
                final_rationale=a.get("final_rationale", ""),
            )
            for a in summary_data.get("assumptions", [])
        ]
        
        # Parse open questions
        open_questions = [
            OpenQuestion(
                question=q["question"],
                context=q.get("context", ""),
                suggested_stakeholder=q.get("suggested_stakeholder", "Product Owner"),
            )
            for q in summary_data.get("open_questions", [])
        ]
        
        # Get metadata
        delib_summary = summary_data.get("deliberation_summary", {})
        
        return DecisionDocument(
            feature_request=feature_request,
            feature_request_summary=summary_data.get("feature_request_summary", ""),
            included_scope=included,
            excluded_scope=excluded,
            assumptions=assumptions,
            open_questions=open_questions,
            total_rounds=delib_summary.get("total_rounds", len(trace) // 2),
            termination_reason=termination_reason,
            proposer_final_confidence=final_proposer.confidence_score,
            critic_final_confidence=final_critic.confidence_score,
            key_tensions=delib_summary.get("key_tensions", []),
            deliberation_trace=trace,
        )
    
    def _build_fallback_document(
        self,
        feature_request: str,
        trace: list[dict],
        final_proposer: ProposerResponse,
        final_critic: CriticResponse,
        termination_reason: str,
    ) -> DecisionDocument:
        """Build DecisionDocument directly from final state (no summarizer)."""
        
        # Extract from final proposer response
        included = [
            ScopeItem(item=s, rationale="From final proposal")
            for s in final_proposer.proposed_scope.get("included", [])
        ]
        excluded = [
            ScopeItem(item=s, rationale="From final proposal")
            for s in final_proposer.proposed_scope.get("excluded", [])
        ]
        
        assumptions = [
            AssumptionResult(
                assumption=a.assumption,
                challenged=(a.status != "MAINTAINED"),
                resolution="REVISED" if a.status == "REVISED" else "ACCEPTED",
                final_rationale=a.rationale,
            )
            for a in final_proposer.assumptions
        ]
        
        open_questions = [
            OpenQuestion(
                question=concern,
                context="Identified by Critic",
                suggested_stakeholder="Product Owner",
            )
            for concern in final_critic.remaining_concerns
        ]
        
        return DecisionDocument(
            feature_request=feature_request,
            feature_request_summary=summary_data.get("feature_request_summary") or "Feature request deliberation completed",
            included_scope=included,
            excluded_scope=excluded,
            assumptions=assumptions,
            open_questions=open_questions,
            total_rounds=len(trace) // 2,
            termination_reason=termination_reason,
            proposer_final_confidence=final_proposer.confidence_score,
            critic_final_confidence=final_critic.confidence_score,
            key_tensions=delib_summary.get("key_tensions", []),
            deliberation_trace=trace,
        )