"""Deliberation logging utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


class DeliberationLogger:
    """Logger for tracking and displaying deliberation progress."""
    
    def __init__(
        self,
        save_trace: bool = True,
        trace_dir: str = "output",
        verbose: bool = True,
    ):
        self.save_trace = save_trace
        self.trace_dir = Path(trace_dir)
        self.verbose = verbose
        self.console = Console()
        self.trace: list[dict] = []
        
        if self.save_trace:
            self.trace_dir.mkdir(parents=True, exist_ok=True)
    
    def log_start(self, feature_request: str, system_context: str):
        """Log deliberation start."""
        self.console.print(Panel(
            f"[bold]Feature Request:[/bold]\n{feature_request}",
            title="🚀 Deliberation Started",
            border_style="green",
        ))
        
        self.trace.append({
            "event": "start",
            "timestamp": datetime.now().isoformat(),
            "feature_request": feature_request,
        })
    
    def log_proposer_turn(self, round_number: int, response: dict):
        """Log a Proposer turn."""
        self.console.print(f"\n[bold cyan]━━━ Round {round_number}: PROPOSER ━━━[/bold cyan]")
        
        if self.verbose:
            # Display scope
            scope = response.get("proposed_scope", {})
            self.console.print("[green]Included:[/green]")
            for item in scope.get("included", []):
                self.console.print(f"  • {item}")
            
            self.console.print("[red]Excluded:[/red]")
            for item in scope.get("excluded", []):
                self.console.print(f"  • {item}")
            
            # Display assumptions
            self.console.print("[yellow]Assumptions:[/yellow]")
            for a in response.get("assumptions", []):
                conf = a.get("confidence", "?")
                self.console.print(f"  [{conf}] {a.get('assumption', '')}")
            
            # Display confidence
            conf_score = response.get("confidence_score", 0)
            self.console.print(f"[bold]Confidence: {conf_score:.0%}[/bold]")
        
        self.trace.append({
            "event": "proposer_turn",
            "round": round_number,
            "agent": "proposer",
            "content": response,
            "timestamp": datetime.now().isoformat(),
        })
    
    def log_critic_turn(self, round_number: int, response: dict):
        """Log a Critic turn."""
        self.console.print(f"\n[bold magenta]━━━ Round {round_number}: CRITIC ━━━[/bold magenta]")
        
        if self.verbose:
            # Display assessment
            assessment = response.get("assessment", "")
            self.console.print(f"[dim]{assessment}[/dim]")
            
            # Display new challenges
            challenges = response.get("new_challenges", [])
            if challenges:
                self.console.print("[red]New Challenges:[/red]")
                for c in challenges:
                    cat = c.get("category", "?")
                    desc = c.get("description", "")
                    self.console.print(f"  [{cat}] {desc}")
            
            # Display resolved
            resolved = response.get("resolved_challenge_ids", [])
            if resolved:
                self.console.print(f"[green]Resolved: {', '.join(resolved)}[/green]")
            
            # Display satisfaction
            satisfied = response.get("satisfaction_signal", False)
            if satisfied:
                self.console.print("[bold green]✓ Critic signals SATISFACTION[/bold green]")
                rationale = response.get("satisfaction_rationale", "")
                if rationale:
                    self.console.print(f"  {rationale}")
            
            # Display confidence
            conf_score = response.get("confidence_score", 0)
            self.console.print(f"[bold]Confidence: {conf_score:.0%}[/bold]")
        
        self.trace.append({
            "event": "critic_turn",
            "round": round_number,
            "agent": "critic",
            "content": response,
            "timestamp": datetime.now().isoformat(),
        })
    
    def log_termination(self, reason: str, total_rounds: int):
        """Log deliberation termination."""
        self.console.print(Panel(
            f"[bold]Reason:[/bold] {reason}\n[bold]Total Rounds:[/bold] {total_rounds}",
            title="🏁 Deliberation Complete",
            border_style="blue",
        ))
        
        self.trace.append({
            "event": "termination",
            "reason": reason,
            "total_rounds": total_rounds,
            "timestamp": datetime.now().isoformat(),
        })
    
    def log_output(self, document_text: str):
        """Log the final decision document."""
        self.console.print("\n")
        self.console.print(Panel(
            Markdown(document_text),
            title="📄 Decision Document",
            border_style="green",
        ))
    
    def save(self, filename: Optional[str] = None) -> Path:
        """Save the trace to a file."""
        if not self.save_trace:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"deliberation_trace_{timestamp}.json"
        
        output_path = self.trace_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.trace, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"[dim]Trace saved to: {output_path}[/dim]")
        return output_path
    
    def get_trace(self) -> list[dict]:
        """Get the deliberation trace."""
        return self.trace