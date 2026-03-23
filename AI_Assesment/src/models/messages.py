"""Message types for agent communication."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChallengeCategory(Enum):
    ASSUMPTION = "ASSUMPTION"
    SCOPE_RISK = "SCOPE_RISK"
    MISSING_CONSTRAINT = "MISSING_CONSTRAINT"
    AMBIGUITY = "AMBIGUITY"
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"


class ChallengeStatus(Enum):
    PENDING = "PENDING"
    ADDRESSED = "ADDRESSED"
    CONCEDED = "CONCEDED"
    DEFENDED = "DEFENDED"


class ResponseAction(Enum):
    DEFEND = "DEFEND"
    REVISE = "REVISE"
    CONCEDE = "CONCEDE"


@dataclass
class Challenge:
    """A specific challenge raised by the Critic."""
    id: str
    category: ChallengeCategory
    description: str
    status: ChallengeStatus = ChallengeStatus.PENDING
    response: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Challenge":
        return cls(
            id=data["id"],
            category=ChallengeCategory(data.get("category", "ASSUMPTION")),
            description=data["description"],
            status=ChallengeStatus(data.get("status", "PENDING")),
            response=data.get("response"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "description": self.description,
            "status": self.status.value,
            "response": self.response,
        }


@dataclass
class Assumption:
    """An assumption surfaced by the Proposer."""
    id: str
    assumption: str
    confidence: str  # HIGH, MEDIUM, LOW
    rationale: str
    status: str = "MAINTAINED"  # MAINTAINED, REVISED, WITHDRAWN

    @classmethod
    def from_dict(cls, data: dict) -> "Assumption":
        return cls(
            id=data.get("id", "A0"),
            assumption=data["assumption"],
            confidence=data.get("confidence", "MEDIUM"),
            rationale=data.get("rationale", ""),
            status=data.get("status", "MAINTAINED"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assumption": self.assumption,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "status": self.status,
        }


@dataclass
class ChallengeResponse:
    """Proposer's response to a specific challenge."""
    challenge_id: str
    action: ResponseAction
    response: str

    @classmethod
    def from_dict(cls, data: dict) -> "ChallengeResponse":
        return cls(
            challenge_id=data["challenge_id"],
            action=ResponseAction(data["action"]),
            response=data["response"],
        )

    def to_dict(self) -> dict:
        return {
            "challenge_id": self.challenge_id,
            "action": self.action.value,
            "response": self.response,
        }


@dataclass
class ProposerResponse:
    """Structured response from the Proposer agent."""
    round_number: int
    proposed_scope: dict  # {included: [], excluded: []}
    assumptions: list[Assumption]
    success_criteria: list[str]
    challenge_responses: list[ChallengeResponse] = field(default_factory=list)
    confidence_score: float = 0.5
    raw_response: str = ""

    @classmethod
    def from_dict(cls, data: dict, round_number: int) -> "ProposerResponse":
        assumptions = [
            Assumption.from_dict(a) for a in data.get("assumptions", [])
        ]
        challenge_responses = [
            ChallengeResponse.from_dict(cr) 
            for cr in data.get("challenge_responses", [])
        ]
        return cls(
            round_number=round_number,
            proposed_scope=data.get("proposed_scope", {"included": [], "excluded": []}),
            assumptions=assumptions,
            success_criteria=data.get("success_criteria", []),
            challenge_responses=challenge_responses,
            confidence_score=float(data.get("confidence_score", 0.5)),
        )

    def to_dict(self) -> dict:
        return {
            "round_number": self.round_number,
            "proposed_scope": self.proposed_scope,
            "assumptions": [a.to_dict() for a in self.assumptions],
            "success_criteria": self.success_criteria,
            "challenge_responses": [cr.to_dict() for cr in self.challenge_responses],
            "confidence_score": self.confidence_score,
        }


@dataclass
class CriticResponse:
    """Structured response from the Critic agent."""
    round_number: int
    new_challenges: list[Challenge]
    resolved_challenge_ids: list[str]
    assessment: str
    satisfaction_signal: bool
    satisfaction_rationale: Optional[str]
    remaining_concerns: list[str]
    confidence_score: float = 0.5
    raw_response: str = ""

    @classmethod
    def from_dict(cls, data: dict, round_number: int) -> "CriticResponse":
        challenges = [
            Challenge.from_dict(c) for c in data.get("new_challenges", [])
        ]
        return cls(
            round_number=round_number,
            new_challenges=challenges,
            resolved_challenge_ids=data.get("resolved_challenge_ids", []),
            assessment=data.get("assessment", ""),
            satisfaction_signal=data.get("satisfaction_signal", False),
            satisfaction_rationale=data.get("satisfaction_rationale"),
            remaining_concerns=data.get("remaining_concerns", []),
            confidence_score=float(data.get("confidence_score", 0.5)),
        )

    def to_dict(self) -> dict:
        return {
            "round_number": self.round_number,
            "new_challenges": [c.to_dict() for c in self.new_challenges],
            "resolved_challenge_ids": self.resolved_challenge_ids,
            "assessment": self.assessment,
            "satisfaction_signal": self.satisfaction_signal,
            "satisfaction_rationale": self.satisfaction_rationale,
            "remaining_concerns": self.remaining_concerns,
            "confidence_score": self.confidence_score,
        }