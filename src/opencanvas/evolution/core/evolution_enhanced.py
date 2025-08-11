"""
Enhanced Evolution System with Concrete Improvements
This version actually makes things better by using proven strategies
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import base evolution system
from .evolution import EvolutionSystem

# Import new components
from .tools_registry import ToolsRegistry
from ..strategies.improvement_strategies import EvolutionStrategies

logger = logging.getLogger(__name__)

class EnhancedEvolutionSystem(EvolutionSystem):
    """
    Enhanced evolution system that actually improves quality
    Uses persistent tool registry and concrete improvement strategies
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize enhanced evolution system"""
        super().__init__(*args, **kwargs)
        
        # Initialize persistent registry
        self.tools_registry = ToolsRegistry()
        
        # Initialize improvement strategies
        self.strategies = EvolutionStrategies()
        
        # Track what's working
        self.successful_improvements = []
        self.failed_improvements = []
        
        logger.info("🚀 Enhanced Evolution System initialized")
        logger.info(f"  📚 Tool Registry: {len(self.tools_registry.tools)} tools")
        logger.info(f"  🎯 Strategies: {len(self.strategies.strategies)} strategies")
    
    def _apply_improvements(self, agent_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """
        Apply improvements with concrete strategies
        Override parent method to use proven approaches
        """
        
        logger.info("🔧 Applying ENHANCED improvements with proven strategies")
        
        results = {
            "prompts_evolved": 0,
            "tools_discovered": [],
            "tools_adopted": [],
            "strategies_applied": [],
            "total_improvements": 0
        }
        
        # Get evaluation data from agent result
        evaluation_data = agent_result.get("evaluation_data", [])
        if not evaluation_data:
            logger.warning("No evaluation data available for improvements")
            return results
        
        # Analyze weaknesses
        avg_eval = self._average_evaluation_data(evaluation_data)
        weaknesses = self.strategies._identify_weaknesses(avg_eval)
        
        logger.info(f"🔍 Identified {len(weaknesses)} weaknesses:")
        for weakness, severity in weaknesses.items():
            logger.info(f"  - {weakness}: severity {severity:.2f}")
        
        # Get best strategy for current state
        strategy = self.strategies.get_strategy_for_weakness(avg_eval)
        
        if strategy:
            logger.info(f"🎯 Applying strategy: {strategy.name}")
            logger.info(f"  Target: {strategy.target_metric}")
            logger.info(f"  Expected impact: +{strategy.expected_impact:.2f}")
            
            # Apply prompt improvements
            prompt_improvements = self.strategies.generate_prompt_improvements(strategy)
            if prompt_improvements:
                self._apply_prompt_improvements(prompt_improvements, iteration_number)
                results["prompts_evolved"] = len(prompt_improvements)
                logger.info(f"  ✅ Applied {len(prompt_improvements)} prompt improvements")
            
            # Generate and implement tool if needed
            tool_spec = self.strategies.generate_tool_specification(strategy)
            
            # Check with registry if we should implement this tool
            tool_decision = self.tools_registry.should_implement_tool(tool_spec["name"])
            
            if tool_decision["implement"]:
                logger.info(f"  🔧 Implementing tool: {tool_spec['name']}")
                logger.info(f"    Reason: {tool_decision['reason']}")
                
                # Propose tool to registry
                self.tools_registry.propose_tool(
                    name=tool_spec["name"],
                    purpose=tool_spec["purpose"],
                    expected_impact=tool_spec["expected_impact"],
                    strategy=tool_spec,
                    iteration=iteration_number
                )
                
                # Implement tool
                implementation_result = self.tool_implementation.implement_tool_from_spec(
                    tool_spec, 
                    iteration_number
                )
                
                if implementation_result["success"] and implementation_result["deployed"]:
                    # Activate in registry
                    self.tools_registry.activate_tool(
                        tool_spec["name"],
                        tool_spec["expected_impact"]
                    )
                    results["tools_adopted"].append(tool_spec["name"])
                    logger.info(f"  ✅ Tool deployed: {tool_spec['name']}")
                else:
                    # Mark as failed in registry
                    self.tools_registry.mark_tool_failed(
                        tool_spec["name"],
                        implementation_result.get("error", "Implementation failed"),
                        0.0
                    )
                    logger.warning(f"  ❌ Tool failed: {tool_spec['name']}")
            else:
                logger.info(f"  ⏭️ Skipping tool: {tool_decision['reason']}")
            
            results["tools_discovered"].append(tool_spec["name"])
            
            # Track strategy application
            results["strategies_applied"].append({
                "name": strategy.name,
                "target": strategy.target_metric,
                "expected_impact": strategy.expected_impact
            })
        else:
            logger.info("📊 No significant weaknesses - focusing on refinement")
            
            # Apply general refinements
            self._apply_general_refinements(iteration_number)
            results["prompts_evolved"] = 1
        
        # Check registry for high-impact opportunities
        opportunities = self.tools_registry.get_high_impact_opportunities()
        if opportunities:
            logger.info(f"💡 Found {len(opportunities)} high-impact tool opportunities in registry")
            for opp in opportunities[:2]:  # Implement top 2
                logger.info(f"  - {opp.name}: expected +{opp.impact:.2f} impact")
        
        results["total_improvements"] = results["prompts_evolved"] + len(results["tools_adopted"])
        
        logger.info(f"✅ Applied {results['total_improvements']} improvements")
        logger.info(f"  - Prompts evolved: {results['prompts_evolved']}")
        logger.info(f"  - Tools deployed: {len(results['tools_adopted'])}")
        logger.info(f"  - Strategies applied: {len(results['strategies_applied'])}")
        
        return results
    
    def _apply_prompt_improvements(self, improvements: Dict[str, str], iteration: int):
        """Apply specific prompt improvements"""
        
        # Load current prompts
        prompts_dir = Path(f"evolution_prompts/iteration_{iteration:03d}")
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        for prompt_type, improvement in improvements.items():
            prompt_file = prompts_dir / f"{prompt_type}_prompt.txt"
            
            # Load existing prompt or use baseline
            if iteration > 1:
                prev_prompt_file = Path(f"evolution_prompts/iteration_{iteration-1:03d}/{prompt_type}_prompt.txt")
                if prev_prompt_file.exists():
                    base_prompt = prev_prompt_file.read_text()
                else:
                    base_prompt = self._get_baseline_prompt(prompt_type)
            else:
                base_prompt = self._get_baseline_prompt(prompt_type)
            
            # Append improvements
            enhanced_prompt = base_prompt + "\n\n" + improvement
            
            # Save enhanced prompt
            prompt_file.write_text(enhanced_prompt)
            
            logger.info(f"  📝 Enhanced {prompt_type} prompt")
    
    def _apply_general_refinements(self, iteration: int):
        """Apply general refinements when no major weaknesses"""
        
        refinements = """
GENERAL QUALITY REFINEMENTS:
- Ensure every slide has a clear, single takeaway message
- Use consistent animation and transition effects
- Add page numbers and progress indicators
- Include a summary slide at the end
- Ensure all images are high-resolution and relevant
- Add speaker notes with additional context
"""
        
        prompts_dir = Path(f"evolution_prompts/iteration_{iteration:03d}")
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        prompt_file = prompts_dir / "refinement_prompt.txt"
        prompt_file.write_text(refinements)
        
        logger.info("  📝 Applied general refinements")
    
    def _average_evaluation_data(self, evaluation_data: List[Dict]) -> Dict:
        """Average multiple evaluation data points"""
        
        if not evaluation_data:
            return {}
        
        # For simplicity, take the first evaluation if only one
        if len(evaluation_data) == 1:
            return evaluation_data[0]
        
        # Average multiple evaluations
        averaged = {}
        
        # Average visual scores
        visual_scores = {}
        for key in ["professional_design", "information_hierarchy", "clarity_readability", "visual_textual_balance"]:
            scores = [e.get("visual_scores", {}).get(key, {}).get("score", 0) for e in evaluation_data]
            visual_scores[key] = {"score": sum(scores) / len(scores) if scores else 0}
        
        visual_scores["overall_visual_score"] = sum(v["score"] for v in visual_scores.values()) / len(visual_scores)
        averaged["visual_scores"] = visual_scores
        
        # Average content scores
        content_scores = {}
        for key in ["logical_structure", "narrative_quality"]:
            scores = [e.get("content_free_scores", {}).get(key, {}).get("score", 0) for e in evaluation_data]
            content_scores[key] = {"score": sum(scores) / len(scores) if scores else 0}
        
        averaged["content_free_scores"] = content_scores
        
        # Average accuracy scores
        accuracy_scores = {}
        for key in ["accuracy", "essential_coverage"]:
            scores = [e.get("content_required_scores", {}).get(key, {}).get("score", 0) for e in evaluation_data]
            accuracy_scores[key] = {"score": sum(scores) / len(scores) if scores else 0}
        
        averaged["content_required_scores"] = accuracy_scores
        
        return averaged
    
    def _get_baseline_prompt(self, prompt_type: str) -> str:
        """Get baseline prompt for a given type"""
        
        # Load from production prompts
        baseline_prompts = {
            "slide_generation": Path("src/opencanvas/prompts/topic_generation_prompt.txt"),
            "content_generation": Path("src/opencanvas/prompts/blog_generation_prompt.txt"),
            "narrative_enhancement": Path("src/opencanvas/prompts/narrative_prompt.txt")
        }
        
        prompt_file = baseline_prompts.get(prompt_type)
        if prompt_file and prompt_file.exists():
            return prompt_file.read_text()
        
        return "# Baseline prompt not found"
    
    def _track_deployed_tools_performance(self, current_iteration: int):
        """
        Track performance with registry integration
        Override parent to use persistent registry
        """
        
        if not hasattr(self, 'evolution_history') or not self.evolution_history:
            logger.warning("No previous iteration data for tool performance tracking")
            return
        
        # Get previous iteration's scores
        previous_iteration = self.evolution_history[-1]
        current_scores = previous_iteration.get('baseline_scores', {})
        
        # Get list of active tools from registry
        active_tools = self.tools_registry.get_active_tools()
        
        for tool in active_tools:
            if tool.iteration_added < current_iteration:
                # Get baseline scores from when tool was added
                baseline_scores = self._get_iteration_scores(tool.iteration_added - 1)
                
                if baseline_scores:
                    # Update registry with performance
                    impact = self.tools_registry.update_tool_performance(
                        tool.name,
                        self._calculate_overall_score(baseline_scores),
                        self._calculate_overall_score(current_scores)
                    )
                    
                    if impact > 0:
                        self.successful_improvements.append(tool.name)
                    else:
                        self.failed_improvements.append(tool.name)
        
        logger.info(f"  📊 Tracked {len(active_tools)} active tools")
        logger.info(f"    ✅ Successful: {len(self.successful_improvements)}")
        logger.info(f"    ❌ Failed: {len(self.failed_improvements)}")
    
    def _get_iteration_scores(self, iteration: int) -> Optional[Dict]:
        """Get scores from a specific iteration"""
        
        for hist in self.evolution_history:
            if hist.get("iteration") == iteration:
                return hist.get("baseline_scores")
        return None
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """Calculate single overall score from multiple metrics"""
        
        if not scores:
            return 0.0
        
        # Weight different aspects
        weights = {
            "visual": 0.3,
            "content_reference_free": 0.3,
            "content_reference_required": 0.2,
            "presentation_overall": 0.2
        }
        
        total = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key in scores:
                total += scores[key] * weight
                total_weight += weight
        
        return total / total_weight if total_weight > 0 else 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status including registry"""
        
        base_status = super().get_system_status()
        
        # Add registry status
        base_status["tools_registry"] = {
            "total_tools": len(self.tools_registry.tools),
            "active": len(self.tools_registry.get_active_tools()),
            "proposed": len(self.tools_registry.get_proposed_tools()),
            "failed": len(self.tools_registry.get_failed_tools())
        }
        
        # Add strategy status
        base_status["strategies"] = {
            "available": len(self.strategies.strategies),
            "successful_improvements": len(self.successful_improvements),
            "failed_improvements": len(self.failed_improvements)
        }
        
        return base_status