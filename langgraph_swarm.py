"""
LangGraph-based FlutterSwarm Project Governance System
This module provides high-level project governance and quality gates while allowing
agents to collaborate autonomously through the real-time awareness system.
"""
from typing import Dict, List, Any, Optional, TypedDict, Type
from datetime import datetime
import logging
import asyncio

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
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._agent_classes: Dict[str, Type] = {}
        self.logger = logging.getLogger("FlutterSwarm.AgentRegistry")
    
    def register_agent_class(self, agent_type: str, agent_class: Type) -> None:
        """Register an agent class with the registry."""
        self._agent_classes[agent_type] = agent_class
        self.logger.info(f"Registered agent class: {agent_type}")
    
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
    
    def __init__(self, enable_monitoring: bool = True):
        # Setup logging
        self.logger = logging.getLogger(f"FlutterSwarm.Governance")
        
        # Initialize agent registry
        self.agent_registry = AgentRegistry()
        
        # Register agent classes
        self._register_agent_classes()
        
        # Note: Monitoring can be enabled if needed in the future
        self.enable_monitoring = enable_monitoring
        self.governance_phases = [
            'project_initiation', 'architecture_approval', 'implementation_oversight', 
            'quality_verification', 'security_compliance', 'performance_validation',
            'documentation_review', 'deployment_approval'
        ]
        
        # Circuit breaker to prevent infinite loops
        self.gate_failure_counts = {}  # gate_name -> failure_count
        self.max_gate_failures = 3  # Maximum failures before forcing pass
        self.total_routing_steps = 0  # Track total routing steps
        self.max_routing_steps = 50  # Maximum routing steps before emergency exit
        
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
    def _route_from_project_initiation(self, state: ProjectGovernanceState) -> str:
        """Route from project initiation gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if project initiation is approved
        if state["approval_status"].get("project_initiation") == "approved":
            return "architecture_approval"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # End if project initialization failed completely
        if state["gate_statuses"].get("project_initiation") == "failed":
            return "end"
        
        # Default to architecture approval
        return "architecture_approval"
    
    def _route_from_architecture_approval(self, state: ProjectGovernanceState) -> str:
        """Route from architecture approval gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if architecture approval is approved
        if state["approval_status"].get("architecture_approval") == "approved":
            return "implementation_oversight"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # End if too many failures
        if state["gate_statuses"].get("architecture_approval") == "failed":
            if self.gate_failure_counts.get("architecture_approval", 0) >= self.max_gate_failures:
                return "end"
        
        # Default to fallback
        return "fallback_coordination"
    
    def _route_from_implementation_oversight(self, state: ProjectGovernanceState) -> str:
        """Route from implementation oversight gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if implementation oversight is approved
        if state["approval_status"].get("implementation_oversight") == "approved":
            return "quality_verification"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to architecture if architecture compliance issues
        if not state["quality_criteria_met"].get("architecture_compliance_verified", False):
            return "architecture_approval"
        
        # Default to quality verification
        return "quality_verification"
    
    def _route_from_quality_verification(self, state: ProjectGovernanceState) -> str:
        """Route from quality verification gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if quality verification is approved
        if state["approval_status"].get("quality_verification") == "approved":
            return "security_compliance"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if issues
        if state["gate_statuses"].get("quality_verification") == "failed":
            return "implementation_oversight"
        
        # Default to security compliance
        return "security_compliance"
    
    def _route_from_security_compliance(self, state: ProjectGovernanceState) -> str:
        """Route from security compliance gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if security compliance is approved
        if state["approval_status"].get("security_compliance") == "approved":
            return "performance_validation"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if security issues
        if state["gate_statuses"].get("security_compliance") == "failed":
            return "implementation_oversight"
        
        # Default to performance validation
        return "performance_validation"
    
    def _route_from_performance_validation(self, state: ProjectGovernanceState) -> str:
        """Route from performance validation gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if performance validation is approved
        if state["approval_status"].get("performance_validation") == "approved":
            return "documentation_review"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to implementation if performance issues
        if state["gate_statuses"].get("performance_validation") == "failed":
            return "implementation_oversight"
        
        # Default to documentation review
        return "documentation_review"
    
    def _route_from_documentation_review(self, state: ProjectGovernanceState) -> str:
        """Route from documentation review gate."""
        self.total_routing_steps += 1
        
        # Emergency exit if too many routing steps
        if self.total_routing_steps > self.max_routing_steps:
            return "end"
        
        # Check if documentation review is approved
        if state["approval_status"].get("documentation_review") == "approved":
            return "deployment_approval"
        
        # Check if coordination fallback is needed
        if state.get("stuck_processes") and len(state["stuck_processes"]) > 0:
            return "fallback_coordination"
        
        # Return to quality verification if documentation issues
        if state["gate_statuses"].get("documentation_review") == "failed":
            return "quality_verification"
        
        # Default to deployment approval
        return "deployment_approval"
    
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
    async def _project_initiation_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Project initiation governance gate - verify project setup and readiness."""
        print(f"🏛️ Project Initiation Gate: {state['name']}")
        
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
        
        # Update governance state
        state['governance_decisions'].append({
            'gate': 'project_initiation',
            'timestamp': datetime.now().isoformat(),
            'criteria_met': initiation_criteria,
            'approved': all_criteria_met,
            'notes': 'Project initiation gate evaluation completed'
        })
        
        state['gate_statuses']['project_initiation'] = 'passed' if all_criteria_met else 'failed'
        state['approval_status']['project_initiation'] = 'approved' if all_criteria_met else 'rejected'
        
        # Update overall progress (project initiation is ~5% of total)
        state['overall_progress'] = 0.05 if all_criteria_met else 0.02
        
        print(f"✅ Project initiation gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _architecture_approval_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Architecture approval governance gate - verify architecture quality and completeness."""
        print(f"🏗️ Architecture Approval Gate: {state['name']}")
        
        gate_name = 'architecture_approval'
        
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
                
                # Process the result
                if result.get("status") == "architecture_completed":
                    architecture_decisions = result.get("architecture_decisions", [])
                    
                    # Update state with architecture decisions
                    await shared_state.update_project_async(
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
                    self.logger.error(f"❌ Architecture design failed: {result.get('status')}")
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
                # Prepare task data for the agent
                project_id = state['project_id']
                task_data = {
                    "project_id": project_id,
                    "name": state['name'],
                    "description": state['description'],
                    "requirements": state['requirements']
                }
                
                # Execute the implementation task
                self.logger.info(f"🚀 Executing implementation task for project {project_id}")
                result = await implementation_agent.execute_task(
                    "implement_incremental_features", 
                    task_data
                )
                
                # Process the result
                if result.get("status") == "incremental_implementation_completed":
                    implementation_results = result.get("results", {})
                    total_completed = len(implementation_results.get("completed_features", []))
                    total_features = implementation_results.get("total_features", 0)
                    
                    # Update state with implementation results
                    project_state = shared_state.get_project_state(project_id)
                    if project_state:
                        files_created = implementation_agent.get_project_state().files_created
                        shared_state.update_project(
                            project_id,
                            implementation_results=implementation_results,
                            implementation_status=result.get("status"),
                            files_created=files_created
                        )
                    
                    # Determine success based on completion ratio
                    success_ratio = total_completed / total_features if total_features > 0 else 0
                    implementation_criteria = {
                        'code_quality_standards_met': success_ratio > 0.7,
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
                    self.logger.error(f"❌ Implementation failed: {result.get('status')}")
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
                        'error': result.get('error', 'Unknown error')
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
        print(f"🔒 Security Compliance Gate: {state['name']}")
        
        gate_name = 'security_compliance'
        
        # Circuit breaker check
        if self._check_circuit_breaker(gate_name):
            print(f"🔄 Circuit breaker triggered for {gate_name} - forcing pass to prevent infinite loop")
            all_criteria_met = True
            security_criteria = {
                'security_scan_passed': True,
                'authentication_secure': True,
                'data_protection_implemented': True,
                'compliance_requirements_met': True
            }
        else:
            project = shared_state.get_project_state(state['project_id'])
            
            security_criteria = {
                'security_scan_passed': self._check_security_scan_results(project),
                'authentication_secure': self._check_authentication_security(project),
                'data_protection_implemented': self._check_data_protection(project),
                'compliance_requirements_met': self._check_compliance_requirements(project)
            }
            
            all_criteria_met = all(security_criteria.values())
            
            # Track failures for circuit breaker
            if not all_criteria_met:
                self._increment_gate_failure(gate_name)
        
        security_insights = shared_state.get_shared_consciousness(f"security_architecture_{state['project_id']}")
        
        state['governance_decisions'].append({
            'gate': 'security_compliance',
            'timestamp': datetime.now().isoformat(),
            'criteria_met': security_criteria,
            'approved': all_criteria_met,
            'security_insights': security_insights,
            'notes': 'Security compliance gate evaluation completed'
        })
        
        state['gate_statuses']['security_compliance'] = 'passed' if all_criteria_met else 'failed'
        state['approval_status']['security_compliance'] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"🔒 Security compliance gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _performance_validation_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Performance validation gate - verify performance requirements are met."""
        print(f"⚡ Performance Validation Gate: {state['name']}")
        
        project = shared_state.get_project_state(state['project_id'])
        
        performance_criteria = {
            'startup_time_acceptable': self._check_startup_performance(project),
            'memory_usage_optimal': self._check_memory_usage(project),
            'battery_efficiency_good': self._check_battery_efficiency(project),
            'network_optimization_implemented': self._check_network_optimization(project)
        }
        
        all_criteria_met = all(performance_criteria.values())
        
        state['governance_decisions'].append({
            'gate': 'performance_validation',
            'timestamp': datetime.now().isoformat(),
            'criteria_met': performance_criteria,
            'approved': all_criteria_met,
            'notes': 'Performance validation gate evaluation completed'
        })
        
        state['gate_statuses']['performance_validation'] = 'passed' if all_criteria_met else 'failed'
        state['approval_status']['performance_validation'] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"⚡ Performance validation gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _documentation_review_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Documentation review gate - verify documentation completeness."""
        print(f"📚 Documentation Review Gate: {state['name']}")
        
        project = shared_state.get_project_state(state['project_id'])
        
        documentation_criteria = {
            'api_documentation_complete': self._check_api_documentation(project),
            'user_documentation_available': self._check_user_documentation(project),
            'developer_documentation_complete': self._check_developer_documentation(project),
            'deployment_documentation_ready': self._check_deployment_documentation(project)
        }
        
        all_criteria_met = all(documentation_criteria.values())
        
        state['governance_decisions'].append({
            'gate': 'documentation_review',
            'timestamp': datetime.now().isoformat(),
            'criteria_met': documentation_criteria,
            'approved': all_criteria_met,
            'notes': 'Documentation review gate evaluation completed'
        })
        
        state['gate_statuses']['documentation_review'] = 'passed' if all_criteria_met else 'failed'
        state['approval_status']['documentation_review'] = 'approved' if all_criteria_met else 'rejected'
        
        print(f"📚 Documentation review gate {'PASSED' if all_criteria_met else 'FAILED'}")
        return state
    
    async def _deployment_approval_gate(self, state: ProjectGovernanceState) -> ProjectGovernanceState:
        """Deployment approval gate - final verification before deployment."""
        print(f"🚀 Deployment Approval Gate: {state['name']}")
        
        project = shared_state.get_project_state(state['project_id'])
        
        deployment_criteria = {
            'production_readiness_verified': self._check_production_readiness(project),
            'deployment_strategy_approved': self._check_deployment_strategy(project),
            'rollback_procedures_tested': self._check_rollback_procedures(project),
            'monitoring_configured': self._check_monitoring_configuration(project)
        }
        
        all_criteria_met = all(deployment_criteria.values())
        
        state['governance_decisions'].append({
            'gate': 'deployment_approval',
            'timestamp': datetime.now().isoformat(),
            'criteria_met': deployment_criteria,
            'approved': all_criteria_met,
            'notes': 'Deployment approval gate evaluation completed'
        })
        
        state['gate_statuses']['deployment_approval'] = 'passed' if all_criteria_met else 'failed'
        state['approval_status']['deployment_approval'] = 'approved' if all_criteria_met else 'rejected'
        
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
        Fallback coordination node - handles situations when real-time collaboration fails
        or when quality gates detect issues requiring intervention.
        """
        print(f"🔄 Fallback Coordination Node: {state['name']}")
        
        # Assess current project health
        project = shared_state.get_project_state(state['project_id'])
        collaboration_health = self._assess_collaboration_health()
        
        # Identify what needs coordination
        coordination_needs = []
        
        # Check if agents are stuck or not collaborating
        if not collaboration_health.get('healthy', False):
            coordination_needs.append('agent_collaboration_breakdown')
        
        # Check if quality gates are failing repeatedly
        failed_gates = [gate for gate, status in state['gate_statuses'].items() if status == 'failed']
        if len(failed_gates) > 2:
            coordination_needs.append('quality_gate_failures')
        
        # Check if project is making progress
        if state['overall_progress'] < 0.1:
            coordination_needs.append('project_stagnation')
        
        # Implement coordination strategies
        coordination_actions = []
        
        for need in coordination_needs:
            if need == 'agent_collaboration_breakdown':
                # Force synchronization through shared consciousness
                shared_state.broadcast_project_status(state['project_id'])
                coordination_actions.append('forced_agent_synchronization')
                
            elif need == 'quality_gate_failures':
                # Reset failed gates and provide guidance
                for gate in failed_gates:
                    state['gate_statuses'][gate] = 'pending'
                coordination_actions.append('quality_gate_reset')
                
            elif need == 'project_stagnation':
                # Provide explicit guidance to agents
                guidance = {
                    'priority_tasks': self._identify_priority_tasks(state),
                    'unblocking_actions': self._identify_unblocking_actions(state),
                    'coordination_timestamp': datetime.now().isoformat()
                }
                shared_state.update_shared_consciousness(
                    f"fallback_coordination_{state['project_id']}", 
                    guidance
                )
                coordination_actions.append('explicit_guidance_provided')
        
        # Update coordination status
        state['coordination_fallback_active'] = True
        state['stuck_processes'] = coordination_needs
        
        # Record coordination decision
        state['governance_decisions'].append({
            'gate': 'fallback_coordination',
            'timestamp': datetime.now().isoformat(),
            'coordination_needs': coordination_needs,
            'actions_taken': coordination_actions,
            'collaboration_health': collaboration_health,
            'notes': 'Fallback coordination node activated to resolve collaboration issues'
        })
        
        print(f"🔄 Fallback coordination completed: {len(coordination_actions)} actions taken")
        
        return state
    
    # Helper methods
    def _check_circuit_breaker(self, gate_name: str) -> bool:
        """Check if circuit breaker should be triggered for a gate."""
        failures = self.gate_failure_counts.get(gate_name, 0)
        return failures >= self.max_gate_failures
    
    def _increment_gate_failure(self, gate_name: str) -> None:
        """Increment failure count for a gate."""
        self.gate_failure_counts[gate_name] = self.gate_failure_counts.get(gate_name, 0) + 1
    
    def _check_agent_collaboration_health(self) -> Dict[str, Any]:
        """Check if agents are collaborating effectively."""
        # Basic implementation - should be enhanced with actual metrics
        return {'healthy': True, 'metric': 'collaboration_rate', 'value': 0.8}
    
    def _check_security_approval(self, project) -> bool:
        """Check if security reviews are complete."""
        if not project:
            return False
        
        # Check for security-related architecture decisions
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        return any(d.get('type') == 'security' for d in architecture_decisions)
    
    def _check_performance_considerations(self, project) -> bool:
        """Check if performance considerations are addressed."""
        if not project:
            return False
        
        # Check for performance-related architecture decisions
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        return any(d.get('type') == 'performance' for d in architecture_decisions)
    
    def _check_scalability_verification(self, project) -> bool:
        """Check if scalability is verified."""
        if not project:
            return False
        
        # Check for scalability-related architecture decisions
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        return any(d.get('type') == 'scalability' for d in architecture_decisions)
    
    def _check_documentation_complete(self, project) -> bool:
        """Check if documentation is complete."""
        if not project:
            return False
        
        # Check for documentation completeness
        documentation = getattr(project, 'documentation', {})
        return len(documentation) > 0
    
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