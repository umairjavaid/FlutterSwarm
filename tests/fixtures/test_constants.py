"""
Test constants and shared data for FlutterSwarm tests.
"""

from datetime import datetime
from typing import Dict, List, Any

# Test project data
SAMPLE_PROJECT_DATA = {
    "simple_todo": {
        "name": "TodoApp",
        "description": "A simple todo application",
        "requirements": [
            "User authentication",
            "Todo CRUD operations",
            "Data persistence",
            "Search functionality"
        ],
        "features": ["auth", "crud", "persistence", "search"],
        "platforms": ["android", "ios"]
    },
    "complex_ecommerce": {
        "name": "ECommerceApp",
        "description": "A comprehensive e-commerce application",
        "requirements": [
            "User authentication and profiles",
            "Product catalog and search",
            "Shopping cart and checkout",
            "Payment processing",
            "Order management",
            "Push notifications",
            "Real-time inventory updates",
            "Offline support",
            "Multi-language support",
            "Analytics integration"
        ],
        "features": [
            "auth", "catalog", "cart", "payment", "orders",
            "notifications", "realtime", "offline", "i18n", "analytics"
        ],
        "platforms": ["android", "ios", "web"]
    },
    "music_streaming": {
        "name": "MusicStreamPro",
        "description": "A comprehensive music streaming application",
        "requirements": [
            "Music streaming from online sources",
            "Local music library management",
            "Playlist creation and management",
            "Offline music downloads",
            "Audio controls with equalizer",
            "Social features",
            "Music discovery",
            "Background playback"
        ],
        "features": [
            "streaming", "playlists", "offline", "equalizer",
            "social", "discovery", "background_playback"
        ],
        "platforms": ["android", "ios", "web", "desktop"]
    }
}

# Test agent capabilities
AGENT_CAPABILITIES = {
    "orchestrator": [
        "workflow_management", "task_delegation", "coordination",
        "progress_monitoring", "decision_making"
    ],
    "architecture": [
        "system_design", "structure_validation", "pattern_recommendation",
        "dependency_analysis", "scalability_planning"
    ],
    "implementation": [
        "code_generation", "flutter_development", "dart_programming",
        "widget_creation", "state_management", "api_integration"
    ],
    "testing": [
        "unit_testing", "widget_testing", "integration_testing",
        "test_automation", "coverage_analysis", "performance_testing"
    ],
    "security": [
        "vulnerability_scanning", "secure_coding", "encryption",
        "authentication", "authorization", "security_analysis"
    ],
    "devops": [
        "ci_cd_setup", "deployment", "build_automation",
        "container_management", "monitoring", "infrastructure"
    ],
    "documentation": [
        "api_documentation", "code_documentation", "user_guides",
        "technical_writing", "markdown_generation"
    ],
    "performance": [
        "performance_analysis", "optimization", "profiling",
        "memory_management", "cpu_optimization", "monitoring"
    ],
    "quality_assurance": [
        "code_review", "quality_metrics", "best_practices",
        "compliance_checking", "issue_detection"
    ]
}

# Test tool configurations
TOOL_TEST_CONFIG = {
    "terminal": {
        "timeout": 30,
        "commands": ["echo test", "ls", "pwd"],
        "error_commands": ["nonexistent_command", "exit 1"]
    },
    "file": {
        "test_files": {
            "dart_code": "test_file.dart",
            "json_config": "test_config.json",
            "yaml_config": "test_config.yaml"
        },
        "test_content": {
            "dart_code": """
import 'package:flutter/material.dart';

class TestWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      child: Text('Test Widget'),
    );
  }
}
""",
            "json_config": '{"test": true, "value": 42}',
            "yaml_config": "test: true\nvalue: 42"
        }
    },
    "flutter": {
        "commands": ["doctor", "version", "analyze", "test"],
        "build_platforms": ["android", "ios", "web"],
        "test_packages": ["test", "flutter_test", "mockito"]
    },
    "git": {
        "operations": ["init", "add", "commit", "status"],
        "test_repo_url": "https://github.com/test/test-repo.git",
        "test_branch": "test-branch"
    },
    "analysis": {
        "scan_types": ["security", "quality", "performance"],
        "metrics": ["complexity", "coverage", "maintainability"]
    }
}

# Test error scenarios
ERROR_SCENARIOS = {
    "api_key_missing": {
        "error_type": "AuthenticationError",
        "message": "API key not provided"
    },
    "invalid_project_id": {
        "error_type": "ValueError",
        "message": "Project not found"
    },
    "agent_timeout": {
        "error_type": "TimeoutError",
        "message": "Agent operation timed out"
    },
    "tool_execution_failed": {
        "error_type": "ToolExecutionError",
        "message": "Tool execution failed"
    },
    "invalid_configuration": {
        "error_type": "ConfigurationError",
        "message": "Invalid configuration provided"
    }
}

# Test message templates
MESSAGE_TEMPLATES = {
    "task_request": {
        "message_type": "TASK_REQUEST",
        "priority": 5,
        "content": {
            "task_description": "test_task",
            "task_data": {"param1": "value1"}
        }
    },
    "collaboration_request": {
        "message_type": "COLLABORATION_REQUEST",
        "priority": 3,
        "content": {
            "collaboration_type": "code_review",
            "data": {"file_path": "lib/main.dart"}
        }
    },
    "state_sync": {
        "message_type": "STATE_SYNC",
        "priority": 1,
        "content": {
            "sync_type": "project_update",
            "data": {"progress": 0.5}
        }
    }
}

# Test build result templates
BUILD_RESULT_TEMPLATES = {
    "success": {
        "status": "completed",
        "files_created": 15,
        "architecture_decisions": 3,
        "test_results": {
            "unit": {"status": "passed", "count": 20},
            "widget": {"status": "passed", "count": 8},
            "integration": {"status": "passed", "count": 3}
        },
        "security_findings": [],
        "performance_metrics": {
            "build_time": 45.2,
            "app_size": "12.5MB",
            "startup_time": "1.2s"
        },
        "documentation": ["README.md", "API.md"],
        "deployment_config": {"platform": "firebase"}
    },
    "with_issues": {
        "status": "completed_with_issues",
        "files_created": 12,
        "architecture_decisions": 2,
        "test_results": {
            "unit": {"status": "failed", "count": 18, "failures": 2},
            "widget": {"status": "passed", "count": 6}
        },
        "security_findings": [
            {
                "severity": "medium",
                "type": "insecure_storage",
                "description": "Sensitive data stored without encryption"
            }
        ],
        "performance_metrics": {
            "build_time": 62.1,
            "app_size": "18.7MB",
            "startup_time": "2.1s"
        },
        "documentation": ["README.md"],
        "deployment_config": {}
    },
    "failed": {
        "status": "failed",
        "files_created": 5,
        "architecture_decisions": 1,
        "test_results": {},
        "security_findings": [],
        "performance_metrics": {},
        "documentation": [],
        "deployment_config": {},
        "error": "Build process failed due to dependency conflicts"
    }
}

# Test configuration data
TEST_CONFIG_DATA = {
    "communication": {
        "messaging": {
            "queue_size": 100,
            "message_ttl": 3600,
            "max_recent_messages": 10
        },
        "collaboration": {
            "max_concurrent_collaborations": 5,
            "timeout": 300
        }
    },
    "agents": {
        "orchestrator": {
            "capabilities": AGENT_CAPABILITIES["orchestrator"],
            "timeout": 60,
            "max_retries": 3
        },
        "implementation": {
            "capabilities": AGENT_CAPABILITIES["implementation"],
            "timeout": 120,
            "max_retries": 2
        }
    },
    "tools": {
        "timeout_default": 60,
        "flutter": {"timeout": 300},
        "terminal": {"timeout": 120},
        "analysis": {"security_scan_depth": "comprehensive"}
    },
    "cli": {
        "console_width": 80,
        "progress_update_interval": 1.0,
        "table_headers": {
            "projects": ["ID", "Name", "Phase", "Progress"]
        }
    },
    "display": {
        "project_id_length": 8,
        "progress_format": "{:.1%}"
    },
    "messages": {
        "welcome": "🐝 Welcome to FlutterSwarm!",
        "project_creating": "📋 Creating new Flutter project...",
        "building": "🔨 Building Flutter project...",
        "build_complete": "✅ Build completed!",
        "no_projects": "📭 No projects found"
    }
}

# Test timing constants
TIMING_CONSTANTS = {
    "quick_operation": 0.1,
    "medium_operation": 1.0,
    "slow_operation": 5.0,
    "timeout_operation": 30.0
}

# Test file paths
TEST_FILE_PATHS = {
    "dart_main": "lib/main.dart",
    "dart_model": "lib/models/user.dart",
    "dart_service": "lib/services/api_service.dart",
    "test_unit": "test/unit/user_test.dart",
    "test_widget": "test/widget/main_widget_test.dart",
    "pubspec": "pubspec.yaml",
    "readme": "README.md"
}

# Architecture-related constants
SAMPLE_ARCHITECTURE_PLAN = {
    "pattern": "Clean Architecture",
    "state_management": "BLoC",
    "layers": {
        "presentation": ["widgets", "pages", "blocs"],
        "domain": ["entities", "use_cases", "repositories"],
        "data": ["datasources", "models", "repositories_impl"]
    },
    "design_principles": ["SOLID", "DRY", "KISS"],
    "technology_stack": {
        "state_management": "flutter_bloc",
        "dependency_injection": "get_it",
        "routing": "go_router",
        "networking": "dio"
    }
}

# CI/CD and DevOps constants
SAMPLE_CI_CD_CONFIG = {
    "ci_system": "github_actions",
    "platforms": ["android", "ios", "web"],
    "workflows": {
        "build_and_test": {
            "triggers": ["push", "pull_request"],
            "steps": ["checkout", "setup", "test", "build"]
        },
        "deploy": {
            "triggers": ["release"],
            "environments": ["staging", "production"]
        }
    },
    "deployment_targets": ["play_store", "app_store", "firebase_hosting"],
    "monitoring": ["firebase_crashlytics", "sentry"]
}

# Documentation configuration
SAMPLE_DOCUMENTATION_CONFIG = {
    "doc_types": ["readme", "api_docs", "user_guide", "architecture"],
    "formats": ["markdown", "html", "pdf"],
    "sections": {
        "readme": ["introduction", "installation", "usage", "contributing"],
        "api_docs": ["endpoints", "models", "authentication", "examples"],
        "user_guide": ["getting_started", "features", "troubleshooting"],
        "architecture": ["overview", "patterns", "layers", "decisions"]
    },
    "templates": {
        "readme_template": "# {project_name}\n\n{description}\n\n## Features\n{features}",
        "api_endpoint_template": "### {method} {path}\n\n{description}\n\n**Parameters:**\n{parameters}"
    }
}

# Performance metrics and benchmarks
SAMPLE_PERFORMANCE_METRICS = {
    "frame_rate": {
        "current": 45,
        "target": 60,
        "threshold": 30
    },
    "memory_usage": {
        "current": 150,  # MB
        "target": 100,
        "threshold": 200
    },
    "startup_time": {
        "current": 2.8,  # seconds
        "target": 2.0,
        "threshold": 3.0
    },
    "app_size": {
        "current": 45,  # MB
        "target": 30,
        "optimization_potential": 15
    },
    "network_latency": {
        "current": 800,  # ms
        "target": 500,
        "threshold": 1000
    },
    "battery_usage": {
        "current": "high",
        "target": "moderate",
        "optimization_areas": ["background_sync", "location_tracking"]
    }
}

# Validation issues for QA testing
SAMPLE_VALIDATION_ISSUES = [
    {
        "type": "syntax_error",
        "severity": "high",
        "file": "lib/main.dart",
        "line": 42,
        "message": "Missing semicolon",
        "fix_suggestion": "Add semicolon at end of statement"
    },
    {
        "type": "unused_import",
        "severity": "low",
        "file": "lib/utils.dart",
        "line": 1,
        "message": "Unused import 'dart:async'",
        "fix_suggestion": "Remove unused import"
    },
    {
        "type": "missing_null_safety",
        "severity": "medium",
        "file": "lib/models/user.dart",
        "line": 15,
        "message": "Variable should be nullable",
        "fix_suggestion": "Add '?' to make variable nullable"
    },
    {
        "type": "performance_issue",
        "severity": "medium",
        "file": "lib/widgets/expensive_widget.dart",
        "line": 25,
        "message": "Widget rebuilds unnecessarily",
        "fix_suggestion": "Use const constructor or memoization"
    }
]

# Code analysis results
SAMPLE_CODE_ANALYSIS_RESULT = {
    "total_files": 45,
    "total_lines": 12500,
    "issues_found": 15,
    "issues_by_severity": {
        "critical": 0,
        "high": 3,
        "medium": 7,
        "low": 5
    },
    "metrics": {
        "cyclomatic_complexity": 3.2,
        "maintainability_index": 75,
        "code_coverage": 82,
        "technical_debt": "2.5 hours"
    },
    "recommendations": [
        "Add unit tests for uncovered code",
        "Refactor complex methods",
        "Fix high-severity issues first"
    ]
}

# Test project data
SAMPLE_PROJECT_CONFIG = {
    "name": "SampleProject",
    "description": "A sample project for testing",
    "requirements": ["auth", "crud", "persistence"],
    "features": ["auth", "crud", "persistence"],
    "platforms": ["android", "ios"]
}

SAMPLE_AGENT_CONFIG = {
    "agent_id": "test_agent",
    "capabilities": ["test_capability"],
    "timeout": 60,
    "max_retries": 2
}
