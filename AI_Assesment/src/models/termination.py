"""Termination state and logic."""

from dataclasses import dataclass
from enum import Enum


class TerminationReason(Enum):
    CRITIC_SATISFIED = "critic_satisfied"
    MAX_ROUNDS_REACHED = "max_rounds_reached"
    STAGNATION_DETECTED = "stagnation_detected"
    ERROR = "error"


@dataclass
class TerminationState:
    """Tracks deliberation termination conditions."""
    
    current_round: int = 0
    min_rounds: int = 2
    max_rounds: int = 6
    critic_satisfied: bool = False
    stagnation_detected: bool = False
    error_occurred: bool = False
    
    # For stagnation detection
    previous_challenge_hashes: set = None
    
    def __post_init__(self):
        if self.previous_challenge_hashes is None:
            self.previous_challenge_hashes = set()
    
    @property
    def min_rounds_met(self) -> bool:
        return self.current_round >= self.min_rounds
    
    @property
    def max_rounds_reached(self) -> bool:
        return self.current_round >= self.max_rounds
    
    @property
    def should_terminate(self) -> bool:
        """Determine if deliberation should end."""
        # Always terminate on error
        if self.error_occurred:
            return True
        
        # Hard stop at max rounds
        if self.max_rounds_reached:
            return True
        
        # Semantic termination: critic satisfied after minimum rounds
        if self.min_rounds_met and self.critic_satisfied:
            return True
        
        # Stagnation: same challenges cycling
        if self.min_rounds_met and self.stagnation_detected:
            return True
        
        return False
    
    @property
    def termination_reason(self) -> TerminationReason:
        """Get the reason for termination."""
        if self.error_occurred:
            return TerminationReason.ERROR
        if self.critic_satisfied and self.min_rounds_met:
            return TerminationReason.CRITIC_SATISFIED
        if self.stagnation_detected:
            return TerminationReason.STAGNATION_DETECTED
        if self.max_rounds_reached:
            return TerminationReason.MAX_ROUNDS_REACHED
        return None
    
    def check_stagnation(self, new_challenges: list) -> bool:
        """Check if we're seeing repeated challenges."""
        # Hash challenges by their description (first 50 chars)
        new_hashes = {c.description[:50] for c in new_challenges}
        
        # If all new challenges were seen before, we're stagnating
        if new_hashes and new_hashes.issubset(self.previous_challenge_hashes):
            self.stagnation_detected = True
            return True
        
        # Update history
        self.previous_challenge_hashes.update(new_hashes)
        return False