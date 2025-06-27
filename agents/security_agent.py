"""
Security Agent - Analyzes and implements security best practices for Flutter applications.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType
from tools import ToolResult, ToolStatus
from utils.function_logger import track_function
from utils.enhancedLLMResponseParser import parse_llm_response_for_agent

class SecurityAgent(BaseAgent):
    """
    The Security Agent specializes in security analysis and implementation.
    It ensures Flutter applications follow security best practices.
    """
    
    def __init__(self):
        super().__init__("security")
        self.security_domains = [
            "authentication", "authorization", "data_protection", 
            "network_security", "local_storage", "code_obfuscation",
            "api_security", "certificate_pinning"
        ]
        self.vulnerability_types = [
            "sql_injection", "xss", "insecure_storage", "weak_crypto",
            "improper_auth", "data_exposure", "man_in_middle"
        ]
        
    @track_function(log_args=True, log_return=True)
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security tasks."""
        try:
            # Analyze task using LLM to understand requirements
            analysis = await self.think(f"Analyze this security task: {task_description}", {
                "task_data": task_data,
                "security_domains": self.security_domains,
                "vulnerability_types": self.vulnerability_types
            })
            
            self.logger.info(f"🔒 Security Agent executing task: {task_description}")
            
            # Route task to appropriate handler
            result = None
            if "security_audit" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._perform_security_audit(task_data)
                )
            elif "implement_authentication" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._implement_authentication(task_data)
                )
            elif "secure_storage" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._implement_secure_storage(task_data)
                )
            elif "network_security" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._implement_network_security(task_data)
                )
            else:
                result = await self.safe_execute_with_retry(
                    lambda: self._handle_general_security_task(task_description, task_data)
                )
            
            # Add execution metadata
            result.update({
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id,
                "task_analysis": analysis[:200] + "..." if len(analysis) > 200 else analysis
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error executing security task: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id
            }
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "architecture_review":
            return await self._review_architecture_security(data)
        elif collaboration_type == "code_security_review":
            return await self._review_code_security(data)
        elif collaboration_type == "security_recommendations":
            return await self._provide_security_recommendations(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "file_added":
            await self._analyze_file_security(change_data)
        elif event == "architecture_completed":
            await self._analyze_architecture_security(change_data["project_id"])
    
    async def _perform_security_audit(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security audit using tools."""
        project_id = task_data["project_id"]
        audit_scope = task_data.get("scope", "full")
        
        project = shared_state.get_project_state(project_id)
        
        self.logger.info(f"🔒 Performing security audit (scope: {audit_scope})")
        
        # Use analysis tool for security scanning
        security_scan_result = await self.execute_tool("analysis", operation="security_scan", scan_type=audit_scope)
        
        # Additional manual checks using file tools
        additional_findings = []
        
        # Check Android manifest for security issues
        android_manifest_result = await self.read_file("android/app/src/main/AndroidManifest.xml")
        if android_manifest_result.status == ToolStatus.SUCCESS:
            manifest_findings = await self._analyze_android_manifest(android_manifest_result.output)
            additional_findings.extend(manifest_findings)
        
        # Check iOS Info.plist for security issues
        ios_plist_result = await self.read_file("ios/Runner/Info.plist")
        if ios_plist_result.status == ToolStatus.SUCCESS:
            plist_findings = await self._analyze_ios_plist(ios_plist_result.output)
            additional_findings.extend(plist_findings)
        
        # Check network security configuration
        network_config_findings = await self._check_network_security_config()
        additional_findings.extend(network_config_findings)
        
        # Combine all findings
        all_findings = []
        if security_scan_result.data:
            all_findings.extend(security_scan_result.data.get("issues", []))
        all_findings.extend(additional_findings)
        
        # Generate security report
        security_report = await self._generate_security_report(all_findings)
        
        # Store findings in project state with defensive access
        if project:
            security_findings = getattr(project, 'security_findings', [])
            security_findings.extend(all_findings)
            shared_state.update_project(project_id, security_findings=security_findings)
        
        return {
            "audit_report": security_report,
            "findings_count": len(all_findings),
            "critical_issues": len([f for f in all_findings if f.get("severity") == "Critical"]),
            "high_issues": len([f for f in all_findings if f.get("severity") == "High"]),
            "medium_issues": len([f for f in all_findings if f.get("severity") == "Medium"]),
            "low_issues": len([f for f in all_findings if f.get("severity") == "Low"]),
            "status": "completed"
        }
    
    async def _implement_authentication(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement secure authentication system using tools."""
        project_id = task_data["project_id"]
        auth_methods = task_data.get("methods", ["email_password"])
        
        self.logger.info(f"🔐 Implementing authentication: {auth_methods}")
        
        # Create authentication directory structure
        auth_dirs = [
            "lib/features/auth/data/models",
            "lib/features/auth/data/repositories",
            "lib/features/auth/data/datasources",
            "lib/features/auth/domain/entities",
            "lib/features/auth/domain/repositories",
            "lib/features/auth/domain/usecases",
            "lib/features/auth/presentation/pages",
            "lib/features/auth/presentation/widgets",
            "lib/features/auth/presentation/bloc"
        ]
        
        for directory in auth_dirs:
            await self.execute_tool("file", operation="create_directory", directory=directory)
        
        # Add security dependencies
        security_dependencies = [
            "crypto",
            "flutter_secure_storage",
            "local_auth",
            "firebase_auth",
            "jwt_decoder"
        ]
        
        await self.execute_tool("flutter", operation="pub_add", packages=security_dependencies)
        
        # Generate authentication files
        generated_files = []
        
        # Generate authentication models
        auth_model_files = await self._generate_auth_models(auth_methods)
        generated_files.extend(auth_model_files)
        
        # Generate authentication service
        auth_service_file = await self._generate_auth_service(auth_methods)
        generated_files.append(auth_service_file)
        
        # Generate authentication repository
        auth_repo_file = await self._generate_auth_repository(auth_methods)
        generated_files.append(auth_repo_file)
        
        # Generate authentication screens
        auth_screen_files = await self._generate_auth_screens(auth_methods)
        generated_files.extend(auth_screen_files)
        
        # Generate security utilities
        security_utils_file = await self._generate_security_utils()
        generated_files.append(security_utils_file)
        
        # Format generated code
        await self.run_command("dart format lib/features/auth/")
        
        # Analyze generated code for security issues
        analysis_result = await self.execute_tool("analysis", operation="security_scan", scan_type="basic")
        
        return {
            "auth_methods": auth_methods,
            "generated_files": generated_files,
            "security_features": ["token_management", "biometric_auth", "secure_storage"],
            "analysis_result": analysis_result.data if analysis_result.data else {},
            "status": "implemented"
        }
    
    async def _implement_secure_storage(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement secure data storage using tools."""
        project_id = task_data["project_id"]
        storage_types = task_data.get("types", ["sensitive_data", "user_preferences"])
        
        self.logger.info(f"🗄️ Implementing secure storage: {storage_types}")
        
        # Add secure storage dependencies
        storage_dependencies = [
            "flutter_secure_storage",
            "encrypted_shared_preferences",
            "sqflite_cipher"
        ]
        
        await self.execute_tool("flutter", operation="pub_add", packages=storage_dependencies)
        
        # Create storage directory structure
        storage_dirs = [
            "lib/core/storage",
            "lib/core/storage/secure",
            "lib/core/storage/local"
        ]
        
        for directory in storage_dirs:
            await self.execute_tool("file", operation="create_directory", directory=directory)
        
        # Generate secure storage implementation
        generated_files = []
        
        # Generate secure storage service
        storage_service_code = await self._generate_secure_storage_service(storage_types)
        storage_service_file = "lib/core/storage/secure/secure_storage_service.dart"
        
        write_result = await self.write_file(storage_service_file, storage_service_code)
        if write_result.status.value == "success":
            generated_files.append(storage_service_file)
        
        # Generate encryption utilities
        encryption_utils_code = await self._generate_encryption_utils()
        encryption_utils_file = "lib/core/storage/secure/encryption_utils.dart"
        
        write_result = await self.write_file(encryption_utils_file, encryption_utils_code)
        if write_result.status.value == "success":
            generated_files.append(encryption_utils_file)
        
        # Generate key management service
        key_management_code = await self._generate_key_management_service()
        key_management_file = "lib/core/storage/secure/key_management_service.dart"
        
        write_result = await self.write_file(key_management_file, key_management_code)
        if write_result.status.value == "success":
            generated_files.append(key_management_file)
        
        # Format generated code
        await self.run_command("dart format lib/core/storage/")
        
        return {
            "storage_types": storage_types,
            "generated_files": generated_files,
            "security_features": ["encryption", "key_management", "secure_preferences"],
            "status": "implemented"
        }
    
    async def _implement_network_security(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement network security measures using tools."""
        project_id = task_data["project_id"]
        security_features = task_data.get("features", ["certificate_pinning", "request_signing"])
        
        self.logger.info(f"🌐 Implementing network security: {security_features}")
        
        # Add network security dependencies
        network_dependencies = [
            "dio",
            "dio_certificate_pinning",
            "crypto"
        ]
        
        await self.execute_tool("flutter", operation="pub_add", packages=network_dependencies)
        
        # Create network security directory
        network_dirs = [
            "lib/core/network",
            "lib/core/network/security",
            "lib/core/network/interceptors"
        ]
        
        for directory in network_dirs:
            await self.execute_tool("file", operation="create_directory", directory=directory)
        
        generated_files = []
        
        # Generate HTTP client with security
        if "certificate_pinning" in security_features:
            pinning_code = await self._generate_certificate_pinning_client()
            pinning_file = "lib/core/network/security/secure_http_client.dart"
            
            write_result = await self.write_file(pinning_file, pinning_code)
            if write_result.status.value == "success":
                generated_files.append(pinning_file)
        
        # Generate request signing interceptor
        if "request_signing" in security_features:
            signing_code = await self._generate_request_signing_interceptor()
            signing_file = "lib/core/network/interceptors/signing_interceptor.dart"
            
            write_result = await self.write_file(signing_file, signing_code)
            if write_result.status.value == "success":
                generated_files.append(signing_file)
        
        # Generate API security configuration
        api_config_code = await self._generate_api_security_config()
        api_config_file = "lib/core/network/security/api_security_config.dart"
        
        write_result = await self.write_file(api_config_file, api_config_code)
        if write_result.status.value == "success":
            generated_files.append(api_config_file)
        
        # Format generated code
        await self.run_command("dart format lib/core/network/")
        
        return {
            "security_features": security_features,
            "generated_files": generated_files,
            "status": "implemented"
        }

    def _parse_security_findings(self, audit_report: str) -> List[Dict[str, Any]]:
        """Parse security findings from audit report using enhanced parser."""
        # Try to parse using enhanced parser for structured security findings
        parsed_files, error = parse_llm_response_for_agent(self, audit_report, {
            "task_type": "security_findings_parsing"
        })
        
        findings = []
        
        # If parser found structured data, extract findings
        if parsed_files:
            for file_info in parsed_files:
                # Look for security findings in the parsed data
                if "findings" in file_info or "vulnerabilities" in file_info:
                    security_data = file_info.get("findings", file_info.get("vulnerabilities", []))
                    if isinstance(security_data, list):
                        findings.extend(security_data)
                elif "severity" in file_info or "security_issue" in file_info:
                    # This looks like a single finding
                    findings.append(file_info)
        
        # If we found structured findings, use them
        if findings:
            self.logger.info(f"✅ Parsed {len(findings)} security findings using enhanced parser")
            # Ensure each finding has required fields
            for i, finding in enumerate(findings):
                if "id" not in finding:
                    finding["id"] = f"SEC-{i + 1}"
                if "status" not in finding:
                    finding["status"] = "identified"
            return findings
        
        # Fallback to simplified parsing if enhanced parser didn't find structured data
        self.logger.info("Using fallback parsing for security findings")
        
        # Create a sample finding based on the audit report content
        findings.append({
            "id": f"SEC-{len(findings) + 1}",
            "title": "Security Analysis Completed",
            "description": audit_report[:200] + "...",
            "severity": "Medium",
            "status": "identified",
            "recommendations": ["Implement additional security measures"]
        })
        
        return findings
    
    async def _review_architecture_security(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Review architecture for security implications."""
        architecture = data.get("architecture", "")
        focus = data.get("focus", "security_implications")
        
        review_prompt = f"""
        Review this architecture from a security perspective:
        
        Architecture: {architecture}
        Focus: {focus}
        
        Analyze:
        1. Security weaknesses in the proposed architecture
        2. Missing security controls
        3. Potential attack vectors
        4. Data flow security
        5. Trust boundaries
        6. Security by design principles
        
        Provide specific, actionable security recommendations.
        """
        
        security_review = await self.think(review_prompt, {
            "architecture": architecture,
            "security_domains": self.security_domains
        })
        
        return {
            "security_review": security_review,
            "focus": focus,
            "reviewer": self.agent_id
        }
    
    async def _analyze_file_security(self, change_data: Dict[str, Any]) -> None:
        """Analyze new files for security issues."""
        filename = change_data.get("filename", "")
        
        if filename.endswith('.dart'):
            # Analyze the file for security issues
            project_id = change_data.get("project_id")
            if project_id:
                project = shared_state.get_project_state(project_id)
                files_created = getattr(project, 'files_created', {}) if project else {}
                if project and filename in files_created:
                    file_content = files_created[filename]
                    await self._analyze_code_security(file_content, filename, project_id)
    
    async def _analyze_code_security(self, code: str, filename: str, project_id: str) -> None:
        """Analyze code for security vulnerabilities."""
        analysis_prompt = f"""
        Analyze this Flutter/Dart code for security vulnerabilities:
        
        File: {filename}
        Code: {code}
        
        Check for:
        1. Hard-coded secrets or credentials
        2. Insecure data handling
        3. Improper input validation
        4. Weak cryptographic usage
        5. Insecure network communications
        6. Platform security misconfigurations
        
        Report any security issues found.
        """
        
        analysis = await self.think(analysis_prompt, {
            "filename": filename,
            "vulnerability_types": self.vulnerability_types
        })
        
        # If issues found, add to project security findings
        if "vulnerability" in analysis.lower() or "security issue" in analysis.lower():
            finding = {
                "id": f"SEC-{filename}",
                "title": f"Security Analysis - {filename}",
                "description": analysis,
                "severity": "Medium",
                "file": filename,
                "status": "identified"
            }
            
            project = shared_state.get_project_state(project_id)
            if project:
                security_findings = getattr(project, 'security_findings', [])
                security_findings.append(finding)
                shared_state.update_project(project_id, security_findings=security_findings)
    
    async def _handle_general_security_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general security tasks."""
        response = await self.think(f"Handle security task: {task_description}", task_data)
        return {"response": response, "task": task_description}
