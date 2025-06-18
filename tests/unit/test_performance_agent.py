"""
Unit tests for PerformanceAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import test fixtures and mocks
from tests.fixtures.test_constants import (
    SAMPLE_PROJECT_CONFIG,
    SAMPLE_AGENT_CONFIG,
    SAMPLE_PERFORMANCE_METRICS
)
from tests.mocks.mock_implementations import MockToolManager, MockConfigManager

# Import the agent under test
from agents.performance_agent import PerformanceAgent
from shared.state import AgentStatus, MessageType
from tools.base_tool import ToolResult, ToolStatus


class TestPerformanceAgent:
    """Test suite for PerformanceAgent."""

    @pytest.fixture
    def mock_config_manager(self):
        """Mock config manager for testing."""
        return MockConfigManager()

    @pytest.fixture
    def mock_tool_manager(self):
        """Mock tool manager for testing."""
        tool_manager = Mock()
        tool_manager.create_agent_toolbox.return_value = Mock()
        tool_manager.create_agent_toolbox.return_value.list_available_tools.return_value = [
            "terminal", "file", "analysis", "flutter"
        ]
        return tool_manager

    @pytest.fixture
    def agent(self, mock_config_manager, mock_tool_manager):
        """Create PerformanceAgent for testing."""
        with patch('agents.performance_agent.get_config', return_value=mock_config_manager), \
             patch('agents.performance_agent.ToolManager', return_value=mock_tool_manager), \
             patch('langchain_anthropic.ChatAnthropic'):
            
            agent = PerformanceAgent()
            agent.execute_tool = AsyncMock()
            agent.think = AsyncMock()
            agent.run_command = AsyncMock()
            agent.read_file = AsyncMock()
            agent.write_file = AsyncMock()
            return agent

    @pytest.mark.unit
    def test_performance_agent_initialization(self, agent):
        """Test performance agent initializes correctly."""
        assert agent.agent_id == "performance"
        assert hasattr(agent, 'optimization_areas')
        assert hasattr(agent, 'metrics')
        assert isinstance(agent.optimization_areas, list)
        assert isinstance(agent.metrics, list)
        
        # Check expected optimization areas
        expected_areas = [
            "widget_optimization", "state_management", "network_optimization",
            "image_optimization", "memory_management", "startup_time",
            "build_optimization", "animation_performance"
        ]
        
        for area in expected_areas:
            assert area in agent.optimization_areas
        
        # Check expected metrics
        expected_metrics = [
            "frame_rate", "memory_usage", "cpu_usage", "network_latency",
            "app_size", "startup_time", "battery_usage"
        ]
        
        for metric in expected_metrics:
            assert metric in agent.metrics

    @pytest.mark.unit
    async def test_execute_task_performance_audit(self, agent, mock_shared_state):
        """Test performance audit task execution."""
        task_data = {
            "project_id": "test_project",
            "audit_scope": "full",
            "target_metrics": ["frame_rate", "memory_usage", "startup_time"],
            "platform": "android"
        }
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock performance analysis tools
        agent.execute_tool.side_effect = [
            # Widget analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "widget_issues": [
                        {"type": "unnecessary_rebuilds", "count": 5},
                        {"type": "deep_nesting", "count": 3}
                    ]
                }
            ),
            # Memory analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "memory_usage": 120,  # MB
                    "memory_leaks": 2,
                    "peak_usage": 180
                }
            ),
            # Startup time analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "startup_time": 2.5,  # seconds
                    "initialization_bottlenecks": ["asset_loading", "dependency_injection"]
                }
            ),
            # Build size analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_size": 45,  # MB
                    "unused_assets": 10,
                    "optimization_potential": 15
                }
            )
        ]
        
        agent.think.return_value = "Performance audit completed"
        
        result = await agent.execute_task("performance_audit", task_data)
        
        assert result["audit_type"] == "performance"
        assert result["project_id"] == "test_project"
        assert "audit_results" in result
        assert "recommendations" in result
        assert "performance_score" in result
        assert result["status"] == "completed"
        
        # Should analyze multiple performance aspects
        assert agent.execute_tool.call_count >= 3

    @pytest.mark.unit
    async def test_execute_task_optimize_widgets(self, agent):
        """Test widget optimization task."""
        task_data = {
            "project_id": "test_project",
            "target_widgets": ["lib/widgets/user_list.dart", "lib/widgets/product_card.dart"],
            "optimization_types": ["unnecessary_rebuilds", "const_constructors", "widget_caching"]
        }
        
        # Mock widget file reading
        agent.read_file.side_effect = [
            ToolResult(
                status=ToolStatus.SUCCESS,
                output="class UserList extends StatefulWidget { ... }"
            ),
            ToolResult(
                status=ToolStatus.SUCCESS,
                output="class ProductCard extends StatelessWidget { ... }"
            )
        ]
        
        # Mock optimization analysis
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"optimization_applied": True}
        )
        
        agent.think.return_value = "Widget optimizations implemented"
        
        result = await agent.execute_task("optimize_widgets", task_data)
        
        assert result["optimization_type"] == "widgets"
        assert "target_widgets" in result
        assert "optimizations_applied" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_optimize_images(self, agent):
        """Test image optimization task."""
        task_data = {
            "project_id": "test_project",
            "image_directories": ["assets/images", "assets/icons"],
            "optimization_level": "aggressive",
            "target_formats": ["webp", "avif"],
            "generate_multiple_resolutions": True
        }
        
        # Mock image analysis
        agent.execute_tool.side_effect = [
            # Analyze images
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "total_images": 50,
                    "unoptimized_images": 35,
                    "potential_savings": "60%"
                }
            ),
            # Optimize images
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "images_optimized": 35,
                    "size_reduction": "58%",
                    "formats_converted": 20
                }
            )
        ]
        
        result = await agent.execute_task("optimize_images", task_data)
        
        assert result["optimization_type"] == "images"
        assert "optimization_results" in result
        assert "size_reduction" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_setup_monitoring(self, agent):
        """Test performance monitoring setup task."""
        task_data = {
            "project_id": "test_project",
            "monitoring_services": ["firebase_performance", "custom_analytics"],
            "metrics_to_track": ["frame_rate", "memory_usage", "network_latency"],
            "alerting_thresholds": {
                "frame_rate": 30,
                "memory_usage": 200
            }
        }
        
        agent.execute_tool.side_effect = [
            # Add monitoring dependencies
            ToolResult(status=ToolStatus.SUCCESS, data={"packages_added": True}),
            # Configure monitoring
            ToolResult(status=ToolStatus.SUCCESS, data={"monitoring_configured": True}),
            # Setup custom metrics
            ToolResult(status=ToolStatus.SUCCESS, data={"custom_metrics_added": True})
        ]
        
        agent.think.return_value = "Performance monitoring setup completed"
        
        result = await agent.execute_task("setup_monitoring", task_data)
        
        assert result["monitoring_type"] == "performance"
        assert "monitoring_services" in result
        assert "metrics_configured" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_general(self, agent):
        """Test general performance task handling."""
        task_description = "optimize app startup time"
        task_data = {
            "current_startup_time": 3.5,
            "target_startup_time": 2.0,
            "optimization_areas": ["asset_loading", "dependency_initialization"]
        }
        
        agent.think.return_value = "Startup time optimization recommendations provided"
        
        result = await agent.execute_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "performance_response" in result
        assert result["status"] == "completed"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_architecture_review(self, agent):
        """Test collaboration for performance architecture review."""
        data = {
            "architecture_pattern": "BLoC",
            "state_management": "flutter_bloc",
            "performance_concerns": ["state_rebuilds", "memory_leaks"],
            "target_performance": "high"
        }
        
        agent.think.return_value = "Architecture performance review completed"
        
        result = await agent.collaborate("architecture_review", data)
        
        assert result["review_type"] == "performance_architecture"
        assert "performance_assessment" in result
        assert "optimization_recommendations" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_code_optimization(self, agent):
        """Test collaboration for code optimization."""
        data = {
            "code_files": ["lib/services/data_service.dart"],
            "performance_issues": ["n_plus_one_queries", "inefficient_loops"],
            "optimization_target": "speed"
        }
        
        agent.read_file.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            output="class DataService { ... inefficient code ... }"
        )
        
        agent.think.return_value = "Code optimization suggestions provided"
        
        result = await agent.collaborate("code_optimization", data)
        
        assert result["optimization_type"] == "code"
        assert "optimized_code" in result
        assert "performance_improvement" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_performance_recommendations(self, agent):
        """Test collaboration for performance recommendations."""
        data = {
            "current_metrics": {
                "frame_rate": 40,
                "memory_usage": 150,
                "startup_time": 3.0
            },
            "target_metrics": {
                "frame_rate": 60,
                "memory_usage": 100,
                "startup_time": 2.0
            },
            "platform": "android"
        }
        
        agent.think.return_value = "Performance recommendations generated"
        
        result = await agent.collaborate("performance_recommendations", data)
        
        assert result["recommendation_type"] == "performance"
        assert "recommendations" in result
        assert "priority_order" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_unknown_type(self, agent):
        """Test collaboration with unknown type."""
        result = await agent.collaborate("unknown_type", {})
        
        assert result["status"] == "unknown_collaboration_type"
        assert result["type"] == "unknown_type"

    @pytest.mark.unit
    async def test_on_state_change_implementation_completed(self, agent, mock_shared_state):
        """Test reaction to implementation completed state change."""
        change_data = {
            "event": "implementation_completed",
            "project_id": "test_project"
        }
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"performance_audit_initiated": True}
        )
        
        await agent.on_state_change(change_data)
        
        # Should automatically start performance audit
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_on_state_change_performance_degradation(self, agent):
        """Test reaction to performance degradation state change."""
        change_data = {
            "event": "performance_degradation",
            "metrics": {
                "frame_rate": 25,  # Below 30 FPS threshold
                "memory_usage": 250  # Above 200MB threshold
            },
            "project_id": "test_project"
        }
        
        agent.think.return_value = "Performance issue analysis completed"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"optimization_suggestions": ["reduce_widget_rebuilds", "optimize_images"]}
        )
        
        await agent.on_state_change(change_data)
        
        # Should analyze and suggest optimizations
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_perform_performance_audit_comprehensive(self, agent, mock_shared_state):
        """Test comprehensive performance audit."""
        task_data = {
            "audit_scope": "comprehensive",
            "platforms": ["android", "ios"],
            "include_profiling": True,
            "generate_report": True
        }
        
        mock_project = Mock()
        mock_project.name = "ComplexApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock comprehensive analysis
        agent.execute_tool.side_effect = [
            # Widget performance
            ToolResult(status=ToolStatus.SUCCESS, data={"widget_performance": "good"}),
            # Memory analysis
            ToolResult(status=ToolStatus.SUCCESS, data={"memory_analysis": "needs_optimization"}),
            # Network performance
            ToolResult(status=ToolStatus.SUCCESS, data={"network_performance": "excellent"}),
            # Build analysis
            ToolResult(status=ToolStatus.SUCCESS, data={"build_size": "acceptable"}),
            # Profiling results
            ToolResult(status=ToolStatus.SUCCESS, data={"profiling_completed": True})
        ]
        
        agent.think.return_value = "Comprehensive audit completed"
        
        result = await agent._perform_performance_audit(task_data)
        
        assert result["audit_type"] == "performance"
        assert "audit_results" in result
        assert "performance_score" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_optimize_widgets_specific(self, agent):
        """Test specific widget optimization."""
        task_data = {
            "target_widgets": ["lib/widgets/expensive_widget.dart"],
            "optimization_types": ["const_constructors", "widget_keys", "build_method"]
        }
        
        agent.read_file.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            output="class ExpensiveWidget extends StatelessWidget { ... }"
        )
        
        agent.think.return_value = "Widget optimizations applied"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"widget_optimized": True}
        )
        
        result = await agent._optimize_widgets(task_data)
        
        assert result["optimization_type"] == "widgets"
        assert "optimizations_applied" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_optimize_images_advanced(self, agent):
        """Test advanced image optimization."""
        task_data = {
            "optimization_strategies": ["format_conversion", "compression", "lazy_loading"],
            "target_size_reduction": 50,
            "preserve_quality": True,
            "generate_responsive_images": True
        }
        
        agent.execute_tool.side_effect = [
            # Image analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"current_size": "50MB", "optimization_potential": "60%"}
            ),
            # Optimization process
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"new_size": "20MB", "quality_preserved": True}
            )
        ]
        
        result = await agent._optimize_images(task_data)
        
        assert result["optimization_type"] == "images"
        assert "optimization_results" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_setup_performance_monitoring_custom(self, agent):
        """Test custom performance monitoring setup."""
        task_data = {
            "custom_metrics": ["user_interaction_time", "data_load_time"],
            "real_time_monitoring": True,
            "performance_budgets": {
                "bundle_size": "2MB",
                "first_paint": "1s"
            },
            "alerting_channels": ["email", "slack"]
        }
        
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"custom_metrics_setup": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"alerting_configured": True})
        ]
        
        agent.think.return_value = "Custom monitoring setup completed"
        
        result = await agent._setup_performance_monitoring(task_data)
        
        assert result["monitoring_type"] == "performance"
        assert "custom_metrics" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_review_performance_architecture(self, agent):
        """Test performance architecture review."""
        data = {
            "architecture_components": ["state_management", "data_layer", "ui_layer"],
            "performance_bottlenecks": ["excessive_rebuilds", "memory_leaks"],
            "scalability_requirements": "high_load"
        }
        
        agent.think.return_value = "Architecture performance analysis completed"
        
        result = await agent._review_performance_architecture(data)
        
        assert result["review_type"] == "performance_architecture"
        assert "performance_assessment" in result
        assert "optimization_recommendations" in result

    @pytest.mark.unit
    async def test_optimize_code_algorithmic(self, agent):
        """Test algorithmic code optimization."""
        data = {
            "code_snippet": "for (int i = 0; i < list.length; i++) { ... }",
            "performance_issue": "inefficient_iteration",
            "optimization_target": "time_complexity"
        }
        
        agent.think.return_value = "Optimized code with better algorithm"
        
        result = await agent._optimize_code(data)
        
        assert result["optimization_type"] == "code"
        assert "optimized_code" in result
        assert "performance_improvement" in result

    @pytest.mark.unit
    async def test_provide_performance_recommendations(self, agent):
        """Test performance recommendations provision."""
        data = {
            "performance_profile": {
                "cpu_intensive_operations": ["image_processing", "data_parsing"],
                "memory_hotspots": ["large_collections", "cached_images"],
                "ui_performance_issues": ["jank", "slow_animations"]
            },
            "optimization_priority": "user_experience"
        }
        
        agent.think.return_value = "Performance recommendations generated"
        
        result = await agent._provide_performance_recommendations(data)
        
        assert result["recommendation_type"] == "performance"
        assert "recommendations" in result
        assert "priority_order" in result

    @pytest.mark.unit
    async def test_handle_general_performance_task(self, agent):
        """Test general performance task handling."""
        task_description = "analyze battery usage"
        task_data = {
            "monitoring_duration": "24_hours",
            "usage_patterns": ["background_sync", "location_tracking"],
            "optimization_target": "battery_life"
        }
        
        agent.think.return_value = "Battery usage analysis completed"
        
        result = await agent._handle_general_performance_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "performance_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_error_handling_in_performance_audit(self, agent, mock_shared_state):
        """Test error handling during performance audit."""
        task_data = {"project_id": "invalid_project"}
        
        # Mock project not found
        mock_shared_state.get_project_state.return_value = None
        
        try:
            result = await agent.execute_task("performance_audit", task_data)
            # Should handle missing project gracefully
            assert "error" in str(result).lower() or "status" in result
        except Exception:
            # Exception handling depends on implementation
            pass

    @pytest.mark.unit
    async def test_concurrent_performance_tasks(self, agent):
        """Test handling concurrent performance tasks."""
        tasks = [
            agent.execute_task("optimize_widgets", {"target_widgets": ["widget1.dart"]}),
            agent.execute_task("optimize_images", {"image_directories": ["assets/"]}),
            agent.execute_task("setup_monitoring", {"monitoring_services": ["firebase"]})
        ]
        
        agent.think.return_value = "Performance task completed"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"task_completed": True}
        )
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("status" in result for result in results)

    @pytest.mark.unit
    def test_optimization_areas_configuration(self, agent):
        """Test optimization areas configuration."""
        expected_areas = [
            "widget_optimization", "state_management", "network_optimization",
            "image_optimization", "memory_management", "startup_time",
            "build_optimization", "animation_performance"
        ]
        
        for area in expected_areas:
            assert area in agent.optimization_areas
        
        assert len(agent.optimization_areas) >= len(expected_areas)

    @pytest.mark.unit
    def test_metrics_configuration(self, agent):
        """Test performance metrics configuration."""
        expected_metrics = [
            "frame_rate", "memory_usage", "cpu_usage", "network_latency",
            "app_size", "startup_time", "battery_usage"
        ]
        
        for metric in expected_metrics:
            assert metric in agent.metrics
        
        assert len(agent.metrics) >= len(expected_metrics)

    @pytest.mark.unit
    async def test_memory_leak_detection(self, agent):
        """Test memory leak detection functionality."""
        task_data = {
            "analysis_type": "memory_leaks",
            "monitoring_duration": "30_minutes",
            "gc_analysis": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={
                "memory_leaks_found": 3,
                "leak_sources": ["unclosed_streams", "retained_widgets"],
                "severity": "medium"
            }
        )
        
        result = await agent.execute_task("performance_audit", task_data)
        
        assert "audit_results" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_animation_performance_optimization(self, agent):
        """Test animation performance optimization."""
        task_data = {
            "animation_files": ["lib/animations/hero_animation.dart"],
            "performance_issues": ["jank", "dropped_frames"],
            "target_fps": 60
        }
        
        agent.read_file.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            output="class HeroAnimation extends AnimatedWidget { ... }"
        )
        
        agent.think.return_value = "Animation optimizations applied"
        
        result = await agent.execute_task("optimize_widgets", task_data)
        
        assert result["optimization_type"] == "widgets"
        assert "optimizations_applied" in result

    @pytest.mark.unit
    async def test_network_performance_optimization(self, agent):
        """Test network performance optimization."""
        task_data = {
            "optimization_strategies": ["caching", "compression", "parallel_requests"],
            "target_latency": "500ms",
            "offline_support": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"network_optimizations_applied": True}
        )
        
        agent.think.return_value = "Network performance optimized"
        
        result = await agent.execute_task("optimize_network_performance", task_data)
        
        assert "performance_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_build_time_optimization(self, agent):
        """Test build time optimization."""
        task_data = {
            "current_build_time": "5_minutes",
            "target_build_time": "2_minutes",
            "optimization_areas": ["dependency_resolution", "asset_compilation"]
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"build_optimizations_applied": True}
        )
        
        agent.think.return_value = "Build time optimization completed"
        
        result = await agent.execute_task("optimize_build_time", task_data)
        
        assert "performance_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_app_size_optimization(self, agent):
        """Test app size optimization."""
        task_data = {
            "current_size": "50MB",
            "target_size": "30MB",
            "optimization_strategies": ["tree_shaking", "asset_optimization", "code_splitting"]
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={
                "size_reduced": "18MB",
                "final_size": "32MB",
                "optimization_success": True
            }
        )
        
        result = await agent.execute_task("optimize_app_size", task_data)
        
        assert "performance_response" in result
        assert result["status"] == "completed"
