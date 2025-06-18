"""
Security Agent - Analyzes and implements security best practices for Flutter applications.
"""

import asyncio
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

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
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security tasks."""
        if "security_audit" in task_description:
            return await self._perform_security_audit(task_data)
        elif "implement_authentication" in task_description:
            return await self._implement_authentication(task_data)
        elif "secure_storage" in task_description:
            return await self._implement_secure_storage(task_data)
        elif "network_security" in task_description:
            return await self._implement_network_security(task_data)
        else:
            return await self._handle_general_security_task(task_description, task_data)
    
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
        """Perform comprehensive security audit."""
        project_id = task_data["project_id"]
        audit_scope = task_data.get("scope", "full")
        
        project = shared_state.get_project_state(project_id)
        
        audit_prompt = f"""
        Perform a comprehensive security audit for this Flutter application:
        
        Project: {project.name}
        Description: {project.description}
        Audit Scope: {audit_scope}
        Files: {list(project.files_created.keys()) if project.files_created else []}
        
        Analyze the following security aspects:
        
        1. **Authentication & Authorization**:
           - Authentication mechanisms
           - Session management
           - Role-based access control
           - Multi-factor authentication
        
        2. **Data Protection**:
           - Sensitive data handling
           - Data encryption at rest
           - Data encryption in transit
           - PII protection
        
        3. **Network Security**:
           - HTTPS implementation
           - Certificate pinning
           - API security
           - Request/response validation
        
        4. **Local Storage Security**:
           - Secure storage usage
           - Key management
           - Database encryption
           - Cache security
        
        5. **Code Security**:
           - Input validation
           - Output encoding
           - SQL injection prevention
           - Cross-site scripting prevention
        
        6. **Platform Security**:
           - iOS keychain usage
           - Android keystore usage
           - Biometric authentication
           - App sandboxing
        
        7. **Third-party Dependencies**:
           - Package vulnerability analysis
           - Dependency security
           - Supply chain security
        
        For each finding, provide:
        - Severity level (Critical, High, Medium, Low)
        - Description of the issue
        - Potential impact
        - Recommended remediation
        - Code examples for fixes
        
        Generate a detailed security report with actionable recommendations.
        """
        
        audit_report = await self.think(audit_prompt, {
            "project": project,
            "security_domains": self.security_domains,
            "vulnerability_types": self.vulnerability_types
        })
        
        # Store security findings
        findings = self._parse_security_findings(audit_report)
        project.security_findings.extend(findings)
        shared_state.update_project(project_id, security_findings=project.security_findings)
        
        return {
            "audit_report": audit_report,
            "findings_count": len(findings),
            "critical_issues": len([f for f in findings if f.get("severity") == "Critical"]),
            "status": "completed"
        }
    
    async def _implement_authentication(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement secure authentication system."""
        project_id = task_data["project_id"]
        auth_methods = task_data.get("methods", ["email_password"])
        
        auth_prompt = f"""
        Implement a secure authentication system for Flutter with these methods:
        {auth_methods}
        
        Create a complete authentication implementation including:
        
        1. **Authentication Service**: Create an abstract authentication service with methods for sign in, sign up, sign out, password reset, and getting current user.
        
        2. **Secure Token Management**:
           - JWT token handling
           - Refresh token implementation
           - Secure token storage
           - Token expiration handling
        
        3. **Biometric Authentication** (if supported): Implement biometric authentication service with availability check and authentication methods.
        
        4. **Multi-Factor Authentication**:
           - SMS verification
           - TOTP implementation
           - Backup codes
        
        5. **Security Features**:
           - Password strength validation
           - Account lockout protection
           - Suspicious activity detection
           - Session management
        
        6. **Error Handling**:
           - Secure error messages
           - Rate limiting
           - Audit logging
        
        Use these security best practices:
        - Never store passwords in plain text
        - Use secure random number generation
        - Implement proper input validation
        - Use HTTPS for all auth communications
        - Implement proper session timeout
        - Use secure storage for sensitive data
        
        Provide complete, production-ready authentication code.
        """
        
        auth_implementation = await self.think(auth_prompt, {
            "methods": auth_methods,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "auth_methods": auth_methods,
            "implementation": auth_implementation,
            "security_features": ["token_management", "biometric_auth", "mfa"],
            "status": "implemented"
        }
    
    async def _implement_secure_storage(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement secure data storage."""
        project_id = task_data["project_id"]
        data_types = task_data.get("data_types", ["user_data", "tokens"])
        
        storage_prompt = f"""
        Implement secure storage for these data types: {data_types}
        
        Create a comprehensive secure storage system:
        
        1. **Secure Storage Service**: Abstract class for secure data storage with methods for storing/retrieving strings, secure data, and key management.
        
        2. **Encryption Implementation**:
           - AES-256 encryption
           - Secure key derivation (PBKDF2)
           - Initialization vectors
           - Authentication tags
        
        3. **Key Management**:
           - Hardware security module usage
           - Key rotation strategy
           - Master key protection
           - Key escrow considerations
        
        4. **Platform-Specific Storage**:
           - iOS: Keychain Services
           - Android: EncryptedSharedPreferences
           - Cross-platform: flutter_secure_storage
        
        5. **Database Encryption**: Encrypted database service with methods for opening encrypted databases, encrypting tables, and creating secure backups.
        
        6. **Data Classification**:
           - Public data (no encryption needed)
           - Internal data (app-level encryption)
           - Confidential data (hardware-backed encryption)
           - Restricted data (additional access controls)
        
        Security considerations:
        - Use hardware-backed keystores when available
        - Implement proper key lifecycle management
        - Use authenticated encryption (AES-GCM)
        - Implement secure deletion
        - Add integrity checking
        - Monitor for tampering attempts
        
        Provide complete secure storage implementation.
        """
        
        storage_implementation = await self.think(storage_prompt, {
            "data_types": data_types,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "data_types": data_types,
            "implementation": storage_implementation,
            "encryption_methods": ["AES-256", "hardware_backed"],
            "status": "implemented"
        }
    
    async def _implement_network_security(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement network security measures."""
        project_id = task_data["project_id"]
        api_endpoints = task_data.get("endpoints", [])
        
        network_prompt = f"""
        Implement comprehensive network security for these API endpoints:
        {api_endpoints}
        
        Create secure networking implementation:
        
        1. **HTTP Client Configuration**: Secure HTTP client with interceptors for security headers, response validation, and error handling. Implement certificate pinning and secure client configuration.
        
        2. **Certificate Pinning**:
           - Pin specific certificates
           - Pin public keys
           - Backup pin strategy
           - Pin failure handling
        
        3. **Request Security**:
           - Request signing
           - Timestamp validation
           - Nonce implementation
           - Rate limiting
        
        4. **API Security Headers**: Implement security headers including content type, authorization, request IDs, and custom security headers with proper token management and timestamp validation.
        
        5. **Response Validation**:
           - Response signature verification
           - Content type validation
           - Size limits
           - Malformed response handling
        
        6. **Error Handling**:
           - Secure error messages
           - Network timeout handling
           - Retry logic with backoff
           - Circuit breaker pattern
        
        Security features to implement:
        - TLS 1.3 enforcement
        - Certificate transparency
        - HTTP Strict Transport Security
        - Content Security Policy
        - Cross-Origin Resource Sharing
        - API rate limiting
        - Request/response encryption
        
        Provide complete network security implementation.
        """
        
        network_implementation = await self.think(network_prompt, {
            "endpoints": api_endpoints,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "endpoints": api_endpoints,
            "implementation": network_implementation,
            "security_features": ["certificate_pinning", "request_signing", "response_validation"],
            "status": "implemented"
        }
    
    def _parse_security_findings(self, audit_report: str) -> List[Dict[str, Any]]:
        """Parse security findings from audit report."""
        # Simplified parsing - in real implementation, this would be more sophisticated
        findings = []
        
        # This would parse the LLM output to extract structured findings
        # For now, create a sample finding
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
                if project and filename in project.files_created:
                    file_content = project.files_created[filename]
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
                project.security_findings.append(finding)
                shared_state.update_project(project_id, security_findings=project.security_findings)
    
    async def _handle_general_security_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general security tasks."""
        response = await self.think(f"Handle security task: {task_description}", task_data)
        return {"response": response, "task": task_description}
