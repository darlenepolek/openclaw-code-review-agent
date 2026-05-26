"""
Base Agent class for the multi-agent review system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import anthropic


class Severity(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    HIGH = "critical"
    CRITICAL = "security-critical"


@dataclass
class ReviewIssue:
    """Represents a code review issue."""
    severity: Severity
    file: str
    line: int
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class ReviewResult:
    """Result from an agent's review."""
    agent_name: str
    issues: List[ReviewIssue]
    summary: str
    tokens_used: int


class BaseAgent(ABC):
    """Abstract base class for review agents."""
    
    def __init__(self, claude_client: anthropic.Anthropic, model: str = "claude-3-opus-20240229"):
        self.client = claude_client
        self.model = model
        self._system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    def analyze(self, diff: str, files: dict[str, str]) -> ReviewResult:
        """Analyze code and return review results."""
        pass
    
    def _query_claude(self, user_message: str) -> tuple[str, int]:
        """Query Claude API and return response + token count."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text, tokens_used
