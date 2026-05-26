"""
OpenClaw Code Review Agent - Multi-Agent Automated Code Review System

A sophisticated AI-powered code review system using OpenClaw orchestration
and Claude AI for deep code analysis.
"""

__version__ = "1.0.0"
__author__ = "darlenepolek"

from .agents import (
    CodeParserAgent,
    SecurityScannerAgent,
    PerformanceAnalyzerAgent,
    ArchitectureReviewerAgent,
)
from .orchestrator import ReviewOrchestrator
from .reviewer import CodeReviewer

__all__ = [
    "CodeParserAgent",
    "SecurityScannerAgent",
    "PerformanceAnalyzerAgent",
    "ArchitectureReviewerAgent",
    "ReviewOrchestrator",
    "CodeReviewer",
]
