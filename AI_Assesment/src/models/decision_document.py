"""Decision document output model."""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class ScopeItem:
    item: str
    rationale: str


@dataclass
class AssumptionResult:
    assumption: str
    challenged: bool
    resolution: str  # ACCEPTED, REVISED, REQUIRES_HUMAN_INPUT
    final_rationale: str


@dataclass
class OpenQuestion:
    question: str
    context: str
    suggested_stakeholder: str


@dataclass
class DecisionDocument:
    """Final output of the deliberation process."""
    
    feature_request: str
    feature_request_summary: str
    
    # Agreed scope
    included_scope: list[ScopeItem] = field(default_factory=list)
    excluded_scope: list[ScopeItem] = field(default_factory=list)
    
    # Assumptions
    assumptions: list[AssumptionResult] = field(default_factory=list)
    
    # Open questions
    open_questions: list[OpenQuestion] = field(default_factory=list)
    
    # Metadata
    total_rounds: int = 0
    termination_reason: str = ""
    proposer_final_confidence: float = 0.0
    critic_final_confidence: float = 0.0
    key_tensions: list[str] = field(default_factory=list)
    
    # Full trace for inspection
    deliberation_trace: list[dict] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Generate a Markdown representation of the decision document."""
        lines = [
            "# Decision Document",
            "",
            f"**Original Request:** {self.feature_request}",
            "",
            f"**Summary:** {self.feature_request_summary}",
            "",
            "---",
            "",
            "## Agreed Scope",
            "",
            "### Included",
        ]
        
        for item in self.included_scope:
            lines.append(f"- **{item.item}**")
            lines.append(f"  - *Rationale:* {item.rationale}")
        
        lines.extend(["", "### Excluded"])
        for item in self.excluded_scope:
            lines.append(f"- **{item.item}**")
            lines.append(f"  - *Rationale:* {item.rationale}")
        
        lines.extend(["", "---", "", "## Assumptions"])
        for a in self.assumptions:
            status_icon = "✅" if a.resolution == "ACCEPTED" else "⚠️" if a.resolution == "REVISED" else "❓"
            lines.append(f"- {status_icon} **{a.assumption}**")
            lines.append(f"  - *Challenged:* {'Yes' if a.challenged else 'No'}")
            lines.append(f"  - *Resolution:* {a.resolution}")
            lines.append(f"  - *Rationale:* {a.final_rationale}")
        
        lines.extend(["", "---", "", "## Open Questions (Require Human Input)"])
        for q in self.open_questions:
            lines.append(f"### {q.question}")
            lines.append(f"- *Context:* {q.context}")
            lines.append(f"- *Suggested Stakeholder:* {q.suggested_stakeholder}")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## Deliberation Metadata",
            "",
            f"- **Total Rounds:** {self.total_rounds}",
            f"- **Termination Reason:** {self.termination_reason}",
            f"- **Proposer Final Confidence:** {self.proposer_final_confidence:.0%}",
            f"- **Critic Final Confidence:** {self.critic_final_confidence:.0%}",
            "",
            "### Key Tensions",
        ])
        for tension in self.key_tensions:
            lines.append(f"- {tension}")
        
        return "\n".join(lines)

    def to_json(self) -> str:
        """Generate a JSON representation."""
        return json.dumps({
            "feature_request": self.feature_request,
            "feature_request_summary": self.feature_request_summary,
            "agreed_scope": {
                "included": [{"item": s.item, "rationale": s.rationale} for s in self.included_scope],
                "excluded": [{"item": s.item, "rationale": s.rationale} for s in self.excluded_scope],
            },
            "assumptions": [
                {
                    "assumption": a.assumption,
                    "challenged": a.challenged,
                    "resolution": a.resolution,
                    "final_rationale": a.final_rationale,
                }
                for a in self.assumptions
            ],
            "open_questions": [
                {
                    "question": q.question,
                    "context": q.context,
                    "suggested_stakeholder": q.suggested_stakeholder,
                }
                for q in self.open_questions
            ],
            "metadata": {
                "total_rounds": self.total_rounds,
                "termination_reason": self.termination_reason,
                "proposer_final_confidence": self.proposer_final_confidence,
                "critic_final_confidence": self.critic_final_confidence,
                "key_tensions": self.key_tensions,
            },
        }, indent=2)