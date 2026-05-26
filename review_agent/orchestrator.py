"""
Orchestrator - Coordinates multiple agents for comprehensive code review.
"""

import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor
import anthropic

from .agents import (
    CodeParserAgent,
    SecurityScannerAgent,
    PerformanceAnalyzerAgent,
    ArchitectureReviewerAgent,
)
from .agents.base import ReviewResult


class ReviewOrchestrator:
    """
    Orchestrates multiple specialized agents to perform comprehensive code review.
    
    This implements the multi-agent collaboration pattern where specialized agents
    work in parallel on different aspects of the code, then their findings are
    synthesized by Claude into a coherent review.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Initialize all specialized agents
        self.agents = [
            CodeParserAgent(self.client, self.model),
            SecurityScannerAgent(self.client, self.model),
            PerformanceAnalyzerAgent(self.client, self.model),
            ArchitectureReviewerAgent(self.client, self.model),
        ]
    
    def review(self, diff: str, files: dict[str, str]) -> dict:
        """
        Execute parallel review across all agents.
        
        Args:
            diff: The git diff of changes
            files: Dictionary of filename -> file content
            
        Returns:
            Combined review results
        """
        results: List[ReviewResult] = []
        total_tokens = 0
        
        # Run agents in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(agent.analyze, diff, files)
                for agent in self.agents
            ]
            
            for future in futures:
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                    total_tokens += result.tokens_used
                except Exception as e:
                    print(f"Agent failed: {e}")
        
        # Synthesize all findings
        final_report = self._synthesize_findings(results, total_tokens)
        
        return final_report
    
    def _synthesize_findings(self, results: List[ReviewResult], total_tokens: int) -> dict:
        """Combine all agent findings into a unified report."""
        
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        # Sort by severity
        severity_order = {
            "security-critical": 0,
            "critical": 1,
            "warning": 2,
            "info": 3,
        }
        all_issues.sort(key=lambda x: severity_order.get(x.severity.value, 99))
        
        return {
            "results": results,
            "all_issues": all_issues,
            "total_tokens": total_tokens,
            "summary": self._generate_summary(results),
        }
    
    def _generate_summary(self, results: List[ReviewResult]) -> str:
        """Generate executive summary of all findings."""
        summaries = [r.summary for r in results]
        return "\n\n".join(summaries)
