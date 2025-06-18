
"""
Performance Agent - Optimizes code and monitors performance for Flutter applications.
"""

import asyncio
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

           # class PerformanceAgent(BaseAgent):
    """
    The Performance Agent specializes in code optimization and performance monitoring.
    It analyzes performance bottlenecks and implements optimization strategies.
    """
    
    def __init__(self):
        super().__init__("performance")
        self.optimization_areas = [
            "widget_optimization", "state_management", "network_optimization",
            "image_optimization", "memory_management", "startup_time",
            "build_optimization", "animation_performance"
        ]
        self.metrics = [
            "frame_rate", "memory_usage", "cpu_usage", "network_latency",
            "app_size", "startup_time", "battery_usage"
        ]
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance tasks."""
        if "performance_audit" in task_description:
            return await self._perform_performance_audit(task_data)
        elif "optimize_widgets" in task_description:
            return await self._optimize_widgets(task_data)
        elif "optimize_images" in task_description:
            return await self._optimize_images(task_data)
        elif "setup_monitoring" in task_description:
            return await self._setup_performance_monitoring(task_data)
        else:
            return await self._handle_general_performance_task(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "architecture_review":
            return await self._review_performance_architecture(data)
        elif collaboration_type == "code_optimization":
            return await self._optimize_code(data)
        elif collaboration_type == "performance_recommendations":
            return await self._provide_performance_recommendations(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "file_added":
            await self._analyze_file_performance(change_data)
        elif event == "implementation_completed":
            await self._perform_performance_analysis(change_data["project_id"])
    
    async def _perform_performance_audit(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive performance audit."""
        project_id = task_data["project_id"]
        focus_areas = task_data.get("focus_areas", self.optimization_areas)
        
        project = shared_state.get_project_state(project_id)
        
        audit_prompt = f"""
        Perform a comprehensive performance audit for this Flutter application:
        
        Project: {project.name}
        Focus Areas: {focus_areas}
        Files: {list(project.files_created.keys()) if project.files_created else []}
        
        Analyze the following performance aspects:
        
           # 1. **Widget Performance**:
           - Unnecessary rebuilds
           - Heavy widgets in build methods
           # - Missing const constructors
           - Inefficient widget trees
           - ListView vs ListView.builder usage
        
        2. **State Management Performance**:
           - Overly broad listeners
           - Unnecessary state changes
           - Memory leaks in state objects
           - Provider/BLoC optimization
        
        3. **Memory Management**:
           - Object lifecycle management
           - Dispose method implementation
           - Stream subscription handling
           - Image caching
           - Large object retention
        
        4. **Network Optimization**:
           - API call efficiency
           - Response caching
           - Image loading optimization
           - Connection pooling
           - Request batching
        
        5. **Startup Performance**:
           - App initialization time
           - Splash screen duration
           - Lazy loading implementation
           - Asset preloading
        
        6. **Build Performance**:
           - APK/IPA size
           - Unnecessary dependencies
           - Asset optimization
           - Code splitting
        
        7. **Animation Performance**:
           - 60 FPS maintenance
           - GPU rasterization
           - Animation curves
           - Implicit vs explicit animations
        
        8. **Platform-Specific Optimizations**:
           - iOS-specific optimizations
           - Android-specific optimizations
           - Web performance considerations
        
        For each finding, provide:
        - Performance impact (High, Medium, Low)
        - Description of the issue
        - Recommended optimization
        - Code examples for fixes
        - Expected performance improvement
        
        Generate a detailed performance report with actionable recommendations.
        """
        
        audit_report = await self.think(audit_prompt, {
            "project": project,
            "optimization_areas": self.optimization_areas,
            "metrics": self.metrics
        })
        
        # Store performance metrics
        performance_data = {
            "audit_date": shared_state._agents[self.agent_id].last_update.isoformat(),
            "focus_areas": focus_areas,
            "report": audit_report,
            "status": "completed"
        }
        
        project.performance_metrics.update(performance_data)
        shared_state.update_project(project_id, performance_metrics=project.performance_metrics)
        
        return {
            "audit_report": audit_report,
            "focus_areas": focus_areas,
            "recommendations_count": "Multiple optimizations identified",
            "status": "completed"
        }
    
    async def _optimize_widgets(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize widget performance."""
        project_id = task_data["project_id"]
        widget_files = task_data.get("widget_files", [])
        
        optimization_prompt = f"""
        Optimize these Flutter widgets for performance:
        
           # Widget Files: {widget_files}
        
        Apply these optimization techniques:
        
        1. **Const Constructors**:
           DART_CODE_REMOVED
        
           # 2. **Widget Extraction**:
           DART_CODE_REMOVED
        
        3. **ListView Optimization**:
           DART_CODE_REMOVED
        
        4. **Avoid Anonymous Functions in Build**:
           DART_CODE_REMOVED
        
        5. **Use RepaintBoundary**:
           DART_CODE_REMOVED
        
           # 6. **Optimize StatefulWidget State**:
           DART_CODE_REMOVED
        
        7. **Use Keys Appropriately**:
           DART_CODE_REMOVED
        
        8. **Lazy Loading**:
           DART_CODE_REMOVED
        
        Provide optimized code with performance improvements explained.
        """
        
        optimized_widgets = await self.think(optimization_prompt, {
            "widget_files": widget_files,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "optimization_type": "widgets",
            "widget_files": widget_files,
            "optimizations": optimized_widgets,
            "status": "optimized"
        }
    
    async def _optimize_images(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize image loading and caching."""
        project_id = task_data["project_id"]
        image_usage = task_data.get("image_usage", [])
        
        image_optimization_prompt = f"""
        Optimize image handling for this Flutter app:
        
        Image Usage: {image_usage}
        
        Implement comprehensive image optimization:
        
        1. **Image Loading Optimization**:
           DART_CODE_REMOVED
        
        2. **Advanced Image Caching**:
           DART_CODE_REMOVED
        
        3. **Responsive Images**:
           DART_CODE_REMOVED
        
        4. **Lazy Image Loading**:
           DART_CODE_REMOVED
        
        5. **Image Preloading**:
           DART_CODE_REMOVED
        
        6. **Asset Optimization**:
           ```yaml
           # pubspec.yaml
           flutter:
             assets:
               - assets/images/
           
           # Use different resolutions
           assets/images/
             icon.png        # 1x
             2.0x/icon.png   # 2x
             3.0x/icon.png   # 3x
           ```
        
        7. **WebP Support**:
           DART_CODE_REMOVED
        
        Provide complete image optimization implementation.
        """
        
        image_optimizations = await self.think(image_optimization_prompt, {
            "image_usage": image_usage,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "optimization_type": "images",
            "optimizations": image_optimizations,
            "techniques": ["caching", "lazy_loading", "responsive_images", "preloading"],
            "status": "optimized"
        }
    
    async def _setup_performance_monitoring(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up performance monitoring infrastructure."""
        project_id = task_data["project_id"]
        metrics_to_track = task_data.get("metrics", self.metrics)
        
        monitoring_prompt = f"""
        Set up comprehensive performance monitoring:
        
        Metrics to Track: {metrics_to_track}
        
        Implement performance monitoring system:
        
        1. **Performance Monitoring Service**:
           DART_CODE_REMOVED
        
        2. **Custom Performance Metrics**:
           DART_CODE_REMOVED
        
        3. **Frame Rate Monitoring**:
           DART_CODE_REMOVED
        
        4. **Memory Usage Monitoring**:
           DART_CODE_REMOVED
        
        5. **Network Performance**:
           DART_CODE_REMOVED
        
        6. **App Startup Monitoring**:
           DART_CODE_REMOVED
        
        7. **Performance Dashboard**:
           DART_CODE_REMOVED
        
        Provide complete performance monitoring implementation.
        """
        
        monitoring_setup = await self.think(monitoring_prompt, {
            "metrics": metrics_to_track,
            "project": shared_state.get_project_state(project_id)
        })
        
        return {
            "monitoring_type": "performance",
            "metrics": metrics_to_track,
            "setup": monitoring_setup,
            "status": "configured"
        }
    
    async def _review_performance_architecture(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Review architecture for performance implications."""
        architecture = data.get("architecture", "")
        focus = data.get("focus", "performance_implications")
        
        review_prompt = f"""
        Review this architecture from a performance perspective:
        
        Architecture: {architecture}
        Focus: {focus}
        
        Analyze:
        1. Scalability bottlenecks
        2. Memory usage patterns
        3. Network efficiency
        4. Rendering performance
        5. State management overhead
        6. Build size implications
        
        Provide specific performance recommendations.
        """
        
        performance_review = await self.think(review_prompt, {
            "architecture": architecture,
            "optimization_areas": self.optimization_areas
        })
        
        return {
            "performance_review": performance_review,
            "focus": focus,
            "reviewer": self.agent_id
        }
    
    async def _analyze_file_performance(self, change_data: Dict[str, Any]) -> None:
        """Analyze new files for performance issues."""
        filename = change_data.get("filename", "")
        
        if filename.endswith('.dart'):
            project_id = change_data.get("project_id")
            if project_id:
                project = shared_state.get_project_state(project_id)
                if project and filename in project.files_created:
                    file_content = project.files_created[filename]
                    await self._analyze_code_performance(file_content, filename, project_id)
    
    async def _analyze_code_performance(self, code: str, filename: str, project_id: str) -> None:
        """Analyze code for performance issues."""
        analysis_prompt = f"""
        Analyze this Flutter/Dart code for performance issues:
        
        File: {filename}
        Code: {code}
        
        Check for:
        1. Inefficient widget usage
           # 2. Missing const constructors
        3. Heavy computations in build methods
        4. Memory leaks
        5. Inefficient loops or algorithms
        6. Unnecessary rebuilds
        
        Report performance issues and suggest optimizations.
        """
        
        analysis = await self.think(analysis_prompt, {
            "filename": filename,
            "optimization_areas": self.optimization_areas
        })
        
        # Store performance analysis
        project = shared_state.get_project_state(project_id)
        if project:
            if "performance_issue" in analysis.lower() or "optimization" in analysis.lower():
                project.performance_metrics[f"{filename}_analysis"] = {
                    "analysis": analysis,
                    "status": "analyzed",
                    "file": filename
                }
                shared_state.update_project(project_id, performance_metrics=project.performance_metrics)
    
    async def _handle_general_performance_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general performance tasks."""
        response = await self.think(f"Handle performance task: {task_description}", task_data)
        return {"response": response, "task": task_description}
