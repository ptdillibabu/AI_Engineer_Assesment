"""Deliberation orchestrator - manages the multi-round dialogue."""

from typing import Optional

from .agents import Proposer, Critic, Summarizer
from .models import (
    ProposerResponse,
    CriticResponse,
    DecisionDocument,
    TerminationState,
    TerminationReason,
)
from .llm import LLMClient
from .utils import DeliberationLogger


class DeliberationOrchestrator:
    """Orchestrates the deliberation between Proposer and Critic agents."""
    
    def __init__(
        self,
        llm_config: dict,
        system_context: str,
        min_rounds: int = 2,
        max_rounds: int = 6,
        use_summarizer: bool = True,
        logger: Optional[DeliberationLogger] = None,
    ):
        self.system_context = system_context
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        self.use_summarizer = use_summarizer
        self.logger = logger or DeliberationLogger()
        
        # Initialize LLM client
        self.llm = LLMClient(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4o-mini"),
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 2000),
        )
        
        # Initialize agents
        self.proposer = Proposer(
            llm_client=self.llm,
            system_context=system_context,
        )
        self.critic = Critic(
            llm_client=self.llm,
            system_context=system_context,
        )
        self.summarizer = Summarizer(
            llm_client=self.llm,
            system_context=system_context,
        ) if use_summarizer else None
    
    def run(self, feature_request: str) -> DecisionDocument:
        """Run the full deliberation process."""
        
        # Reset agents for fresh deliberation
        self.proposer.reset()
        self.critic.reset()
        
        # Initialize state
        state = TerminationState(
            min_rounds=self.min_rounds,
            max_rounds=self.max_rounds,
        )
        
        self.logger.log_start(feature_request, self.system_context)
        
        proposer_response: Optional[ProposerResponse] = None
        critic_response: Optional[CriticResponse] = None
        all_challenges = []
        
        # Main deliberation loop
        while not state.should_terminate:
            state.current_round += 1
            
            # === PROPOSER TURN ===
            previous_challenges = critic_response.new_challenges if critic_response else []
            
            proposer_response = self.proposer.respond(
                feature_request=feature_request,
                round_number=state.current_round,
                previous_challenges=previous_challenges,
            )
            
            self.logger.log_proposer_turn(
                state.current_round,
                proposer_response.to_dict(),
            )
            
            # === CRITIC TURN ===
            can_signal_satisfaction = state.current_round >= self.min_rounds
            
            critic_response = self.critic.respond(
                proposal=proposer_response,
                round_number=state.current_round,
                can_signal_satisfaction=can_signal_satisfaction,
            )
            
            self.logger.log_critic_turn(
                state.current_round,
                critic_response.to_dict(),
            )
            
            # Track all challenges for stagnation detection
            all_challenges.extend(critic_response.new_challenges)
            
            # === UPDATE TERMINATION STATE ===
            state.critic_satisfied = critic_response.satisfaction_signal
            state.check_stagnation(critic_response.new_challenges)
        
        # === GENERATE FINAL OUTPUT ===
        termination_reason = state.termination_reason.value
        self.logger.log_termination(termination_reason, state.current_round)
        
        # Generate decision document
        if self.summarizer and proposer_response and critic_response:
            document = self.summarizer.respond(
                feature_request=feature_request,
                deliberation_trace=self.logger.get_trace(),
                final_proposer=proposer_response,
                final_critic=critic_response,
                termination_reason=termination_reason,
            )
        else:
            # Fallback without summarizer
            document = self._build_basic_document(
                feature_request,
                proposer_response,
                critic_response,
                state,
            )
        
        # Log and save
        self.logger.log_output(document.to_markdown())
        self.logger.save()
        
        return document
    
    def _build_basic_document(
        self,
        feature_request: str,
        proposer: ProposerResponse,
        critic: CriticResponse,
        state: TerminationState,
    ) -> DecisionDocument:
        """Build a basic decision document without summarizer."""
        from .models.decision_document import ScopeItem, AssumptionResult, OpenQuestion
        
        included = [
            ScopeItem(item=s, rationale="From final proposal")
            for s in proposer.proposed_scope.get("included", [])
        ]
        excluded = [
            ScopeItem(item=s, rationale="From final proposal")
            for s in proposer.proposed_scope.get("excluded", [])
        ]
        
        assumptions = [
            AssumptionResult(
                assumption=a.assumption,
                challenged=(a.status != "MAINTAINED"),
                resolution="REVISED" if a.status == "REVISED" else "ACCEPTED",
                final_rationale=a.rationale,
            )
            for a in proposer.assumptions
        ]
        
        open_questions = [
            OpenQuestion(
                question=concern,
                context="Identified during deliberation",
                suggested_stakeholder="Product Owner",
            )
            for concern in critic.remaining_concerns
        ]
        
        return DecisionDocument(
            feature_request=feature_request,
            feature_request_summary="Deliberation completed",
            included_scope=included,
            excluded_scope=excluded,
            assumptions=assumptions,
            open_questions=open_questions,
            total_rounds=state.current_round,
            termination_reason=state.termination_reason.value,
            proposer_final_confidence=proposer.confidence_score,
            critic_final_confidence=critic.confidence_score,
            key_tensions=[],
            deliberation_trace=self.logger.get_trace(),
        )