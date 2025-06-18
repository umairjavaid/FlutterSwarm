"""
Progress Tracker for FlutterSwarm
Tracks detailed progress information across different phases of Flutter app development.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class BuildPhase(Enum):
    """Build phases for Flutter development."""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


@dataclass
class PhaseProgress:
    """Progress information for a specific phase."""
    phase: BuildPhase
    start_time: datetime
    end_time: Optional[datetime] = None
    progress: float = 0.0
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    milestones_completed: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    
    @property
    def is_completed(self) -> bool:
        return self.end_time is not None
    
    @property
    def duration_so_far(self) -> timedelta:
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.now() - self.start_time


@dataclass
class ProjectProgress:
    """Comprehensive progress tracking for a project."""
    project_id: str
    start_time: datetime
    current_phase: BuildPhase = BuildPhase.INITIALIZATION
    overall_progress: float = 0.0
    phases: Dict[BuildPhase, PhaseProgress] = field(default_factory=dict)
    estimated_completion: Optional[datetime] = None
    
    def get_current_phase_progress(self) -> Optional[PhaseProgress]:
        return self.phases.get(self.current_phase)
    
    def get_total_duration(self) -> timedelta:
        return datetime.now() - self.start_time


class ProgressTracker:
    """
    Tracks detailed progress information across different phases of Flutter app development.
    Provides estimates, milestone tracking, and performance analytics.
    """
    
    def __init__(self):
        self.projects: Dict[str, ProjectProgress] = {}
        
        # Phase duration estimates (in minutes)
        self.phase_estimates = {
            BuildPhase.INITIALIZATION: 2,
            BuildPhase.PLANNING: 5,
            BuildPhase.ARCHITECTURE: 10,
            BuildPhase.IMPLEMENTATION: 30,
            BuildPhase.TESTING: 15,
            BuildPhase.SECURITY: 8,
            BuildPhase.PERFORMANCE: 5,
            BuildPhase.DOCUMENTATION: 10,
            BuildPhase.DEPLOYMENT: 5,
        }
        
        # Phase weight for overall progress calculation
        self.phase_weights = {
            BuildPhase.INITIALIZATION: 0.02,
            BuildPhase.PLANNING: 0.05,
            BuildPhase.ARCHITECTURE: 0.08,
            BuildPhase.IMPLEMENTATION: 0.40,
            BuildPhase.TESTING: 0.20,
            BuildPhase.SECURITY: 0.08,
            BuildPhase.PERFORMANCE: 0.05,
            BuildPhase.DOCUMENTATION: 0.07,
            BuildPhase.DEPLOYMENT: 0.05,
        }
    
    def start_project_tracking(self, project_id: str) -> None:
        """Start tracking progress for a new project."""
        if project_id in self.projects:
            return  # Already tracking
        
        self.projects[project_id] = ProjectProgress(
            project_id=project_id,
            start_time=datetime.now()
        )
        
        # Initialize first phase
        self._start_phase(project_id, BuildPhase.INITIALIZATION)
        
        print(f"📊 Started progress tracking for project: {project_id}")
    
    def update_project_progress(self, project_id: str, phase: str, progress: float) -> None:
        """Update project progress."""
        if project_id not in self.projects:
            self.start_project_tracking(project_id)
        
        project = self.projects[project_id]
        
        # Convert string phase to enum
        try:
            current_phase = BuildPhase(phase.lower())
        except ValueError:
            current_phase = BuildPhase.IMPLEMENTATION  # Default fallback
        
        # Check if phase changed
        if project.current_phase != current_phase:
            self._complete_phase(project_id, project.current_phase)
            self._start_phase(project_id, current_phase)
            project.current_phase = current_phase
        
        # Update phase progress
        if current_phase in project.phases:
            project.phases[current_phase].progress = progress
        
        # Update overall progress
        project.overall_progress = self._calculate_overall_progress(project_id)
        
        # Update estimated completion
        project.estimated_completion = self._estimate_completion(project_id)
    
    def add_milestone(self, project_id: str, phase: BuildPhase, milestone: str) -> None:
        """Add a completed milestone to a phase."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        if phase in project.phases:
            project.phases[phase].milestones_completed.append(milestone)
            print(f"✅ Milestone completed in {phase.value}: {milestone}")
    
    def add_blocker(self, project_id: str, phase: BuildPhase, blocker: str) -> None:
        """Add a blocker to a phase."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        if phase in project.phases:
            project.phases[phase].blockers.append(blocker)
            print(f"🚫 Blocker added to {phase.value}: {blocker}")
    
    def remove_blocker(self, project_id: str, phase: BuildPhase, blocker: str) -> None:
        """Remove a blocker from a phase."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        if phase in project.phases and blocker in project.phases[phase].blockers:
            project.phases[phase].blockers.remove(blocker)
            print(f"✅ Blocker resolved in {phase.value}: {blocker}")
    
    def _start_phase(self, project_id: str, phase: BuildPhase) -> None:
        """Start a new phase."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        
        if phase not in project.phases:
            estimated_duration = timedelta(minutes=self.phase_estimates.get(phase, 10))
            
            project.phases[phase] = PhaseProgress(
                phase=phase,
                start_time=datetime.now(),
                estimated_duration=estimated_duration
            )
            
            print(f"🚀 Started phase: {phase.value} (estimated: {estimated_duration})")
    
    def _complete_phase(self, project_id: str, phase: BuildPhase) -> None:
        """Complete a phase."""
        if project_id not in self.projects:
            return
        
        project = self.projects[project_id]
        
        if phase in project.phases and not project.phases[phase].is_completed:
            phase_progress = project.phases[phase]
            phase_progress.end_time = datetime.now()
            phase_progress.actual_duration = phase_progress.duration_so_far
            phase_progress.progress = 1.0
            
            print(f"✅ Completed phase: {phase.value} (duration: {phase_progress.actual_duration})")
    
    def _calculate_overall_progress(self, project_id: str) -> float:
        """Calculate overall project progress based on phase weights."""
        if project_id not in self.projects:
            return 0.0
        
        project = self.projects[project_id]
        total_progress = 0.0
        
        for phase, weight in self.phase_weights.items():
            if phase in project.phases:
                phase_progress = project.phases[phase].progress
                total_progress += phase_progress * weight
            # If phase hasn't started, it contributes 0 to total progress
        
        return min(total_progress, 1.0)  # Cap at 100%
    
    def _estimate_completion(self, project_id: str) -> Optional[datetime]:
        """Estimate project completion time."""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        # Calculate remaining work
        remaining_phases = []
        for phase in BuildPhase:
            if phase not in project.phases or not project.phases[phase].is_completed:
                remaining_phases.append(phase)
        
        # Estimate remaining time based on phase estimates
        remaining_time = timedelta()
        for phase in remaining_phases:
            if phase in project.phases:
                # Phase in progress
                phase_progress = project.phases[phase]
                if phase_progress.estimated_duration:
                    remaining_phase_time = phase_progress.estimated_duration * (1 - phase_progress.progress)
                    remaining_time += remaining_phase_time
            else:
                # Phase not started
                estimated_duration = timedelta(minutes=self.phase_estimates.get(phase, 10))
                remaining_time += estimated_duration
        
        return datetime.now() + remaining_time
    
    def get_current_phase(self, project_id: str) -> str:
        """Get the current phase for a project."""
        if project_id not in self.projects:
            return BuildPhase.INITIALIZATION.value
        
        return self.projects[project_id].current_phase.value
    
    def get_overall_progress(self) -> float:
        """Get overall progress across all projects."""
        if not self.projects:
            return 0.0
        
        total_progress = sum(project.overall_progress for project in self.projects.values())
        return total_progress / len(self.projects)
    
    def get_project_progress(self, project_id: str) -> float:
        """Get progress for a specific project."""
        if project_id not in self.projects:
            return 0.0
        
        return self.projects[project_id].overall_progress
    
    def get_phase_summary(self) -> Dict[str, Any]:
        """Get a summary of all phases across all projects."""
        summary = {}
        
        for project_id, project in self.projects.items():
            summary[project_id] = {
                "current_phase": project.current_phase.value,
                "overall_progress": project.overall_progress,
                "total_duration": str(project.get_total_duration()),
                "estimated_completion": project.estimated_completion.isoformat() if project.estimated_completion else None,
                "phases": {
                    phase.value: {
                        "progress": phase_progress.progress,
                        "is_completed": phase_progress.is_completed,
                        "duration": str(phase_progress.duration_so_far),
                        "milestones": len(phase_progress.milestones_completed),
                        "blockers": len(phase_progress.blockers)
                    }
                    for phase, phase_progress in project.phases.items()
                }
            }
        
        return summary
    
    def get_detailed_progress(self, project_id: str) -> Dict[str, Any]:
        """Get detailed progress information for a project."""
        if project_id not in self.projects:
            return {}
        
        project = self.projects[project_id]
        
        return {
            "project_id": project_id,
            "start_time": project.start_time.isoformat(),
            "current_phase": project.current_phase.value,
            "overall_progress": project.overall_progress,
            "total_duration": str(project.get_total_duration()),
            "estimated_completion": project.estimated_completion.isoformat() if project.estimated_completion else None,
            "phases": {
                phase.value: {
                    "start_time": phase_progress.start_time.isoformat(),
                    "end_time": phase_progress.end_time.isoformat() if phase_progress.end_time else None,
                    "progress": phase_progress.progress,
                    "is_completed": phase_progress.is_completed,
                    "estimated_duration": str(phase_progress.estimated_duration) if phase_progress.estimated_duration else None,
                    "actual_duration": str(phase_progress.actual_duration) if phase_progress.actual_duration else None,
                    "duration_so_far": str(phase_progress.duration_so_far),
                    "milestones_completed": phase_progress.milestones_completed,
                    "blockers": phase_progress.blockers
                }
                for phase, phase_progress in project.phases.items()
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics across all projects."""
        if not self.projects:
            return {}
        
        # Calculate average phase durations
        phase_durations = {phase: [] for phase in BuildPhase}
        total_projects = len(self.projects)
        completed_projects = 0
        
        for project in self.projects.values():
            if project.current_phase == BuildPhase.COMPLETED:
                completed_projects += 1
            
            for phase, phase_progress in project.phases.items():
                if phase_progress.is_completed and phase_progress.actual_duration:
                    phase_durations[phase].append(phase_progress.actual_duration.total_seconds())
        
        avg_phase_durations = {}
        for phase, durations in phase_durations.items():
            if durations:
                avg_seconds = sum(durations) / len(durations)
                avg_phase_durations[phase.value] = str(timedelta(seconds=avg_seconds))
        
        return {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "completion_rate": completed_projects / total_projects if total_projects > 0 else 0,
            "average_phase_durations": avg_phase_durations,
            "current_projects": [
                {
                    "project_id": project.project_id,
                    "current_phase": project.current_phase.value,
                    "progress": project.overall_progress,
                    "duration": str(project.get_total_duration())
                }
                for project in self.projects.values()
                if project.current_phase != BuildPhase.COMPLETED
            ]
        }
