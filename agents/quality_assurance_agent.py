"""
Quality Assurance Agent - Monitors and validates FlutterSwarm agent outputs.
Identifies issues in generated code and coordinates fixes with other agents.
"""

import asyncio
import os
import re
from typing import Dict, List, Any, Optional, Set
from agents.base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

class QualityAssuranceAgent(BaseAgent):
    """
    The Quality Assurance Agent monitors all outputs from other agents,
    identifies issues, inconsistencies, and problems in generated code,
    and coordinates with other agents to fix them.
    """
    
    def __init__(self):
        super().__init__("quality_assurance")
        self.code_quality_rules = {
            "dart": [
                "missing_imports",
                "undefined_variables", 
                "syntax_errors",
                "naming_conventions",
                "unused_imports",
                "missing_null_safety",
                "incorrect_widget_usage",
                "missing_keys",
                "async_without_await"
            ],
            "yaml": [
                "invalid_yaml_syntax",
                "missing_dependencies",
                "version_conflicts",
                "invalid_flutter_config"
            ],
            "architecture": [
                "circular_dependencies",
                "missing_abstractions",
                "tight_coupling",
                "single_responsibility_violation"
            ]
        }
        
        self.file_patterns = {
            "dart": r"\.dart$",
            "yaml": r"\.yaml$",
            "pubspec": r"pubspec\.yaml$"
        }
        
        self.monitored_issues = set()
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute QA tasks."""
        if "validate_project" in task_description:
            return await self._validate_entire_project(task_data)
        elif "review_code_quality" in task_description:
            return await self._review_code_quality(task_data)
        elif "check_consistency" in task_description:
            return await self._check_project_consistency(task_data)
        elif "fix_issues" in task_description:
            return await self._coordinate_issue_fixes(task_data)
        else:
            return await self._handle_general_qa_task(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "code_review":
            return await self._perform_code_review(data)
        elif collaboration_type == "issue_validation":
            return await self._validate_reported_issue(data)
        elif collaboration_type == "quality_metrics":
            return await self._calculate_quality_metrics(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes and monitor for issues."""
        event = change_data.get("event")
        
        if event == "file_created":
            await self._analyze_new_file(change_data)
        elif event == "agent_task_completed":
            await self._validate_task_output(change_data)
        elif event == "build_failed":
            await self._analyze_build_failure(change_data)
    
    async def _validate_entire_project(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive project validation."""
        project_id = task_data["project_id"]
        project = shared_state.get_project_state(project_id)
        
        validation_prompt = f"""
        Perform comprehensive quality assurance validation for this Flutter project:
        
        Project: {project.name}
        Files: {len(project.files_created) if hasattr(project, 'files_created') else 0}
        Current Phase: {project.current_phase}
        
        Validate the following aspects:
        
        1. **Code Quality**:
           - Dart syntax correctness
           - Flutter best practices adherence
           - Null safety implementation
           - Widget hierarchy correctness
           - State management consistency
        
        2. **Architecture Consistency**:
           - Proper separation of concerns
           - Consistent naming conventions
           - Appropriate design patterns usage
           - Dependency injection setup
        
        3. **Project Structure**:
           - Proper folder organization
           - File naming conventions
           - Import statements consistency
           - Asset organization
        
        4. **Dependencies**:
           - pubspec.yaml correctness
           - Version compatibility
           - Missing dependencies
           - Unused dependencies
        
        5. **Integration**:
           - Cross-file compatibility
           - API integration correctness
           - Navigation flow consistency
           - State synchronization
        
        For each validation category, provide:
        - ✅ Passed checks
        - ❌ Failed checks with specific issues
        - 🔧 Recommended fixes
        - 📋 Affected files
        
        Be thorough and specific about any issues found.
        """
        
        validation_result = await self.think(validation_prompt, {
            "project": project,
            "quality_rules": self.code_quality_rules
        })
        
        # Parse validation results and create issue reports
        issues = await self._parse_validation_issues(validation_result)
        
        # Store issues for tracking
        for issue in issues:
            self.monitored_issues.add(issue["id"])
            shared_state.report_issue(project_id, issue)
        
        return {
            "validation_status": "completed",
            "issues_found": len(issues),
            "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
            "issues": issues,
            "recommendations": await self._generate_fix_recommendations(issues)
        }
    
    async def _analyze_new_file(self, change_data: Dict[str, Any]) -> None:
        """Analyze newly created files for immediate issues."""
        file_path = change_data.get("file_path", "")
        file_content = change_data.get("content", "")
        project_id = change_data.get("project_id", "")
        
        if not file_path or not file_content:
            return
        
        # Determine file type and appropriate validation
        file_type = self._determine_file_type(file_path)
        
        analysis_prompt = f"""
        Analyze this newly created {file_type} file for immediate quality issues:
        
        File: {file_path}
        Content:
        ```{file_type}
        {file_content}
        ```
        
        Check for:
        1. Syntax errors
        2. Import issues
        3. Naming convention violations
        4. Missing null safety
        5. Incorrect Flutter patterns
        6. Performance anti-patterns
        7. Security vulnerabilities
        
        Provide specific line-by-line issues if found.
        """
        
        analysis = await self.think(analysis_prompt, {
            "file_type": file_type,
            "file_path": file_path
        })
        
        # If issues found, create issue reports
        if "❌" in analysis or "ERROR" in analysis.upper():
            await self._create_issue_report(project_id, file_path, analysis)
    
    async def _coordinate_issue_fixes(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with other agents to fix identified issues."""
        project_id = task_data["project_id"]
        issues = task_data.get("issues", [])
        
        fix_coordination_plan = await self._create_fix_plan(issues)
        
        # Assign fix tasks to appropriate agents
        for fix_task in fix_coordination_plan:
            target_agent = fix_task["assigned_agent"]
            
            self.send_message_to_agent(
                to_agent=target_agent,
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_description": f"fix_{fix_task['issue_type']}",
                    "task_data": {
                        "project_id": project_id,
                        "issue_details": fix_task["issue_details"],
                        "fix_instructions": fix_task["fix_instructions"],
                        "affected_files": fix_task["affected_files"]
                    }
                },
                priority=4
            )
        
        return {
            "fix_plan_created": True,
            "tasks_assigned": len(fix_coordination_plan),
            "target_agents": list(set([task["assigned_agent"] for task in fix_coordination_plan]))
        }
    
    async def _create_fix_plan(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a coordinated plan to fix all identified issues."""
        fix_plan_prompt = f"""
        Create a coordinated fix plan for these identified issues:
        
        Issues: {issues}
        
        Available agents and their capabilities:
        - Implementation Agent: Dart/Flutter code fixes, widget corrections, state management
        - Architecture Agent: Design pattern fixes, structural improvements
        - Security Agent: Security vulnerability fixes, authentication issues
        - Performance Agent: Performance optimizations, memory issues
        - Testing Agent: Test fixes, coverage improvements
        - DevOps Agent: Build configuration, dependency issues
        - Documentation Agent: Comment fixes, documentation updates
        
        For each issue, determine:
        1. Which agent should handle the fix
        2. Priority level (1-5)
        3. Dependencies between fixes
        4. Specific fix instructions
        5. Expected outcome
        
        Create a logical order for fixes to avoid conflicts.
        """
        
        fix_plan = await self.think(fix_plan_prompt, {
            "issues": issues,
            "available_agents": self.get_other_agents()
        })
        
        return await self._parse_fix_plan(fix_plan)
    
    async def _parse_fix_plan(self, fix_plan_text: str) -> List[Dict[str, Any]]:
        """Parse the fix plan text into structured tasks."""
        # This would parse the LLM output into structured fix tasks
        # For now, create a simple structure
        tasks = []
        
        # Extract tasks from the fix plan (simplified parsing)
        if "Implementation Agent" in fix_plan_text:
            tasks.append({
                "assigned_agent": "implementation",
                "issue_type": "code_quality",
                "issue_details": "Code quality improvements needed",
                "fix_instructions": "Review and fix code quality issues",
                "affected_files": [],
                "priority": 3
            })
        
        if "Architecture Agent" in fix_plan_text:
            tasks.append({
                "assigned_agent": "architecture",
                "issue_type": "architecture",
                "issue_details": "Architecture consistency improvements",
                "fix_instructions": "Review and improve architecture consistency",
                "affected_files": [],
                "priority": 4
            })
        
        return tasks
    
    async def _parse_validation_issues(self, validation_text: str) -> List[Dict[str, Any]]:
        """Parse validation results into structured issue reports."""
        issues = []
        
        # Parse validation text for issues (simplified)
        if "❌" in validation_text:
            issues.append({
                "id": f"qa_{len(self.monitored_issues) + 1}",
                "type": "validation_failure",
                "severity": "medium",
                "description": "Quality validation issues detected",
                "affected_files": [],
                "fix_suggestions": []
            })
        
        return issues
    
    async def _create_issue_report(self, project_id: str, file_path: str, analysis: str) -> None:
        """Create an issue report for tracking."""
        issue = {
            "id": f"qa_file_{len(self.monitored_issues) + 1}",
            "project_id": project_id,
            "file_path": file_path,
            "type": "file_analysis",
            "severity": "medium",
            "description": f"Issues found in {file_path}",
            "analysis": analysis,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.monitored_issues.add(issue["id"])
        shared_state.report_issue(project_id, issue)
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type based on extension."""
        if file_path.endswith('.dart'):
            return 'dart'
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return 'yaml'
        elif file_path.endswith('.json'):
            return 'json'
        else:
            return 'text'
    
    async def _generate_fix_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate high-level fix recommendations."""
        recommendations = []
        
        for issue in issues:
            if issue["severity"] == "critical":
                recommendations.append(f"🚨 Critical: {issue['description']} - Immediate attention required")
            elif issue["severity"] == "high":
                recommendations.append(f"⚠️ High: {issue['description']} - Should be fixed soon")
            else:
                recommendations.append(f"📝 Medium: {issue['description']} - Consider fixing")
        
        return recommendations
    
    async def _handle_general_qa_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general QA tasks."""
        qa_prompt = f"""
        Handle this quality assurance task: {task_description}
        
        Task data: {task_data}
        
        Provide a thorough quality assurance response with:
        1. Analysis of the situation
        2. Quality assessment
        3. Specific recommendations
        4. Action items for improvement
        """
        
        response = await self.think(qa_prompt, task_data)
        
        return {
            "task": task_description,
            "qa_response": response,
            "status": "completed"
        }
