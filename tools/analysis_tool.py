"""
Analysis tool for code analysis, quality checks, and security scanning.
"""

import os
import re
import time
import json
from typing import Dict, Any, Optional, List, Union
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool
from .file_tool import FileTool

class AnalysisTool(BaseTool):
    """
    Tool for code analysis, quality checks, and security scanning.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="analysis",
            description="Perform code analysis, quality checks, and security scanning",
            timeout=120
        )
        self.project_directory = project_directory or os.getcwd()
        self.terminal = TerminalTool(self.project_directory)
        self.file_tool = FileTool(self.project_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute analysis operation.
        
        Args:
            operation: Type of operation (dart_analyze, security_scan, complexity, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with analysis results
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        start_time = time.time()
        
        try:
            if operation == "dart_analyze":
                return await self._dart_analyze(**kwargs)
            elif operation == "security_scan":
                return await self._security_scan(**kwargs)
            elif operation == "complexity_analysis":
                return await self._complexity_analysis(**kwargs)
            elif operation == "dependency_check":
                return await self._dependency_check(**kwargs)
            elif operation == "code_metrics":
                return await self._code_metrics(**kwargs)
            elif operation == "test_coverage":
                return await self._test_coverage(**kwargs)
            elif operation == "lint_check":
                return await self._lint_check(**kwargs)
            elif operation == "dead_code":
                return await self._dead_code_analysis(**kwargs)
            elif operation == "performance_analysis":
                return await self._performance_analysis(**kwargs)
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Unknown analysis operation: {operation}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Analysis operation '{operation}' failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _dart_analyze(self, file_path: Optional[str] = None, fix: bool = False, **kwargs) -> ToolResult:
        """Analyze Dart code for issues."""
        command = "dart analyze"
        
        if file_path:
            command += f" {file_path}"
        
        if fix:
            command += " --fix"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS or result.output:
            # Parse analysis results
            issues = self._parse_dart_analyze_output(result.output)
            
            result.data = {
                "file_path": file_path,
                "fix_applied": fix,
                "total_issues": len(issues),
                "errors": len([i for i in issues if i["severity"] == "error"]),
                "warnings": len([i for i in issues if i["severity"] == "warning"]),
                "infos": len([i for i in issues if i["severity"] == "info"]),
                "issues": issues
            }
        
        return result
    
    async def _security_scan(self, scan_type: str = "basic", **kwargs) -> ToolResult:
        """Perform security analysis."""
        security_issues = []
        
        if scan_type in ["basic", "comprehensive"]:
            # Check for common security issues in Dart/Flutter code
            security_issues.extend(await self._check_hardcoded_secrets())
            security_issues.extend(await self._check_insecure_network_calls())
            security_issues.extend(await self._check_insecure_storage())
            security_issues.extend(await self._check_permission_issues())
        
        if scan_type == "comprehensive":
            # Additional comprehensive checks
            security_issues.extend(await self._check_cryptographic_issues())
            security_issues.extend(await self._check_input_validation())
            security_issues.extend(await self._check_dependency_vulnerabilities())
        
        severity_counts = {}
        for issue in security_issues:
            severity = issue.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Security scan completed: {len(security_issues)} issues found",
            data={
                "scan_type": scan_type,
                "total_issues": len(security_issues),
                "severity_breakdown": severity_counts,
                "issues": security_issues
            }
        )
    
    async def _complexity_analysis(self, file_path: Optional[str] = None, **kwargs) -> ToolResult:
        """Analyze code complexity."""
        target_files = []
        
        if file_path:
            target_files = [file_path]
        else:
            # Find all Dart files
            result = await self.file_tool.execute("search", pattern="*.dart")
            if result.status == ToolStatus.SUCCESS:
                target_files = result.data.get("matches", [])
        
        complexity_results = []
        
        for file in target_files:
            file_result = await self.file_tool.execute("read", file_path=file)
            if file_result.status == ToolStatus.SUCCESS:
                complexity = self._calculate_complexity(file_result.output, file)
                complexity_results.append(complexity)
        
        # Calculate overall metrics
        total_lines = sum(r["lines_of_code"] for r in complexity_results)
        avg_complexity = sum(r["cyclomatic_complexity"] for r in complexity_results) / len(complexity_results) if complexity_results else 0
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Complexity analysis completed for {len(complexity_results)} files",
            data={
                "files_analyzed": len(complexity_results),
                "total_lines_of_code": total_lines,
                "average_complexity": avg_complexity,
                "file_results": complexity_results
            }
        )
    
    async def _dependency_check(self, **kwargs) -> ToolResult:
        """Check dependencies for issues."""
        # Read pubspec.yaml
        pubspec_result = await self.file_tool.read_yaml("pubspec.yaml")
        
        if pubspec_result.status != ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Could not read pubspec.yaml"
            )
        
        pubspec = pubspec_result.data["yaml_data"]
        dependencies = pubspec.get("dependencies", {})
        dev_dependencies = pubspec.get("dev_dependencies", {})
        
        # Check for outdated packages
        outdated_result = await self.terminal.execute("flutter pub outdated --json")
        outdated_info = {}
        
        if outdated_result.status == ToolStatus.SUCCESS:
            try:
                outdated_info = json.loads(outdated_result.output)
            except json.JSONDecodeError:
                pass
        
        # Analyze dependencies
        dependency_issues = []
        
        # Check for version constraints
        for dep_name, dep_version in dependencies.items():
            if isinstance(dep_version, str):
                if "^" not in dep_version and ">" not in dep_version and "<" not in dep_version:
                    dependency_issues.append({
                        "type": "version_constraint",
                        "severity": "warning",
                        "message": f"Dependency '{dep_name}' has no version constraint",
                        "dependency": dep_name,
                        "version": dep_version
                    })
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Dependency check completed: {len(dependency_issues)} issues found",
            data={
                "total_dependencies": len(dependencies),
                "total_dev_dependencies": len(dev_dependencies),
                "issues": dependency_issues,
                "outdated_info": outdated_info
            }
        )
    
    async def _code_metrics(self, **kwargs) -> ToolResult:
        """Calculate code metrics."""
        # Find all Dart files
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        
        if dart_files_result.status != ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Could not find Dart files"
            )
        
        dart_files = dart_files_result.data.get("matches", [])
        
        metrics = {
            "total_files": len(dart_files),
            "total_lines": 0,
            "total_classes": 0,
            "total_methods": 0,
            "total_widgets": 0,
            "test_files": 0,
            "file_metrics": []
        }
        
        for file_path in dart_files:
            file_result = await self.file_tool.execute("read", file_path=file_path)
            if file_result.status == ToolStatus.SUCCESS:
                file_metrics = self._calculate_file_metrics(file_result.output, file_path)
                metrics["file_metrics"].append(file_metrics)
                
                metrics["total_lines"] += file_metrics["lines_of_code"]
                metrics["total_classes"] += file_metrics["class_count"]
                metrics["total_methods"] += file_metrics["method_count"]
                metrics["total_widgets"] += file_metrics["widget_count"]
                
                if "test" in file_path:
                    metrics["test_files"] += 1
        
        # Calculate additional metrics
        metrics["average_lines_per_file"] = metrics["total_lines"] / metrics["total_files"] if metrics["total_files"] > 0 else 0
        metrics["test_coverage_ratio"] = metrics["test_files"] / metrics["total_files"] if metrics["total_files"] > 0 else 0
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Code metrics calculated for {metrics['total_files']} files",
            data=metrics
        )
    
    async def _test_coverage(self, **kwargs) -> ToolResult:
        """Analyze test coverage."""
        # Run tests with coverage
        coverage_result = await self.terminal.execute("flutter test --coverage")
        
        if coverage_result.status != ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Failed to run tests with coverage"
            )
        
        # Check if coverage file exists
        coverage_file = os.path.join(self.project_directory, "coverage", "lcov.info")
        coverage_data = {}
        
        if os.path.exists(coverage_file):
            coverage_data = await self._parse_lcov_file(coverage_file)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Test coverage analysis completed",
            data={
                "coverage_file_exists": os.path.exists(coverage_file),
                "coverage_data": coverage_data
            }
        )
    
    async def _lint_check(self, **kwargs) -> ToolResult:
        """Perform linting checks."""
        # Use dart analyze as the primary linter
        analyze_result = await self._dart_analyze()
        
        # Additional custom lint checks
        custom_issues = []
        
        # Find all Dart files
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        
        if dart_files_result.status == ToolStatus.SUCCESS:
            dart_files = dart_files_result.data.get("matches", [])
            
            for file_path in dart_files:
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    file_issues = self._custom_lint_checks(file_result.output, file_path)
                    custom_issues.extend(file_issues)
        
        total_issues = (analyze_result.data.get("total_issues", 0) if analyze_result.data else 0) + len(custom_issues)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Lint check completed: {total_issues} issues found",
            data={
                "dart_analyze_issues": analyze_result.data.get("issues", []) if analyze_result.data else [],
                "custom_lint_issues": custom_issues,
                "total_issues": total_issues
            }
        )
    
    async def _dead_code_analysis(self, **kwargs) -> ToolResult:
        """Analyze for dead/unused code."""
        dead_code_issues = []
        
        # Find all Dart files
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        
        if dart_files_result.status == ToolStatus.SUCCESS:
            dart_files = dart_files_result.data.get("matches", [])
            
            # Build a map of defined and used symbols
            defined_symbols = {}
            used_symbols = set()
            
            for file_path in dart_files:
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    symbols = self._extract_symbols(file_result.output, file_path)
                    defined_symbols.update(symbols["defined"])
                    used_symbols.update(symbols["used"])
            
            # Find unused symbols
            for symbol, info in defined_symbols.items():
                if symbol not in used_symbols and not symbol.startswith("_") and symbol != "main":
                    dead_code_issues.append({
                        "type": "unused_symbol",
                        "severity": "warning",
                        "symbol": symbol,
                        "file": info["file"],
                        "line": info.get("line", 0),
                        "message": f"Unused symbol '{symbol}'"
                    })
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Dead code analysis completed: {len(dead_code_issues)} issues found",
            data={
                "dead_code_issues": dead_code_issues,
                "total_issues": len(dead_code_issues)
            }
        )
    
    async def _performance_analysis(self, **kwargs) -> ToolResult:
        """Analyze code for performance issues."""
        performance_issues = []
        
        # Find all Dart files
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        
        if dart_files_result.status == ToolStatus.SUCCESS:
            dart_files = dart_files_result.data.get("matches", [])
            
            for file_path in dart_files:
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    file_issues = self._check_performance_issues(file_result.output, file_path)
                    performance_issues.extend(file_issues)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Performance analysis completed: {len(performance_issues)} issues found",
            data={
                "performance_issues": performance_issues,
                "total_issues": len(performance_issues)
            }
        )
    
    def _parse_dart_analyze_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse dart analyze output."""
        issues = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if '•' in line and any(keyword in line.lower() for keyword in ['error', 'warning', 'info']):
                # Parse the issue
                parts = line.split('•')
                if len(parts) >= 2:
                    message_part = parts[1].strip()
                    
                    # Extract severity
                    severity = "info"
                    if "error" in line.lower():
                        severity = "error"
                    elif "warning" in line.lower():
                        severity = "warning"
                    
                    # Try to extract file and line info
                    file_info = parts[0].strip() if parts[0].strip() else "unknown"
                    
                    issues.append({
                        "severity": severity,
                        "message": message_part,
                        "location": file_info,
                        "raw_line": line
                    })
        
        return issues
    
    async def _check_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets."""
        issues = []
        
        # Patterns for common secrets
        secret_patterns = [
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']', "API key"),
            (r'password\s*[:=]\s*["\'][^"\']+["\']', "Password"),
            (r'secret\s*[:=]\s*["\'][^"\']+["\']', "Secret"),
            (r'token\s*[:=]\s*["\'][^"\']+["\']', "Token"),
            (r'["\'][A-Za-z0-9]{20,}["\']', "Potential API key")
        ]
        
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        if dart_files_result.status == ToolStatus.SUCCESS:
            for file_path in dart_files_result.data.get("matches", []):
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    content = file_result.output
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, secret_type in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    "type": "hardcoded_secret",
                                    "severity": "high",
                                    "message": f"Potential {secret_type} found",
                                    "file": file_path,
                                    "line": line_num,
                                    "line_content": line.strip()
                                })
        
        return issues
    
    async def _check_insecure_network_calls(self) -> List[Dict[str, Any]]:
        """Check for insecure network calls."""
        issues = []
        
        # Patterns for insecure network usage
        insecure_patterns = [
            (r'http://[^"\'\s]+', "HTTP URL (should use HTTPS)"),
            (r'allowInsecure\s*:\s*true', "Insecure connection allowed"),
            (r'badCertificateCallback', "Certificate validation bypassed")
        ]
        
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        if dart_files_result.status == ToolStatus.SUCCESS:
            for file_path in dart_files_result.data.get("matches", []):
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    content = file_result.output
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, issue_type in insecure_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    "type": "insecure_network",
                                    "severity": "medium",
                                    "message": issue_type,
                                    "file": file_path,
                                    "line": line_num,
                                    "line_content": line.strip()
                                })
        
        return issues
    
    async def _check_insecure_storage(self) -> List[Dict[str, Any]]:
        """Check for insecure storage usage."""
        issues = []
        
        # Patterns for insecure storage
        storage_patterns = [
            (r'SharedPreferences.*\.setString.*password', "Password stored in SharedPreferences"),
            (r'SharedPreferences.*\.setString.*token', "Token stored in SharedPreferences"),
            (r'File.*\.writeAsString.*password', "Password written to file")
        ]
        
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        if dart_files_result.status == ToolStatus.SUCCESS:
            for file_path in dart_files_result.data.get("matches", []):
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    content = file_result.output
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, issue_type in storage_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    "type": "insecure_storage",
                                    "severity": "high",
                                    "message": issue_type,
                                    "file": file_path,
                                    "line": line_num,
                                    "line_content": line.strip()
                                })
        
        return issues
    
    async def _check_permission_issues(self) -> List[Dict[str, Any]]:
        """Check for permission-related issues."""
        issues = []
        
        # Check Android manifest
        android_manifest = "android/app/src/main/AndroidManifest.xml"
        manifest_result = await self.file_tool.execute("read", file_path=android_manifest)
        
        if manifest_result.status == ToolStatus.SUCCESS:
            content = manifest_result.output
            
            # Check for dangerous permissions
            dangerous_permissions = [
                "android.permission.READ_CONTACTS",
                "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO",
                "android.permission.ACCESS_FINE_LOCATION"
            ]
            
            for permission in dangerous_permissions:
                if permission in content:
                    issues.append({
                        "type": "permission_issue",
                        "severity": "medium",
                        "message": f"Dangerous permission requested: {permission}",
                        "file": android_manifest,
                        "permission": permission
                    })
        
        return issues
    
    async def _check_cryptographic_issues(self) -> List[Dict[str, Any]]:
        """Check for cryptographic issues."""
        issues = []
        
        # Patterns for crypto issues
        crypto_patterns = [
            (r'MD5|SHA1', "Weak hash algorithm"),
            (r'DES|3DES', "Weak encryption algorithm"),
            (r'Random\(\)', "Insecure random number generation")
        ]
        
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        if dart_files_result.status == ToolStatus.SUCCESS:
            for file_path in dart_files_result.data.get("matches", []):
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    content = file_result.output
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, issue_type in crypto_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    "type": "cryptographic_issue",
                                    "severity": "high",
                                    "message": issue_type,
                                    "file": file_path,
                                    "line": line_num,
                                    "line_content": line.strip()
                                })
        
        return issues
    
    async def _check_input_validation(self) -> List[Dict[str, Any]]:
        """Check for input validation issues."""
        issues = []
        
        # Patterns for input validation issues
        validation_patterns = [
            (r'TextEditingController.*\.text(?!\s*\.isEmpty)', "Unvalidated text input"),
            (r'int\.parse\(.*\)(?!\s*catch)', "Unhandled integer parsing"),
            (r'double\.parse\(.*\)(?!\s*catch)', "Unhandled double parsing")
        ]
        
        dart_files_result = await self.file_tool.execute("search", pattern="*.dart")
        if dart_files_result.status == ToolStatus.SUCCESS:
            for file_path in dart_files_result.data.get("matches", []):
                file_result = await self.file_tool.execute("read", file_path=file_path)
                if file_result.status == ToolStatus.SUCCESS:
                    content = file_result.output
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, issue_type in validation_patterns:
                            if re.search(pattern, line):
                                issues.append({
                                    "type": "input_validation",
                                    "severity": "medium",
                                    "message": issue_type,
                                    "file": file_path,
                                    "line": line_num,
                                    "line_content": line.strip()
                                })
        
        return issues
    
    async def _check_dependency_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check for dependency vulnerabilities."""
        issues = []
        
        # This would typically integrate with a vulnerability database
        # For now, we'll do basic checks
        
        pubspec_result = await self.file_tool.read_yaml("pubspec.yaml")
        if pubspec_result.status == ToolStatus.SUCCESS:
            pubspec = pubspec_result.data["yaml_data"]
            dependencies = pubspec.get("dependencies", {})
            
            # Check for known vulnerable packages (example)
            vulnerable_packages = {
                "http": ["0.12.0", "0.12.1"],  # Example vulnerable versions
            }
            
            for dep_name, dep_version in dependencies.items():
                if dep_name in vulnerable_packages:
                    if isinstance(dep_version, str) and any(vuln_ver in dep_version for vuln_ver in vulnerable_packages[dep_name]):
                        issues.append({
                            "type": "vulnerable_dependency",
                            "severity": "high",
                            "message": f"Vulnerable version of {dep_name}: {dep_version}",
                            "package": dep_name,
                            "version": dep_version
                        })
        
        return issues
    
    def _calculate_complexity(self, content: str, file_path: str) -> Dict[str, Any]:
        """Calculate cyclomatic complexity for a file."""
        lines = content.split('\n')
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?']
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                for keyword in decision_keywords:
                    complexity += line.count(keyword)
        
        return {
            "file": file_path,
            "lines_of_code": len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
            "total_lines": len(lines),
            "cyclomatic_complexity": complexity
        }
    
    def _calculate_file_metrics(self, content: str, file_path: str) -> Dict[str, Any]:
        """Calculate various metrics for a file."""
        lines = content.split('\n')
        
        # Count different elements
        class_count = len(re.findall(r'\bclass\s+\w+', content))
        method_count = len(re.findall(r'\w+\s*\([^)]*\)\s*{', content))
        widget_count = len(re.findall(r'extends\s+\w*Widget|extends\s+State<', content))
        
        return {
            "file": file_path,
            "lines_of_code": len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
            "total_lines": len(lines),
            "class_count": class_count,
            "method_count": method_count,
            "widget_count": widget_count
        }
    
    async def _parse_lcov_file(self, file_path: str) -> Dict[str, Any]:
        """Parse LCOV coverage file."""
        file_result = await self.file_tool.execute("read", file_path=file_path)
        
        if file_result.status != ToolStatus.SUCCESS:
            return {}
        
        content = file_result.output
        coverage_data = {
            "files": [],
            "total_lines": 0,
            "covered_lines": 0
        }
        
        current_file = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('SF:'):
                current_file = {
                    "file": line[3:],
                    "lines_found": 0,
                    "lines_hit": 0
                }
            elif line.startswith('LF:') and current_file:
                current_file["lines_found"] = int(line[3:])
            elif line.startswith('LH:') and current_file:
                current_file["lines_hit"] = int(line[3:])
            elif line == 'end_of_record' and current_file:
                coverage_data["files"].append(current_file)
                coverage_data["total_lines"] += current_file["lines_found"]
                coverage_data["covered_lines"] += current_file["lines_hit"]
                current_file = None
        
        if coverage_data["total_lines"] > 0:
            coverage_data["coverage_percentage"] = (coverage_data["covered_lines"] / coverage_data["total_lines"]) * 100
        else:
            coverage_data["coverage_percentage"] = 0
        
        return coverage_data
    
    def _custom_lint_checks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Perform custom lint checks."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for TODO/FIXME comments
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    "type": "todo_comment",
                    "severity": "info",
                    "message": "TODO/FIXME comment found",
                    "file": file_path,
                    "line": line_num,
                    "line_content": line
                })
            
            # Check for print statements
            if line.startswith('print('):
                issues.append({
                    "type": "debug_print",
                    "severity": "warning",
                    "message": "Debug print statement found",
                    "file": file_path,
                    "line": line_num,
                    "line_content": line
                })
        
        return issues
    
    def _extract_symbols(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract defined and used symbols from code."""
        defined = {}
        used = set()
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Find class definitions
            class_match = re.search(r'\bclass\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(1)
                defined[class_name] = {"file": file_path, "line": line_num, "type": "class"}
            
            # Find function definitions
            func_match = re.search(r'\b(\w+)\s*\([^)]*\)\s*{', line)
            if func_match:
                func_name = func_match.group(1)
                defined[func_name] = {"file": file_path, "line": line_num, "type": "function"}
            
            # Find symbol usage (simplified)
            symbols = re.findall(r'\b[a-zA-Z_]\w*\b', line)
            used.update(symbols)
        
        return {"defined": defined, "used": used}
    
    def _check_performance_issues(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Check for potential performance issues."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for inefficient operations
            if 'setState(() {' in line and 'for' in line:
                issues.append({
                    "type": "performance_issue",
                    "severity": "warning",
                    "message": "Potential expensive operation in setState",
                    "file": file_path,
                    "line": line_num,
                    "line_content": line
                })
            
            # Check for missing const constructors
            if re.search(r'Widget\([^)]*\)(?!\s*const)', line):
                issues.append({
                    "type": "performance_issue",
                    "severity": "info",
                    "message": "Consider using const constructor",
                    "file": file_path,
                    "line": line_num,
                    "line_content": line
                })
        
        return issues
    
    # Public methods for test and agent compatibility
    async def dart_analyze(self, **kwargs):
        return await self.execute("dart_analyze", **kwargs)
    
    async def security_scan(self, **kwargs):
        return await self.execute("security_scan", **kwargs)
    
    async def calculate_metrics(self, **kwargs):
        return await self.execute("code_metrics", **kwargs)
    
    async def analyze_dependencies(self, **kwargs):
        return await self.execute("dependency_check", **kwargs)
    
    async def analyze_performance(self, **kwargs):
        return await self.execute("performance_analysis", **kwargs)
