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
    
    def __init__(self, agent_type: str, api_key: str = None, model: str = None, prompts_registry = None):
        """Initialize evolution agent with specific type
        
        Args:
            agent_type: Type of agent (reflection, improvement, implementation, orchestrator)
            api_key: API key for Claude
            model: Model to use
            prompts_registry: PromptsRegistryManager instance for accessing prompt history
        """
        
        if agent_type not in AGENT_PROMPTS:
            raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {list(AGENT_PROMPTS.keys())}")
        
        self.agent_type = agent_type
        self.name = f"{agent_type.title()} Agent"
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.model = model or AGENT_CONFIG["model"]
        self.prompts_registry = prompts_registry
        
        if not self.api_key:
            raise ValueError(f"API key required for {self.name}")
        
        self.client = Anthropic(api_key=self.api_key)
        self.system_prompt = AGENT_PROMPTS[agent_type]
        self.valid_actions = AGENT_ACTIONS[agent_type]
        self.history = []
        
        if self.prompts_registry:
            logger.info(f"✅ {self.name} initialized with prompts registry")
        else:
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
        elif action == "generate_adaptive_prompt_enhancements":
            return self._generate_adaptive_prompt_enhancements(input_data)
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
        prompt_only = input_data.get("prompt_only", False)
        
        # Get registry context for the reflection agent
        registry_context = self._get_tool_context()
        
        # Add prompt-only mode context
        if prompt_only:
            prompt_only_context = """

IMPORTANT: PROMPT-ONLY MODE ACTIVE
- Focus primarily on gaps that can be addressed through prompt improvements
- Still identify tool-required gaps but classify them as "deferred_tool_required"
- For each gap, prioritize prompt-based solutions over tool-based solutions
- Consider creative prompt-based workarounds for complex issues
- Examples of prompt-addressable gaps:
  * Content organization and structure
  * Source adherence and accuracy
  * Formatting and visual hierarchy
  * Clarity and readability improvements
  * Engagement through better content framing
"""
        else:
            prompt_only_context = ""
        
        evaluations_json = json.dumps(evaluations, indent=2)
        topics_str = str(topics)
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_ANALYZE_EVALUATIONS',
            evaluations_json=evaluations_json,
            topics_str=topics_str,
            registry_context=registry_context
        ) + prompt_only_context

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
            
            # Log gap identification results
            gaps = result.get('identified_gaps', [])
            
            if len(gaps) == 0:
                logger.info("📊 No gaps identified in this reflection attempt")
                # Don't modify result - let orchestrator handle retries
            elif len(gaps) < 3:
                logger.warning(f"⚠️ Only {len(gaps)} gaps identified - fewer than optimal but continuing")
            else:
                logger.info(f"✅ {len(gaps)} gaps identified by reflection agent")
            
            # Log identified gaps with reasoning
            if "identified_gaps" in result:
                gaps = result['identified_gaps']
                logger.info(f"  🔍 Identified {len(gaps)} gaps:")
                for gap in gaps[:5]:  # Log top 5
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
        prompt_only = input_data.get("prompt_only", False)
        
        reflection_json = json.dumps(reflection_results, indent=2)
        baseline_json = json.dumps(current_baseline, indent=2)
        
        # If in prompt-only mode, add context to focus on prompt improvements
        if prompt_only:
            prompt_context = "\n\nIMPORTANT: PROMPT-ONLY MODE ACTIVE\n"
            prompt_context += "Focus exclusively on prompt improvements. Do NOT propose any tools.\n"
            prompt_context += "Consider these proven prompt patterns:\n"
            prompt_context += "- Explicit source adherence instructions\n"
            prompt_context += "- Structured, numbered steps\n"
            prompt_context += "- Specific examples of desired output\n"
            prompt_context += "- Balance between constraints and creativity\n"
            
            # Get prompts registry context if available
            if hasattr(self, 'prompts_registry') and self.prompts_registry:
                prompt_context += "\n" + self.prompts_registry.get_context_for_agents()
        else:
            prompt_context = ""
        
        prompt = EvolutionPrompts.get_prompt(
            'CORE_DESIGN_IMPROVEMENTS',
            iteration_number=iteration_number,
            reflection_json=reflection_json,
            baseline_json=baseline_json
        ) + prompt_context


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
        
        # Check for similar failed edits if prompts registry is available
        if self.prompts_registry and improvements:
            logger.info("🔍 Checking for similar failed prompt edits...")
            for improvement in improvements:
                if improvement.get('category') == 'prompt' or improvement.get('type') == 'prompt_enhancement':
                    # Extract proposed changes from improvement
                    proposed_changes = []
                    if 'implementation' in improvement:
                        details = improvement['implementation'].get('details', '')
                        if details:
                            proposed_changes.append(details)
                    
                    if proposed_changes:
                        similar = self.prompts_registry.check_similar_edits(proposed_changes)
                        
                        if similar['exact_matches']:
                            logger.warning(f"  ⚠️ Found exact matches for proposed changes in {improvement.get('name', 'Unknown')}")
                            for match in similar['exact_matches']:
                                logger.warning(f"    - Previously failed: {match['edit_name']} (degradation: {match['degradation']:.3f})")
                                logger.warning(f"      Lesson: {match['lesson']}")
                        
                        if similar['pattern_warnings']:
                            logger.warning(f"  ⚠️ Pattern warnings for {improvement.get('name', 'Unknown')}:")
                            for warning in similar['pattern_warnings']:
                                logger.warning(f"    - Pattern: {warning['pattern']} (failure rate: {warning['failure_rate']:.2f})")
                                logger.warning(f"      Warning: {warning['warning']}")
        
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
            # Phase 1: Reflection with retry mechanism
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
            
            reflection_agent = EvolutionAgent("reflection", self.api_key, prompts_registry=self.prompts_registry)
            
            # Retry up to 3 times if no gaps are found
            max_reflection_retries = 3
            reflection_result = None
            
            for attempt in range(max_reflection_retries):
                logger.info(f"  🔄 Reflection attempt {attempt + 1}/{max_reflection_retries}")
                
                reflection_result = reflection_agent.process({
                    "action": "analyze_evaluations",
                    "evaluations": evaluation_data,
                    "topics": topics,
                    "attempt_number": attempt + 1,  # Pass attempt number for context
                    "instruction": "Be thorough in identifying areas for improvement" if attempt > 0 else None,
                    "prompt_only": input_data.get("prompt_only", False)  # Pass prompt_only flag
                })
                
                if not reflection_result.get("success"):
                    phases["reflection"] = reflection_result
                    coordination_log.append({
                        "phase": "reflection",
                        "agent": "reflection",
                        "action": "analyze_evaluations",
                        "attempt": attempt + 1,
                        "success": False,
                        "timestamp": datetime.now().isoformat()
                    })
                    return self._handle_phase_failure("reflection", reflection_result, coordination_log)
                
                # Check if gaps were identified
                identified_gaps = reflection_result.get("identified_gaps", [])
                if len(identified_gaps) > 0:
                    logger.info(f"  ✅ Found {len(identified_gaps)} gaps on attempt {attempt + 1}")
                    break
                else:
                    logger.info(f"  ⚠️ No gaps found on attempt {attempt + 1}")
                    if attempt < max_reflection_retries - 1:
                        logger.info(f"  🔄 Retrying reflection analysis...")
                        import time
                        time.sleep(2)  # Brief pause between retries
            
            phases["reflection"] = reflection_result
            coordination_log.append({
                "phase": "reflection",
                "agent": "reflection",
                "action": "analyze_evaluations",
                "attempts": attempt + 1,
                "success": reflection_result.get("success", False),
                "gaps_found": len(reflection_result.get("identified_gaps", [])),
                "timestamp": datetime.now().isoformat()
            })
            
            # After all retries, check if no gaps were identified
            identified_gaps = reflection_result.get("identified_gaps", [])
            
            # Filter gaps if in prompt-only mode
            prompt_only = input_data.get("prompt_only", False)
            if prompt_only and identified_gaps:
                logger.info(f"  📝 PROMPT-ONLY MODE: Filtering gaps...")
                original_count = len(identified_gaps)
                
                # Filter to keep only prompt-addressable gaps
                prompt_addressable_gaps = []
                deferred_tool_gaps = []
                
                for gap in identified_gaps:
                    solution_type = gap.get("solution_type", "unknown")
                    if solution_type in ["prompt", "both"]:
                        # For "both" type, emphasize prompt solution in prompt-only mode
                        if solution_type == "both":
                            gap["solution_type"] = "prompt"
                            gap["original_type"] = "both"
                            gap["note"] = "Originally required both prompt and tool, focusing on prompt solution"
                        prompt_addressable_gaps.append(gap)
                    elif solution_type == "tool":
                        gap["deferred"] = True
                        gap["reason"] = "Tool required - deferred in prompt-only mode"
                        deferred_tool_gaps.append(gap)
                
                logger.info(f"    - Original gaps: {original_count}")
                logger.info(f"    - Prompt-addressable: {len(prompt_addressable_gaps)}")
                logger.info(f"    - Deferred (tool-required): {len(deferred_tool_gaps)}")
                
                # Log deferred gaps for reference
                if deferred_tool_gaps:
                    logger.info(f"  📋 Deferred tool-required gaps:")
                    for gap in deferred_tool_gaps[:3]:  # Log first 3
                        logger.info(f"    - {gap.get('description', 'Unknown')[:80]}...")
                
                # Update reflection result with filtered gaps
                reflection_result["identified_gaps"] = prompt_addressable_gaps
                reflection_result["deferred_gaps"] = deferred_tool_gaps
                identified_gaps = prompt_addressable_gaps
                
                # If no prompt-addressable gaps but have tool gaps, explain the situation
                if len(prompt_addressable_gaps) == 0 and len(deferred_tool_gaps) > 0:
                    logger.info("📝 PROMPT-ONLY MODE: No prompt-addressable gaps found")
                    logger.info(f"  ℹ️ {len(deferred_tool_gaps)} tool-required gaps were deferred")
                    logger.info("✅ Prompt optimization has reached its limit")
                    return {
                        "success": True,
                        "early_termination": True,
                        "reason": "prompt_optimization_exhausted",
                        "phases": phases,
                        "coordination_log": coordination_log,
                        "message": f"Prompt optimization complete - {len(deferred_tool_gaps)} remaining gaps require tools",
                        "deferred_gaps": deferred_tool_gaps
                    }
            
            if len(identified_gaps) == 0:
                if prompt_only:
                    message = "No gaps identified - prompt optimization complete"
                else:
                    message = "No quality gaps identified after 3 reflection attempts - system has reached optimal state"
                
                logger.info("🎉 NO GAPS IDENTIFIED - SYSTEM IS OPTIMIZED!")
                logger.info(f"✅ {message}")
                return {
                    "success": True,
                    "early_termination": True,
                    "reason": "optimal_state_reached",
                    "phases": phases,
                    "coordination_log": coordination_log,
                    "message": message
                }
            
            # Phase 2: Improvement Design
            logger.info("🛠️ Phase 2: Improvement Design")
            improvement_agent = EvolutionAgent("improvement", self.api_key, prompts_registry=self.prompts_registry)
            
            # Extract baseline from evaluation data
            current_baseline = self._extract_baseline_from_evaluations(evaluation_data)
            
            improvement_result = improvement_agent.process({
                "action": "design_improvements",
                "reflection_results": reflection_result,
                "current_baseline": current_baseline,
                "iteration_number": iteration_number,
                "prompt_only": input_data.get("prompt_only", False)  # Pass prompt_only flag
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
            implementation_agent = EvolutionAgent("implementation", self.api_key, prompts_registry=self.prompts_registry)
            
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
                logger.info("📝 Phase 3a: Adaptive Prompt Enhancement for prompt-type gaps")
                
                # Check if we're in prompt-only mode
                prompt_only = input_data.get("prompt_only", False)
                max_iterations = getattr(self, 'max_iterations', 10)
                
                # Use adaptive enhancement via implementation agent
                prompt_enhancement_result = implementation_agent.process({
                    "action": "generate_adaptive_prompt_enhancements",
                    "gaps": prompt_gaps,
                    "iteration_number": iteration_number,
                    "max_iterations": max_iterations,
                    "temperature_schedule": "adaptive",
                    "current_prompts": self._get_current_prompts(),
                    "prompt_only": prompt_only,
                    "force_creative_solutions": True
                })
                
                if prompt_enhancement_result.get("success"):
                    successful_count = prompt_enhancement_result.get("successful_enhancements", 0)
                    failed_count = prompt_enhancement_result.get("failed_enhancements", 0)
                    temperature = prompt_enhancement_result.get("temperature", 0.5)
                    creativity = prompt_enhancement_result.get("creativity_level", "unknown")
                    
                    logger.info(f"  🌡️ Temperature: {temperature:.3f} ({creativity} creativity)")
                    logger.info(f"  📝 Enhanced: {successful_count}/{len(prompt_gaps)} gaps successfully")
                    
                    if failed_count > 0:
                        logger.info(f"  ⚠️ Failed: {failed_count} enhancements failed validation")
                    
                    prompt_enhancements = prompt_enhancement_result.get("enhancements", [])
                    
                    # Log details of successful enhancements
                    for enhancement in prompt_enhancements[:3]:
                        gap_id = enhancement.get('gap_id', 'unknown')
                        gap_type = enhancement.get('gap_type', 'unknown')
                        enh_count = len(enhancement.get('enhancements', []))
                        logger.info(f"    - Gap {gap_id} ({gap_type}): {enh_count} enhancements generated")
                    
                else:
                    logger.warning(f"  ❌ Adaptive prompt enhancement failed: {prompt_enhancement_result.get('error', 'Unknown error')}")
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
    
    def _call_claude(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """Make API call to Claude with JSON validation and retry logic"""
        
        # Diagnostic logging - log prompt length and key sections
        logger.debug(f"🔍 DIAGNOSTIC: Calling Claude with prompt length: {len(prompt)} chars")
        if "CRITICAL INSTRUCTION: ALWAYS IDENTIFY GAPS" in prompt:
            logger.info("📝 Using enhanced gap identification prompt")
        
        for attempt in range(max_retries):
            try:
                # Add JSON format emphasis for retry attempts
                final_prompt = prompt
                if attempt > 0:
                    logger.warning(f"⚠️ Retry attempt {attempt + 1}/{max_retries} - emphasizing JSON format")
                    final_prompt = prompt + "\n\nIMPORTANT: You MUST respond with valid JSON only. Do not include any text before or after the JSON object."
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=AGENT_CONFIG["max_tokens"],
                    temperature=AGENT_CONFIG["temperature"],
                    system=self.system_prompt + "\n\nYou MUST always respond with valid JSON format only.",
                    messages=[{"role": "user", "content": final_prompt}]
                )
                
                response_text = message.content[0].text.strip()
                
                # Log raw response for diagnostic purposes
                logger.debug(f"🔍 DIAGNOSTIC: Raw Claude response length: {len(response_text)} chars")
                logger.debug(f"🔍 DIAGNOSTIC: Response preview: {response_text[:500]}...")
                
                # Extract and validate JSON
                json_response = self._extract_and_validate_json(response_text, attempt + 1)
                
                if json_response is not None:
                    # Additional validation for gap identification responses
                    if "analyze_evaluations" in prompt and "identified_gaps" in json_response:
                        gaps = json_response["identified_gaps"]
                        if len(gaps) == 0:
                            if attempt < max_retries - 1:
                                logger.warning(f"⚠️ Attempt {attempt + 1}: No gaps identified, retrying with stronger prompt")
                                continue
                            else:
                                logger.error(f"❌ FAILED: Claude refused to identify gaps after {max_retries} attempts")
                                return {"error": "Claude failed to identify any gaps despite multiple attempts"}
                        else:
                            logger.info(f"✅ DIAGNOSTIC: Found {len(gaps)} gaps in response (attempt {attempt + 1})")
                    
                    return json_response
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Attempt {attempt + 1}: Invalid JSON, retrying...")
                        continue
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Attempt {attempt + 1}: API call failed ({e}), retrying...")
                    continue
                else:
                    logger.error(f"❌ Claude API call failed after {max_retries} attempts: {e}")
                    return {"error": str(e)}
        
        logger.error(f"❌ Failed to get valid JSON response after {max_retries} attempts")
        return {"error": "Failed to get valid JSON response from Claude"}
    
    def _extract_and_validate_json(self, response_text: str, attempt: int) -> Dict[str, Any]:
        """Extract and validate JSON from Claude response"""
        
        # Try direct parsing first
        try:
            parsed = json.loads(response_text)
            logger.debug(f"✅ Direct JSON parsing successful (attempt {attempt})")
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON from code blocks
        import re
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^{}]*"identified_gaps"[^{}]*\})',
            r'(\{.*\})'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        logger.debug(f"✅ JSON extracted with pattern (attempt {attempt})")
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Try to find any JSON-like structure
        lines = response_text.split('\n')
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('{') or in_json:
                in_json = True
                json_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and stripped.endswith('}'):
                    break
        
        if json_lines:
            try:
                json_text = '\n'.join(json_lines)
                parsed = json.loads(json_text)
                logger.debug(f"✅ JSON extracted by brace counting (attempt {attempt})")
                return parsed
            except json.JSONDecodeError:
                pass
        
        logger.warning(f"⚠️ Could not extract valid JSON from response (attempt {attempt})")
        logger.debug(f"🔍 Response text: {response_text[:1000]}...")
        return None
    
    def _get_tool_context(self, evaluation_weaknesses: List[Dict] = None, missing_capabilities: List[str] = None) -> str:
        """Get current tool ecosystem context with evaluation gaps and prompts history"""
        context_parts = []
        
        # Get tools context
        try:
            from opencanvas.evolution.core.tools import ToolsManager
            tools_manager = ToolsManager()
            tools_context = tools_manager.get_context_for_agents(
                evaluation_weaknesses=evaluation_weaknesses,
                missing_capabilities=missing_capabilities
            )
            context_parts.append(tools_context)
        except Exception:
            context_parts.append("Tool context unavailable")
        
        # Add prompts registry context if available
        if self.prompts_registry:
            try:
                prompts_context = self.prompts_registry.get_context_for_agents()
                context_parts.append("\n" + prompts_context)
            except Exception as e:
                logger.debug(f"Failed to get prompts registry context: {e}")
        
        return "\n".join(context_parts)
    
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
        
        # Count weaknesses from both old and new formats
        weakness_count = len(reflection_phase.get("identified_gaps", []))
        if weakness_count == 0:
            # Fallback to old format
            weakness_count = len(reflection_phase.get("weakness_patterns", []))
        
        return {
            "iteration_summary": {
                "iteration_number": iteration_number,
                "weaknesses_identified": weakness_count,
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
    
    def _get_current_prompts(self) -> Dict[str, str]:
        """Get current prompts for enhancement
        
        This method should be overridden by the orchestrator to provide
        the actual current prompts from the generation system.
        """
        
        # Import prompts from the centralized location
        from ..prompts.evolution_prompts import EvolutionPrompts
        
        return {
            "generation_prompt": EvolutionPrompts.TOPIC_GENERATION_BASE,
            "slide_generation_prompt": EvolutionPrompts.TOPIC_GENERATION_BASE,
            "pdf_generation_prompt": EvolutionPrompts.PDF_GENERATION_BASE
        }
    
    def _enhance_prompts_for_gaps(self, prompt_gaps: List[Dict]) -> Dict[str, Any]:
        """Legacy method - replaced by adaptive enhancement
        
        This method is kept for backward compatibility but now delegates
        to the new adaptive enhancement system.
        """
        
        logger.info("Using legacy prompt enhancement method - consider upgrading to adaptive enhancement")
        
        # Convert to adaptive enhancement call
        try:
            # Use the first gap's iteration context if available
            iteration_number = getattr(self, 'current_iteration', 1)
            
            # Create a minimal implementation agent for this
            implementation_agent = EvolutionAgent("implementation", self.api_key, prompts_registry=self.prompts_registry)
            
            result = implementation_agent.process({
                "action": "generate_adaptive_prompt_enhancements",
                "gaps": prompt_gaps,
                "iteration_number": iteration_number,
                "max_iterations": 10,
                "temperature_schedule": "conservative",  # Use conservative for legacy
                "current_prompts": self._get_current_prompts(),
                "prompt_only": True
            })
            
            if result.get("success"):
                # Convert new format to legacy format
                enhanced_prompts = []
                for enhancement in result.get("enhancements", []):
                    gap_id = enhancement.get("gap_id")
                    for enh in enhancement.get("enhancements", []):
                        enhanced_prompts.append({
                            "gap_id": gap_id,
                            "prompt_section": "generation",
                            "improvement_type": enh.get("type", "unknown"),
                            "enhanced_instruction": enh.get("content", ""),
                            "expected_impact": enh.get("justification", "")
                        })
                
                return {
                    "success": True,
                    "enhanced_prompts": enhanced_prompts,
                    "integration_plan": "Apply enhancements to generation prompts"
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
                
        except Exception as e:
            logger.error(f"Legacy prompt enhancement failed: {e}")
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
    
    def _generate_adaptive_prompt_enhancements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate prompt enhancements with adaptive temperature control
        
        This method uses temperature-based creativity to generate prompt enhancements
        that address identified gaps while preserving prompt structure integrity.
        """
        
        try:
            # Import the adaptive enhancer
            from ..core.adaptive_enhancer import AdaptivePromptEnhancer
            
            # Extract input parameters
            gaps = input_data.get("gaps", [])
            iteration_number = input_data.get("iteration_number", 1)
            max_iterations = input_data.get("max_iterations", 10)
            temperature_schedule = input_data.get("temperature_schedule", "adaptive")
            current_prompts = input_data.get("current_prompts", {})
            prompt_only = input_data.get("prompt_only", True)
            force_creative_solutions = input_data.get("force_creative_solutions", False)
            
            if not gaps:
                logger.warning("No gaps provided for prompt enhancement")
                return {
                    "success": False,
                    "error": "No gaps provided",
                    "enhancements": []
                }
            
            # Initialize adaptive enhancer
            enhancer = AdaptivePromptEnhancer(
                iteration=iteration_number,
                max_iterations=max_iterations,
                temperature_schedule=temperature_schedule
            )
            
            logger.info(f"🌡️ Adaptive enhancement at temperature {enhancer.temperature:.3f} ({enhancer.get_creativity_level()} creativity)")
            
            # Get current prompts - need to determine relevant prompt types
            if not current_prompts:
                current_prompts = self._get_default_prompts()
            
            # Generate enhancements for each gap
            all_enhancements = []
            successful_enhancements = 0
            failed_enhancements = 0
            
            for gap in gaps:
                gap_id = gap.get("gap_id", f"gap_{len(all_enhancements)}")
                logger.info(f"    🎯 Enhancing for gap: {gap_id} ({gap.get('dimension', 'unknown')})")
                
                # Determine which prompt to enhance based on gap type
                prompt_key = self._determine_prompt_key_for_gap(gap)
                current_prompt = current_prompts.get(prompt_key, "")
                
                if not current_prompt:
                    logger.warning(f"No current prompt found for key: {prompt_key}")
                    # Create a basic prompt to enhance
                    current_prompt = self._create_basic_prompt_for_gap(gap)
                
                # Generate enhancement
                enhancement_result = enhancer.generate_enhancement(
                    gap=gap,
                    current_prompt=current_prompt,
                    prompt_registry=self.prompts_registry
                )
                
                if enhancement_result.get("success"):
                    enhancement_result["prompt_key"] = prompt_key
                    enhancement_result["original_prompt_preview"] = current_prompt[:150] + "..." if len(current_prompt) > 150 else current_prompt
                    all_enhancements.append(enhancement_result)
                    successful_enhancements += 1
                    logger.info(f"      ✅ Generated {len(enhancement_result.get('enhancements', []))} enhancements")
                else:
                    failed_enhancements += 1
                    logger.warning(f"      ❌ Enhancement failed: {enhancement_result.get('error', 'Unknown error')}")
                    # Still add failed attempts for tracking
                    all_enhancements.append(enhancement_result)
            
            # Generate summary
            enhancement_summary = enhancer.get_enhancement_summary()
            
            logger.info(f"🎨 Enhancement Summary:")
            logger.info(f"    - Temperature: {enhancer.temperature:.3f}")
            logger.info(f"    - Creativity: {enhancer.get_creativity_level()}")
            logger.info(f"    - Successful: {successful_enhancements}/{len(gaps)}")
            logger.info(f"    - Failed: {failed_enhancements}/{len(gaps)}")
            
            # Validate all successful enhancements preserve structure
            validated_enhancements = []
            for enhancement in all_enhancements:
                if enhancement.get("success") and self._validate_enhancement_structure(enhancement):
                    validated_enhancements.append(enhancement)
                elif enhancement.get("success"):
                    logger.warning(f"Enhancement {enhancement.get('gap_id')} failed structure validation")
            
            result = {
                "success": True,
                "action": "generate_adaptive_prompt_enhancements",
                "agent_type": self.agent_type,
                "enhancements": validated_enhancements,
                "total_gaps_processed": len(gaps),
                "successful_enhancements": len(validated_enhancements),
                "failed_enhancements": len(gaps) - len(validated_enhancements),
                "temperature": enhancer.temperature,
                "creativity_level": enhancer.get_creativity_level(),
                "iteration": iteration_number,
                "enhancement_summary": enhancement_summary,
                "validation_passed": len(validated_enhancements) > 0
            }
            
            # Add to history
            self._add_to_history("generate_adaptive_prompt_enhancements", input_data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate adaptive prompt enhancements: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": str(e),
                "action": "generate_adaptive_prompt_enhancements",
                "agent_type": self.agent_type,
                "enhancements": []
            }
    
    def _determine_prompt_key_for_gap(self, gap: Dict[str, Any]) -> str:
        """Determine which prompt key to use based on gap characteristics"""
        
        gap_dimension = gap.get("dimension", "unknown").lower()
        gap_description = gap.get("description", "").lower()
        
        # Map gap types to prompt keys
        if "accuracy" in gap_dimension or "source" in gap_description:
            return "generation_prompt"  # Main generation prompt for source accuracy
        elif "content" in gap_dimension or "coverage" in gap_description:
            return "generation_prompt"  # Main generation prompt for content coverage
        elif "visual" in gap_dimension or "design" in gap_description:
            return "slide_generation_prompt"  # Slide-specific prompt for visual issues
        else:
            return "generation_prompt"  # Default to main generation prompt
    
    def _create_basic_prompt_for_gap(self, gap: Dict[str, Any]) -> str:
        """Create a basic prompt when none exists for the gap type"""
        
        gap_type = gap.get("dimension", "unknown")
        
        basic_prompts = {
            "accuracy": "Generate content that strictly adheres to the source material. Topic: {topic}, Purpose: {purpose}, Theme: {theme}",
            "content": "Generate comprehensive content covering all important aspects. Topic: {topic}, Purpose: {purpose}, Theme: {theme}", 
            "visual": "Generate well-designed, visually appealing content. Topic: {topic}, Purpose: {purpose}, Theme: {theme}",
            "overall": "Generate high-quality content optimized for excellence. Topic: {topic}, Purpose: {purpose}, Theme: {theme}"
        }
        
        return basic_prompts.get(gap_type, basic_prompts["overall"])
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """Get default prompts when none are provided"""
        
        # Import prompts from the centralized location
        from ..prompts.evolution_prompts import EvolutionPrompts
        
        return {
            "generation_prompt": EvolutionPrompts.TOPIC_GENERATION_BASE,
            "slide_generation_prompt": EvolutionPrompts.TOPIC_GENERATION_BASE,
            "pdf_generation_prompt": EvolutionPrompts.PDF_GENERATION_BASE
        }
    
    def _validate_enhancement_structure(self, enhancement: Dict[str, Any]) -> bool:
        """Validate that enhancement preserves prompt structure"""
        
        try:
            # Check if enhancement has required fields
            required_fields = ["gap_id", "enhancements"]
            for field in required_fields:
                if field not in enhancement:
                    logger.warning(f"Enhancement missing required field: {field}")
                    return False
            
            # Check if enhancements are valid
            enhancements = enhancement.get("enhancements", [])
            if not enhancements:
                logger.warning("Enhancement contains no enhancements")
                return False
            
            # Validate each individual enhancement
            for enh in enhancements:
                if not enh.get("validated", False):
                    logger.warning(f"Enhancement not validated: {enh.get('type', 'unknown')}")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Enhancement structure validation failed: {e}")
            return False
    
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
    def create_all_agents(api_key: str = None, prompts_registry = None) -> Dict[str, EvolutionAgent]:
        """Create all agent types"""
        agents = {}
        for agent_type in AGENT_PROMPTS.keys():
            agents[agent_type] = EvolutionAgent(agent_type, api_key, prompts_registry=prompts_registry)
        return agents
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get all available agent types"""
        return list(AGENT_PROMPTS.keys())