"""
Unified Evolution Agent System - Single agent class with type-based behavior
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import Anthropic

from opencanvas.config import Config
from opencanvas.evolution.config.agent_prompts import AGENT_PROMPTS, AGENT_ACTIONS, AGENT_CONFIG
from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts

logger = logging.getLogger(__name__)

class EvolutionAgent:
    """
    Unified agent that can act as any evolution specialist based on agent_type
    """
    
    def __init__(self, agent_type: str, api_key: str = None, model: str = None):
        """Initialize evolution agent with specific type"""
        
        if agent_type not in AGENT_PROMPTS:
            raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {list(AGENT_PROMPTS.keys())}")
        
        self.agent_type = agent_type
        self.name = f"{agent_type.title()} Agent"
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.model = model or AGENT_CONFIG["model"]
        
        if not self.api_key:
            raise ValueError(f"API key required for {self.name}")
        
        self.client = Anthropic(api_key=self.api_key)
        self.system_prompt = AGENT_PROMPTS[agent_type]
        self.valid_actions = AGENT_ACTIONS[agent_type]
        self.history = []
        
        logger.info(f"✅ {self.name} initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input using agent-specific logic"""
        
        action = input_data.get("action")
        if action not in self.valid_actions:
            return {
                "success": False,
                "error": f"{self.name} cannot perform action '{action}'. Valid actions: {self.valid_actions}"
            }
        
        logger.info(f"🤖 {self.name} processing action: {action}")
        
        try:
            # Route to agent-specific processing
            if self.agent_type == "reflection":
                return self._process_reflection(input_data)
            elif self.agent_type == "improvement":
                return self._process_improvement(input_data)
            elif self.agent_type == "implementation":
                return self._process_implementation(input_data)
            elif self.agent_type == "orchestrator":
                return self._process_orchestration(input_data)
            else:
                return {"success": False, "error": f"Unknown agent type: {self.agent_type}"}
                
        except Exception as e:
            logger.error(f"❌ {self.name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type,
                "action": action
            }
    
    def _process_reflection(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reflection-specific actions"""
        
        action = input_data.get("action")
        
        if action == "analyze_evaluations":
            return self._analyze_evaluations(input_data)
        elif action == "compare_iterations":
            return self._compare_iterations(input_data)
        elif action == "identify_root_causes":
            return self._identify_root_causes(input_data)
        else:
            return self._generic_reflection_process(input_data)
    
    def _process_improvement(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process improvement-specific actions"""
        
        action = input_data.get("action")
        
        if action == "design_improvements":
            return self._design_improvements(input_data)
        elif action == "prioritize_improvements":
            return self._prioritize_improvements(input_data)
        else:
            return self._generic_improvement_process(input_data)
    
    def _process_implementation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process implementation-specific actions"""
        
        action = input_data.get("action")
        
        if action == "implement_improvements":
            return self._implement_improvements(input_data)
        elif action == "propose_tools":
            return self._propose_tools(input_data)
        else:
            return self._generic_implementation_process(input_data)
    
    def _process_orchestration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestration-specific actions"""
        
        action = input_data.get("action")
        
        if action == "run_evolution_cycle":
            return self._run_evolution_cycle(input_data)
        elif action == "coordinate_agents":
            return self._coordinate_agents(input_data)
        else:
            return self._generic_orchestration_process(input_data)
    
    def _analyze_evaluations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze evaluation results to identify patterns"""
        
        evaluations = input_data.get("evaluations", [])
        topics = input_data.get("topics", [])
        
        # Get registry context for the reflection agent
        registry_context = self._get_tool_context()
        
        evaluations_json = json.dumps(evaluations, indent=2)
        topics_str = str(topics)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_ANALYZE_EVALUATIONS',
            evaluations_json=evaluations_json,
            topics_str=topics_str,
            registry_context=registry_context
        )

        result = self._call_claude(prompt)
        
        # Log key reflection findings with new structure
        if isinstance(result, dict):
            logger.info("📊 REFLECTION ANALYSIS RESULTS:")
            
            # Log baseline performance
            if "baseline_performance" in result:
                baseline = result["baseline_performance"]
                logger.info(f"  📈 Baseline Performance:")
                logger.info(f"    - Visual: {baseline.get('visual', 0):.2f}/5.0")
                logger.info(f"    - Content Free: {baseline.get('content_free', 0):.2f}/5.0")
                logger.info(f"    - Content Required: {baseline.get('content_required', 0):.2f}/5.0")
                logger.info(f"    - Overall: {baseline.get('overall', 0):.2f}/5.0")
            
            # Log identified gaps with reasoning
            if "identified_gaps" in result:
                gaps = result['identified_gaps']
                logger.info(f"  🔍 Identified {len(gaps)} gaps:")
                for gap in gaps[:3]:  # Log top 3
                    logger.info(f"    - {gap.get('description', 'Unknown gap')}")
                    logger.info(f"      Score: {gap.get('current_score', 0):.2f} → {gap.get('target_score', 0):.2f}")
                    logger.info(f"      Solution: {gap.get('solution_type', 'unknown')} - {gap.get('solution_rationale', 'No rationale')[:100]}...")
            
            # Log routing summary
            if "routing_summary" in result:
                routing = result["routing_summary"]
                logger.info(f"  🚦 Routing Summary:")
                logger.info(f"    - Prompt gaps: {len(routing.get('prompt_gaps', []))}")
                logger.info(f"    - Tool gaps: {len(routing.get('tool_gaps', []))}")
                logger.info(f"    - Both needed: {len(routing.get('both_gaps', []))}")
            
            # Keep backward compatibility - check for old structure too
            if "weakness_patterns" in result:
                logger.info(f"  🔴 Weaknesses found (old format): {len(result['weakness_patterns'])} patterns")
                for pattern in result.get('weakness_patterns', [])[:3]:  # Log top 3
                    logger.info(f"    - {pattern.get('dimension', 'Unknown')}: {pattern.get('avg_score', 0):.2f}/5.0")
            
            if "missing_tools" in result:
                logger.info(f"  🔧 Missing tools identified: {len(result['missing_tools'])}")
                for tool in result.get('missing_tools', [])[:3]:  # Log top 3
                    logger.info(f"    - {tool}")
            
            if "missing_capabilities" in result:
                logger.info(f"  ⚠️  Missing capabilities: {len(result['missing_capabilities'])}")
                for cap in result.get('missing_capabilities', [])[:3]:
                    logger.info(f"    - {cap}")
            
            if "opportunities" in result:
                logger.info(f"  💡 Improvement opportunities: {len(result['opportunities'])}")
                for opp in result.get('opportunities', [])[:3]:
                    sol_type = opp.get('solution_type', 'unknown')
                    logger.info(f"    - {opp.get('area', 'Unknown')} ({sol_type})")
        
        # Add to history
        self._add_to_history("analyze_evaluations", input_data, result)
        
        return {
            "success": True,
            "action": "analyze_evaluations",
            "agent_type": self.agent_type,
            **result
        }
    
    def _design_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design specific improvements based on reflection results"""
        
        reflection_results = input_data.get("reflection_results", {})
        current_baseline = input_data.get("current_baseline", {})
        iteration_number = input_data.get("iteration_number", 1)
        
        reflection_json = json.dumps(reflection_results, indent=2)
        baseline_json = json.dumps(current_baseline, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_DESIGN_IMPROVEMENTS',
            iteration_number=iteration_number,
            reflection_json=reflection_json,
            baseline_json=baseline_json
        )


        result = self._call_claude(prompt)
        
        # Log improvement proposals
        if isinstance(result, dict):
            logger.info("🛠️ IMPROVEMENT DESIGN RESULTS:")
            if "improvements" in result:
                logger.info(f"  📋 Improvements designed: {len(result['improvements'])}")
                for imp in result.get('improvements', [])[:5]:  # Log top 5
                    imp_type = imp.get('solution_type', 'unknown')
                    logger.info(f"    - {imp.get('name', 'Unknown')} ({imp_type})")
                    logger.info(f"      Description: {imp.get('description', 'N/A')[:100]}...")
        
        # Add to history
        self._add_to_history("design_improvements", input_data, result)
        
        return {
            "success": True,
            "action": "design_improvements",
            "agent_type": self.agent_type,
            **result
        }
    
    def _implement_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement designed improvements as deployable artifacts"""
        
        improvements = input_data.get("improvements", [])
        current_system_config = input_data.get("current_system_config", {})
        iteration_number = input_data.get("iteration_number", 1)
        
        # Get tool context with evaluation weaknesses and missing capabilities
        tool_context = self._get_tool_context(
            evaluation_weaknesses=input_data.get("weaknesses", []),
            missing_capabilities=input_data.get("missing_capabilities", [])
        )
        
        improvements_json = json.dumps(improvements, indent=2)
        config_json = json.dumps(current_system_config, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_IMPLEMENT_IMPROVEMENTS',
            iteration_number=iteration_number,
            improvements_json=improvements_json,
            config_json=config_json
        )


        result = self._call_claude(prompt)
        
        # Add to history
        self._add_to_history("implement_improvements", input_data, result)
        
        return {
            "success": True,
            "action": "implement_improvements", 
            "agent_type": self.agent_type,
            "implementation_package": result
        }
    
    def _run_evolution_cycle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate complete evolution cycle through all agents"""
        
        evaluation_data = input_data.get("evaluation_data", [])
        topics = input_data.get("topics", [])
        iteration_number = input_data.get("iteration_number", 1)
        previous_implementations = input_data.get("previous_implementations", [])
        
        logger.info(f"🎭 Orchestrating evolution cycle {iteration_number} with {len(evaluation_data)} evaluations")
        
        coordination_log = []
        phases = {}
        
        try:
            # Phase 1: Reflection
            logger.info("🔍 Phase 1: Reflection Analysis")
            logger.info(f"  📊 Analyzing {len(evaluation_data)} evaluation results")
            
            # Log what we're passing to reflection
            if evaluation_data:
                avg_scores = {}
                for eval in evaluation_data:
                    for key, val in eval.get('overall_scores', {}).items():
                        if key not in avg_scores:
                            avg_scores[key] = []
                        avg_scores[key].append(val)
                
                for key, vals in avg_scores.items():
                    if vals:
                        logger.info(f"  - Average {key}: {sum(vals)/len(vals):.2f}")
            
            reflection_agent = EvolutionAgent("reflection", self.api_key)
            
            reflection_result = reflection_agent.process({
                "action": "analyze_evaluations",
                "evaluations": evaluation_data,
                "topics": topics
            })
            
            phases["reflection"] = reflection_result
            coordination_log.append({
                "phase": "reflection",
                "agent": "reflection",
                "action": "analyze_evaluations", 
                "success": reflection_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            })
            
            if not reflection_result.get("success"):
                return self._handle_phase_failure("reflection", reflection_result, coordination_log)
            
            # Phase 2: Improvement Design
            logger.info("🛠️ Phase 2: Improvement Design")
            improvement_agent = EvolutionAgent("improvement", self.api_key)
            
            # Extract baseline from evaluation data
            current_baseline = self._extract_baseline_from_evaluations(evaluation_data)
            
            improvement_result = improvement_agent.process({
                "action": "design_improvements",
                "reflection_results": reflection_result,
                "current_baseline": current_baseline,
                "iteration_number": iteration_number
            })
            
            phases["improvement"] = improvement_result
            coordination_log.append({
                "phase": "improvement",
                "agent": "improvement", 
                "action": "design_improvements",
                "success": improvement_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            })
            
            if not improvement_result.get("success"):
                return self._handle_phase_failure("improvement", improvement_result, coordination_log)
            
            # Phase 3: Solution Routing based on gap types
            tool_proposals = []
            prompt_enhancements = []
            implementation_agent = EvolutionAgent("implementation", self.api_key)
            
            # Handle both new and old reflection structures
            identified_gaps = reflection_result.get("identified_gaps", [])
            routing_summary = reflection_result.get("routing_summary", {})
            
            # Fallback to old structure if new structure not present
            if not identified_gaps and "weakness_patterns" in reflection_result:
                logger.info("⚠️ Using old reflection structure format")
                # Convert old structure to new format
                weakness_patterns = reflection_result.get("weakness_patterns", [])
                identified_gaps = []
                for i, pattern in enumerate(weakness_patterns):
                    gap = {
                        "gap_id": f"gap_{i+1:03d}",
                        "description": pattern.get("description", "Unknown weakness"),
                        "dimension": pattern.get("dimension", "unknown"),
                        "current_score": pattern.get("avg_score", 0),
                        "target_score": pattern.get("improvement_potential", 4.0),
                        "solution_type": pattern.get("solution_type", "tool"),
                        "solution_rationale": pattern.get("solution_rationale", "Legacy format")
                    }
                    identified_gaps.append(gap)
                
                # Build routing summary from converted gaps
                routing_summary = {
                    "tool_gaps": [g["gap_id"] for g in identified_gaps if g["solution_type"] == "tool"],
                    "prompt_gaps": [g["gap_id"] for g in identified_gaps if g["solution_type"] == "prompt"],
                    "both_gaps": [g["gap_id"] for g in identified_gaps if g["solution_type"] == "both"]
                }
            
            # Use the routing summary for clear separation
            tool_gap_ids = routing_summary.get("tool_gaps", [])
            prompt_gap_ids = routing_summary.get("prompt_gaps", [])
            both_gap_ids = routing_summary.get("both_gaps", [])
            
            # Get the actual gap objects for routing
            tool_gaps = [g for g in identified_gaps if g.get("gap_id") in tool_gap_ids + both_gap_ids]
            prompt_gaps = [g for g in identified_gaps if g.get("gap_id") in prompt_gap_ids + both_gap_ids]
            
            # Log routing decision with clear reasoning
            logger.info(f"🚦 Solution Routing based on gap analysis:")
            logger.info(f"  📝 Prompt solutions needed: {len(prompt_gap_ids)} gaps")
            logger.info(f"  🔧 Tool solutions needed: {len(tool_gap_ids)} gaps") 
            logger.info(f"  🔀 Both approaches needed: {len(both_gap_ids)} gaps")
            
            # Route to prompt enhancement if prompt-type gaps exist
            if prompt_gaps:
                logger.info("📝 Phase 3a: Prompt Enhancement for prompt-type gaps")
                
                # Create prompt enhancement request
                prompt_enhancement_result = self._enhance_prompts_for_gaps(prompt_gaps)
                
                if prompt_enhancement_result.get("success"):
                    prompt_enhancements = prompt_enhancement_result.get("enhanced_prompts", [])
                    logger.info(f"  📝 Enhanced {len(prompt_enhancements)} prompts for {len(prompt_gaps)} gaps")
                    for enhancement in prompt_enhancements[:3]:
                        logger.info(f"    - {enhancement.get('prompt_section', 'Unknown')}: {enhancement.get('improvement_type', 'Unknown')}")
                else:
                    logger.warning("  ⚠️ Prompt enhancement failed, continuing with existing prompts")
                    prompt_enhancements = []
            
            # Route to tool proposal if tool-type gaps exist
            if tool_gaps:
                logger.info("🔧 Phase 3b: Tool Proposal for tool-type gaps")
                
                tool_proposal_result = implementation_agent.process({
                    "action": "propose_tools",
                    "weaknesses": tool_gaps,  # Only pass tool-type gaps
                    "missing_capabilities": reflection_result.get("missing_tools", [])
                })
                
                if tool_proposal_result.get("success"):
                    tool_proposals = tool_proposal_result.get("proposed_tools", [])
                    # Add gap tracking to each tool
                    for tool in tool_proposals:
                        # Map tool to the gaps it targets
                        targeted_gaps = [g for g in tool_gaps 
                                       if g.get("dimension") in tool.get("addresses", "")]
                        tool["targets_gaps"] = targeted_gaps
                        tool["solution_type"] = "tool"
                    logger.info(f"  📦 Proposed {len(tool_proposals)} new tools for {len(tool_gaps)} gaps")
                    
                # Add to phases tracking
                phases["tool_proposal"] = {
                    "success": tool_proposal_result.get("success", False),
                    "proposed_tools": tool_proposals,
                    "tool_count": len(tool_proposals),
                    "targeted_gaps": tool_gaps
                }
                    
                # Add to coordination log
                coordination_log.append({
                    "phase": "tool_proposal",
                    "agent": "implementation",
                    "action": "propose_tools",
                    "success": tool_proposal_result.get("success", False),
                    "tools_proposed": len(tool_proposals),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Phase 3b: Implementation
            logger.info("⚙️ Phase 3b: Implementation")
            
            implementation_result = implementation_agent.process({
                "action": "implement_improvements",
                "improvements": improvement_result.get("improvements", []),
                "proposed_tools": tool_proposals,
                "current_system_config": {},
                "iteration_number": iteration_number
            })
            
            phases["implementation"] = implementation_result
            coordination_log.append({
                "phase": "implementation",
                "agent": "implementation",
                "action": "implement_improvements",
                "success": implementation_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            })
            
            if not implementation_result.get("success"):
                return self._handle_phase_failure("implementation", implementation_result, coordination_log)
            
            # Phase 4: Integration (simplified)
            logger.info("🔗 Phase 4: Integration")
            phases["integration"] = {
                "success": True,
                "message": "Implementation package ready for deployment"
            }
            coordination_log.append({
                "phase": "integration",
                "agent": "orchestrator",
                "action": "integration",
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate evolution summary
            evolution_summary = self._generate_evolution_summary(phases, iteration_number)
            
            # Extract tool proposals for evolution tracking
            tools_discovered = []
            if "tool_proposal" in phases and phases["tool_proposal"].get("proposed_tools"):
                for tool in phases["tool_proposal"]["proposed_tools"]:
                    tools_discovered.append({
                        "name": tool.get("name", "unnamed_tool"),
                        "purpose": tool.get("purpose", ""),
                        "phase": "tool_proposal",
                        "iteration": iteration_number
                    })
            
            logger.info("✅ Evolution cycle completed successfully")
            
            return {
                "success": True,
                "iteration_number": iteration_number,
                "phases": phases,
                "agent_coordination_log": coordination_log,
                "evolution_summary": evolution_summary,
                "tools_discovered": tools_discovered,
                "tools_adopted": []  # Tools are proposed but not yet adopted/implemented
            }
            
        except Exception as e:
            logger.error(f"❌ Evolution cycle failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "iteration_number": iteration_number,
                "phases": phases,
                "agent_coordination_log": coordination_log
            }
    
    def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """Make API call to Claude"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=AGENT_CONFIG["max_tokens"],
                temperature=AGENT_CONFIG["temperature"],
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Try to parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"response": response_text}
                
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return {"error": str(e)}
    
    def _get_tool_context(self, evaluation_weaknesses: List[Dict] = None, missing_capabilities: List[str] = None) -> str:
        """Get current tool ecosystem context with evaluation gaps"""
        try:
            from opencanvas.evolution.core.tools import ToolsManager
            tools_manager = ToolsManager()
            return tools_manager.get_context_for_agents(
                evaluation_weaknesses=evaluation_weaknesses,
                missing_capabilities=missing_capabilities
            )
        except Exception:
            return "Tool context unavailable"
    
    def _add_to_history(self, action: str, input_data: Dict, result: Dict):
        """Add interaction to agent history"""
        self.history.append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "result": result
        })
    
    def _extract_baseline_from_evaluations(self, evaluation_data: List[Dict]) -> Dict[str, float]:
        """Extract baseline scores from evaluation data"""
        baseline = {}
        score_collections = {}
        
        for eval_data in evaluation_data:
            overall_scores = eval_data.get("overall_scores", {})
            for category, score in overall_scores.items():
                if category not in score_collections:
                    score_collections[category] = []
                score_collections[category].append(score)
        
        # Calculate averages
        for category, scores in score_collections.items():
            baseline[category] = sum(scores) / len(scores) if scores else 0.0
            
        return baseline
    
    def _generate_evolution_summary(self, phases: Dict, iteration_number: int) -> Dict[str, Any]:
        """Generate summary of evolution cycle"""
        
        reflection_phase = phases.get("reflection", {})
        improvement_phase = phases.get("improvement", {})
        implementation_phase = phases.get("implementation", {})
        
        return {
            "iteration_summary": {
                "iteration_number": iteration_number,
                "weaknesses_identified": len(reflection_phase.get("weakness_patterns", [])),
                "improvements_designed": len(improvement_phase.get("improvements", [])),
                "implementations_created": len(implementation_phase.get("implementation_package", {}).get("prompt_enhancements", [])),
                "missing_tools_identified": len(reflection_phase.get("missing_tools", [])),
                "tools_proposed": len(implementation_phase.get("proposed_tools", []) if "proposed_tools" in implementation_phase else 
                                     implementation_phase.get("implementation_package", {}).get("proposed_tools", []))
            },
            "agent_performance": {
                "reflection_agent": "success" if reflection_phase.get("success") else "failed",
                "improvement_agent": "success" if improvement_phase.get("success") else "failed", 
                "implementation_agent": "success" if implementation_phase.get("success") else "failed"
            }
        }
    
    def _handle_phase_failure(self, phase_name: str, result: Dict, coordination_log: List) -> Dict[str, Any]:
        """Handle phase failure"""
        return {
            "success": False,
            "error": f"Phase {phase_name} failed: {result.get('error', 'Unknown error')}",
            "failed_phase": phase_name,
            "agent_coordination_log": coordination_log
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "agent_type": self.agent_type,
            "model": self.model,
            "api_available": bool(self.api_key),
            "valid_actions": self.valid_actions,
            "history_length": len(self.history),
            "last_action": self.history[-1]["action"] if self.history else None
        }
    
    # Generic processing methods for simpler actions
    def _generic_reflection_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic reflection processing"""
        action = input_data.get("action")
        input_json = json.dumps(input_data, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_REFLECTION',
            action=action,
            input_json=input_json
        )
        
        result = self._call_claude(prompt)
        self._add_to_history(action, input_data, result)
        return {"success": True, "action": action, "agent_type": self.agent_type, **result}
    
    def _generic_improvement_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic improvement processing"""
        action = input_data.get("action")
        input_json = json.dumps(input_data, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_IMPROVEMENT',
            action=action,
            input_json=input_json
        )
        
        result = self._call_claude(prompt)
        self._add_to_history(action, input_data, result)
        return {"success": True, "action": action, "agent_type": self.agent_type, **result}
    
    def _enhance_prompts_for_gaps(self, prompt_gaps: List[Dict]) -> Dict[str, Any]:
        """Enhance generation prompts to address prompt-type gaps"""
        
        gaps_summary = []
        for gap in prompt_gaps:
            gap_info = {
                "gap_id": gap.get("gap_id", "unknown"),
                "description": gap.get("description", "Unknown gap"),
                "current_score": gap.get("current_score", 0),
                "target_score": gap.get("target_score", 4.0),
                "dimension": gap.get("dimension", "unknown"),
                "solution_reasoning": gap.get("solution_reasoning", {})
            }
            gaps_summary.append(gap_info)
        
        gaps_json = json.dumps(gaps_summary, indent=2)
        
        prompt = f"""Based on the identified gaps that can be fixed with better prompts, design specific prompt enhancements.

GAPS REQUIRING PROMPT SOLUTIONS:
{gaps_json}

For each gap, design prompt enhancements that will:
1. Add specific instructions to prevent the identified issues
2. Include quality standards and constraints
3. Provide clear examples of desired output
4. Add validation criteria within the prompt

Return a JSON object with:
{{
  "enhanced_prompts": [
    {{
      "gap_id": "gap_001",
      "prompt_section": "blog_generation|slide_creation|formatting",
      "improvement_type": "instruction|constraint|example|validation",
      "original_instruction": "Current prompt text (if modifying)",
      "enhanced_instruction": "Improved prompt text",
      "expected_impact": "How this addresses the gap"
    }}
  ],
  "integration_plan": "How to integrate these enhancements"
}}
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                return {"success": True, **result}
            except json.JSONDecodeError:
                return {"success": True, "enhanced_prompts": [], "response": response_text}
                
        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _propose_tools(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Propose new tools based on identified gaps"""
        
        gaps = input_data.get("weaknesses", [])  # These are now gap objects
        missing_capabilities = input_data.get("missing_capabilities", [])
        
        # Convert gaps to a format for the prompt
        gaps_summary = []
        for gap in gaps:
            gap_info = {
                "gap_id": gap.get("gap_id", "unknown"),
                "description": gap.get("description", "Unknown gap"),
                "current_score": gap.get("current_score", 0),
                "target_score": gap.get("target_score", 4.0),
                "dimension": gap.get("dimension", "unknown"),
                "solution_rationale": gap.get("solution_rationale", "")
            }
            gaps_summary.append(gap_info)
        
        # Get full tool context including current ecosystem and evaluation gaps
        tool_context = self._get_tool_context(
            evaluation_weaknesses=gaps,
            missing_capabilities=missing_capabilities
        )
        
        gaps_json = json.dumps(gaps_summary, indent=2)
        
        prompt = f"""Based on the identified gaps that require tool solutions, propose specific NEW TOOLS that should be created.

GAPS REQUIRING TOOL SOLUTIONS:
{gaps_json}

TOOL ECOSYSTEM CONTEXT:
{tool_context}

Based on the above gaps and context, propose specific tools with clear implementation details. Each tool should:
1. Target a specific gap identified above (reference gap_id)
2. Be implementable as a Python class using ONLY available resources (Claude/GPT/Gemini APIs, Python stdlib)
3. Have clear inputs (HTML/content) and outputs (enhanced HTML/content)
4. Integrate with the existing generation pipeline
5. Avoid repeating failed patterns from the registry

Return a JSON object with:
{{
  "proposed_tools": [
    {{
      "name": "ToolName",
      "purpose": "Clear purpose statement",
      "targets_gap_id": "gap_001",
      "addresses": "dimension (e.g., visual, content, accuracy)",
      "implementation_approach": "How it will work",
      "expected_impact": X.X,
      "priority": "high|medium|low"
    }}
  ],
  "priority_ranking": ["ToolName1", "ToolName2"],
  "implementation_plan": "Step-by-step plan to create these tools"
}}
"""
        
        result = self._call_claude(prompt)
        
        # Log tool proposals
        if isinstance(result, dict):
            logger.info("🔧 TOOL PROPOSAL RESULTS:")
            if "proposed_tools" in result:
                logger.info(f"  📦 Tools proposed: {len(result['proposed_tools'])}")
                for tool in result.get('proposed_tools', [])[:5]:  # Log top 5
                    logger.info(f"    - {tool.get('name', 'Unknown')}")
                    logger.info(f"      Purpose: {tool.get('purpose', 'N/A')[:100]}...")
                    logger.info(f"      Impact: {tool.get('expected_impact', 'Unknown')}")
                    logger.info(f"      Complexity: {tool.get('complexity', 'Unknown')}")
        
        self._add_to_history("propose_tools", input_data, result)
        
        return {
            "success": True,
            "action": "propose_tools",
            "agent_type": self.agent_type,
            **result
        }
    
    def _generic_implementation_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic implementation processing"""
        action = input_data.get("action")
        input_json = json.dumps(input_data, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_IMPLEMENTATION',
            action=action,
            input_json=input_json
        )
        
        result = self._call_claude(prompt)
        self._add_to_history(action, input_data, result)
        return {"success": True, "action": action, "agent_type": self.agent_type, **result}
    
    def _generic_orchestration_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic orchestration processing"""
        action = input_data.get("action")
        input_json = json.dumps(input_data, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_ORCHESTRATION',
            action=action,
            input_json=input_json
        )
        
        result = self._call_claude(prompt)
        self._add_to_history(action, input_data, result)
        return {"success": True, "action": action, "agent_type": self.agent_type, **result}


class AgentFactory:
    """Factory for creating evolution agents"""
    
    @staticmethod
    def create_agent(agent_type: str, api_key: str = None) -> EvolutionAgent:
        """Create a single agent"""
        return EvolutionAgent(agent_type, api_key)
    
    @staticmethod
    def create_all_agents(api_key: str = None) -> Dict[str, EvolutionAgent]:
        """Create all agent types"""
        agents = {}
        for agent_type in AGENT_PROMPTS.keys():
            agents[agent_type] = EvolutionAgent(agent_type, api_key)
        return agents
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get all available agent types"""
        return list(AGENT_PROMPTS.keys())