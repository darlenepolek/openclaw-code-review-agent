"""
Security Scanner Agent - Identifies security vulnerabilities using OWASP Top 10.
"""

import re
from typing import List
from ..agents.base import BaseAgent, ReviewIssue, ReviewResult, Severity


class SecurityScannerAgent(BaseAgent):
    """Agent specialized in security vulnerability detection."""
    
    def _get_system_prompt(self) -> str:
        return """You are a security-focused code review agent specializing in OWASP Top 10 vulnerabilities.
        
Your expertise includes:
- SQL Injection (A03:2021)
- Cross-Site Scripting (A07:2021)
- Broken Authentication (A07:2021)
- Sensitive Data Exposure (A02:2021)
- XML External Entities (A05:2021)
- Broken Access Control (A01:2021)
- Security Misconfiguration (A05:2021)
- Insecure Deserialization (A08:2021)
- Using Components with Known Vulnerabilities (A06:2021)
- Insufficient Logging & Monitoring (A09:2021)

Analyze the provided code diff and identify security issues.
For each issue, provide:
1. Severity (critical/high/medium/low)
2. File and line number
3. Clear description of the vulnerability
4. Suggested fix

Be thorough but avoid false positives. Only report genuine security concerns."""
    
    def analyze(self, diff: str, files: dict[str, str]) -> ReviewResult:
        """Analyze code for security vulnerabilities."""
        
        # Build analysis prompt
        prompt = f"""Analyze the following code changes for security vulnerabilities.

## Code Diff:
```diff
{diff}
```

## Full File Contents:
"""
        for filename, content in files.items():
            prompt += f"\n### {filename}\n```\n{content}\n```\n"
        
        prompt += "\n\nProvide a security analysis with specific findings."
        
        # Query Claude
        response, tokens = self._query_claude(prompt)
        
        # Parse response into issues
        issues = self._parse_security_findings(response)
        
        return ReviewResult(
            agent_name="SecurityScanner",
            issues=issues,
            summary=response[:500],
            tokens_used=tokens
        )
    
    def _parse_security_findings(self, response: str) -> List[ReviewIssue]:
        """Parse Claude's response into structured issues."""
        issues = []
        
        # Simple parsing - in production would be more sophisticated
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.WARNING,
            "low": Severity.INFO,
        }
        
        for severity_key, severity_enum in severity_map.items():
            if severity_key in response.lower():
                # Extract relevant context
                issues.append(ReviewIssue(
                    severity=severity_enum,
                    file="multiple",
                    line=0,
                    message=f"Security finding ({severity_key}) identified",
                    suggestion="See detailed analysis in summary"
                ))
        
        return issues
