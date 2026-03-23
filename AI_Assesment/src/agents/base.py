"""Base agent interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..llm.client import LLMClient


class BaseAgent(ABC):
    """Abstract base class for deliberation agents."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompt_path: Optional[str] = None,
        system_context: str = "",
    ):
        self.llm = llm_client
        self.system_context = system_context
        self.prompt_template = self._load_prompt(prompt_path)
        self.conversation_history: list[dict] = []
    
    def _load_prompt(self, prompt_path: Optional[str]) -> str:
        """Load prompt template from file."""
        if prompt_path is None:
            prompt_path = self._default_prompt_path()
        
        path = Path(prompt_path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        
        # Fallback to prompts directory relative to project root
        fallback_path = Path(__file__).parent.parent.parent / "prompts" / path.name
        if fallback_path.exists():
            return fallback_path.read_text(encoding="utf-8")
        
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    @abstractmethod
    def _default_prompt_path(self) -> str:
        """Return the default prompt file path for this agent."""
        pass
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with context substitution."""
        return self.prompt_template.replace("{{system_context}}", self.system_context)
    
    def reset(self):
        """Reset conversation history for a new deliberation."""
        self.conversation_history = []
    
    @abstractmethod
    def respond(self, **kwargs):
        """Generate a response. Implementation varies by agent type."""
        pass