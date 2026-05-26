#!/usr/bin/env python3
"""
OpenClaw Code Review Agent - CLI Interface

Usage:
    python -m review_agent start --repo owner/repo
    python -m review_agent review --pr 123
    python -m review_agent batch --last 10
"""

import argparse
import sys
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

from .reviewer import CodeReviewer


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Code Review Agent - AI-powered code review"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command (webhook mode)
    start_parser = subparsers.add_parser("start", help="Start webhook server")
    start_parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    start_parser.add_argument("--port", type=int, default=8080, help="Webhook port")
    
    # Review command (single PR)
    review_parser = subparsers.add_parser("review", help="Review a single PR")
    review_parser.add_argument("--pr", type=int, required=True, help="PR number")
    review_parser.add_argument("--repo", help="Repository (owner/repo)")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch review recent PRs")
    batch_parser.add_argument("--last", type=int, default=10, help="Number of recent PRs")
    batch_parser.add_argument("--repo", help="Repository (owner/repo)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize reviewer
    api_key = os.getenv("ANTHROPIC_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    reviewer = CodeReviewer(api_key, github_token)
    
    if args.command == "start":
        print(f"🚀 Starting webhook server on port {args.port}")
        print(f"📡 Watching repository: {args.repo}")
        # In production, would start Flask/FastAPI server here
        
    elif args.command == "review":
        repo = args.repo or os.getenv("DEFAULT_REPO")
        if not repo:
            print("❌ Repository required (--repo or DEFAULT_REPO env)")
            sys.exit(1)
        
        print(f"🔍 Reviewing PR #{args.pr} in {repo}")
        result = reviewer.review_pr(repo, args.pr)
        print(result)
        
    elif args.command == "batch":
        repo = args.repo or os.getenv("DEFAULT_REPO")
        if not repo:
            print("❌ Repository required (--repo or DEFAULT_REPO env)")
            sys.exit(1)
        
        print(f"📋 Batch reviewing last {args.last} PRs in {repo}")
        results = reviewer.batch_review(repo, args.last)
        for r in results:
            print(r)


if __name__ == "__main__":
    main()
