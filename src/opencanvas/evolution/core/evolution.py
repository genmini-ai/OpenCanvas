"""
Main Evolution Logic - Simplified orchestration of the complete evolution system
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from opencanvas.config import Config
from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator

from .agents import EvolutionAgent
from .tools import ToolsManager, ToolDiscovery
from .prompts import PromptManager

logger = logging.getLogger(__name__)

class EvolutionSystem:
    """
    Main evolution system that orchestrates agents, tools, and prompts
    for systematic presentation quality improvement
    """
    
    def __init__(self, 
                 output_dir: str = "evolution_output",
                 test_topics: List[str] = None,
                 max_iterations: int = 5,
                 improvement_threshold: float = 0.2):
        """Initialize evolution system"""
        
        logger.info(f"🔧 Initializing EvolutionSystem with output_dir={output_dir}, max_iterations={max_iterations}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test topics for evolution cycles
        self.test_topics = test_topics or [
            "sustainable energy solutions for developing countries",
            "artificial intelligence applications in healthcare", 
            "quantum computing principles and algorithms",
            "climate change mitigation strategies",
            "blockchain technology beyond cryptocurrency"
        ]
        
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        
        # Initialize core components
        self.tools_manager = ToolsManager()
        self.prompt_manager = PromptManager()
        self.orchestrator = EvolutionAgent("orchestrator")
        
        # Initialize checkpoint manager for production baseline
        from ..checkpoints import CheckpointManager
        self.checkpoint_manager = CheckpointManager()
        logger.info(f"📦 Using baseline checkpoint from production code")
        
        # Initialize automatic tool implementation (human review optional)
        from .tool_implementation import AutomaticToolImplementation
        self.tool_implementation = AutomaticToolImplementation(require_human_review=False)
        logger.info(f"🤖 Automatic tool implementation enabled (auto-deploy mode)")
        
        # Evolution state
        self.evolution_history = []
        self.current_baseline = {}
        
        logger.info(f"🚀 Evolution system initialized")
        logger.info(f"📁 Output: {output_dir}")
        logger.info(f"🎯 Topics: {len(self.test_topics)}")
        logger.info(f"🔄 Max iterations: {max_iterations}")
    
    def run_evolution_cycle(self, start_iteration: int = 1) -> Dict[str, Any]:
        """Run complete evolution cycle"""
        
        logger.info("="*70)
        logger.info(f"🔄 Starting evolution cycle from iteration {start_iteration}")
        logger.info(f"📋 Topics: {self.test_topics}")
        logger.info(f"🔢 Max iterations: {self.max_iterations}")
        logger.info(f"📊 Improvement threshold: {self.improvement_threshold}")
        logger.info("="*70)
        
        evolution_results = {
            "start_time": datetime.now().isoformat(),
            "test_topics": self.test_topics,
            "system_type": "unified_evolution_system",
            "iterations": [],
            "tools_discovered": [],
            "tools_adopted": [],
            "best_iteration": None,
            "final_improvement": None
        }
        
        current_iteration = start_iteration
        previous_baseline = None
        
        while current_iteration <= self.max_iterations:
            logger.info(f"🔄 EVOLUTION ITERATION {current_iteration}")
            
            try:
                # Run single iteration
                iteration_result = self._run_single_iteration(current_iteration, previous_baseline)
                
                if not iteration_result["success"]:
                    logger.error(f"❌ Iteration {current_iteration} failed: {iteration_result.get('error', 'Unknown error')}")
                    logger.error(f"Full iteration result: {json.dumps(iteration_result, indent=2, default=str)}")
                    # Add failed iteration to results so we can see what happened
                    evolution_results["iterations"].append(iteration_result)
                    break
                
                evolution_results["iterations"].append(iteration_result)
                self.evolution_history.append(iteration_result)
                
                # Update baseline
                current_baseline = iteration_result["baseline_scores"]
                
                # Check if we should continue
                if previous_baseline:
                    improvement_achieved = self._check_improvement(previous_baseline, current_baseline)
                    if not improvement_achieved:
                        logger.info(f"📊 Improvement below threshold, stopping at iteration {current_iteration}")
                        break
                
                # Update tools discovered/adopted
                if iteration_result.get("tools_discovered"):
                    evolution_results["tools_discovered"].extend(iteration_result["tools_discovered"])
                if iteration_result.get("tools_adopted"):
                    evolution_results["tools_adopted"].extend(iteration_result["tools_adopted"])
                
                previous_baseline = current_baseline
                current_iteration += 1
                
            except Exception as e:
                logger.error(f"❌ Iteration {current_iteration} failed: {e}")
                break
        
        # Finalize results
        evolution_results["end_time"] = datetime.now().isoformat()
        evolution_results["total_iterations"] = len(evolution_results["iterations"])
        evolution_results["best_iteration"] = self._find_best_iteration(evolution_results["iterations"])
        evolution_results["final_improvement"] = self._calculate_total_improvement(evolution_results["iterations"])
        
        # Save results
        results_path = self.output_dir / "evolution_results.json"
        with open(results_path, 'w') as f:
            json.dump(evolution_results, f, indent=2, default=str)
        
        logger.info(f"🎉 Evolution cycle complete!")
        logger.info(f"📁 Results: {results_path}")
        
        return evolution_results
    
    def _run_single_iteration(self, iteration_number: int, previous_baseline: Optional[Dict] = None) -> Dict[str, Any]:
        """Run a single evolution iteration"""
        
        logger.info(f"🚀 Starting iteration {iteration_number}")
        
        iteration_dir = self.output_dir / f"iteration_{iteration_number}"
        iteration_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Iteration directory: {iteration_dir}")
        
        try:
            # Step 0: Track performance of tools deployed in previous iterations
            if hasattr(self, '_tools_to_track') and self._tools_to_track and iteration_number > 1:
                logger.info("📊 Step 0: Tracking performance of previously deployed tools...")
                self._track_deployed_tools_performance(iteration_number)
            
            # Step 1: Generate test presentations
            logger.info(f"📝 Step 1: Generating {len(self.test_topics)} test presentations...")
            generation_result = self._generate_test_presentations(iteration_dir, iteration_number)
            if not generation_result["success"]:
                logger.error(f"❌ Generation failed: {generation_result.get('errors', 'No error details')}")
                return {"success": False, "error": f"Generation failed: {generation_result.get('errors', [])}", "iteration": iteration_number}
            
            # Step 2: Evaluate presentations
            logger.info(f"📊 Step 2: Evaluating {len(generation_result['presentations'])} presentations...")
            evaluation_result = self._evaluate_presentations(iteration_dir, generation_result["presentations"])
            if not evaluation_result["success"]:
                logger.error(f"❌ Evaluation failed: {evaluation_result.get('errors', 'No error details')}")
                return {"success": False, "error": f"Evaluation failed: {evaluation_result.get('errors', [])}", "iteration": iteration_number}
            
            # Step 3: Run agent-based analysis and improvement
            logger.info("🤖 Step 3: Running agent-based analysis...")
            agent_result = self.orchestrator.process({
                "action": "plan_evolution_cycle",
                "evaluation_data": evaluation_result["evaluation_data"], 
                "topics": self.test_topics,
                "iteration_number": iteration_number,
                "previous_implementations": []
            })
            
            if not agent_result.get("success"):
                logger.error(f"❌ Agent analysis failed: {agent_result.get('error', 'No error details')}")
                return {"success": False, "error": f"Agent cycle failed: {agent_result.get('error', 'Unknown')}", "iteration": iteration_number}
            
            # Step 4: Apply improvements (prompts and tools)
            logger.info("🔧 Step 4: Applying improvements...")
            improvements_result = self._apply_improvements(agent_result, iteration_number)
            
            # Step 5: Calculate baseline scores
            logger.info("📊 Step 5: Calculating baseline scores...")
            baseline_scores = self._extract_baseline_scores(evaluation_result["evaluation_data"])
            logger.info(f"  📈 Baseline scores: {json.dumps(baseline_scores, indent=2)}")
            
            # Prepare iteration result
            # Extract tools from agent result (orchestrator returns these)
            tools_discovered = agent_result.get("tools_discovered", [])
            tools_adopted = agent_result.get("tools_adopted", [])
            
            # Also include any tools from improvements
            if improvements_result.get("tools_discovered"):
                tools_discovered.extend(improvements_result["tools_discovered"])
            if improvements_result.get("tools_adopted"):
                tools_adopted.extend(improvements_result["tools_adopted"])
            
            iteration_result = {
                "success": True,
                "iteration": iteration_number,
                "baseline_scores": baseline_scores,
                "improvement_from_previous": self._calculate_improvement(previous_baseline, baseline_scores) if previous_baseline else {},
                "agent_analysis": agent_result.get("evolution_summary", {}),
                "improvements_applied": improvements_result,
                "presentations_generated": len(generation_result["presentations"]),
                "evaluation_data": evaluation_result["evaluation_data"],
                "tools_discovered": tools_discovered,
                "tools_adopted": tools_adopted
            }
            
            # Print iteration summary
            self._print_iteration_summary(iteration_result)
            
            return iteration_result
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Single iteration failed: {e}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return {"success": False, "error": str(e), "iteration": iteration_number, "traceback": traceback.format_exc()}
    
    def _generate_test_presentations(self, iteration_dir: Path, iteration_number: int) -> Dict[str, Any]:
        """Generate test presentations for evaluation"""
        
        logger.info(f"🚀 Generating {len(self.test_topics)} test presentations")
        
        presentations_dir = iteration_dir / "presentations"
        presentations_dir.mkdir(exist_ok=True)
        
        # Use evolved prompts if available (after iteration 1)
        if iteration_number > 1:
            from .evolved_router import EvolvedGenerationRouter
            router = EvolvedGenerationRouter(
                api_key=Config.ANTHROPIC_API_KEY,
                brave_api_key=Config.BRAVE_API_KEY,
                evolution_iteration=iteration_number
            )
        else:
            logger.info(f"📦 Using BASELINE prompts (first iteration)")
            router = GenerationRouter(
                api_key=Config.ANTHROPIC_API_KEY,
                brave_api_key=Config.BRAVE_API_KEY
            )
        
        presentations = []
        errors = []
        
        for i, topic in enumerate(self.test_topics):
            try:
                topic_slug = topic.replace(" ", "_").replace(",", "")[:30]
                topic_dir = presentations_dir / f"{i+1}_{topic_slug}"
                
                result = router.generate(
                    input_source=topic,
                    purpose="evolution testing",
                    theme="professional blue", 
                    output_dir=str(topic_dir)
                )
                
                if result and result.get('html_file'):
                    # Convert to PDF
                    converter = PresentationConverter(
                        html_file=result['html_file'],
                        output_dir=str(topic_dir),
                        method="playwright",
                        zoom_factor=1.2
                    )
                    pdf_path = converter.convert(output_filename="presentation.pdf")
                    
                    # Save source content for reference-required evaluation
                    source_content_path = None
                    if result.get('blog_content'):
                        source_content_path = topic_dir / "sources" / "source_content.txt"
                        source_content_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(source_content_path, 'w', encoding='utf-8') as f:
                            f.write(result['blog_content'])
                        logger.info(f"    📝 Saved source content for evaluation: {source_content_path.name}")
                    
                    presentations.append({
                        "topic": topic,
                        "html_path": result['html_file'],
                        "pdf_path": pdf_path,
                        "source_content_path": str(source_content_path) if source_content_path else None,
                        "output_dir": str(topic_dir),
                        "result": result  # Keep full result for reference
                    })
                else:
                    errors.append(f"Generation failed for: {topic}")
                    
            except Exception as e:
                errors.append(f"Error with {topic}: {e}")
        
        success = len(presentations) > 0
        logger.info(f"✅ Generated {len(presentations)} presentations ({len(errors)} errors)")
        
        return {
            "success": success,
            "presentations": presentations,
            "errors": errors
        }
    
    def _evaluate_presentations(self, iteration_dir: Path, presentations: List[Dict]) -> Dict[str, Any]:
        """Evaluate generated presentations"""
        
        logger.info(f"📊 Evaluating {len(presentations)} presentations")
        
        eval_config = Config.get_evaluation_config()
        evaluator = PresentationEvaluator(
            api_key=eval_config['api_key'],
            model=eval_config['model'],
            provider=eval_config['provider']
        )
        
        evaluation_data = []
        errors = []
        
        for i, presentation in enumerate(presentations, 1):
            try:
                logger.info(f"  📊 Evaluating presentation {i}/{len(presentations)}: {presentation['topic'][:50]}...")
                
                # Use evaluate_presentation_with_sources WITH source content
                # This enables reference-required evaluation for content accuracy
                eval_result = evaluator.evaluate_presentation_with_sources(
                    presentation_pdf_path=presentation['pdf_path'],
                    source_content_path=presentation.get('source_content_path'),  # Use saved source content
                    source_pdf_path=None  # No PDF source (using text source)
                )
                
                # Convert dataclass to dict and log the evaluation scores
                if eval_result:
                    # Convert EvaluationResult dataclass to dict
                    from dataclasses import asdict
                    eval_dict = asdict(eval_result) if hasattr(eval_result, '__dataclass_fields__') else eval_result
                    
                    overall_scores = eval_dict.get('overall_scores', {}) if isinstance(eval_dict, dict) else {}
                    if overall_scores:
                        logger.info(f"    ✅ Evaluation scores for '{presentation['topic'][:30]}':")
                        logger.info(f"      - Visual Design: {overall_scores.get('visual_design', 0):.2f}/5.0")
                        logger.info(f"      - Content Quality: {overall_scores.get('content_quality', 0):.2f}/5.0")
                        logger.info(f"      - Overall Score: {overall_scores.get('overall_score', 0):.2f}/5.0")
                    else:
                        logger.warning(f"    ⚠️  No overall scores available for '{presentation['topic'][:30]}'")
                    
                    # Add source info
                    eval_dict['source_path'] = presentation['topic']
                    eval_dict['topic'] = presentation['topic']
                    evaluation_data.append(eval_dict)
                
            except Exception as e:
                logger.error(f"    ❌ Evaluation failed for {presentation['topic']}: {e}")
                errors.append(f"Evaluation failed for {presentation['topic']}: {e}")
        
        success = len(evaluation_data) > 0
        
        # Calculate and log aggregate metrics
        if evaluation_data:
            avg_scores = self._calculate_average_scores(evaluation_data)
            logger.info("📈 EVALUATION SUMMARY:")
            logger.info(f"  - Average Visual Design: {avg_scores.get('visual_design', 0):.2f}/5.0")
            logger.info(f"  - Average Content Quality: {avg_scores.get('content_quality', 0):.2f}/5.0")
            logger.info(f"  - Average Overall Score: {avg_scores.get('overall_score', 0):.2f}/5.0")
            logger.info(f"  - Total Presentations Evaluated: {len(evaluation_data)}")
            logger.info(f"  - Evaluation Errors: {len(errors)}")
        
        logger.info(f"✅ Evaluation phase complete: {len(evaluation_data)} successful, {len(errors)} errors")
        
        return {
            "success": success,
            "evaluation_data": evaluation_data,
            "errors": errors,
            "average_scores": avg_scores if evaluation_data else {}
        }
    
    def _calculate_average_scores(self, evaluation_data: List[Dict]) -> Dict[str, float]:
        """Calculate average scores across all evaluations"""
        score_sums = {}
        score_counts = {}
        
        for eval_data in evaluation_data:
            overall_scores = eval_data.get('overall_scores', {})
            # Handle None or empty overall_scores
            if not overall_scores:
                logger.warning("Evaluation data missing overall_scores")
                continue
                
            for key, value in overall_scores.items():
                if isinstance(value, (int, float)):
                    if key not in score_sums:
                        score_sums[key] = 0
                        score_counts[key] = 0
                    score_sums[key] += value
                    score_counts[key] += 1
        
        avg_scores = {}
        for key in score_sums:
            if score_counts[key] > 0:
                avg_scores[key] = score_sums[key] / score_counts[key]
        
        return avg_scores
    
    def _apply_improvements(self, agent_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Apply improvements from agent analysis"""
        
        logger.info("🔧 Applying evolution improvements")
        
        results = {
            "prompts_evolved": 0,
            "tools_discovered": [],
            "tools_adopted": [],
            "total_improvements": 0
        }
        
        # Extract improvements from agent results
        implementation_phase = agent_result.get("phases", {}).get("implementation", {})
        implementation_package = implementation_phase.get("implementation_package", {})
        
        # Apply prompt improvements
        prompt_enhancements = implementation_package.get("prompt_enhancements", [])
        if prompt_enhancements:
            logger.info(f"  📝 Applying {len(prompt_enhancements)} prompt enhancements:")
            # Create prompt evolution iteration
            improvements = []
            for enhancement in prompt_enhancements:
                prompt_type = enhancement.get('prompt_type', 'unknown')
                key_enhancements = enhancement.get('key_enhancements', [])
                logger.info(f"    - {prompt_type} prompt:")
                for enh in key_enhancements[:3]:  # Log first 3 enhancements
                    logger.info(f"      • {enh[:100]}...")
                
                improvements.append({
                    "name": f"Prompt enhancement {prompt_type}",
                    "description": key_enhancements,
                    "solution_type": "prompt_enhancement"
                })
            
            baseline_scores = self._extract_baseline_from_agent_result(agent_result)
            self.prompt_manager.create_iteration(iteration_number, improvements, baseline_scores)
            results["prompts_evolved"] = len(prompt_enhancements)
        
        # Handle tool discoveries and AUTOMATIC IMPLEMENTATION
        proposed_tools = implementation_package.get("proposed_tools", [])
        if proposed_tools:
            logger.info(f"  🔧 Processing {len(proposed_tools)} tool proposals:")
        
        for tool_spec in proposed_tools:
            tool_name = tool_spec.get("name", "Unknown")
            logger.info(f"    - Proposing: {tool_name}")
            
            # First, log to TOOLS.md
            discovery_result = self.tools_manager.propose_tool(tool_spec)
            if discovery_result["success"]:
                logger.info(f"      ✅ Added to TOOLS.md with {discovery_result['priority']} priority")
                logger.info(f"      📋 Recommendation: {discovery_result['recommendation']}")
                
                # NOW: Actually implement the tool automatically!
                if discovery_result["priority"] in ["high", "medium"]:
                    logger.info(f"      🤖 AUTO-IMPLEMENTING {tool_name}...")
                    implementation_result = self.tool_implementation.implement_tool_from_spec(
                        tool_spec, 
                        iteration_number
                    )
                    
                    if implementation_result["success"]:
                        if implementation_result["deployed"]:
                            logger.info(f"      🚀 DEPLOYED: {tool_name} is now active!")
                            results["tools_adopted"].append(tool_name)
                            
                            # Schedule performance tracking for next iteration
                            if not hasattr(self, '_tools_to_track'):
                                self._tools_to_track = []
                            self._tools_to_track.append({
                                "tool_name": tool_name,
                                "iteration_deployed": iteration_number,
                                "baseline_scores": self._extract_baseline_from_agent_result(agent_result)
                            })
                            
                        else:
                            logger.info(f"      ⏸️  Implementation complete, deployment pending")
                    else:
                        logger.warning(f"      ❌ Implementation failed: {implementation_result.get('error')}")
                
                results["tools_discovered"].append({
                    "name": tool_name,
                    "priority": discovery_result["priority"],
                    "recommendation": discovery_result["recommendation"],
                    "implemented": implementation_result.get("success", False) if 'implementation_result' in locals() else False
                })
            else:
                logger.warning(f"      ❌ Failed: {discovery_result.get('error', 'Unknown error')}")
        
        # Simulate tool effects if tools were proposed
        if results["tools_discovered"]:
            from .tool_simulator import ToolSimulator
            simulator = ToolSimulator()
            
            # Get current baseline scores
            current_scores = self._extract_baseline_from_agent_result(agent_result)
            
            # Simulate combined effect
            tool_names = [tool["name"] for tool in results["tools_discovered"]]
            simulation = simulator.estimate_combined_effect(tool_names, current_scores)
            
            logger.info(f"  🔮 Tool Simulation Results:")
            logger.info(f"    - Average improvement: {simulation['average_improvement']:.3f}")
            logger.info(f"    - Speed impact: {simulation['total_speed_impact']:.1%}")
            logger.info(f"    - Recommendation: {simulation['recommendation']}")
            
            # Store simulation results
            results["tool_simulation"] = simulation
        
        results["total_improvements"] = results["prompts_evolved"] + len(results["tools_discovered"])
        
        logger.info(f"✅ Applied {results['total_improvements']} improvements")
        
        return results
    
    def _extract_baseline_scores(self, evaluation_data: List[Dict]) -> Dict[str, float]:
        """Extract baseline scores from evaluation data"""
        
        baseline = {}
        score_collections = {}
        
        for eval_data in evaluation_data:
            overall_scores = eval_data.get("overall_scores", {})
            if not overall_scores:
                logger.warning("Skipping evaluation data without overall_scores")
                continue
                
            for category, score in overall_scores.items():
                if isinstance(score, (int, float)):
                    if category not in score_collections:
                        score_collections[category] = []
                    score_collections[category].append(score)
        
        for category, scores in score_collections.items():
            baseline[category] = sum(scores) / len(scores) if scores else 0.0
            
        return baseline
    
    def _extract_baseline_from_agent_result(self, agent_result: Dict[str, Any]) -> Dict[str, float]:
        """Extract baseline from agent result for prompt evolution"""
        
        # This is a simplified extraction - in real implementation would be more sophisticated
        return {
            "visual": 3.0,
            "content_reference_free": 3.5,
            "presentation_overall": 3.25
        }
    
    def _check_improvement(self, previous_baseline: Dict[str, float], current_baseline: Dict[str, float]) -> bool:
        """Check if sufficient improvement was achieved"""
        
        improvements = []
        for key in current_baseline:
            if key in previous_baseline:
                improvement = current_baseline[key] - previous_baseline[key]
                improvements.append(improvement)
        
        if not improvements:
            return False
        
        avg_improvement = sum(improvements) / len(improvements)
        return avg_improvement >= self.improvement_threshold
    
    def _calculate_improvement(self, previous_baseline: Dict[str, float], current_baseline: Dict[str, float]) -> Dict[str, float]:
        """Calculate improvement metrics"""
        
        if not previous_baseline:
            return {}
        
        improvements = {}
        for key in current_baseline:
            if key in previous_baseline:
                improvements[key] = current_baseline[key] - previous_baseline[key]
        
        return improvements
    
    def _find_best_iteration(self, iterations: List[Dict]) -> Optional[Dict]:
        """Find the best performing iteration"""
        
        if not iterations:
            return None
        
        best_iteration = None
        best_score = 0
        
        for iteration in iterations:
            # Skip failed iterations that don't have baseline_scores
            if not iteration.get('success', False) or 'baseline_scores' not in iteration:
                continue
                
            if 'presentation_overall' in iteration['baseline_scores']:
                score = iteration['baseline_scores']['presentation_overall']
                if score > best_score:
                    best_score = score
                    best_iteration = iteration
        
        return best_iteration
    
    def _calculate_total_improvement(self, iterations: List[Dict]) -> Optional[Dict]:
        """Calculate total improvement from first to last iteration"""
        
        # Filter out failed iterations
        successful_iterations = [i for i in iterations if i.get('success', False) and 'baseline_scores' in i]
        
        if len(successful_iterations) < 2:
            return None
        
        first = successful_iterations[0]['baseline_scores']
        last = successful_iterations[-1]['baseline_scores']
        
        return self._calculate_improvement(first, last)
    
    def _track_deployed_tools_performance(self, current_iteration: int):
        """Track performance of tools deployed in previous iterations"""
        
        # Get current evaluation scores to compare with baseline
        if not hasattr(self, 'evolution_history') or not self.evolution_history:
            logger.warning("No previous iteration data for tool performance tracking")
            return
        
        # Use previous iteration's scores as "after" scores
        previous_iteration = self.evolution_history[-1]
        current_scores = previous_iteration.get('baseline_scores', {})
        
        # Track each tool that was deployed
        tools_to_remove = []
        for i, tool_info in enumerate(self._tools_to_track):
            tool_name = tool_info['tool_name']
            deployment_iteration = tool_info['iteration_deployed']
            baseline_scores = tool_info['baseline_scores']
            
            # Only track tools deployed in previous iteration (not current)
            if deployment_iteration < current_iteration:
                logger.info(f"  📈 Tracking {tool_name} (deployed in iteration {deployment_iteration})")
                
                success, improvement = self.tool_implementation.track_tool_performance(
                    tool_name=tool_name,
                    before_scores=baseline_scores,
                    after_scores=current_scores,
                    iteration=current_iteration
                )
                
                if success:
                    logger.info(f"    ✅ {tool_name}: +{improvement:.3f} improvement - SUCCESS")
                else:
                    logger.warning(f"    ❌ {tool_name}: {improvement:.3f} improvement - FAILED")
                
                # Remove from tracking list after evaluation
                tools_to_remove.append(i)
        
        # Remove tracked tools (in reverse order to avoid index issues)
        for i in reversed(tools_to_remove):
            del self._tools_to_track[i]
        
        logger.info(f"  📊 Completed performance tracking for {len(tools_to_remove)} tools")
    
    def _print_iteration_summary(self, iteration_result: Dict):
        """Print summary of iteration results"""
        
        logger.info("="*60)
        logger.info(f"🔄 ITERATION {iteration_result['iteration']} COMPLETE - SUMMARY")
        logger.info("="*60)
        
        # Generation & Evaluation stats
        logger.info(f"📝 Presentations Generated: {iteration_result.get('presentations_generated', 0)}")
        logger.info(f"📊 Evaluations Completed: {len(iteration_result.get('evaluation_data', []))}")
        
        # Baseline scores
        logger.info("📈 BASELINE SCORES (Current Performance):")
        for category, score in iteration_result['baseline_scores'].items():
            logger.info(f"  - {category.replace('_', ' ').title()}: {score:.3f}/5.0")
        
        # Also print to console for visibility
        print(f"\n{'='*60}")
        print(f"🔄 EVOLUTION ITERATION {iteration_result['iteration']} SUMMARY")
        print(f"{'='*60}")
        
        # Baseline scores
        print(f"\n📊 BASELINE SCORES:")
        for category, score in iteration_result['baseline_scores'].items():
            print(f"  {category.replace('_', ' ').title()}: {score:.3f}/5")
        
        # Improvements
        improvements = iteration_result['improvements_applied']
        print(f"\n🔧 IMPROVEMENTS APPLIED:")
        print(f"  Prompts Evolved: {improvements.get('prompts_evolved', 0)}")
        print(f"  Tools Discovered: {len(improvements.get('tools_discovered', []))}")
        print(f"  Total Improvements: {improvements.get('total_improvements', 0)}")
        
        # Improvement from previous
        if iteration_result['improvement_from_previous']:
            print(f"\n📈 IMPROVEMENT FROM PREVIOUS:")
            for category, improvement in iteration_result['improvement_from_previous'].items():
                sign = "+" if improvement >= 0 else ""
                print(f"  {category.replace('_', ' ').title()}: {sign}{improvement:.3f}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        
        return {
            "evolution_system": "unified",
            "components": {
                "tools_manager": self.tools_manager.get_tool_summary(),
                "prompt_manager": {
                    "current_iteration": self.prompt_manager.current_iteration,
                    "evolution_history": len(self.prompt_manager.get_evolution_history()["iterations"])
                },
                "orchestrator": self.orchestrator.get_agent_status()
            },
            "configuration": {
                "max_iterations": self.max_iterations,
                "improvement_threshold": self.improvement_threshold,
                "test_topics": len(self.test_topics)
            },
            "history": {
                "total_iterations_run": len(self.evolution_history),
                "output_directory": str(self.output_dir)
            }
        }