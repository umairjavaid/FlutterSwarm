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
        """Perform comprehensive project validation using tools."""
        project_id = task_data["project_id"]
        project = shared_state.get_project_state(project_id)
        
        self.logger.info(f"🔍 Validating project: {project.name}")
        
        validation_results = {}
        issues = []
        
        # 1. Code Quality Analysis
        self.logger.info("📋 Running code quality analysis...")
        code_analysis = await self.execute_tool("analysis", operation="dart_analyze")
        validation_results["code_analysis"] = code_analysis.data if code_analysis.data else {}
        
        if code_analysis.data:
            issues.extend(code_analysis.data.get("issues", []))
        
        # 2. Security Scan
        self.logger.info("🔒 Running security scan...")
        security_scan = await self.execute_tool("analysis", operation="security_scan", scan_type="comprehensive")
        validation_results["security_scan"] = security_scan.data if security_scan.data else {}
        
        if security_scan.data:
            issues.extend(security_scan.data.get("issues", []))
        
        # 3. Code Metrics Analysis
        self.logger.info("📊 Calculating code metrics...")
        metrics_analysis = await self.execute_tool("analysis", operation="code_metrics")
        validation_results["code_metrics"] = metrics_analysis.data if metrics_analysis.data else {}
        
        # 4. Dependency Check
        self.logger.info("📦 Checking dependencies...")
        dependency_check = await self.execute_tool("analysis", operation="dependency_check")
        validation_results["dependency_check"] = dependency_check.data if dependency_check.data else {}
        
        if dependency_check.data:
            issues.extend(dependency_check.data.get("issues", []))
        
        # 5. Test Coverage Analysis
        self.logger.info("🧪 Analyzing test coverage...")
        coverage_analysis = await self.execute_tool("analysis", operation="test_coverage")
        validation_results["test_coverage"] = coverage_analysis.data if coverage_analysis.data else {}
        
        # 6. Performance Analysis
        self.logger.info("⚡ Running performance analysis...")
        performance_analysis = await self.execute_tool("analysis", operation="performance_analysis")
        validation_results["performance_analysis"] = performance_analysis.data if performance_analysis.data else {}
        
        if performance_analysis.data:
            issues.extend(performance_analysis.data.get("performance_issues", []))
        
        # 7. Dead Code Analysis
        self.logger.info("🗑️ Analyzing dead code...")
        dead_code_analysis = await self.execute_tool("analysis", operation="dead_code")
        validation_results["dead_code_analysis"] = dead_code_analysis.data if dead_code_analysis.data else {}
        
        if dead_code_analysis.data:
            issues.extend(dead_code_analysis.data.get("dead_code_issues", []))
        
        # 8. Project Structure Validation
        self.logger.info("🏗️ Validating project structure...")
        structure_validation = await self._validate_project_structure()
        validation_results["structure_validation"] = structure_validation
        issues.extend(structure_validation.get("issues", []))
        
        # 9. Flutter Doctor Check
        self.logger.info("👨‍⚕️ Running Flutter doctor...")
        doctor_result = await self.execute_tool("flutter", operation="doctor", verbose=True)
        validation_results["flutter_doctor"] = doctor_result.data if doctor_result.data else {}
        
        if doctor_result.data and doctor_result.data.get("environment_issues"):
            issues.extend(doctor_result.data["environment_issues"])
        
        # Generate recommendations based on all findings
        recommendations = await self._generate_fix_recommendations(issues)
        
        # Categorize issues by severity
        critical_issues = [i for i in issues if i.get("severity") in ["critical", "Critical"]]
        high_issues = [i for i in issues if i.get("severity") in ["high", "High"]]
        medium_issues = [i for i in issues if i.get("severity") in ["medium", "Medium"]]
        low_issues = [i for i in issues if i.get("severity") in ["low", "Low", "info", "Info"]]
        
        # Store issues for tracking
        for issue in issues:
            issue_id = f"{issue.get('type', 'unknown')}_{hash(str(issue))}"
            self.monitored_issues.add(issue_id)
            if hasattr(project, 'issues'):
                shared_state.report_issue(project_id, {**issue, "id": issue_id})
        
        return {
            "validation_status": "completed",
            "validation_results": validation_results,
            "issues_found": len(issues),
            "critical_issues": len(critical_issues),
            "high_issues": len(high_issues),
            "medium_issues": len(medium_issues),
            "low_issues": len(low_issues),
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _validate_project_structure(self) -> Dict[str, Any]:
        """Validate Flutter project structure using file tools."""
        structure_issues = []
        
        # Check for required Flutter files
        required_files = [
            "pubspec.yaml",
            "lib/main.dart",
            "android/app/build.gradle",
            "ios/Runner/Info.plist"
        ]
        
        for required_file in required_files:
            exists_result = await self.execute_tool("file", operation="exists", path=required_file)
            if exists_result.data and not exists_result.data.get("exists", False):
                structure_issues.append({
                    "type": "missing_required_file",
                    "severity": "high",
                    "message": f"Missing required file: {required_file}",
                    "file": required_file
                })
        
        # Check for recommended directories
        recommended_dirs = [
            "lib/core",
            "lib/features",
            "lib/shared",
            "test/unit",
            "test/widget"
        ]
        
        for recommended_dir in recommended_dirs:
            exists_result = await self.execute_tool("file", operation="exists", path=recommended_dir)
            if exists_result.data and not exists_result.data.get("exists", False):
                structure_issues.append({
                    "type": "missing_recommended_directory",
                    "severity": "medium",
                    "message": f"Missing recommended directory: {recommended_dir}",
                    "directory": recommended_dir
                })
        
        # Check lib directory structure
        lib_structure = await self._analyze_lib_structure()
        structure_issues.extend(lib_structure.get("issues", []))
        
        return {
            "issues": structure_issues,
            "required_files_check": "completed",
            "directory_structure_check": "completed"
        }
    
    async def _analyze_lib_structure(self) -> Dict[str, Any]:
        """Analyze lib directory structure."""
        issues = []
        
        # List all Dart files in lib
        dart_files_result = await self.execute_tool("file", operation="search", pattern="*.dart", directory="lib")
        
        if dart_files_result.status.value == "success" and dart_files_result.data:
            dart_files = dart_files_result.data.get("matches", [])
            
            # Check for files in root lib directory (should be minimal)
            root_files = [f for f in dart_files if "/" not in f.replace("lib/", "")]
            
            if len(root_files) > 3:  # main.dart and maybe a couple others
                issues.append({
                    "type": "too_many_root_files",
                    "severity": "medium",
                    "message": f"Too many files in lib root directory: {len(root_files)}. Consider organizing into subdirectories.",
                    "file_count": len(root_files)
                })
            
            # Check for proper feature organization
            feature_dirs = []
            for file in dart_files:
                if "features/" in file:
                    feature_name = file.split("features/")[1].split("/")[0]
                    if feature_name not in feature_dirs:
                        feature_dirs.append(feature_name)
            
            # Analyze each feature for proper structure
            for feature in feature_dirs:
                feature_analysis = await self._analyze_feature_structure(feature)
                issues.extend(feature_analysis.get("issues", []))
        
        return {"issues": issues}
    
    async def _analyze_feature_structure(self, feature_name: str) -> Dict[str, Any]:
        """Analyze individual feature structure."""
        issues = []
        
        # Check for clean architecture layers
        expected_layers = ["data", "domain", "presentation"]
        
        for layer in expected_layers:
            layer_path = f"lib/features/{feature_name}/{layer}"
            exists_result = await self.execute_tool("file", operation="exists", path=layer_path)
            
            if exists_result.data and not exists_result.data.get("exists", False):
                issues.append({
                    "type": "missing_architecture_layer",
                    "severity": "medium",
                    "message": f"Feature '{feature_name}' missing {layer} layer",
                    "feature": feature_name,
                    "layer": layer
                })
        
        return {"issues": issues}
    
    async def _generate_fix_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate fix recommendations for identified issues."""
        recommendations = []
        
        # Group issues by type
        issue_groups = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue)
        
        # Generate recommendations for each issue type
        for issue_type, type_issues in issue_groups.items():
            recommendation = await self._generate_type_specific_recommendation(issue_type, type_issues)
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_type_specific_recommendation(self, issue_type: str, issues: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate recommendations for specific issue types."""
        recommendation_map = {
            "missing_required_file": {
                "action": "create_missing_files",
                "description": "Create missing required files",
                "priority": "high",
                "automated": True
            },
            "missing_recommended_directory": {
                "action": "create_directories",
                "description": "Create recommended directory structure",
                "priority": "medium",
                "automated": True
            },
            "hardcoded_secret": {
                "action": "move_to_secure_storage",
                "description": "Move hardcoded secrets to secure configuration",
                "priority": "critical",
                "automated": False
            },
            "insecure_network": {
                "action": "implement_https",
                "description": "Replace HTTP calls with HTTPS and implement certificate pinning",
                "priority": "high",
                "automated": False
            },
            "performance_issue": {
                "action": "optimize_performance",
                "description": "Optimize identified performance bottlenecks",
                "priority": "medium",
                "automated": False
            },
            "unused_symbol": {
                "action": "remove_dead_code",
                "description": "Remove unused code to improve maintainability",
                "priority": "low",
                "automated": True
            }
        }
        
        if issue_type in recommendation_map:
            base_recommendation = recommendation_map[issue_type]
            
            return {
                **base_recommendation,
                "issue_type": issue_type,
                "issue_count": len(issues),
                "affected_files": list(set(issue.get("file", "") for issue in issues if issue.get("file"))),
                "details": issues
            }
        
        return None

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
