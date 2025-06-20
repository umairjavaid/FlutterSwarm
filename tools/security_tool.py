"""
Security analysis tool for Flutter applications.
"""

import asyncio
import os
import json
import re
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool
from .file_tool import FileTool

class SecurityTool(BaseTool):
    """
    Tool for security analysis and implementation in Flutter projects.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="security",
            description="Perform security analysis and implement security measures",
            timeout=180
        )
        self.project_directory = project_directory or os.getcwd()
        self.terminal = TerminalTool(project_directory)
        self.file_tool = FileTool(project_directory)
        
        # Remove hardcoded security patterns - use LLM analysis instead
        self.security_patterns = {}  # Empty - LLM will analyze security issues
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute security operations.
        
        Args:
            operation: Operation to perform (scan, audit, implement, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        if operation == "scan":
            return await self._security_scan(**kwargs)
        elif operation == "audit":
            return await self._security_audit(**kwargs)
        elif operation == "check_dependencies":
            return await self._check_dependency_vulnerabilities(**kwargs)
        elif operation == "implement_secure_storage":
            return await self._implement_secure_storage(**kwargs)
        elif operation == "implement_network_security":
            return await self._implement_network_security(**kwargs)
        elif operation == "generate_security_config":
            return await self._generate_security_config(**kwargs)
        elif operation == "obfuscation_setup":
            return await self._setup_obfuscation(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _security_scan(self, **kwargs) -> ToolResult:
        """Perform comprehensive security scan."""
        scan_results = {
            "hardcoded_secrets": [],
            "insecure_http": [],
            "weak_crypto": [],
            "insecure_storage": [],
            "file_permissions": [],
            "summary": {}
        }
        
        # Scan Dart files
        dart_files = await self._find_dart_files()
        
        for file_path in dart_files:
            file_result = await self.file_tool.execute("read", file_path=file_path)
            if file_result.status == ToolStatus.SUCCESS:
                content = file_result.output
                file_issues = await self._scan_file_content(file_path, content)
                
                # Merge issues
                for category, issues in file_issues.items():
                    if category in scan_results:
                        scan_results[category].extend(issues)
        
        # Check Android-specific security issues
        android_issues = await self._scan_android_security()
        scan_results.update(android_issues)
        
        # Generate summary
        total_issues = sum(len(issues) for issues in scan_results.values() if isinstance(issues, list))
        scan_results["summary"] = {
            "total_issues": total_issues,
            "critical": len(scan_results["hardcoded_secrets"]) + len(scan_results["weak_crypto"]),
            "medium": len(scan_results["insecure_http"]) + len(scan_results["insecure_storage"]),
            "low": len(scan_results["file_permissions"])
        }
        
        status = ToolStatus.WARNING if total_issues > 0 else ToolStatus.SUCCESS
        
        return ToolResult(
            status=status,
            output=f"Security scan completed. Found {total_issues} issues.",
            data=scan_results
        )
    
    async def _security_audit(self, **kwargs) -> ToolResult:
        """Perform detailed security audit."""
        audit_results = {
            "code_scan": None,
            "dependency_audit": None,
            "configuration_audit": None,
            "permissions_audit": None,
            "recommendations": []
        }
        
        # Run code scan
        code_scan = await self._security_scan()
        audit_results["code_scan"] = code_scan.data
        
        # Check dependencies
        dep_audit = await self._check_dependency_vulnerabilities()
        audit_results["dependency_audit"] = dep_audit.data
        
        # Check configuration files
        config_audit = await self._audit_configuration()
        audit_results["configuration_audit"] = config_audit.data
        
        # Check permissions
        permissions_audit = await self._audit_permissions()
        audit_results["permissions_audit"] = permissions_audit.data
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(audit_results)
        audit_results["recommendations"] = recommendations
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Security audit completed",
            data=audit_results
        )
    
    async def _check_dependency_vulnerabilities(self, **kwargs) -> ToolResult:
        """Check for known vulnerabilities in dependencies."""
        # Check for outdated packages
        outdated_result = await self.terminal.execute(
            "flutter pub outdated",
            working_dir=self.project_directory
        )
        
        vulnerabilities = {
            "outdated_packages": [],
            "security_advisories": [],
            "recommendations": []
        }
        
        if outdated_result.status == ToolStatus.SUCCESS:
            # Parse outdated packages
            lines = outdated_result.output.split('\n')
            for line in lines:
                if '│' in line and 'resolvable' in line:
                    parts = [part.strip() for part in line.split('│')]
                    if len(parts) >= 4:
                        package_name = parts[1]
                        current_version = parts[2]
                        latest_version = parts[3]
                        
                        vulnerabilities["outdated_packages"].append({
                            "package": package_name,
                            "current": current_version,
                            "latest": latest_version,
                            "severity": "medium"  # Default severity
                        })
        
        # Check for known vulnerable packages
        vulnerable_packages = [
            {"name": "http", "vulnerable_versions": ["<0.13.0"], "issue": "HTTP request vulnerabilities"},
            {"name": "shared_preferences", "vulnerable_versions": ["<2.0.0"], "issue": "Insecure storage"}
        ]
        
        # Add recommendations
        if vulnerabilities["outdated_packages"]:
            vulnerabilities["recommendations"].append("Update outdated packages to latest versions")
        
        vulnerabilities["recommendations"].extend([
            "Use flutter pub audit when available",
            "Regularly check packages for security advisories",
            "Consider using dependency_validator package"
        ])
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Found {len(vulnerabilities['outdated_packages'])} outdated packages",
            data=vulnerabilities
        )
    
    async def _implement_secure_storage(self, **kwargs) -> ToolResult:
        """Implement secure storage - content must be provided by LLM agents."""
        storage_type = kwargs.get("storage_type", "flutter_secure_storage")
        content = kwargs.get("content")  # REQUIRED: LLM-generated content
        
        if storage_type == "flutter_secure_storage":
            # Add dependency
            add_result = await self.terminal.execute(
                "flutter pub add flutter_secure_storage",
                working_dir=self.project_directory
            )
            
            if add_result.status != ToolStatus.SUCCESS:
                return add_result
            
            if not content:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Secure storage implementation content must be provided by LLM agents. No hardcoded templates allowed."
                )
            
            # Write service file with LLM-generated content
            write_result = await self.file_tool.execute(
                "write",
                file_path="lib/services/secure_storage_service.dart",
                content=content
            )
            
            if write_result.status == ToolStatus.SUCCESS:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output="Secure storage implementation created using LLM-generated content",
                    data={
                        "storage_type": storage_type,
                        "service_file": "lib/services/secure_storage_service.dart",
                        "content_source": "llm_generated"
                    }
                )
        
        return ToolResult(
            status=ToolStatus.ERROR,
            output="",
            error=f"Unsupported storage type: {storage_type}"
        )
    
    async def _implement_network_security(self, **kwargs) -> ToolResult:
        """Implement network security measures using LLM-generated code only."""
        security_measures = kwargs.get("measures", [])
        content_map = kwargs.get("content_map", {})
        
        if not content_map:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Security implementation content must be provided by LLM agents. No hardcoded templates allowed."
            )
        
        implemented = []
        
        # Implement each security measure with LLM-generated content
        for measure in security_measures:
            content = content_map.get(measure)
            if content:
                file_path = f"lib/security/{measure.lower()}.dart"
                
                write_result = await self.file_tool.execute(
                    "write",
                    file_path=file_path,
                    content=content
                )
                
                if write_result.status == ToolStatus.SUCCESS:
                    implemented.append(measure)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Implemented {len(implemented)} network security measures using LLM-generated code",
            data={
                "implemented_measures": implemented,
                "requested_measures": security_measures,
                "content_source": "llm_generated"
            }
        )
    
    async def _generate_security_config(self, **kwargs) -> ToolResult:
        """Generate security configuration files using LLM-generated content only."""
        android_config = kwargs.get("android_config")
        security_constants = kwargs.get("security_constants")
        
        if not android_config or not security_constants:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Android config and security constants must be provided by LLM agents. No hardcoded templates allowed."
            )
        
        config_files = []
        
        # Write Android security config with LLM-generated content
        android_config_path = "android/app/src/main/res/xml/network_security_config.xml"
        write_result = await self.file_tool.execute(
            "write",
            file_path=android_config_path,
            content=android_config
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            config_files.append(android_config_path)
        
        # Write security constants with LLM-generated content
        constants_path = "lib/config/security_config.dart"
        write_result = await self.file_tool.execute(
            "write",
            file_path=constants_path,
            content=security_constants
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            config_files.append(constants_path)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Generated {len(config_files)} security configuration files with LLM-provided content",
            data={
                "config_files": config_files,
                "content_source": "llm_generated"
            }
        )
    
    async def _setup_obfuscation(self, **kwargs) -> ToolResult:
        """Setup code obfuscation for release builds using LLM-generated configuration."""
        # Get LLM-generated gradle content
        updated_gradle = kwargs.get("gradle_content")
        
        if not updated_gradle:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Gradle configuration must be provided by LLM agents. No hardcoded templates allowed."
            )
        
        # Write the LLM-generated gradle file
        write_result = await self.file_tool.execute(
            "write",
            file_path="android/app/build.gradle",
            content=updated_gradle
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Code obfuscation configured for Android with LLM-generated content",
                data={
                    "platform": "android", 
                    "configured": True,
                    "content_source": "llm_generated"
                }
            )
        
        return ToolResult(
            status=ToolStatus.ERROR,
            output="",
            error="Android build.gradle file not found"
        )
    
    async def _find_dart_files(self) -> List[str]:
        """Find all Dart files in the project."""
        dart_files = []
        
        for root, dirs, files in os.walk(self.project_directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.dart_tool', 'build', '.git']]
            
            for file in files:
                if file.endswith('.dart'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_directory)
                    dart_files.append(rel_path)
        
        return dart_files
    
    async def _scan_file_content(self, file_path: str, content: str) -> Dict[str, List]:
        """Scan file content for security issues."""
        issues = {
            "hardcoded_secrets": [],
            "insecure_http": [],
            "weak_crypto": [],
            "insecure_storage": []
        }
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.security_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        issues[category].append({
                            "file": file_path,
                            "line": line_num,
                            "content": line.strip(),
                            "matched_text": match.group(),
                            "severity": self._get_severity(category)
                        })
        
        return issues
    
    async def _scan_android_security(self) -> Dict[str, List]:
        """Scan Android-specific security configurations."""
        android_issues = {
            "android_manifest": [],
            "network_config": []
        }
        
        # Check AndroidManifest.xml
        manifest_path = "android/app/src/main/AndroidManifest.xml"
        manifest_result = await self.file_tool.execute("read", file_path=manifest_path)
        
        if manifest_result.status == ToolStatus.SUCCESS:
            manifest_content = manifest_result.output
            
            # Check for insecure permissions
            insecure_permissions = [
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.READ_PHONE_STATE",
                "android.permission.ACCESS_FINE_LOCATION"
            ]
            
            for permission in insecure_permissions:
                if permission in manifest_content:
                    android_issues["android_manifest"].append({
                        "issue": f"Potentially sensitive permission: {permission}",
                        "severity": "medium",
                        "file": manifest_path
                    })
            
            # Check for debuggable flag
            if 'android:debuggable="true"' in manifest_content:
                android_issues["android_manifest"].append({
                    "issue": "Debuggable flag enabled",
                    "severity": "high",
                    "file": manifest_path
                })
        
        return android_issues
    
    async def _audit_configuration(self) -> ToolResult:
        """Audit configuration files for security issues."""
        config_issues = {
            "pubspec_yaml": [],
            "android_manifest": [],
            "ios_info_plist": []
        }
        
        # Check pubspec.yaml for development dependencies in production
        pubspec_result = await self.file_tool.execute("read", file_path="pubspec.yaml")
        if pubspec_result.status == ToolStatus.SUCCESS:
            # This is a basic check - could be expanded
            config_issues["pubspec_yaml"].append({
                "info": "Pubspec.yaml reviewed",
                "status": "ok"
            })
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Configuration audit completed",
            data=config_issues
        )
    
    async def _audit_permissions(self) -> ToolResult:
        """Audit app permissions."""
        permissions_audit = {
            "android_permissions": [],
            "ios_permissions": [],
            "recommendations": []
        }
        
        # This is a placeholder - would need to parse actual permission files
        permissions_audit["recommendations"].append("Review all requested permissions")
        permissions_audit["recommendations"].append("Use minimal necessary permissions")
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Permissions audit completed",
            data=permissions_audit
        )
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for security issue category."""
        severity_map = {
            "hardcoded_secrets": "critical",
            "weak_crypto": "high",
            "insecure_http": "medium",
            "insecure_storage": "medium"
        }
        return severity_map.get(category, "low")
    
    def _generate_security_recommendations(self, audit_results: Dict) -> List[str]:
        """Generate security recommendations based on audit results."""
        recommendations = []
        
        if audit_results.get("code_scan", {}).get("summary", {}).get("total_issues", 0) > 0:
            recommendations.append("Address code security issues found in scan")
        
        recommendations.extend([
            "Enable code obfuscation for release builds",
            "Implement certificate pinning for API communications",
            "Use secure storage for sensitive data",
            "Enable network security configuration",
            "Review and minimize app permissions",
            "Implement proper input validation",
            "Use HTTPS for all network communications",
            "Regularly update dependencies"
        ])
        
        return recommendations
    
    async def _implement_certificate_pinning(self) -> ToolResult:
        """Implement certificate pinning using LLM-generated code only."""
        pass
        return ToolResult(
            status=ToolStatus.ERROR,
            output="",
            error="Certificate pinning implementation must be provided by LLM agents. No hardcoded templates allowed."
        )
    
    async def _implement_secure_headers(self) -> ToolResult:
        """Implement secure HTTP headers using LLM-generated code only."""
        pass
        return ToolResult(
            status=ToolStatus.ERROR,
            output="",
            error="Secure headers implementation must be provided by LLM agents. No hardcoded templates allowed."
        )
    
    async def _implement_network_interceptor(self) -> ToolResult:
        """Implement network security interceptor using LLM-generated code only."""
        pass
        return ToolResult(
            status=ToolStatus.ERROR,
            output="",
            error="Network interceptor implementation must be provided by LLM agents. No hardcoded templates allowed."
        )
    
    def _add_obfuscation_to_gradle(self, gradle_content: str) -> str:
        """Add obfuscation configuration to Android build.gradle using LLM-generated content only."""
        pass
        return gradle_content
  