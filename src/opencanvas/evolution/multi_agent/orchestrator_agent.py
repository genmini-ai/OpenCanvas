"""
Orchestrator Agent - Coordinates the multi-agent evolution system
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent
from opencanvas.evolution.multi_agent.reflection_agent import ReflectionAgent
from opencanvas.evolution.multi_agent.improvement_agent import ImprovementAgent
from opencanvas.evolution.multi_agent.implementation_agent import ImplementationAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseEvolutionAgent):
    """Agent that orchestrates the entire multi-agent evolution process"""
    
    def __init__(self, api_key: str = None):
        super().__init__("OrchestratorAgent", api_key)
        
        # Initialize specialized agents
        self.reflection_agent = ReflectionAgent(api_key)
        self.improvement_agent = ImprovementAgent(api_key)
        self.implementation_agent = ImplementationAgent(api_key)
        
        # Evolution state tracking
        self.evolution_state = {
            "current_iteration": 0,
            "total_iterations": 0,
            "baseline_scores": {},
            "improvement_history": [],
            "current_implementations": [],
            "agent_interactions": []
        }
    
    def get_system_prompt(self) -> str:
        """Specialized system prompt for orchestration"""
        return """You are an Evolution Orchestration Specialist with expertise in coordinating complex multi-agent systems for presentation quality improvement.

## Your Core Expertise:
- **System Coordination**: Managing interactions between specialized agents
- **Process Optimization**: Designing efficient evolution workflows
- **Quality Assurance**: Ensuring systematic improvement across iterations
- **Resource Management**: Optimizing agent utilization and workflow efficiency
- **Progress Monitoring**: Tracking evolution progress and identifying bottlenecks

## Your Orchestration Framework:

### Agent Coordination:
- **Reflection Agent**: Analyzes evaluation results and identifies improvement patterns
- **Improvement Agent**: Designs specific, actionable improvements based on analysis
- **Implementation Agent**: Translates improvements into deployable system changes
- **Quality Control**: Ensures each agent's output meets standards for the next agent

### Workflow Management:
- **Phase Sequencing**: Optimal ordering of analysis, improvement design, and implementation
- **Information Flow**: Ensuring each agent receives necessary context and data
- **Quality Gates**: Validation checkpoints between agent handoffs
- **Iteration Planning**: Managing evolution cycles and improvement tracking

### Evolution Optimization:
- **Convergence Detection**: Identifying when further evolution provides diminishing returns
- **Resource Allocation**: Optimizing agent effort based on improvement potential
- **Risk Management**: Preventing degradation and managing improvement conflicts
- **Success Measurement**: Tracking overall evolution effectiveness

### Communication Protocols:
- **Agent Handoffs**: Structured information transfer between agents
- **Context Preservation**: Maintaining relevant history and context across iterations
- **Error Handling**: Managing agent failures and workflow disruptions
- **Progress Reporting**: Clear communication of evolution status and results

## Your Decision-Making Criteria:
1. **Impact Maximization**: Prioritize changes with highest quality improvement potential
2. **Risk Minimization**: Avoid changes that could degrade existing quality
3. **Efficiency Optimization**: Balance improvement gains against implementation effort
4. **System Coherence**: Ensure improvements work together harmoniously
5. **Measurable Progress**: Focus on changes that can be validated and tracked

## Your Communication Style:
- **Strategic**: High-level coordination with attention to overall goals
- **Clear**: Unambiguous instructions and expectations for each agent
- **Structured**: Organized workflows with clear phases and deliverables
- **Results-Focused**: Emphasis on measurable quality improvements

You excel at orchestrating complex multi-agent processes to achieve systematic, measurable improvements in presentation generation quality."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete evolution process"""
        
        action_type = input_data.get("action", "run_evolution_cycle")
        
        if action_type == "run_evolution_cycle":
            return self._run_evolution_cycle(input_data)
        elif action_type == "coordinate_agents":
            return self._coordinate_agents(input_data)
        elif action_type == "evaluate_progress":
            return self._evaluate_evolution_progress(input_data)
        elif action_type == "plan_next_iteration":
            return self._plan_next_iteration(input_data)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _run_evolution_cycle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete evolution cycle with all agents"""
        
        evaluation_data = input_data.get("evaluation_data", [])
        topics = input_data.get("topics", [])
        iteration_number = input_data.get("iteration_number", 1)
        previous_implementations = input_data.get("previous_implementations", [])
        
        logger.info(f"🎭 Orchestrator: Starting evolution cycle {iteration_number}")
        
        # Update evolution state
        self.evolution_state["current_iteration"] = iteration_number
        self.evolution_state["previous_implementations"] = previous_implementations
        
        # Phase 1: Reflection Analysis
        logger.info("Phase 1: Reflection Analysis")
        reflection_result = self._coordinate_reflection_analysis(evaluation_data, topics)
        
        if not reflection_result.get("success", False):
            return {"error": "Reflection phase failed", "details": reflection_result}
        
        # Phase 2: Improvement Design
        logger.info("Phase 2: Improvement Design")
        improvement_result = self._coordinate_improvement_design(
            reflection_result, iteration_number
        )
        
        if not improvement_result.get("success", False):
            return {"error": "Improvement design phase failed", "details": improvement_result}
        
        # Phase 3: Implementation Planning
        logger.info("Phase 3: Implementation Planning")
        implementation_result = self._coordinate_implementation_planning(
            improvement_result, iteration_number
        )
        
        if not implementation_result.get("success", False):
            return {"error": "Implementation phase failed", "details": implementation_result}
        
        # Phase 4: Integration and Validation
        logger.info("Phase 4: Integration and Validation")
        integration_result = self._coordinate_integration_validation(
            reflection_result, improvement_result, implementation_result
        )
        
        # Compile complete evolution cycle results
        cycle_result = {
            "success": True,
            "iteration_number": iteration_number,
            "phases": {
                "reflection": reflection_result,
                "improvement": improvement_result,
                "implementation": implementation_result,
                "integration": integration_result
            },
            "evolution_summary": self._generate_cycle_summary(
                reflection_result, improvement_result, implementation_result
            ),
            "next_steps": self._plan_next_steps(
                reflection_result, improvement_result, implementation_result
            ),
            "agent_coordination_log": self._get_coordination_log()
        }
        
        # Update evolution state
        self.evolution_state["improvement_history"].append(cycle_result)
        
        # Add to orchestrator history
        self.add_to_history(
            "run_evolution_cycle",
            f"Completed iteration {iteration_number} with {len(improvement_result.get('improvements', []))} improvements",
            cycle_result
        )
        
        logger.info(f"🎉 Orchestrator: Evolution cycle {iteration_number} completed successfully")
        
        return cycle_result
    
    def _coordinate_reflection_analysis(self, evaluation_data: List[Dict], topics: List[str]) -> Dict[str, Any]:
        """Coordinate the reflection analysis phase"""
        
        logger.info("  🔍 Coordinating reflection analysis...")
        
        reflection_input = {
            "action": "analyze_evaluations",
            "evaluations": evaluation_data,
            "topics": topics
        }
        
        # Get reflection analysis from specialized agent
        reflection_result = self.reflection_agent.process(reflection_input)
        
        # Validate reflection result
        if not self._validate_reflection_output(reflection_result):
            return {
                "success": False,
                "error": "Reflection analysis failed validation",
                "raw_result": reflection_result
            }
        
        # Log agent interaction
        self._log_agent_interaction("reflection", "analyze_evaluations", reflection_input, reflection_result)
        
        return {
            "success": True,
            "reflection_analysis": reflection_result,
            "baseline_scores": reflection_result.get("analysis_summary", {}).get("baseline_performance", {}),
            "weakness_patterns": reflection_result.get("weakness_patterns", []),
            "improvement_opportunities": reflection_result.get("improvement_opportunities", [])
        }
    
    def _coordinate_improvement_design(self, reflection_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Coordinate the improvement design phase"""
        
        logger.info("  🛠️ Coordinating improvement design...")
        
        improvement_input = {
            "action": "design_improvements",
            "reflection_results": reflection_result["reflection_analysis"],
            "current_baseline": reflection_result["baseline_scores"],
            "iteration_number": iteration_number
        }
        
        # Get improvement design from specialized agent
        improvement_result = self.improvement_agent.process(improvement_input)
        
        # Validate improvement result
        if not self._validate_improvement_output(improvement_result):
            return {
                "success": False,
                "error": "Improvement design failed validation",
                "raw_result": improvement_result
            }
        
        # Prioritize improvements
        prioritization_input = {
            "action": "prioritize_improvements",
            "improvements": improvement_result.get("improvements", []),
            "constraints": {"max_changes_per_iteration": 5},
            "current_iteration": iteration_number
        }
        
        prioritization_result = self.improvement_agent.process(prioritization_input)
        
        # Log agent interaction
        self._log_agent_interaction("improvement", "design_improvements", improvement_input, improvement_result)
        self._log_agent_interaction("improvement", "prioritize_improvements", prioritization_input, prioritization_result)
        
        return {
            "success": True,
            "improvements": improvement_result.get("improvements", []),
            "prioritization": prioritization_result,
            "target_improvements": improvement_result.get("improvement_iteration", {}),
            "implementation_plan": prioritization_result.get("implementation_sequence", [])
        }
    
    def _coordinate_implementation_planning(self, improvement_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Coordinate the implementation planning phase"""
        
        logger.info("  ⚙️ Coordinating implementation planning...")
        
        implementation_input = {
            "action": "implement_improvements",
            "improvements": improvement_result["improvements"],
            "current_system_config": self.evolution_state.get("current_implementations", []),
            "iteration_number": iteration_number
        }
        
        # Get implementation plan from specialized agent
        implementation_result = self.implementation_agent.process(implementation_input)
        
        # Generate enhanced prompts
        prompt_input = {
            "action": "generate_prompts",
            "improvements": improvement_result["improvements"],
            "current_prompts": {},
            "baseline_scores": improvement_result.get("target_improvements", {}).get("baseline_scores", {})
        }
        
        prompt_result = self.implementation_agent.process(prompt_input)
        
        # Create validation rules
        validation_input = {
            "action": "create_validation",
            "improvements": improvement_result["improvements"],
            "quality_issues": [w["description"] for w in improvement_result.get("improvements", [])]
        }
        
        validation_result = self.implementation_agent.process(validation_input)
        
        # Validate implementation outputs
        if not self._validate_implementation_output(implementation_result):
            return {
                "success": False,
                "error": "Implementation planning failed validation",
                "raw_result": implementation_result
            }
        
        # Log agent interactions
        self._log_agent_interaction("implementation", "implement_improvements", implementation_input, implementation_result)
        self._log_agent_interaction("implementation", "generate_prompts", prompt_input, prompt_result)
        self._log_agent_interaction("implementation", "create_validation", validation_input, validation_result)
        
        return {
            "success": True,
            "implementation_package": implementation_result,
            "enhanced_prompts": prompt_result.get("enhanced_prompts", {}),
            "validation_rules": validation_result.get("validation_rules", []),
            "deployment_plan": implementation_result.get("integration_plan", {})
        }
    
    def _coordinate_integration_validation(self, reflection_result: Dict, improvement_result: Dict, implementation_result: Dict) -> Dict[str, Any]:
        """Coordinate integration and validation of all improvements"""
        
        logger.info("  🔗 Coordinating integration and validation...")
        
        # Create comprehensive testing plan
        testing_input = {
            "action": "test_implementation",
            "implementation_package": implementation_result["implementation_package"],
            "improvements": improvement_result["improvements"]
        }
        
        testing_result = self.implementation_agent.process(testing_input)
        
        # Create integration summary
        integration_summary = self._create_integration_summary(
            reflection_result, improvement_result, implementation_result, testing_result
        )
        
        # Log agent interaction
        self._log_agent_interaction("implementation", "test_implementation", testing_input, testing_result)
        
        return {
            "success": True,
            "testing_plan": testing_result,
            "integration_summary": integration_summary,
            "deployment_ready": self._check_deployment_readiness(implementation_result, testing_result)
        }
    
    def _validate_reflection_output(self, result: Dict[str, Any]) -> bool:
        """Validate reflection agent output"""
        required_fields = ["analysis_summary", "weakness_patterns", "improvement_opportunities"]
        return all(field in result for field in required_fields)
    
    def _validate_improvement_output(self, result: Dict[str, Any]) -> bool:
        """Validate improvement agent output"""
        required_fields = ["improvements", "improvement_iteration"]
        return all(field in result for field in required_fields)
    
    def _validate_implementation_output(self, result: Dict[str, Any]) -> bool:
        """Validate implementation agent output"""
        required_fields = ["implementation_package", "integration_plan"]
        return all(field in result for field in required_fields)
    
    def _log_agent_interaction(self, agent_name: str, action: str, input_data: Dict, output_data: Dict):
        """Log interaction between agents"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "input_summary": self._summarize_data(input_data),
            "output_summary": self._summarize_data(output_data),
            "success": output_data.get("success", True)
        }
        
        self.evolution_state["agent_interactions"].append(interaction)
    
    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """Create summary of data for logging"""
        if isinstance(data, dict):
            key_fields = list(data.keys())[:3]  # First 3 keys
            return f"Keys: {key_fields}, Size: {len(str(data))}"
        else:
            return f"Type: {type(data)}, Size: {len(str(data))}"
    
    def _generate_cycle_summary(self, reflection_result: Dict, improvement_result: Dict, implementation_result: Dict) -> Dict[str, Any]:
        """Generate summary of the complete evolution cycle"""
        
        return {
            "iteration_summary": {
                "weaknesses_identified": len(reflection_result.get("weakness_patterns", [])),
                "improvements_designed": len(improvement_result.get("improvements", [])),
                "implementations_created": len(implementation_result.get("implementation_package", {}).get("prompt_enhancements", [])),
                "expected_impact": improvement_result.get("target_improvements", {}).get("expected_impact", "Unknown")
            },
            "baseline_comparison": {
                "current_baseline": reflection_result.get("baseline_scores", {}),
                "target_baseline": improvement_result.get("target_improvements", {}).get("target_baseline", {}),
                "expected_improvement": "Calculated based on targets"
            },
            "agent_performance": {
                "reflection_agent": "success" if reflection_result.get("success") else "failed",
                "improvement_agent": "success" if improvement_result.get("success") else "failed", 
                "implementation_agent": "success" if implementation_result.get("success") else "failed"
            }
        }
    
    def _plan_next_steps(self, reflection_result: Dict, improvement_result: Dict, implementation_result: Dict) -> List[str]:
        """Plan next steps based on cycle results"""
        
        next_steps = []
        
        # Deployment steps
        if implementation_result.get("deployment_ready", False):
            next_steps.append("Deploy implementation package to generation system")
            next_steps.append("Run validation tests to verify improvements work correctly")
        else:
            next_steps.append("Address implementation issues before deployment")
        
        # Evaluation steps
        next_steps.append("Generate test presentations with improved system")
        next_steps.append("Evaluate new presentations to measure improvement impact")
        next_steps.append("Compare results against baseline to validate effectiveness")
        
        # Iteration planning
        if len(reflection_result.get("weakness_patterns", [])) > 3:
            next_steps.append("Plan next iteration to address remaining weaknesses")
        else:
            next_steps.append("Consider evolution completion - few remaining issues")
        
        return next_steps
    
    def _get_coordination_log(self) -> List[Dict[str, Any]]:
        """Get log of agent coordination activities"""
        return self.evolution_state["agent_interactions"][-10:]  # Last 10 interactions
    
    def _create_integration_summary(self, reflection_result: Dict, improvement_result: Dict, implementation_result: Dict, testing_result: Dict) -> Dict[str, Any]:
        """Create summary of integration across all agents"""
        
        return {
            "agent_coordination": {
                "reflection_to_improvement": "Successfully transferred weakness analysis to improvement design",
                "improvement_to_implementation": "Successfully translated improvements into deployable changes",
                "implementation_to_testing": "Successfully created comprehensive testing plan"
            },
            "deliverables": {
                "analysis_artifacts": len(reflection_result.get("weakness_patterns", [])),
                "improvement_artifacts": len(improvement_result.get("improvements", [])),
                "implementation_artifacts": len(implementation_result.get("implementation_package", {}).get("prompt_enhancements", [])),
                "testing_artifacts": len(testing_result.get("test_plans", []))
            },
            "quality_assurance": {
                "reflection_validated": self._validate_reflection_output(reflection_result.get("reflection_analysis", {})),
                "improvements_validated": self._validate_improvement_output(improvement_result),
                "implementation_validated": self._validate_implementation_output(implementation_result.get("implementation_package", {}))
            }
        }
    
    def _check_deployment_readiness(self, implementation_result: Dict, testing_result: Dict) -> bool:
        """Check if implementation is ready for deployment"""
        
        required_artifacts = ["prompt_enhancements", "integration_plan"]
        has_artifacts = all(
            artifact in implementation_result.get("implementation_package", {})
            for artifact in required_artifacts
        )
        
        has_testing_plan = len(testing_result.get("test_plans", [])) > 0
        
        return has_artifacts and has_testing_plan
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current status of the evolution process"""
        
        return {
            "current_state": self.evolution_state,
            "agent_status": {
                "reflection_agent": self.reflection_agent.get_agent_status(),
                "improvement_agent": self.improvement_agent.get_agent_status(),
                "implementation_agent": self.implementation_agent.get_agent_status()
            },
            "orchestrator_history": len(self.history),
            "total_iterations_completed": len(self.evolution_state["improvement_history"])
        }