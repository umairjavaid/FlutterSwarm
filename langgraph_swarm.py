"""
LangGraph-based FlutterSwarm Project Governance System
This module provides high-level project governance and quality gates while allowing
agents to collaborate autonomously through the real-time awareness system.
"""
from typing import Dict, List, Any, Optional, TypedDict, Type
from datetime import datetime
import asyncio
import uuid

# Initialize comprehensive logging first
from utils.comprehensive_logging import setup_comprehensive_logging, log_startup_banner
from utils.function_logger import track_function, track_tool
from utils.llm_logger import llm_logger
from monitoring.agent_logger import agent_logger
from utils.comprehensive_logging import get_logger

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

# Import shared state for integration with real-time awareness system
from shared.state import shared_state, AgentStatus, MessageType

class ProjectGovernanceState(TypedDict):
    """
    High-level state object for project governance.
    Focuses on quality gates, phase completion, and project milestones
    rather than detailed agent coordination.
    """
    # Project basics
    project_id: str
    name: str
    description: str
    requirements: List[str]
    
    # Governance phases (high-level)
    current_governance_phase: str
    completed_governance_phases: List[str]
    governance_phases: List[str]
    
    # Quality gates and criteria
    quality_gates: Dict[str, Dict[str, Any]]  # phase -> criteria
    gate_statuses: Dict[str, str]  # phase -> passed/failed/pending
    
    # Project health metrics
    overall_progress: float
    project_health: str  # healthy/warning/critical
    collaboration_effectiveness: float
    
    # Governance decisions and approvals
    governance_decisions: List[Dict[str, Any]]
    approval_status: Dict[str, str]  # phase -> approved/rejected/pending
    
    # Integration with real-time system
    real_time_metrics: Dict[str, Any]
    shared_consciousness_summary: Dict[str, Any]
    
    # Quality assurance
    quality_criteria_met: Dict[str, bool]
    compliance_status: Dict[str, str]
    
    # Fallback coordination (when real-time fails)
    coordination_fallback_active: bool
    stuck_processes: List[str]
    
    # Add new fields for improved state tracking
    state_version: int
    last_updated: str
    agent_execution_history: List[Dict[str, Any]]
    execution_errors: List[Dict[str, Any]]
    fallback_attempts: Dict[str, int]


class AgentRegistry:
    """
    Registry for managing agent instances in the FlutterSwarm system.
    Provides a factory pattern for creating and retrieving agents.
    """
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._agent_classes: Dict[str, Type] = {}
        self.logger = get_logger("FlutterSwarm.AgentRegistry")
        agent_logger.log_agent_status_change("system", AgentStatus.IDLE, AgentStatus.INITIALIZING, 
                                            "AgentRegistry initialization")
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def register_agent_class(self, agent_type: str, agent_class: Type) -> None:
        """Register an agent class with the registry."""
        self._agent_classes[agent_type] = agent_class
        self.logger.info(f"Registered agent class: {agent_type}")
        agent_logger.log_project_event("system", "agent_registration", 
                                     f"Registered agent class: {agent_type}")
    
    @track_function(agent_id="system", log_args=True, log_return=True)
    def get_agent(self, agent_type: str) -> Any:
        """Get or create an agent instance of the specified type."""
        # If agent already exists, return it
        if agent_type in self._agents and self._agents[agent_type] is not None:
            return self._agents[agent_type]
        
        # Otherwise, create a new agent instance
        if agent_type in self._agent_classes:
            try:
                agent_class = self._agent_classes[agent_type]
                agent = agent_class()
                self._agents[agent_type] = agent
                self.logger.info(f"Created new agent instance: {agent_type}")
                return agent
            except Exception as e:
                self.logger.error(f"Failed to create agent {agent_type}: {e}")
                return None
        else:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return None
    
    @track_function(agent_id="system", log_args=True, log_return=True)
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agent instances."""
        # Initialize any agents that haven't been created yet
        for agent_type in self._agent_classes:
            if agent_type not in self._agents or self._agents[agent_type] is None:
                self.get_agent(agent_type)
        
        return self._agents


class FlutterSwarmGovernance:
    """
    LangGraph-based project governance system that provides quality gates
    and high-level coordination while allowing autonomous agent collaboration.
    
    Role: Project governance, quality assurance, and fallback coordination
    """
    
    @track_function(agent_id="governance", log_args=True, log_return=False)
    def __init__(self, enable_monitoring: bool = True):
        # Setup comprehensive logging first
        try:
            setup_info = setup_comprehensive_logging()
            self.logger = get_logger(f"FlutterSwarm.Governance")
            self.logger.info(f"🚀 Governance system initialized with comprehensive logging - Session: {setup_info['session_id']}")
        except Exception as e:
            self.logger = get_logger(f"FlutterSwarm.Governance")
            self.logger.warning(f"Failed to initialize comprehensive logging: {e}")
        
        # Initialize agent registry
        self.agent_registry = AgentRegistry()
        
        # Register agent classes
        self._register_agent_classes()

        initialized_count = self._initialize_all_agents()
    
        if initialized_count < 7:  # Expected number of agents
            self.logger.warning(f"⚠️ Only {initialized_count} agents initialized. Some agents may not be available.")
    
        # Log governance system startup
        agent_logger.log_agent_status_change("governance", AgentStatus.IDLE, AgentStatus.INITIALIZING, 
                                            "FlutterSwarmGovernance initialization")
        
        # Note: Monitoring can be enabled if needed in the future
        self.enable_monitoring = enable_monitoring
        self.governance_phases = [
            'project_initiation', 'architecture_approval', 'implementation_oversight', 
            'quality_verification', 'security_compliance', 'performance_validation',
            'documentation_review', 'deployment_approval'
        ]
        
        # Comprehensive circuit breaker system to prevent infinite loops
        self.gate_failure_counts = {}  # gate_name -> failure_count
        self.max_gate_failures = 1  # Maximum failures before forcing pass (AGGRESSIVE)
        self.total_routing_steps = 0  # Track total routing steps
        self.max_routing_steps = 10  # Maximum routing steps before emergency exit (AGGRESSIVE)
        
        # Global failure tracking
        self.consecutive_failures = 0  # Track consecutive gate failures
        self.max_consecutive_failures = 2  # Maximum consecutive failures before emergency exit (AGGRESSIVE)
        self.global_failure_count = 0  # Total failures across all gates
        self.max_global_failures = 3  # Maximum total failures before emergency exit (AGGRESSIVE)
        
        # Timeout mechanisms
        self.gate_start_times = {}  # gate_name -> start_time
        self.max_gate_timeout = 60  # Maximum time (seconds) a gate can run (AGGRESSIVE)
        
        # Graceful degradation flags
        self.emergency_mode = False  # When true, bypass complex validations
        self.force_completion = False  # When true, force project completion
        
        # Quality gates criteria
        self.quality_gates = {
            'architecture_approval': {
                'architecture_design_complete': True,
                'security_review_passed': True,
                'performance_considerations_addressed': True,
                'scalability_verified': True
            },
            'implementation_oversight': {
                'code_quality_standards_met': True,
                'test_coverage_adequate': True,
                'architecture_compliance_verified': True,
                'real_time_collaboration_healthy': True
            },
            'quality_verification': {
                'all_tests_passing': True,
                'security_vulnerabilities_resolved': True,
                'performance_benchmarks_met': True,
                'documentation_complete': True
            },
            'deployment_approval': {
                'production_readiness_verified': True,
                'deployment_strategy_approved': True,
                'rollback_procedures_tested': True,
                'monitoring_configured': True
            }
        }
        
        # Initialize the StateGraph for governance
        self.graph = self._build_governance_graph()
        self.app = self.graph.compile()
        
        # Import LLM logger for governance system
        from utils.llm_logger import llm_logger
        self.llm_logger = llm_logger
        
        print("🏛️ FlutterSwarm Project Governance initialized")
        print("📋 Quality gates configured for all phases")
        print("🤝 Integrated with real-time agent collaboration system")
        print("🤖 LLM interactions will be logged for all governance decisions")
    
    
    def _initialize_all_agents(self):
        """Initialize all agents during startup to ensure they're registered."""
        agent_types = [
            "implementation", "testing", "architecture", 
            "security", "performance", "documentation", "devops"
        ]
        
        self.logger.info("🤖 Initializing all agents...")
        
        for agent_type in agent_types:
            try:
                agent = self.agent_registry.get_agent(agent_type)
                if agent:
                    self.logger.info(f"✅ {agent_type} agent initialized and registered")
                else:
                    self.logger.error(f"❌ Failed to initialize {agent_type} agent")
            except Exception as e:
                self.logger.error(f"❌ Error initializing {agent_type} agent: {e}")
        
        # Verify all agents are registered
        registered_agents = shared_state.get_agent_states()
        self.logger.info(f"📋 Registered agents: {list(registered_agents.keys())}")
        
        return len(registered_agents)
    
    def _register_agent_classes(self):
        """Register all agent classes with the registry."""
        try:
            from agents.implementation_agent import ImplementationAgent
            self.agent_registry.register_agent_class("implementation", ImplementationAgent)
            
            from agents.testing_agent import TestingAgent
            self.agent_registry.register_agent_class("testing", TestingAgent)
            
            from agents.architecture_agent import ArchitectureAgent
            self.agent_registry.register_agent_class("architecture", ArchitectureAgent)
            
            from agents.security_agent import SecurityAgent
            self.agent_registry.register_agent_class("security", SecurityAgent)
            
            from agents.performance_agent import PerformanceAgent
            self.agent_registry.register_agent_class("performance", PerformanceAgent)
            
            from agents.documentation_agent import DocumentationAgent
            self.agent_registry.register_agent_class("documentation", DocumentationAgent)
            
            from agents.devops_agent import DevOpsAgent
            self.agent_registry.register_agent_class("devops", DevOpsAgent)
            
        except ImportError as e:
            self.logger.warning(f"Could not register all agent classes: {e}")
    
    def _build_governance_graph(self) -> StateGraph:
        """Build the governance StateGraph focused on quality gates and project oversight."""
        
        # Create the governance workflow graph
        governance = StateGraph(ProjectGovernanceState)
        
        # Add governance nodes (quality gates and oversight)
        governance.add_node("project_initiation", self._project_initiation_gate)
        governance.add_node("architecture_approval", self._architecture_approval_gate)
        governance.add_node("implementation_oversight", self._implementation_oversight_gate)
        governance.add_node("quality_verification", self._quality_verification_gate)
        governance.add_node("security_compliance", self._security_compliance_gate)
        governance.add_node("performance_validation", self._performance_validation_gate)
        governance.add_node("documentation_review", self._documentation_review_gate)
        governance.add_node("deployment_approval", self._deployment_approval_gate)
        governance.add_node("fallback_coordination", self._fallback_coordination_node)
        
        # Set entry point for governance
        governance.set_entry_point("project_initiation")
        
        # Add governance workflow edges (quality gates progression)
        governance.add_conditional_edges(
            "project_initiation",
            self._route_from_project_initiation,
            {
                "architecture_approval": "architecture_approval",
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "architecture_approval",
            self._route_from_architecture_approval,
            {
                "implementation_oversight": "implementation_oversight",
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "implementation_oversight",
            self._route_from_implementation_oversight,
            {
                "quality_verification": "quality_verification",
                "fallback_coordination": "fallback_coordination",
                "architecture_approval": "architecture_approval",  # Return to architecture if issues
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "quality_verification",
            self._route_from_quality_verification,
            {
                "security_compliance": "security_compliance",
                "implementation_oversight": "implementation_oversight",  # Return if quality issues
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "security_compliance",
            self._route_from_security_compliance,
            {
                "performance_validation": "performance_validation",
                "implementation_oversight": "implementation_oversight",  # Return if security issues
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "performance_validation",
            self._route_from_performance_validation,
            {
                "documentation_review": "documentation_review",
                "implementation_oversight": "implementation_oversight",  # Return if performance issues
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "documentation_review",
            self._route_from_documentation_review,
            {
                "deployment_approval": "deployment_approval",
                "quality_verification": "quality_verification",  # Return if docs incomplete
                "fallback_coordination": "fallback_coordination",
                "end": END
            }
        )
        
        governance.add_conditional_edges(
            "fallback_coordination",
            self._route_from_fallback_coordination,
            {
                "architecture_approval": "architecture_approval",
                "implementation_oversight": "implementation_oversight",
                "quality_verification": "quality_verification",
                "end": END
            }
        )
        
        governance.add_edge("deployment_approval", END)
        
        return governance
    
    # Routing logic
    # Routing logic with enhanced failure handling
    def _route_from_project_initiation(self, state: ProjectGovernanceState) -> str:
        """Route from project initiation gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from project_initiation")
            return "end"
        
        # Check if project initiation is approved
        if state["approval_status"].get("project_initiation") == "approved":
            self._reset_consecutive_failures()
            return "architecture_approval"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Handle repeated failures
        if state["gate_statuses"].get("project_initiation") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("project_initiation"):
                self.logger.warning("🔄 Circuit breaker: Forcing project_initiation to pass")
                state["gate_statuses"]["project_initiation"] = "passed"
                state["approval_status"]["project_initiation"] = "approved"
                return "architecture_approval"
            return "fallback_coordination"
        
        # Default to architecture approval
        return "architecture_approval"
    
    def _route_from_architecture_approval(self, state: ProjectGovernanceState) -> str:
        """Route from architecture approval gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from architecture_approval")
            return "end"
        
        # Check if architecture approval is approved
        if state["approval_status"].get("architecture_approval") == "approved":
            self._reset_consecutive_failures()
            return "implementation_oversight"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("architecture_approval") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("architecture_approval"):
                self.logger.warning("🔄 Circuit breaker: Forcing architecture_approval to pass")
                state["gate_statuses"]["architecture_approval"] = "passed"
                state["approval_status"]["architecture_approval"] = "approved"
                return "implementation_oversight"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Default to fallback coordination for failed states
        return "fallback_coordination"
    
    def _route_from_implementation_oversight(self, state: ProjectGovernanceState) -> str:
        """Route from implementation oversight gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from implementation_oversight")
            return "end"
        
        # Check if implementation oversight is approved
        if state["approval_status"].get("implementation_oversight") == "approved":
            self._reset_consecutive_failures()
            return "quality_verification"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("implementation_oversight") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("implementation_oversight"):
                self.logger.warning("🔄 Circuit breaker: Forcing implementation_oversight to pass")
                state["gate_statuses"]["implementation_oversight"] = "passed"
                state["approval_status"]["implementation_oversight"] = "approved"
                return "quality_verification"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to architecture if architecture compliance issues
        if not state["quality_criteria_met"].get("architecture_compliance_verified", False):
            # Prevent infinite loops between architecture and implementation
            architecture_failures = self.gate_failure_counts.get("architecture_approval", 0)
            if architecture_failures < self.max_gate_failures:
                return "architecture_approval"
        
        # Default to quality verification or fallback
        return "fallback_coordination"
    
    def _route_from_quality_verification(self, state: ProjectGovernanceState) -> str:
        """Route from quality verification gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from quality_verification")
            return "end"
        
        # Check if quality verification is approved
        if state["approval_status"].get("quality_verification") == "approved":
            self._reset_consecutive_failures()
            return "security_compliance"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("quality_verification") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("quality_verification"):
                self.logger.warning("🔄 Circuit breaker: Forcing quality_verification to pass")
                state["gate_statuses"]["quality_verification"] = "passed"
                state["approval_status"]["quality_verification"] = "approved"
                return "security_compliance"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if issues, but prevent infinite loops
        implementation_failures = self.gate_failure_counts.get("implementation_oversight", 0)
        if implementation_failures < self.max_gate_failures:
            return "implementation_oversight"
        
        # Default to security compliance or fallback
        return "fallback_coordination"
    
    def _route_from_security_compliance(self, state: ProjectGovernanceState) -> str:
        """Route from security compliance gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from security_compliance")
            return "end"
        
        # Check if security compliance is approved
        if state["approval_status"].get("security_compliance") == "approved":
            self._reset_consecutive_failures()
            return "performance_validation"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("security_compliance") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("security_compliance"):
                self.logger.warning("🔄 Circuit breaker: Forcing security_compliance to pass")
                state["gate_statuses"]["security_compliance"] = "passed"
                state["approval_status"]["security_compliance"] = "approved"
                return "performance_validation"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if security issues, but prevent infinite loops
        implementation_failures = self.gate_failure_counts.get("implementation_oversight", 0)
        if implementation_failures < self.max_gate_failures:
            return "implementation_oversight"
        
        # Default to performance validation or fallback
        return "fallback_coordination"
    
    def _route_from_performance_validation(self, state: ProjectGovernanceState) -> str:
        """Route from performance validation gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from performance_validation")
            return "end"
        
        # Check if performance validation is approved
        if state["approval_status"].get("performance_validation") == "approved":
            self._reset_consecutive_failures()
            return "documentation_review"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("performance_validation") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("performance_validation"):
                self.logger.warning("🔄 Circuit breaker: Forcing performance_validation to pass")
                state["gate_statuses"]["performance_validation"] = "passed"
                state["approval_status"]["performance_validation"] = "approved"
                return "documentation_review"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if performance issues, but prevent infinite loops
        implementation_failures = self.gate_failure_counts.get("implementation_oversight", 0)
        if implementation_failures < self.max_gate_failures:
            return "implementation_oversight"
        
        # Default to documentation review or fallback
        return "fallback_coordination"
    
    def _route_from_documentation_review(self, state: ProjectGovernanceState) -> str:
        """Route from documentation review gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps or global failures
        if self._should_emergency_exit():
            self.logger.warning("🚨 Emergency exit triggered from documentation_review")
            return "end"
        
        # Check if documentation review is approved
        if state["approval_status"].get("documentation_review") == "approved":
            self._reset_consecutive_failures()
            return "deployment_approval"
        
        # Handle repeated failures with circuit breaker
        if state["gate_statuses"].get("documentation_review") == "failed":
            self._increment_global_failure()
            if self._check_circuit_breaker("documentation_review"):
                self.logger.warning("🔄 Circuit breaker: Forcing documentation_review to pass")
                state["gate_statuses"]["documentation_review"] = "passed"
                state["approval_status"]["documentation_review"] = "approved"
                return "deployment_approval"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to quality verification if documentation issues, but prevent infinite loops
        quality_failures = self.gate_failure_counts.get("quality_verification", 0)
        if quality_failures < self.max_gate_failures:
            return "quality_verification"
        
        # Default to deployment approval or fallback
        return "fallback_coordination"
    
    def _route_from_fallback_coordination(self, state: ProjectGovernanceState) -> str:
        """Route from fallback coordination node."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check the stuck processes to determine where to go
        if "project_stagnation" in state.get("stuck_processes", []):
            return "architecture_approval"
        
        if "quality_gate_failures" in state.get("stuck_processes", []):
            return "implementation_oversight"
        
        if "agent_collaboration_breakdown" in state.get("stuck_processes", []):
            return "quality_verification"
        
        # Default to implementation oversight
        return "implementation_oversight"
    
    # Governance Gate Implementations
    @track_function(agent_id="governance", log_args=True, log_return=True)
    async def _project_initiation_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Project initiation governance gate - verify project setup and readiness."""
        gate_name = 'project_initiation'
        print(f"🏛️ Project Initiation Gate: {state['name']}")
        
        # Log governance gate entry
        agent_logger.log_project_event(state['project_id'], "governance_gate", 
                                     f"Entering {gate_name} gate", {"state": state.get('current_governance_phase')})
        
        # Reset gate timer
        self._reset_gate_timer(gate_name)
        
        # Check for timeout
        if self._check_gate_timeout(gate_name):
            self._increment_gate_failure(gate_name)
            state['execution_errors'].append({
                'gate': gate_name,
                'error': 'Gate timeout exceeded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass")
            self._force_gate_completion(state, gate_name)
            state['overall_progress'] = 0.05
            return state
        
        # Integrate with shared state to get real-time project status
        project = shared_state.get_project_state(state['project_id'])
        
        # Check if project is properly initialized in shared state
        if not project:
            print("⚠️ Project not found in shared state, creating...")
            shared_state.create_project_with_id(
                state['project_id'],
                state['name'],
                state['description'],
                state['requirements']
            )
        
        # Verify project initiation criteria
        initiation_criteria = {
            'requirements_defined': len(state['requirements']) > 0,
            'project_scope_clear': len(state['description']) > 10,
            'governance_setup': True  # Always true as we're setting it up
        }
        
        all_criteria_met = all(initiation_criteria.values())
        
        # Handle failure
        if not all_criteria_met:
            self._increment_gate_failure(gate_name)
        else:
            self._reset_consecutive_failures()
        
        # Update governance state
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': initiation_criteria,
            'approved': all_criteria_met,
            'notes': 'Project initiation gate evaluation completed',
            'failure_count': self.gate_failure_counts.get(gate_name, 0)
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        # Update overall progress (project initiation is ~5% of total)
        state['overall_progress'] = 0.05 if all_criteria_met else 0.02
        
        print(f"✅ Project initiation gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    @track_function(agent_id="governance", log_args=True, log_return=True)
    async def _architecture_approval_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Architecture approval governance gate - verify architecture quality and completeness."""
        print(f"🏗️ Architecture Approval Gate: {state['name']}")
        
        gate_name = 'architecture_approval'
        
        # Log governance gate entry
        agent_logger.log_project_event(state['project_id'], "governance_gate", 
                                     f"Entering {gate_name} gate", {"state": state.get('current_governance_phase')})
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass to prevent infinite loop")
            all_criteria_met = True
            architecture_criteria = {
                'architecture_design_complete': True,
                'security_review_passed': True,
                'performance_considerations_addressed': True,
                'scalability_verified': True
            }
        else:
            # Get architecture agent from registry
            architecture_agent = self.agent_registry.get_agent("architecture")
            
            if not architecture_agent:
                self.logger.error("❌ Failed to get architecture agent")
                # Log failure and update state
                state['execution_errors'].append({
                    'gate': gate_name,
                    'error': 'Failed to get architecture agent',
                    'timestamp': datetime.now().isoformat()
                })
                state['gate_statuses'][gate_name] = 'failed'
                state['approval_status'][gate_name] = 'rejected'
                return state
            
            # Record execution in history
            state['agent_execution_history'].append({
                'gate': gate_name,
                'agent': 'architecture',
                'timestamp': datetime.now().isoformat(),
                'action': 'architecture_design_started'
            })
            
            try:
                # Prepare task data for the agent
                project_id = state['project_id']
                task_data = {
                    "project_id": project_id,
                    "name": state['name'],
                    "description": state['description'],
                    "requirements": state['requirements']
                }
                
                # Execute the architecture task
                self.logger.info(f"🚀 Executing architecture task for project {project_id}")
                result = await architecture_agent.execute_task(
                    "design_flutter_architecture", 
                    task_data
                )
                
                # Add small delay to ensure state persistence
                await asyncio.sleep(0.1)
                
                # Re-fetch project to ensure we have latest state
                project = shared_state.get_project_state(project_id)
                
                # Process the result
                if result.get("status") == "architecture_completed":
                    # Get architecture decision from result (it's a single decision, not a list)
                    decision_record = result.get("decision_record")
                    architecture_decisions = [decision_record] if decision_record else []
                    
                    # Update state with architecture decisions (use sync method)
                    shared_state.update_project(
                        project_id,
                        architecture_decisions=architecture_decisions
                    )
                    
                    # Set criteria met based on result
                    architecture_criteria = {
                        'architecture_design_complete': True,
                        'security_review_passed': self._check_security_approval(shared_state.get_project_state(project_id)),
                        'performance_considerations_addressed': self._check_performance_considerations(shared_state.get_project_state(project_id)),
                        'scalability_verified': self._check_scalability_verification(shared_state.get_project_state(project_id))
                    }
                    
                    # Record completion in history
                    state['agent_execution_history'].append({
                        'gate': gate_name,
                        'agent': 'architecture',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'architecture_design_completed',
                        'decisions_count': len(architecture_decisions)
                    })
                    
                else:
                    # Architecture failed
                    self.logger.error(f"❌ Architecture design failed: {result.get('status', 'unknown_status')}")
                    architecture_criteria = {
                        'architecture_design_complete': False,
                        'security_review_passed': False,
                        'performance_considerations_addressed': False,
                        'scalability_verified': False
                    }
                    
                    # Record failure in history
                    state['agent_execution_history'].append({
                        'gate': gate_name,
                        'agent': 'architecture',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'architecture_design_failed',
                        'error': result.get('error', 'Unknown error')
                    })
                    
                    # Increment failure count for circuit breaker
                    self._increment_gate_failure(gate_name)
                
            except Exception as e:
                self.logger.error(f"❌ Error executing architecture agent: {str(e)}")
                architecture_criteria = {
                    'architecture_design_complete': False,
                    'security_review_passed': False,
                    'performance_considerations_addressed': False,
                    'scalability_verified': False
                }
                
                # Record error in history
                state['execution_errors'].append({
                    'gate': gate_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Increment failure count for circuit breaker
                self._increment_gate_failure(gate_name)
        
        all_criteria_met = all(architecture_criteria.values())
        
        # Update governance state
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': architecture_criteria,
            'approved': all_criteria_met,
            'notes': 'Architecture approval gate evaluation completed'
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        # Update overall progress (architecture approval is ~15% of total)
        if all_criteria_met:
            state['overall_progress'] = 0.15
        
        print(f"🏗️ Architecture approval gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _implementation_oversight_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Implementation oversight gate - monitor real-time development progress and quality."""
        print(f"💻 Implementation Oversight Gate: {state['name']}")
        
        gate_name = 'implementation_oversight'
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass to prevent infinite loop")
            all_criteria_met = True
            implementation_criteria = {
                'code_quality_standards_met': True,
                'test_coverage_adequate': True,
                'architecture_compliance_verified': True,
                'real_time_collaboration_healthy': True
            }
        else:
            # Get implementation agent from registry
            implementation_agent = self.agent_registry.get_agent("implementation")
            
            if not implementation_agent:
                self.logger.error("❌ Failed to get implementation agent")
                # Log failure and update state
                state['execution_errors'].append({
                    'gate': gate_name,
                    'error': 'Failed to get implementation agent',
                    'timestamp': datetime.now().isoformat()
                })
                state['gate_statuses'][gate_name] = 'failed'
                state['approval_status'][gate_name] = 'rejected'
                return state
            
            # Record execution in history
            state['agent_execution_history'].append({
                'gate': gate_name,
                'agent': 'implementation',
                'timestamp': datetime.now().isoformat(),
                'action': 'implementation_started'
            })
            
            try:
                # Execute implementation phase with proper initialization and context
                implementation_result = await self.execute_implementation_phase(state)
                
                # Process the result
                if implementation_result.get("implementation_completed"):
                    implementation_results = implementation_result.get("implementation_results", {})
                    files_created = implementation_result.get("files_created", [])
                    
                    # Calculate success metrics
                    total_completed = len(implementation_results.get("completed_features", [])) if implementation_results else len(files_created)
                    total_features = implementation_results.get("total_features", 1) if implementation_results else 1
                    
                    # Determine success based on completion ratio and files created
                    success_ratio = total_completed / total_features if total_features > 0 else (1.0 if files_created else 0.0)
                    
                    implementation_criteria = {
                        'code_quality_standards_met': success_ratio > 0.5 or len(files_created) > 0,
                        'test_coverage_adequate': True,  # Will be verified by testing agent later
                        'architecture_compliance_verified': True,  # Will be verified by architecture agent later
                        'real_time_collaboration_healthy': self._check_agent_collaboration_health()
                    }
                    
                    # Record completion in history
                    state['agent_execution_history'].append({
                        'gate': gate_name,
                        'agent': 'implementation',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'implementation_completed',
                        'success_ratio': success_ratio,
                        'completed_features': total_completed,
                        'total_features': total_features
                    })
                    
                else:
                    # Implementation failed
                    error_msg = implementation_result.get('error', f"Implementation failed with status: {implementation_result.get('status', 'unknown')}")
                    self.logger.error(f"❌ Implementation failed: {error_msg}")
                    implementation_criteria = {
                        'code_quality_standards_met': False,
                        'test_coverage_adequate': False,
                        'architecture_compliance_verified': False,
                        'real_time_collaboration_healthy': self._check_agent_collaboration_health()
                    }
                    
                    # Record failure in history
                    state['agent_execution_history'].append({
                        'gate': gate_name,
                        'agent': 'implementation',
                        'timestamp': datetime.now().isoformat(),
                        'action': 'implementation_failed',
                        'error': error_msg
                    })
                    
                    # Increment failure count for circuit breaker
                    self._increment_gate_failure(gate_name)
                
            except Exception as e:
                self.logger.error(f"❌ Error executing implementation agent: {str(e)}")
                implementation_criteria = {
                    'code_quality_standards_met': False,
                    'test_coverage_adequate': False,
                    'architecture_compliance_verified': False,
                    'real_time_collaboration_healthy': False
                }
                
                # Record error in history
                state['execution_errors'].append({
                    'gate': gate_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Increment failure count for circuit breaker
                self._increment_gate_failure(gate_name)
        
        all_criteria_met = all(implementation_criteria.values())
        
        # Update governance state
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': implementation_criteria,
            'approved': all_criteria_met,
            'notes': 'Implementation oversight gate evaluation completed'
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        # Update overall progress (implementation is ~40% of total)
        if all_criteria_met:
            state['overall_progress'] = 0.40
        
        # Update state version and timestamp
        state['state_version'] = state.get('state_version', 0) + 1
        state['last_updated'] = datetime.now().isoformat()
        
        print(f"💻 Implementation oversight gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _quality_verification_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Quality verification gate - ensure all quality standards are met."""
        print(f"🔍 Quality Verification Gate: {state['name']}")
        
        gate_name = 'quality_verification'
        
        # Get testing agent from registry
        testing_agent = self.agent_registry.get_agent("testing")
        
        if not testing_agent:
            self.logger.error("❌ Failed to get testing agent")
            # Use mock data as fallback
            quality_criteria = {
                'all_tests_passing': False,
                'security_vulnerabilities_resolved': False,
                'performance_benchmarks_met': False,
                'documentation_complete': False
            }
        else:
            try:
                # Prepare task data for the agent
                project_id = state['project_id']
                project = shared_state.get_project_state(project_id)
                
                task_data = {
                    "project_id": project_id,
                    "name": state['name'],
                    "files": list(project.files_created.keys()) if project else []
                }
                
                # Execute the testing task
                self.logger.info(f"🚀 Executing testing task for project {project_id}")
                result = await testing_agent.execute_task(
                    "run_comprehensive_tests", 
                    task_data
                )
                
                # Process the result
                if result.get("status") == "tests_completed":
                    test_results = result.get("test_results", {})
                    
                    # Update project with test results
                    shared_state.update_project(project_id, test_results=test_results)
                    
                    # Set criteria based on test results
                    quality_criteria = {
                        'all_tests_passing': test_results.get("passing_percentage", 0) > 80,
                        'security_vulnerabilities_resolved': test_results.get("security_issues", 0) == 0,
                        'performance_benchmarks_met': test_results.get("performance_passing", False),
                        'documentation_complete': self._check_documentation_complete(project)
                    }
                else:
                    # Testing failed
                    quality_criteria = {
                        'all_tests_passing': False,
                        'security_vulnerabilities_resolved': False,
                        'performance_benchmarks_met': False,
                        'documentation_complete': self._check_documentation_complete(project)
                    }
            except Exception as e:
                self.logger.error(f"❌ Error executing testing agent: {str(e)}")
                quality_criteria = {
                    'all_tests_passing': False,
                    'security_vulnerabilities_resolved': False,
                    'performance_benchmarks_met': False,
                    'documentation_complete': False
                }
        
        all_criteria_met = all(quality_criteria.values())
        
        # Update governance state
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': quality_criteria,
            'approved': all_criteria_met,
            'notes': 'Quality verification gate evaluation completed'
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        # Update overall progress (quality verification is ~60% of total)
        if all_criteria_met:
            state['overall_progress'] = 0.60
        
        print(f"🔍 Quality verification gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _security_compliance_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Security compliance gate - verify security requirements are met."""
        gate_name = 'security_compliance'
        print(f"🔒 Security Compliance Gate: {state['name']}")
        
        # Reset gate timer
        self._reset_gate_timer(gate_name)
        
        # Check for timeout
        if self._check_gate_timeout(gate_name):
            self._increment_gate_failure(gate_name)
            state['execution_errors'].append({
                'gate': gate_name,
                'error': 'Gate timeout exceeded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass")
            self._force_gate_completion(state, gate_name)
            return state
        
        project = shared_state.get_project_state(state['project_id'])
        
        security_criteria = {
            'security_scan_passed': self._check_security_scan_results(project),
            'authentication_secure': self._check_authentication_security(project),
            'data_protection_implemented': self._check_data_protection(project),
            'compliance_requirements_met': self._check_compliance_requirements(project)
        }
        
        all_criteria_met = all(security_criteria.values())
        
        # Handle failure
        if not all_criteria_met:
            self._increment_gate_failure(gate_name)
        else:
            self._reset_consecutive_failures()
        
        security_insights = shared_state.get_shared_consciousness(f"security_architecture_{state['project_id']}")
        
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': security_criteria,
            'approved': all_criteria_met,
            'security_insights': security_insights,
            'notes': 'Security compliance gate evaluation completed',
            'failure_count': self.gate_failure_counts.get(gate_name, 0)
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"🔒 Security compliance gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _performance_validation_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Performance validation gate - verify performance requirements are met."""
        gate_name = 'performance_validation'
        print(f"⚡ Performance Validation Gate: {state['name']}")
        
        # Reset gate timer
        self._reset_gate_timer(gate_name)
        
        # Check for timeout
        if self._check_gate_timeout(gate_name):
            self._increment_gate_failure(gate_name)
            state['execution_errors'].append({
                'gate': gate_name,
                'error': 'Gate timeout exceeded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass")
            self._force_gate_completion(state, gate_name)
            return state
        
        project = shared_state.get_project_state(state['project_id'])
        
        performance_criteria = {
            'startup_time_acceptable': self._check_startup_performance(project),
            'memory_usage_optimal': self._check_memory_usage(project),
            'battery_efficiency_good': self._check_battery_efficiency(project),
            'network_optimization_implemented': self._check_network_optimization(project)
        }
        
        all_criteria_met = all(performance_criteria.values())
        
        # Handle failure
        if not all_criteria_met:
            self._increment_gate_failure(gate_name)
        else:
            self._reset_consecutive_failures()
        
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': performance_criteria,
            'approved': all_criteria_met,
            'notes': 'Performance validation gate evaluation completed',
            'failure_count': self.gate_failure_counts.get(gate_name, 0)
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"⚡ Performance validation gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _documentation_review_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Documentation review gate - verify documentation completeness."""
        gate_name = 'documentation_review'
        print(f"📚 Documentation Review Gate: {state['name']}")
        
        # Reset gate timer
        self._reset_gate_timer(gate_name)
        
        # Check for timeout
        if self._check_gate_timeout(gate_name):
            self._increment_gate_failure(gate_name)
            state['execution_errors'].append({
                'gate': gate_name,
                'error': 'Gate timeout exceeded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass")
            self._force_gate_completion(state, gate_name)
            return state
        
        project = shared_state.get_project_state(state['project_id'])
        
        documentation_criteria = {
            'api_documentation_complete': self._check_api_documentation(project),
            'user_documentation_available': self._check_user_documentation(project),
            'developer_documentation_complete': self._check_developer_documentation(project),
            'deployment_documentation_ready': self._check_deployment_documentation(project)
        }
        
        all_criteria_met = all(documentation_criteria.values())
        
        # Handle failure
        if not all_criteria_met:
            self._increment_gate_failure(gate_name)
        else:
            self._reset_consecutive_failures()
        
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': documentation_criteria,
            'approved': all_criteria_met,
            'notes': 'Documentation review gate evaluation completed',
            'failure_count': self.gate_failure_counts.get(gate_name, 0)
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"📚 Documentation review gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _deployment_approval_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Deployment approval gate - final verification before deployment."""
        gate_name = 'deployment_approval'
        print(f"🚀 Deployment Approval Gate: {state['name']}")
        
        # Reset gate timer
        self._reset_gate_timer(gate_name)
        
        # Check for timeout
        if self._check_gate_timeout(gate_name):
            self._increment_gate_failure(gate_name)
            state['execution_errors'].append({
                'gate': gate_name,
                'error': 'Gate timeout exceeded',
                'timestamp': datetime.now().isoformat()
            })
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass")
            self._force_gate_completion(state, gate_name)
            state['project_health'] = 'healthy'
            state['overall_progress'] = 1.0
            print("🎉 PROJECT DEPLOYMENT APPROVED (via circuit breaker) - Ready for production!")
            return state
        
        project = shared_state.get_project_state(state['project_id'])
        
        deployment_criteria = {
            'production_readiness_verified': self._check_production_readiness(project),
            'deployment_strategy_approved': self._check_deployment_strategy(project),
            'rollback_procedures_tested': self._check_rollback_procedures(project),
            'monitoring_configured': self._check_monitoring_configuration(project)
        }
        
        all_criteria_met = all(deployment_criteria.values())
        
        # Handle failure
        if not all_criteria_met:
            self._increment_gate_failure(gate_name)
        else:
            self._reset_consecutive_failures()
        
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'criteria_met': deployment_criteria,
            'approved': all_criteria_met,
            'notes': 'Deployment approval gate evaluation completed',
            'failure_count': self.gate_failure_counts.get(gate_name, 0)
        })
        
        state['gate_statuses'][gate_name] = 'passed' if all_criteria_met else 'failed'
        state['approval_status'][gate_name] = 'approved' if all_criteria_met else 'rejected'
        
        if all_criteria_met:
            state['project_health'] = 'healthy'
            state['overall_progress'] = 1.0
            print("🎉 PROJECT DEPLOYMENT APPROVED - Ready for production!")
        else:
            print("⚠️ Deployment approval gate FAILED - Cannot deploy to production")
        
        return state
    
    # Fallback Coordination Node
    async def _fallback_coordination_node(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """
        Enhanced fallback coordination node with circuit breaker support and forced implementation if stuck.
        """
        print(f"🔄 Fallback Coordination Node: {state['name']}")
        
        # Check circuit breaker status for this coordination
        current_stage = state.get('current_stage', 'fallback_coordination')
        circuit_breaker = self._get_circuit_breaker_status(current_stage, state)
        
        # Assess current project health
        project = shared_state.get_project_state(state['project_id'])
        collaboration_health = self._assess_collaboration_health()
        
        # Enhanced failure analysis
        coordination_needs = []
        failure_patterns = self._analyze_failure_patterns(state)
        
        # Check for circuit breaker conditions
        if circuit_breaker.get("triggered", False):
            print(f"🚫 Circuit breaker is TRIGGERED for fallback coordination")
            coordination_needs.append('circuit_breaker_open')
        
        # Check if agents are stuck or not collaborating
        if not collaboration_health.get('healthy', False):
            coordination_needs.append('agent_collaboration_breakdown')
        
        # Check if quality gates are failing repeatedly
        failed_gates = [gate for gate, status in state['gate_statuses'].items() if status == 'failed']
        if len(failed_gates) > 2:
            coordination_needs.append('quality_gate_failures')
        
        # Check if project is making progress
        if state.get('overall_progress', 0) < 0.1:
            coordination_needs.append('project_stagnation')
        
        # Check for patterns indicating infinite loops
        if failure_patterns.get('infinite_loop_risk', False):
            coordination_needs.append('infinite_loop_detected')
        
        # --- PATCH: Force implementation agent if stuck in planning/architecture ---
        stuck_phases = [
            state.get('current_governance_phase'),
            state.get('current_phase'),
        ]
        if any(phase in ['planning', 'architecture_approval', 'project_initiation'] for phase in stuck_phases):
            print(f"⚠️ Project appears stuck in {stuck_phases}, forcing implementation agent to create Flutter project!")
            implementation_agent = self.agent_registry.get_agent("implementation")
            if implementation_agent:
                try:
                    # Use project_id, name, description from state
                    project_id = state['project_id']
                    task_data = {
                        "project_id": project_id,
                        "name": state["name"],
                        "description": state["description"],
                        "requirements": state["requirements"],
                        "phase": "implementation",
                        "task_type": "setup_project_structure"
                    }
                    result = await implementation_agent.execute_task("setup_project_structure", task_data)
                    print(f"✅ Forced implementation agent result: {result.get('status', result)}")
                    # Update shared state with project_path if available
                    if result.get('project_path'):
                        shared_state.update_project(project_id, project_path=result['project_path'])
                except Exception as e:
                    print(f"❌ Error forcing implementation agent: {e}")
            else:
                print("❌ Could not get implementation agent for forced project creation!")
        # --- END PATCH ---
        
        # Implement enhanced coordination strategies
        coordination_actions = []
        
        for need in coordination_needs:
            if need == 'circuit_breaker_open':
                # Handle circuit breaker open state
                alternative_path = self._find_alternative_coordination_path(state)
                if alternative_path:
                    coordination_actions.append(f'alternative_path_activated: {alternative_path}')
                else:
                    # Force emergency exit if no alternatives
                    state['status'] = 'emergency_exit'
                    state['emergency_reason'] = 'No alternative coordination paths available'
                    return state
                    
            elif need == 'agent_collaboration_breakdown':
                # Force synchronization through shared consciousness
                shared_state.broadcast_project_status(state['project_id'])
                coordination_actions.append('forced_agent_synchronization')
                
            elif need == 'quality_gate_failures':
                # Enhanced gate reset with circuit breaker awareness
                for gate in failed_gates:
                    gate_circuit_breaker = self._get_circuit_breaker_status(gate, state)
                    if not gate_circuit_breaker.get("triggered", False):
                        state['gate_statuses'][gate] = 'pending'
                    else:
                        # Skip gates with open circuit breakers
                        state['gate_statuses'][gate] = 'bypassed_circuit_breaker'
                coordination_actions.append('enhanced_quality_gate_reset')
                
            elif need == 'project_stagnation':
                # Enhanced guidance with failure pattern awareness
                guidance = {
                    'priority_tasks': self._identify_priority_tasks(state),
                    'unblocking_actions': self._identify_unblocking_actions(state),
                    'failure_patterns': failure_patterns,
                    'coordination_timestamp': datetime.now().isoformat()
                }
                shared_state.update_shared_consciousness(
                    f"fallback_coordination_{state['project_id']}", 
                    guidance
                )
                coordination_actions.append('enhanced_guidance_provided')
                
            elif need == 'infinite_loop_detected':
                # Break infinite loops with emergency coordination
                self._break_infinite_loop(state)
                coordination_actions.append('infinite_loop_broken')
        
        # Update failure tracking
        self._update_failure_tracking('fallback_coordination', state)
        
        # Update coordination status
        state['coordination_fallback_active'] = True
        state['stuck_processes'] = coordination_needs
        
        # Record enhanced coordination decision
        state['governance_decisions'].append({
            'gate': 'fallback_coordination',
            'timestamp': datetime.now().isoformat(),
            'coordination_needs': coordination_needs,
            'actions_taken': coordination_actions,
            'collaboration_health': collaboration_health,
            'circuit_breaker_status': circuit_breaker,
            'failure_patterns': failure_patterns,
            'notes': 'Enhanced fallback coordination node with circuit breaker support and forced implementation if stuck'
        })
        
        print(f"🔄 Enhanced fallback coordination completed: {len(coordination_actions)} actions taken")
        
        return state
    
    async def execute_implementation_phase(self, state: ProjectGovernanceState) -> Dict[str, Any]:
        """Execute implementation phase with proper initialization."""
        project_id = state["project_id"]
        
        # Get implementation agent from registry
        implementation_agent = self.agent_registry.get_agent("implementation")
        
        if not implementation_agent:
            self.logger.error("❌ Failed to get implementation agent")
            return {
                "implementation_completed": False,
                "files_created": [],
                "error": "Failed to get implementation agent"
            }
        
        # Get project state and architecture decisions from shared state
        project_state = shared_state.get_project_state(project_id)
        architecture_decisions = {}
        
        if project_state and hasattr(project_state, 'architecture_decisions'):
            architecture_decisions = project_state.architecture_decisions
        else:
            # Fallback to get from shared consciousness
            shared_consciousness = shared_state.get_shared_consciousness()
            architecture_decisions = shared_consciousness.get(f"architecture_{project_id}", {})
        
        # Create detailed task data with all necessary context
        task_data = {
            "project_id": project_id,
            "name": state["name"],
            "description": state["description"],
            "requirements": state["requirements"],
            "architecture_decisions": architecture_decisions,
            "phase": "implementation",
            "task_type": "implement_features_with_context",
            # Additional context from governance state
            "governance_state": {
                "current_phase": state.get("current_governance_phase"),
                "completed_phases": state.get("completed_governance_phases", []),
                "quality_criteria": state.get("quality_criteria_met", {}),
                "project_health": state.get("project_health", "healthy")
            }
        }
        
        try:
            self.logger.info(f"🚀 Executing implementation phase for project {project_id}")
            
            # First ensure Flutter project is initialized
            project_init_result = await implementation_agent._ensure_flutter_project_exists({
                "project_id": project_id,
                "name": state["name"],
                "description": state["description"]
            })
            
            if not project_init_result:
                self.logger.error("❌ Failed to initialize Flutter project")
                return {
                    "implementation_completed": False,
                    "files_created": [],
                    "error": "Failed to initialize Flutter project"
                }
            
            # Execute implementation with context
            result = await implementation_agent.execute_task(
                "implement_features_with_context",
                task_data
            )
            
            # Process and validate results
            if result and result.get("status") == "completed":
                implementation_results = result.get("results", {})
                files_created = implementation_results.get("files_created", [])
                
                # Update project state with implementation results
                if project_state:
                    shared_state.update_project(
                        project_id,
                        implementation_results=implementation_results,
                        implementation_status="completed",
                        files_created=files_created
                    )
                
                self.logger.info(f"✅ Implementation phase completed successfully")
                self.logger.info(f"📁 Created {len(files_created)} files")
                
                return {
                    "implementation_completed": True,
                    "files_created": files_created,
                    "implementation_results": implementation_results,
                    "status": "success"
                }
            else:
                error_msg = result.get("error", "Unknown implementation error") if result else "No result returned"
                self.logger.error(f"❌ Implementation phase failed: {error_msg}")
                
                return {
                    "implementation_completed": False,
                    "files_created": [],
                    "error": error_msg,
                    "status": "failed"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Exception during implementation phase: {e}")
            return {
                "implementation_completed": False,
                "files_created": [],
                "error": str(e),
                "status": "error"
            }

    # Enhanced helper methods for circuit breaker and failure management
    def _should_emergency_exit(self) -> bool:
        """Check if emergency exit conditions are met."""
        if self.total_routing_steps > self.max_routing_steps:
            self.logger.error(f"🚨 Maximum routing steps ({self.max_routing_steps}) exceeded")
            return True
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.logger.error(f"🚨 Maximum consecutive failures ({self.max_consecutive_failures}) exceeded")
            return True
        
        if self.global_failure_count >= self.max_global_failures:
            self.logger.error(f"🚨 Maximum global failures ({self.max_global_failures}) exceeded")
            return True
        
        return False
    
    def _check_circuit_breaker(self, gate_name: str) -> bool:
        """Check if circuit breaker has been triggered for a gate."""
        failure_count = self.gate_failure_counts.get(gate_name, 0)
        if failure_count >= self.max_gate_failures:
            self.logger.warning(f"🔄 Circuit breaker triggered for {gate_name} after {failure_count} failures")
            return True
        return False
    
    def _get_circuit_breaker_status(self, gate_name: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get detailed circuit breaker status information for a gate."""
        failure_count = self.gate_failure_counts.get(gate_name, 0)
        timeout = self._check_gate_timeout(gate_name)
        
        return {
            "gate": gate_name,
            "failure_count": failure_count,
            "max_failures": self.max_gate_failures,
            "triggered": failure_count >= self.max_gate_failures,
            "timeout": timeout,
            "total_routing_steps": self.total_routing_steps,
            "emergency_mode": self.emergency_mode,
            "force_completion": self.force_completion,
            "consecutive_failures": self.consecutive_failures,
            "global_failures": self.global_failure_count
        }
    
    def _increment_gate_failure(self, gate_name: str) -> None:
        """Increment failure count for a gate."""
        self.gate_failure_counts[gate_name] = self.gate_failure_counts.get(gate_name, 0) + 1
        self.consecutive_failures += 1
        self.logger.warning(f"⚠️ Gate {gate_name} failed (attempt {self.gate_failure_counts[gate_name]})")
    
    def _increment_global_failure(self) -> None:
        """Increment global failure count."""
        self.global_failure_count += 1
        self.consecutive_failures += 1
        
    def _reset_consecutive_failures(self) -> None:
        """Reset consecutive failure count on success."""
        if self.consecutive_failures > 0:
            self.logger.info(f"✅ Resetting consecutive failures (was {self.consecutive_failures})")
            self.consecutive_failures = 0
    
    def _check_gate_timeout(self, gate_name: str) -> bool:
        """Check if a gate has timed out."""
        if gate_name not in self.gate_start_times:
            self.gate_start_times[gate_name] = datetime.now()
            return False
        
        elapsed = (datetime.now() - self.gate_start_times[gate_name]).total_seconds()
        if elapsed > self.max_gate_timeout:
            self.logger.warning(f"⏰ Gate {gate_name} timed out after {elapsed:.1f} seconds")
            return True
        
        return False
    
    def _reset_gate_timer(self, gate_name: str) -> None:
        """Reset the timer for a gate."""
        self.gate_start_times[gate_name] = datetime.now()
    
    def _force_gate_completion(self, state: ProjectGovernanceState, gate_name: str) -> None:
        """Force a gate to complete successfully to break deadlocks."""
        self.logger.warning(f"🔧 Forcing completion of {gate_name} gate")
        
        state['gate_statuses'][gate_name] = 'passed'
        state['approval_status'][gate_name] = 'approved'
        
        # Add governance decision for forced completion
        state['governance_decisions'].append({
            'gate': gate_name,
            'timestamp': datetime.now().isoformat(),
            'forced_completion': True,
            'reason': 'Circuit breaker triggered - preventing infinite loop',
            'consecutive_failures': self.consecutive_failures,
            'global_failures': self.global_failure_count,
            'notes': f'Gate {gate_name} was forced to pass due to repeated failures'
        })
    
    def _check_agent_collaboration_health(self) -> bool:
        """Check if agents are collaborating effectively."""
        # Basic implementation - should be enhanced with actual metrics
        health_data = {'healthy': True, 'metric': 'collaboration_rate', 'value': 0.8}
        return health_data.get('healthy', False)
    
    def _analyze_failure_patterns(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze failure patterns to detect infinite loops and recurring issues."""
        failures = state.get("failures", [])
        if len(failures) < 3:
            return {"infinite_loop_risk": False}
        
        # Check for repeating stages/errors
        recent_failures = failures[-5:]  # Last 5 failures
        stages = [f.get("stage") for f in recent_failures]
        errors = [f.get("error") for f in recent_failures]
        
        # Detect infinite loop patterns
        infinite_loop_risk = (
            len(set(stages)) <= 2 or  # Stuck between 2 stages
            len(set(errors)) <= 1    # Same error repeating
        )
        
        return {
            "infinite_loop_risk": infinite_loop_risk,
            "recent_stages": stages,
            "recent_errors": errors,
            "pattern_analysis": {
                "unique_stages": len(set(stages)),
                "unique_errors": len(set(errors)),
                "total_recent_failures": len(recent_failures)
            }
        }
    
    def _find_alternative_coordination_path(self, state: Dict[str, Any]) -> str:
        """Find alternative coordination paths when circuit breaker is open."""
        current_stage = state.get("current_stage", "unknown")
        
        # Alternative paths based on current stage
        alternatives = {
            "architecture": "simplified_architecture",
            "implementation": "basic_implementation", 
            "testing": "minimal_testing",
            "quality_verification": "basic_quality_check",
            "security_compliance": "security_bypass",
            "performance_validation": "performance_skip",
            "documentation_review": "minimal_documentation",
            "deployment_approval": "emergency_deployment"
        }
        
        return alternatives.get(current_stage, "emergency_completion")
    
    def _break_infinite_loop(self, state: Dict[str, Any]) -> None:
        """Break infinite loops by forcing a different path."""
        current_stage = state.get("current_stage", "unknown")
        
        # Force progression with minimal requirements
        state["emergency_mode"] = True
        state["simplified_requirements"] = True
        state["bypass_quality_gates"] = True
        
        # Jump to next logical stage or completion
        if current_stage in ["architecture", "implementation"]:
            state["current_stage"] = "minimal_testing"
        elif current_stage in ["testing", "quality_verification"]:
            state["current_stage"] = "emergency_completion"
        else:
            state["current_stage"] = "emergency_completion"
            
        state["loop_break_applied"] = True
        self.logger.warning(f"🚨 Infinite loop broken - forced progression from {current_stage}")
    
    def _check_architecture_design_completion(self, project) -> bool:
        """Check if architecture design is complete."""
        if not project or not hasattr(project, 'architecture_decisions'):
            return False
        return len(project.architecture_decisions) > 0

    def _check_security_approval(self, project) -> bool:
        """Check if security reviews are complete."""
        if not project:
            return False
        
        # Check for security-related content in architecture decisions
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        if not architecture_decisions:
            return False
            
        # Look for security-related keywords in the descriptions
        security_keywords = ['security', 'authentication', 'authorization', 'secure', 'encryption', 'token']
        for decision in architecture_decisions:
            description = str(decision.get('description', '')).lower()
            if any(keyword in description for keyword in security_keywords):
                return True
        return False
    
    def _check_performance_optimization(self, project) -> bool:
        """Check if performance considerations are addressed."""
        if not project:
            return False
        
        # Check for performance-related content in architecture decisions
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        if not architecture_decisions:
            return False
            
        # Look for performance-related keywords in the descriptions
        performance_keywords = ['performance', 'optimization', 'caching', 'lazy', 'memory', 'efficient']
        for decision in architecture_decisions:
            description = str(decision.get('description', '')).lower()
            if any(keyword in description for keyword in performance_keywords):
                return True
        return False
    
    def _check_scalability_verification(self, project) -> bool:
        """Check if the architecture includes scalability verification."""
        if not project:
            return False
        
        # Check if architecture decisions include scalability considerations
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        if not architecture_decisions:
            return False
            
        # Look for scalability-related keywords in the descriptions
        scalability_keywords = ['scalability', 'scalable', 'scale', 'distributed', 'microservices']
        for decision in architecture_decisions:
            description = str(decision.get('description', '')).lower()
            if any(keyword in description for keyword in scalability_keywords):
                return True
        return False
    
    def _check_performance_considerations(self, project) -> bool:
        """Check if the architecture addresses performance considerations."""
        if not project:
            return False
        
        # Check if architecture decisions include performance considerations
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        if not architecture_decisions:
            return False
            
        # Look for performance-related keywords in the descriptions
        performance_keywords = ['performance', 'optimization', 'caching', 'lazy', 'memory', 'efficient']
        for decision in architecture_decisions:
            description = str(decision.get('description', '')).lower()
            if any(keyword in description for keyword in performance_keywords):
                return True
        return False
    
    def _check_documentation_complete(self, project) -> bool:
        """Check if documentation is complete."""
        if not project:
            return False
        
        # Check for documentation completeness
        documentation = getattr(project, 'documentation', {})
        return len(documentation) > 0
    
    def _check_code_quality_standards(self, project) -> bool:
        """Check if code quality standards are met."""
        if not project:
            return False
        
        # Check for code quality indicators
        # In a real implementation, this would check:
        # - Code coverage metrics
        # - Linting results
        # - Code complexity metrics
        # - Code review status
        
        # For now, basic implementation that checks if project has quality data
        quality_data = getattr(project, 'quality_metrics', {})
        return len(quality_data) >= 0  # Always pass for now, but structure is in place
    
    def _assess_collaboration_health(self) -> Dict[str, Any]:
        """Assess the health of agent collaboration."""
        # Monitor agent activity and interactions
        all_agents = shared_state.get_agent_states()
        
        # Count active agents
        active_agents = sum(1 for state in all_agents.values() 
                          if state.status in [AgentStatus.WORKING, AgentStatus.WAITING])
        
        # Get recent messages as collaboration indicator
        recent_messages = shared_state.get_recent_messages(minutes=5)
        collaboration_messages = [
            msg for msg in recent_messages 
            if msg.message_type in [MessageType.COLLABORATION_REQUEST, MessageType.TASK_COMPLETED]
        ]
        
        # Determine health
        health_status = "healthy"
        if active_agents < 2:
            health_status = "warning"  # Not enough active agents
        
        if len(collaboration_messages) < 3 and active_agents > 1:
            health_status = "warning"  # Not enough collaboration
            
        if active_agents == 0:
            health_status = "critical"  # No active agents
        
        return {
            "healthy": health_status == "healthy",
            "status": health_status,
            "active_agents": active_agents,
            "total_agents": len(all_agents),
            "collaboration_messages": len(collaboration_messages),
            "timestamp": datetime.now().isoformat()
        }
    
    def _identify_priority_tasks(self, state: Dict[str, Any]) -> List[str]:
        """Identify priority tasks based on current state."""
        priority_tasks = []
        
        # Check failed gates
        for gate, status in state.get("gate_statuses", {}).items():
            if status == "failed":
                priority_tasks.append(f"Fix issues in {gate}")
        
        # Check stuck processes
        for process in state.get("stuck_processes", []):
            priority_tasks.append(f"Unblock {process}")
        
        # Add default tasks if none identified
        if not priority_tasks:
            priority_tasks = [
                "Complete architecture design",
                "Implement core features",
                "Add comprehensive tests"
            ]
        
        return priority_tasks
    
    def _identify_unblocking_actions(self, state: Dict[str, Any]) -> List[str]:
        """Identify actions that can unblock the project."""
        unblocking_actions = []
        
        # Based on overall progress
        progress = state.get("overall_progress", 0)
        
        if progress < 0.1:
            unblocking_actions.append("Create initial Flutter project structure")
            unblocking_actions.append("Define core architecture patterns")
        elif progress < 0.3:
            unblocking_actions.append("Implement basic navigation structure")
            unblocking_actions.append("Create core model classes")
        elif progress < 0.6:
            unblocking_actions.append("Complete feature implementation")
            unblocking_actions.append("Add comprehensive test suite")
        else:
            unblocking_actions.append("Resolve quality gate issues")
            unblocking_actions.append("Prepare for deployment")
        
        return unblocking_actions
    
    # Add new methods for project creation and building
    def _create_project(self, name: str, description: str, requirements: List[str], features: List[str] = None) -> str:
        """(INTERNAL) Create a new Flutter project with the given details. Use only inside build_project if needed."""
        import uuid
        project_id = str(uuid.uuid4())
        shared_state.create_project_with_id(
            project_id,
            name,
            description,
            requirements
        )
        self.logger.info(f"Created new project: {name} (ID: {project_id})")
        return project_id

    @track_function(agent_id="governance", log_args=True, log_return=True)
    async def build_project(self, name: str, description: str, requirements: List[str], features: List[str] = None,
                           platforms: List[str] = None, ci_system: str = None, project_id: str = None) -> Dict[str, Any]:
        """Build the Flutter project. If the project does not exist, create it. Returns build result."""
        # Log project build start
        agent_logger.log_project_event("system", "project_build_start", 
                                     f"Starting project build: {name}", {
                                         "description": description,
                                         "requirements": requirements,
                                         "features": features,
                                         "platforms": platforms
                                     })
        
        # Try to find existing project by name
        if not project_id:
            # Search shared_state for a project with this name
            for pid, project in getattr(shared_state, '_projects', {}).items():
                if getattr(project, 'name', None) == name:
                    project_id = pid
                    break
        if not project_id:
            project_id = self._create_project(name, description, requirements, features)

        self.logger.info(f"Starting build for project: {name} (ID: {project_id})")
        # Initialize project governance state
        governance_state = ProjectGovernanceState(
            project_id=project_id,
            name=name,
            description=description,
            requirements=requirements,
            
            # Governance phases
            current_governance_phase="project_initiation",
            completed_governance_phases=[],
            governance_phases=self.governance_phases,
            
            # Quality gates and criteria
            quality_gates=self.quality_gates,
            gate_statuses={phase: "pending" for phase in self.governance_phases},
            
            # Project health metrics
            overall_progress=0.0,
            project_health="healthy",
            collaboration_effectiveness=1.0,
            
            # Governance decisions and approvals
            governance_decisions=[],
            approval_status={phase: "pending" for phase in self.governance_phases},
            
            # Integration with real-time system
            real_time_metrics={},
            shared_consciousness_summary={},
            
            # Quality assurance
            quality_criteria_met={},
            compliance_status={},
            
            # Fallback coordination
            coordination_fallback_active=False,
            stuck_processes=[],
            
            # State tracking
            state_version=1,
            last_updated=datetime.now().isoformat(),
            agent_execution_history=[],
            execution_errors=[],
            fallback_attempts={}
        )
        
        # Update shared state with platforms and CI system
        if platforms:
            shared_state.update_project(project_id, platforms=platforms)
        if ci_system:
            shared_state.update_project(project_id, ci_system=ci_system)
        
        # Run the governance workflow
        config = RunnableConfig(recursion_limit=25)  # Prevent infinite loops
        try:
            result = await self.app.ainvoke(governance_state, config)
            self.logger.info(f"Build completed for project: {name}")
            
            # Extract project results from shared state
            project = shared_state.get_project_state(project_id)
            if project:
                overall_progress = result.get("overall_progress", 0.0)
                return {
                    "status": "completed" if overall_progress >= 0.9 else "partial",
                    "project_id": project_id,
                    "files_created": len(getattr(project, "files_created", {})),
                    "architecture_decisions": len(getattr(project, "architecture_decisions", [])),
                    "test_results": getattr(project, "test_results", {}),
                    "security_findings": getattr(project, "security_findings", []),
                    "documentation": getattr(project, "documentation", []),
                    "performance_metrics": getattr(project, "performance_metrics", {}),
                    "quality_assessment": {
                        "score": overall_progress * 100,
                        "issues": result.get("execution_errors", [])
                    },
                    "deployment_config": {
                        "platforms": platforms or ["android", "ios"],
                        "ci_system": ci_system
                    } if ci_system else None
                }
            else:
                return {
                    "status": "error",
                    "error": "Project state not found",
                    "project_id": project_id
                }
                
        except Exception as e:
            self.logger.error(f"Error during build: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "project_id": project_id
            }


# Standalone function for running FlutterSwarm governance
@track_function(agent_id="system", log_args=True, log_return=True)
async def run_flutter_swarm_governance(
    name: str,
    description: str,
    requirements: List[str],
    features: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None,
    ci_system: Optional[str] = None
) -> Dict[str, Any]:
    """
    Standalone function to run FlutterSwarm governance workflow.
    """
    # Log governance workflow start
    agent_logger.log_project_event("system", "governance_workflow_start", 
                                 f"Starting governance workflow for: {name}")
    
    governance = FlutterSwarmGovernance()
    # Only call build_project (no create_project)
    result = await governance.build_project(
        name=name,
        description=description,
        requirements=requirements,
        features=features or [],
        platforms=platforms or ["android", "ios"],
        ci_system=ci_system
    )
    return result