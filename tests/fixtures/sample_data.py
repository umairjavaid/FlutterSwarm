"""
Test fixtures and sample data for FlutterSwarm tests.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

# Sample project data for testing
SAMPLE_PROJECTS = {
    "simple_todo": {
        "name": "SimpleTodo",
        "description": "A simple todo application",
        "requirements": [
            "Add new todos",
            "Mark todos as complete",
            "Delete todos",
            "Basic local storage"
        ],
        "features": ["crud", "storage"],
        "expected_files": [
            "lib/main.dart",
            "lib/models/todo.dart",
            "lib/services/todo_service.dart",
            "lib/screens/todo_list.dart"
        ]
    },
    "ecommerce_app": {
        "name": "ShopMaster",
        "description": "A comprehensive e-commerce application",
        "requirements": [
            "User authentication",
            "Product catalog",
            "Shopping cart",
            "Payment processing",
            "Order management",
            "User reviews",
            "Push notifications",
            "Offline support"
        ],
        "features": ["auth", "catalog", "cart", "payments", "orders", "reviews", "notifications", "offline"],
        "expected_files": [
            "lib/main.dart",
            "lib/models/user.dart",
            "lib/models/product.dart",
            "lib/models/order.dart",
            "lib/services/auth_service.dart",
            "lib/services/payment_service.dart",
            "lib/screens/product_list.dart",
            "lib/screens/cart_screen.dart"
        ]
    },
    "social_app": {
        "name": "SocialConnect",
        "description": "A social networking application",
        "requirements": [
            "User profiles",
            "Post creation and sharing",
            "Real-time messaging",
            "Friend connections",
            "Photo/video sharing",
            "Privacy controls",
            "Content moderation",
            "Analytics tracking"
        ],
        "features": ["profiles", "posts", "messaging", "media", "privacy", "moderation", "analytics"],
        "expected_files": [
            "lib/main.dart",
            "lib/models/user.dart",
            "lib/models/post.dart",
            "lib/models/message.dart",
            "lib/services/social_service.dart",
            "lib/services/messaging_service.dart",
            "lib/screens/profile_screen.dart",
            "lib/screens/feed_screen.dart"
        ]
    }
}

# Sample agent configurations
SAMPLE_AGENT_CONFIGS = {
    "orchestrator": {
        "capabilities": ["coordination", "planning", "task_delegation"],
        "timeout": 60,
        "max_retries": 3,
        "priority": 10
    },
    "architecture": {
        "capabilities": ["system_design", "pattern_selection", "structure_planning"],
        "timeout": 90,
        "max_retries": 2,
        "priority": 9
    },
    "implementation": {
        "capabilities": ["coding", "flutter_development", "dart_programming"],
        "timeout": 180,
        "max_retries": 3,
        "priority": 8
    },
    "testing": {
        "capabilities": ["unit_testing", "widget_testing", "integration_testing"],
        "timeout": 120,
        "max_retries": 2,
        "priority": 7
    },
    "security": {
        "capabilities": ["vulnerability_scanning", "secure_coding", "authentication"],
        "timeout": 90,
        "max_retries": 2,
        "priority": 8
    },
    "devops": {
        "capabilities": ["deployment", "ci_cd", "infrastructure"],
        "timeout": 150,
        "max_retries": 3,
        "priority": 6
    },
    "documentation": {
        "capabilities": ["technical_writing", "api_documentation", "user_guides"],
        "timeout": 60,
        "max_retries": 2,
        "priority": 5
    },
    "performance": {
        "capabilities": ["optimization", "profiling", "monitoring"],
        "timeout": 120,
        "max_retries": 2,
        "priority": 7
    },
    "quality_assurance": {
        "capabilities": ["code_review", "quality_metrics", "standards_compliance"],
        "timeout": 90,
        "max_retries": 2,
        "priority": 6
    }
}

# Sample tool responses for testing
SAMPLE_TOOL_RESPONSES = {
    "terminal": {
        "flutter_version": {
            "status": "SUCCESS",
            "output": "Flutter 3.16.0 • channel stable • https://github.com/flutter/flutter.git",
            "data": {"version": "3.16.0", "channel": "stable"}
        },
        "dart_version": {
            "status": "SUCCESS", 
            "output": "Dart SDK version: 3.2.0",
            "data": {"version": "3.2.0"}
        },
        "git_status": {
            "status": "SUCCESS",
            "output": "On branch main\nnothing to commit, working tree clean",
            "data": {"branch": "main", "clean": True}
        }
    },
    "file": {
        "read_pubspec": {
            "status": "SUCCESS",
            "output": "name: test_app\nversion: 1.0.0\ndependencies:\n  flutter:\n    sdk: flutter",
            "data": {"file_type": "yaml", "lines": 4}
        },
        "write_success": {
            "status": "SUCCESS",
            "output": "File written successfully",
            "data": {"bytes_written": 1024}
        }
    },
    "flutter": {
        "create_project": {
            "status": "SUCCESS",
            "output": "Creating project test_app...\nProject created successfully",
            "data": {"project_name": "test_app", "template": "app"}
        },
        "pub_get": {
            "status": "SUCCESS",
            "output": "Running pub get...\nGot dependencies!",
            "data": {"packages_resolved": 45}
        },
        "test_run": {
            "status": "SUCCESS",
            "output": "Running tests...\nAll tests passed! (15 tests)",
            "data": {"tests_run": 15, "passed": 15, "failed": 0}
        }
    },
    "git": {
        "init": {
            "status": "SUCCESS",
            "output": "Initialized empty Git repository in /path/to/project/.git/",
            "data": {"repository_path": "/path/to/project/.git/"}
        },
        "add": {
            "status": "SUCCESS",
            "output": "Files added to staging area",
            "data": {"files_added": 5}
        },
        "commit": {
            "status": "SUCCESS",
            "output": "[main abc1234] Initial commit\n 5 files changed, 150 insertions(+)",
            "data": {"commit_hash": "abc1234", "files_changed": 5}
        }
    }
}

# Sample build results
SAMPLE_BUILD_RESULTS = {
    "successful_build": {
        "status": "completed",
        "files_created": 25,
        "architecture_decisions": 5,
        "test_results": {
            "unit": {"status": "passed", "tests": 20, "coverage": "85%"},
            "widget": {"status": "passed", "tests": 10, "coverage": "90%"},
            "integration": {"status": "passed", "tests": 5, "coverage": "75%"}
        },
        "security_findings": [
            {"type": "info", "message": "No critical vulnerabilities found"},
            {"type": "warning", "message": "Consider adding input validation"}
        ],
        "performance_metrics": {
            "build_time": "2m 30s",
            "app_size": "12.5 MB",
            "startup_time": "1.2s"
        },
        "documentation": [
            "README.md",
            "API_DOCS.md", 
            "ARCHITECTURE.md"
        ],
        "deployment_config": {
            "status": "configured",
            "platforms": ["android", "ios", "web"],
            "ci_system": "github_actions"
        }
    },
    "build_with_issues": {
        "status": "completed_with_warnings",
        "files_created": 18,
        "architecture_decisions": 3,
        "test_results": {
            "unit": {"status": "passed", "tests": 15, "coverage": "70%"},
            "widget": {"status": "failed", "tests": 8, "coverage": "60%"},
            "integration": {"status": "skipped", "tests": 0, "coverage": "0%"}
        },
        "security_findings": [
            {"type": "warning", "message": "Weak password validation"},
            {"type": "error", "message": "SQL injection vulnerability in search"}
        ],
        "performance_metrics": {
            "build_time": "3m 45s",
            "app_size": "18.2 MB",
            "startup_time": "2.8s"
        },
        "documentation": ["README.md"],
        "deployment_config": {
            "status": "incomplete",
            "issues": ["Missing environment variables"]
        }
    }
}

# Sample error scenarios
SAMPLE_ERROR_SCENARIOS = {
    "dependency_conflict": {
        "type": "dependency",
        "severity": "high",
        "description": "Conflicting package versions detected",
        "affected_files": ["pubspec.yaml"],
        "error_details": {
            "package1": "http ^0.13.0",
            "package2": "dio ^4.0.0",
            "conflict": "Both packages have conflicting HTTP implementations"
        },
        "fix_suggestions": [
            "Use dependency overrides in pubspec.yaml",
            "Choose one HTTP client package",
            "Update packages to compatible versions"
        ]
    },
    "build_failure": {
        "type": "build",
        "severity": "critical",
        "description": "Flutter build failed due to compilation errors",
        "affected_files": ["lib/main.dart", "lib/models/user.dart"],
        "error_details": {
            "error_count": 3,
            "warning_count": 5,
            "main_error": "Undefined class 'UserModel'"
        },
        "fix_suggestions": [
            "Import missing dependencies",
            "Fix undefined class references",
            "Resolve type mismatches"
        ]
    },
    "test_failures": {
        "type": "testing",
        "severity": "medium",
        "description": "Multiple test failures detected",
        "affected_files": ["test/user_test.dart", "test/auth_test.dart"],
        "error_details": {
            "failed_tests": 5,
            "total_tests": 20,
            "main_issues": ["Null safety violations", "Mock setup failures"]
        },
        "fix_suggestions": [
            "Update tests for null safety",
            "Fix mock object configurations",
            "Add missing test dependencies"
        ]
    }
}

# Sample agent communication messages
SAMPLE_MESSAGES = {
    "task_assignment": {
        "type": "TASK_REQUEST",
        "from_agent": "orchestrator",
        "to_agent": "implementation",
        "content": {
            "task_type": "implement_feature",
            "feature_name": "user_authentication",
            "requirements": ["login", "registration", "password_reset"],
            "deadline": "2024-01-15",
            "priority": "high"
        }
    },
    "collaboration_request": {
        "type": "COLLABORATION_REQUEST",
        "from_agent": "implementation",
        "to_agent": "testing",
        "content": {
            "request_type": "test_feature",
            "feature": "user_authentication",
            "files_created": ["lib/auth/login.dart", "lib/auth/register.dart"],
            "test_types": ["unit", "widget", "integration"]
        }
    },
    "status_update": {
        "type": "STATUS_UPDATE",
        "from_agent": "testing",
        "to_agent": None,  # Broadcast
        "content": {
            "status": "completed",
            "task": "authentication_tests",
            "results": {
                "tests_written": 15,
                "tests_passed": 13,
                "coverage": "87%"
            }
        }
    },
    "error_report": {
        "type": "ERROR_REPORT",
        "from_agent": "security",
        "to_agent": "orchestrator",
        "content": {
            "error_type": "security_vulnerability",
            "severity": "high",
            "description": "Unencrypted data transmission detected",
            "affected_components": ["authentication", "user_data"],
            "recommended_actions": ["Implement HTTPS", "Add data encryption"]
        }
    }
}

# Performance benchmarks for testing
PERFORMANCE_BENCHMARKS = {
    "small_project": {
        "max_build_time": 60,  # seconds
        "max_file_count": 15,
        "max_memory_usage": 256,  # MB
        "expected_test_coverage": 80  # percent
    },
    "medium_project": {
        "max_build_time": 180,
        "max_file_count": 50,
        "max_memory_usage": 512,
        "expected_test_coverage": 75
    },
    "large_project": {
        "max_build_time": 300,
        "max_file_count": 100,
        "max_memory_usage": 1024,
        "expected_test_coverage": 70
    }
}

# Test data utilities
def get_sample_project(project_type: str) -> Dict[str, Any]:
    """Get sample project data by type."""
    return SAMPLE_PROJECTS.get(project_type, SAMPLE_PROJECTS["simple_todo"])

def get_agent_config(agent_id: str) -> Dict[str, Any]:
    """Get sample agent configuration."""
    return SAMPLE_AGENT_CONFIGS.get(agent_id, {})

def get_tool_response(tool_name: str, operation: str) -> Dict[str, Any]:
    """Get sample tool response."""
    return SAMPLE_TOOL_RESPONSES.get(tool_name, {}).get(operation, {})

def get_build_result(result_type: str = "successful_build") -> Dict[str, Any]:
    """Get sample build result."""
    return SAMPLE_BUILD_RESULTS.get(result_type, SAMPLE_BUILD_RESULTS["successful_build"])

def get_error_scenario(scenario_type: str) -> Dict[str, Any]:
    """Get sample error scenario."""
    return SAMPLE_ERROR_SCENARIOS.get(scenario_type, {})

def get_sample_message(message_type: str) -> Dict[str, Any]:
    """Get sample agent message."""
    return SAMPLE_MESSAGES.get(message_type, {})

def get_performance_benchmark(project_size: str) -> Dict[str, Any]:
    """Get performance benchmark for project size."""
    return PERFORMANCE_BENCHMARKS.get(project_size, PERFORMANCE_BENCHMARKS["small_project"])
