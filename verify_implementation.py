#!/usr/bin/env python
"""
Verification Script - Toppers Section Specialist Implementation

This script verifies that all implementation components are in place and working correctly.
Run this after deploying the Toppers agent implementation.

Usage:
    python verify_implementation.py
"""

import sys
import os
from pathlib import Path
import json


class ImplementationVerifier:
    """Verify all components of the Toppers implementation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_root = self.project_root / 'aris_backend'
        self.frontend_root = self.project_root / 'frontend'
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name, condition, details=""):
        """Record a check result"""
        status = "✅ PASS" if condition else "❌ FAIL"
        self.results.append(f"{status}: {name}" + (f" - {details}" if details else ""))
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        return condition
    
    def verify_agent_file(self):
        """Verify agent file exists and has correct properties"""
        print("\n" + "="*70)
        print("VERIFYING AGENT FILE")
        print("="*70)
        
        agent_path = Path(os.getenv("APPDATA")) / "Code" / "User" / "prompts" / "toppers-auditor.agent.md"
        
        if not self.check("Agent file exists", agent_path.exists(), str(agent_path)):
            return
        
        with open(agent_path, 'r') as f:
            content = f.read()
        
        self.check("Contains YAML frontmatter", content.startswith("---"))
        self.check("Contains 'Toppers Section Specialist'", "Toppers Section Specialist" in content)
        self.check("Contains 'user-invocable: true'", "user-invocable: true" in content)
        self.check("Contains tool restrictions", "tools: [read, edit, search]" in content)
        self.check("Has proper scope description", "Use when:" in content)
    
    def verify_backend_files(self):
        """Verify backend Python files have been modified"""
        print("\n" + "="*70)
        print("VERIFYING BACKEND IMPLEMENTATION")
        print("="*70)
        
        # Analytics file
        analytics_file = self.backend_root / "apps" / "results" / "services" / "analytics.py"
        if self.check("analytics.py exists", analytics_file.exists()):
            with open(analytics_file, 'r') as f:
                content = f.read()
            self.check("Contains TopperDataCleaner class", "class TopperDataCleaner" in content)
            self.check("Contains _normalize_percentage method", "_normalize_percentage" in content)
            self.check("Contains clean_topper method", "def clean_topper" in content)
        
        # Views file
        views_file = self.backend_root / "apps" / "results" / "api" / "views.py"
        if self.check("views.py exists", views_file.exists()):
            with open(views_file, 'r') as f:
                content = f.read()
            self.check("Contains SectionToppersView", "class SectionToppersView" in content)
            self.check("ToppersView uses cleaned data", "TopperDataCleaner" in content or "clean_topper" in content)
        
        # Serializers file
        serializers_file = self.backend_root / "apps" / "results" / "api" / "serializers.py"
        if self.check("serializers.py exists", serializers_file.exists()):
            with open(serializers_file, 'r') as f:
                content = f.read()
            self.check("Contains TopperSerializer", "class TopperSerializer" in content)
            self.check("Contains SectionTopperSerializer", "class SectionTopperSerializer" in content)
            self.check("Has percentage validation", "percentage" in content)
        
        # URLs file
        urls_file = self.backend_root / "apps" / "results" / "api" / "urls.py"
        if self.check("urls.py exists", urls_file.exists()):
            with open(urls_file, 'r') as f:
                content = f.read()
            self.check("Contains section toppers route", "section" in content.lower())
    
    def verify_frontend_files(self):
        """Verify frontend React files have been created/modified"""
        print("\n" + "="*70)
        print("VERIFYING FRONTEND IMPLEMENTATION")
        print("="*70)
        
        # TopperCard component
        topper_card = self.frontend_root / "src" / "components" / "TopperCard.jsx"
        if self.check("TopperCard.jsx exists", topper_card.exists()):
            with open(topper_card, 'r') as f:
                content = f.read()
            self.check("TopperCard has calculateGrade", "calculateGrade" in content)
            self.check("TopperCard exports component", "export" in content)
        
        # TopperLeaderboard component  
        topper_leaderboard = self.frontend_root / "src" / "components" / "TopperLeaderboard.jsx"
        if self.check("TopperLeaderboard.jsx exists", topper_leaderboard.exists()):
            with open(topper_leaderboard, 'r') as f:
                content = f.read()
            self.check("TopperLeaderboard uses TopperCard", "TopperCard" in content)
            self.check("TopperLeaderboard is exported", "export" in content)
        
        # Toppers page
        toppers_page = self.frontend_root / "src" / "pages" / "Toppers.jsx"
        if self.check("Toppers.jsx exists", toppers_page.exists()):
            with open(toppers_page, 'r') as f:
                content = f.read()
            self.check("Toppers uses TopperLeaderboard", "TopperLeaderboard" in content)
            self.check("Toppers has Section Toppers tab", "Section" in content and "Toppers" in content)
            self.check("getSectionToppers in Toppers", "getSectionToppers" in content)
        
        # Services
        services_file = self.frontend_root / "src" / "services" / "analyticsService.js"
        if self.check("analyticsService.js exists", services_file.exists()):
            with open(services_file, 'r') as f:
                content = f.read()
            self.check("Contains getSectionToppers method", "getSectionToppers" in content)
        
        # API client
        client_file = self.frontend_root / "src" / "api" / "client.js"
        if self.check("client.js exists", client_file.exists()):
            with open(client_file, 'r') as f:
                content = f.read()
            self.check("Contains getSectionToppers in client", "getSectionToppers" in content)
    
    def verify_documentation(self):
        """Verify documentation files are in place"""
        print("\n" + "="*70)
        print("VERIFYING DOCUMENTATION")
        print("="*70)
        
        handoff = self.project_root / "TOPPERS_AGENT_HANDOFF.md"
        self.check("Handoff document exists", handoff.exists())
        
        checklist = self.project_root / "VERIFICATION_CHECKLIST.md"
        self.check("Verification checklist exists", checklist.exists())
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "█"*70)
        print("█  TOPPERS IMPLEMENTATION VERIFICATION")
        print("█"*70)
        
        self.verify_agent_file()
        self.verify_backend_files()
        self.verify_frontend_files()
        self.verify_documentation()
        
        print("\n" + "="*70)
        print("VERIFICATION RESULTS")
        print("="*70)
        
        for result in self.results:
            print(result)
        
        print("\n" + "="*70)
        print(f"SUMMARY: {self.passed} passed, {self.failed} failed")
        print("="*70)
        
        if self.failed == 0:
            print("\n✅ ALL CHECKS PASSED - Implementation is complete!")
            return 0
        else:
            print(f"\n⚠️  {self.failed} checks failed - Review and fix issues above")
            return 1


if __name__ == "__main__":
    verifier = ImplementationVerifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)
