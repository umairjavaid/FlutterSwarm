"""
Unit tests for the SecurityAgent.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.security_agent import SecurityAgent
from shared.state import AgentStatus, MessageType, AgentMessage
from tests.mocks.mock_implementations import MockToolManager, MockAnthropicClient
from tests.fixtures.test_constants import AGENT_CAPABILITIES


@pytest.mark.unit
class TestSecurityAgent:
    """Test suite for SecurityAgent."""
    
    @pytest.fixture
    def security_agent(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create security agent for testing."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            return SecurityAgent()
    
    def test_initialization(self, security_agent):
        """Test security agent initialization."""
        assert security_agent.agent_id == "security"
        assert security_agent.capabilities == AGENT_CAPABILITIES["security"]
        assert not security_agent.is_running
        assert security_agent.status == AgentStatus.IDLE
        
    @pytest.mark.asyncio
    async def test_vulnerability_scanning(self, security_agent):
        """Test vulnerability scanning capabilities."""
        # Mock security scan tool
        security_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Security scan completed",
            data={
                "vulnerabilities": [
                    {
                        "severity": "HIGH",
                        "type": "insecure_storage",
                        "file": "lib/services/storage_service.dart",
                        "line": 42,
                        "description": "Sensitive data stored without encryption",
                        "recommendation": "Use secure storage with encryption"
                    },
                    {
                        "severity": "MEDIUM", 
                        "type": "weak_authentication",
                        "file": "lib/auth/auth_service.dart",
                        "line": 15,
                        "description": "Weak password requirements",
                        "recommendation": "Implement stronger password policy"
                    }
                ],
                "scan_time": 12.5,
                "files_scanned": 25
            }
        ))
        
        # Perform security scan
        result = await security_agent._perform_vulnerability_scan({
            "scan_type": "comprehensive",
            "target_directories": ["lib/", "test/"],
            "include_dependencies": True
        })
        
        # Verify scan results
        assert result["status"] == "completed"
        assert len(result["vulnerabilities"]) == 2
        assert result["vulnerabilities"][0]["severity"] == "HIGH"
        security_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_secure_storage_implementation(self, security_agent):
        """Test secure storage implementation."""
        # Mock secure storage code generation
        security_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:crypto/crypto.dart';

class SecureStorageService {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: IOSAccessibility.first_unlock_this_device,
    ),
  );
  
  Future<void> storeSecurely(String key, String value) async {
    final encryptedValue = _encrypt(value);
    await _storage.write(key: key, value: encryptedValue);
  }
  
  Future<String?> getSecurely(String key) async {
    final encryptedValue = await _storage.read(key: key);
    if (encryptedValue == null) return null;
    return _decrypt(encryptedValue);
  }
  
  String _encrypt(String value) {
    // Implementation of encryption
    return value; // Simplified for example
  }
  
  String _decrypt(String encryptedValue) {
    // Implementation of decryption
    return encryptedValue; // Simplified for example
  }
}
"""
        ))
        
        # Mock file operations
        security_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Secure storage service created"
        ))
        
        # Implement secure storage
        result = await security_agent._implement_secure_storage({
            "storage_type": "flutter_secure_storage",
            "encryption_algorithm": "AES-256",
            "key_derivation": "PBKDF2"
        })
        
        # Verify secure storage implementation
        assert result["status"] == "completed"
        security_agent.llm.ainvoke.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_authentication_security(self, security_agent):
        """Test authentication security implementation."""
        # Mock secure authentication code generation
        security_agent._implement_secure_auth = AsyncMock(return_value={
            "status": "completed",
            "auth_files": ["secure_auth_service.dart", "biometric_auth.dart"],
            "security_features": ["biometric", "mfa", "session_management"]
        })
        
        # Implement secure authentication
        result = await security_agent._setup_secure_authentication({
            "auth_methods": ["password", "biometric", "mfa"],
            "session_timeout": 1800,  # 30 minutes
            "password_policy": {
                "min_length": 12,
                "require_special_chars": True,
                "require_numbers": True,
                "require_uppercase": True
            }
        })
        
        # Verify authentication security
        assert result["status"] == "completed"
        security_agent._implement_secure_auth.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_network_security(self, security_agent):
        """Test network security implementation."""
        # Mock network security setup
        security_agent._setup_network_security = AsyncMock(return_value={
            "status": "completed",
            "security_features": ["ssl_pinning", "certificate_validation", "request_signing"],
            "network_files": ["secure_http_client.dart", "certificate_validator.dart"]
        })
        
        # Setup network security
        result = await security_agent._implement_network_security({
            "ssl_pinning": True,
            "certificate_validation": "strict",
            "request_encryption": True,
            "api_key_security": "header_based"
        })
        
        # Verify network security
        assert result["status"] == "completed"
        security_agent._setup_network_security.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_data_encryption(self, security_agent):
        """Test data encryption implementation."""
        # Mock encryption service generation
        security_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
import 'dart:convert';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';

class EncryptionService {
  static final _key = Key.fromSecureRandom(32);
  static final _iv = IV.fromSecureRandom(16);
  static final _encrypter = Encrypter(AES(_key));
  
  static String encryptData(String data) {
    final encrypted = _encrypter.encrypt(data, iv: _iv);
    return encrypted.base64;
  }
  
  static String decryptData(String encryptedData) {
    final encrypted = Encrypted.fromBase64(encryptedData);
    return _encrypter.decrypt(encrypted, iv: _iv);
  }
  
  static String hashData(String data) {
    final bytes = utf8.encode(data);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }
}
"""
        ))
        
        # Mock file operations
        security_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Encryption service created"
        ))
        
        # Implement data encryption
        result = await security_agent._implement_data_encryption({
            "encryption_algorithm": "AES-256",
            "key_management": "secure_random",
            "data_types": ["user_data", "sensitive_configs", "api_responses"]
        })
        
        # Verify encryption implementation
        assert result["status"] == "completed"
        security_agent.llm.ainvoke.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_permission_management(self, security_agent):
        """Test permission management implementation."""
        # Mock permission setup
        security_agent._setup_permissions = AsyncMock(return_value={
            "status": "completed",
            "permission_files": ["permission_handler.dart", "app_permissions.dart"],
            "managed_permissions": ["camera", "location", "storage", "contacts"]
        })
        
        # Setup permission management
        result = await security_agent._implement_permission_management({
            "required_permissions": ["camera", "location", "storage"],
            "permission_rationale": True,
            "graceful_degradation": True
        })
        
        # Verify permission management
        assert result["status"] == "completed"
        security_agent._setup_permissions.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_code_obfuscation(self, security_agent):
        """Test code obfuscation setup."""
        # Mock obfuscation setup
        security_agent._setup_code_obfuscation = AsyncMock(return_value={
            "status": "completed",
            "obfuscation_config": "android/app/proguard-rules.pro",
            "obfuscated_builds": ["release"]
        })
        
        # Setup code obfuscation
        result = await security_agent._implement_code_obfuscation({
            "obfuscation_level": "aggressive",
            "preserve_annotations": ["@override", "@required"],
            "target_builds": ["release"]
        })
        
        # Verify obfuscation setup
        assert result["status"] == "completed"
        security_agent._setup_code_obfuscation.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_security_audit(self, security_agent):
        """Test comprehensive security audit."""
        # Mock security audit
        security_agent._perform_security_audit = AsyncMock(return_value={
            "status": "completed",
            "audit_report": {
                "overall_score": 85,
                "categories": {
                    "authentication": 90,
                    "data_protection": 80,
                    "network_security": 85,
                    "code_security": 88
                },
                "recommendations": [
                    "Implement certificate pinning",
                    "Add additional input validation",
                    "Enable runtime security checks"
                ]
            }
        })
        
        # Perform security audit
        result = await security_agent._conduct_security_audit({
            "audit_scope": "comprehensive",
            "include_dependencies": True,
            "check_compliance": ["OWASP", "GDPR"]
        })
        
        # Verify audit results
        assert result["status"] == "completed"
        assert result["audit_report"]["overall_score"] == 85
        security_agent._perform_security_audit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_dependency_security_scan(self, security_agent):
        """Test dependency security scanning."""
        # Mock dependency scan
        security_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Dependency scan completed",
            data={
                "vulnerable_packages": [
                    {
                        "package": "http",
                        "version": "0.12.2",
                        "vulnerability": "CVE-2021-1234",
                        "severity": "MEDIUM",
                        "fix_version": "0.13.0"
                    }
                ],
                "total_packages": 45,
                "vulnerable_packages_count": 1
            }
        ))
        
        # Scan dependencies
        result = await security_agent._scan_dependencies({
            "scan_type": "security_vulnerabilities",
            "check_licenses": True,
            "auto_fix": False
        })
        
        # Verify dependency scan
        assert result["vulnerable_packages_count"] == 1
        assert result["vulnerable_packages"][0]["severity"] == "MEDIUM"
        
    @pytest.mark.asyncio
    async def test_runtime_security(self, security_agent):
        """Test runtime security implementation."""
        # Mock runtime security setup
        security_agent._implement_runtime_security = AsyncMock(return_value={
            "status": "completed",
            "security_features": ["root_detection", "debug_detection", "tamper_detection"],
            "security_files": ["runtime_security.dart", "app_integrity.dart"]
        })
        
        # Implement runtime security
        result = await security_agent._setup_runtime_security({
            "anti_tampering": True,
            "root_detection": True,
            "debug_detection": True,
            "certificate_validation": True
        })
        
        # Verify runtime security
        assert result["status"] == "completed"
        security_agent._implement_runtime_security.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_security_logging(self, security_agent):
        """Test security logging implementation."""
        # Mock security logging setup
        security_agent._setup_security_logging = AsyncMock(return_value={
            "status": "completed",
            "logging_features": ["auth_events", "security_violations", "access_logs"],
            "log_files": ["security_logger.dart", "audit_trail.dart"]
        })
        
        # Setup security logging
        result = await security_agent._implement_security_logging({
            "log_auth_events": True,
            "log_security_violations": True,
            "log_data_access": True,
            "secure_log_storage": True
        })
        
        # Verify security logging
        assert result["status"] == "completed"
        security_agent._setup_security_logging.assert_called_once()
        
    def test_security_risk_assessment(self, security_agent):
        """Test security risk assessment."""
        # Mock risk factors
        risk_factors = {
            "authentication_strength": 85,
            "data_encryption": 90,
            "network_security": 80,
            "code_security": 75,
            "dependency_security": 70,
            "runtime_protection": 65
        }
        
        # Calculate risk score
        risk_score = security_agent._calculate_security_risk(risk_factors)
        
        # Verify risk calculation
        assert 0 <= risk_score <= 100
        assert risk_score > 70  # Should be relatively secure
        
    @pytest.mark.asyncio
    async def test_security_compliance_check(self, security_agent):
        """Test security compliance checking."""
        # Mock compliance check
        security_agent._check_compliance = AsyncMock(return_value={
            "OWASP": {
                "compliant": True,
                "score": 88,
                "missing_controls": ["A10:2021 - Server-Side Request Forgery"]
            },
            "GDPR": {
                "compliant": False,
                "score": 75,
                "missing_controls": ["Data minimization", "Privacy by design"]
            }
        })
        
        # Check compliance
        result = await security_agent._verify_compliance({
            "standards": ["OWASP", "GDPR"],
            "generate_report": True
        })
        
        # Verify compliance check
        assert result["OWASP"]["compliant"] == True
        assert result["GDPR"]["compliant"] == False
        security_agent._check_compliance.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_security_testing_integration(self, security_agent):
        """Test security testing integration."""
        # Mock security test generation
        security_agent._generate_security_tests = AsyncMock(return_value={
            "status": "completed",
            "test_files": [
                "test/security/auth_security_test.dart",
                "test/security/data_encryption_test.dart",
                "test/security/network_security_test.dart"
            ],
            "test_scenarios": ["sql_injection", "xss", "csrf", "auth_bypass"]
        })
        
        # Generate security tests
        result = await security_agent._create_security_tests({
            "test_types": ["authentication", "authorization", "data_validation"],
            "attack_scenarios": ["injection", "broken_auth", "sensitive_data_exposure"]
        })
        
        # Verify security test generation
        assert result["status"] == "completed"
        assert len(result["test_files"]) == 3
        security_agent._generate_security_tests.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_incident_response(self, security_agent):
        """Test security incident response."""
        # Mock incident handling
        security_agent._handle_security_incident = AsyncMock(return_value={
            "status": "handled",
            "incident_id": "SEC-2024-001",
            "severity": "HIGH",
            "actions_taken": ["disabled_affected_feature", "notified_users", "patched_vulnerability"]
        })
        
        # Handle security incident
        result = await security_agent._respond_to_incident({
            "incident_type": "data_breach",
            "affected_components": ["user_service", "auth_service"],
            "severity": "HIGH"
        })
        
        # Verify incident response
        assert result["status"] == "handled"
        assert result["severity"] == "HIGH"
        security_agent._handle_security_incident.assert_called_once()
