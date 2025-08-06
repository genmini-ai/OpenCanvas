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
        
        # Evolution state
        self.evolution_history = []
        self.current_baseline = {}
        
        logger.info(f"🚀 Evolution system initialized")
        logger.info(f"📁 Output: {output_dir}")
        logger.info(f"🎯 Topics: {len(self.test_topics)}")
        logger.info(f"🔄 Max iterations: {max_iterations}")
    
    def run_evolution_cycle(self, start_iteration: int = 1) -> Dict[str, Any]:
        """Run complete evolution cycle"""
        
        logger.info(f"🔄 Starting evolution cycle from iteration {start_iteration}")
        
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
                    logger.error(f"Iteration {current_iteration} failed")
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
        
        iteration_dir = self.output_dir / f"iteration_{iteration_number}"
        iteration_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Iteration directory: {iteration_dir}")
        
        try:
            # Step 1: Generate test presentations
            generation_result = self._generate_test_presentations(iteration_dir, iteration_number)
            if not generation_result["success"]:
                return {"success": False, "error": "Generation failed", "iteration": iteration_number}
            
            # Step 2: Evaluate presentations
            evaluation_result = self._evaluate_presentations(iteration_dir, generation_result["presentations"])
            if not evaluation_result["success"]:
                return {"success": False, "error": "Evaluation failed", "iteration": iteration_number}
            
            # Step 3: Run agent-based analysis and improvement
            agent_result = self.orchestrator.process({
                "action": "run_evolution_cycle",
                "evaluation_data": evaluation_result["evaluation_data"], 
                "topics": self.test_topics,
                "iteration_number": iteration_number,
                "previous_implementations": []
            })
            
            if not agent_result.get("success"):
                return {"success": False, "error": "Agent cycle failed", "iteration": iteration_number}
            
            # Step 4: Apply improvements (prompts and tools)
            improvements_result = self._apply_improvements(agent_result, iteration_number)
            
            # Step 5: Calculate baseline scores
            baseline_scores = self._extract_baseline_scores(evaluation_result["evaluation_data"])
            
            # Prepare iteration result
            iteration_result = {
                "success": True,
                "iteration": iteration_number,
                "baseline_scores": baseline_scores,
                "improvement_from_previous": self._calculate_improvement(previous_baseline, baseline_scores) if previous_baseline else {},
                "agent_analysis": agent_result.get("evolution_summary", {}),
                "improvements_applied": improvements_result,
                "presentations_generated": len(generation_result["presentations"]),
                "evaluation_data": evaluation_result["evaluation_data"],
                "tools_discovered": improvements_result.get("tools_discovered", []),
                "tools_adopted": improvements_result.get("tools_adopted", [])
            }
            
            # Print iteration summary
            self._print_iteration_summary(iteration_result)
            
            return iteration_result
            
        except Exception as e:
            logger.error(f"❌ Single iteration failed: {e}")
            return {"success": False, "error": str(e), "iteration": iteration_number}
    
    def _generate_test_presentations(self, iteration_dir: Path, iteration_number: int) -> Dict[str, Any]:
        """Generate test presentations for evaluation"""
        
        logger.info(f"🚀 Generating {len(self.test_topics)} test presentations")
        
        presentations_dir = iteration_dir / "presentations"
        presentations_dir.mkdir(exist_ok=True)
        
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
                    
                    presentations.append({
                        "topic": topic,
                        "html_path": result['html_file'],
                        "pdf_path": pdf_path,
                        "output_dir": str(topic_dir)
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
        
        for presentation in presentations:
            try:
                eval_result = evaluator.evaluate_presentation_with_sources(
                    presentation_pdf_path=presentation['pdf_path'],
                    source_content_path=None,
                    source_pdf_path=None
                )
                
                # Add source info
                eval_result['source_path'] = presentation['topic']
                eval_result['topic'] = presentation['topic']
                evaluation_data.append(eval_result)
                
            except Exception as e:
                errors.append(f"Evaluation failed for {presentation['topic']}: {e}")
        
        success = len(evaluation_data) > 0
        logger.info(f"✅ Evaluated {len(evaluation_data)} presentations ({len(errors)} errors)")
        
        return {
            "success": success,
            "evaluation_data": evaluation_data,
            "errors": errors
        }
    
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
            # Create prompt evolution iteration
            improvements = []
            for enhancement in prompt_enhancements:
                improvements.append({
                    "name": f"Prompt enhancement {enhancement.get('prompt_type', 'unknown')}",
                    "description": enhancement.get('key_enhancements', []),
                    "solution_type": "prompt_enhancement"
                })
            
            baseline_scores = self._extract_baseline_from_agent_result(agent_result)
            self.prompt_manager.create_iteration(iteration_number, improvements, baseline_scores)
            results["prompts_evolved"] = len(prompt_enhancements)
        
        # Handle tool discoveries
        proposed_tools = implementation_package.get("proposed_tools", [])
        for tool_spec in proposed_tools:
            discovery_result = self.tools_manager.propose_tool(tool_spec)
            if discovery_result["success"]:
                results["tools_discovered"].append({
                    "name": tool_spec["name"],
                    "priority": discovery_result["priority"],
                    "recommendation": discovery_result["recommendation"]
                })
        
        # TODO: Tool testing and adoption would happen in real implementation
        # For now, just track discoveries
        
        results["total_improvements"] = results["prompts_evolved"] + len(results["tools_discovered"])
        
        logger.info(f"✅ Applied {results['total_improvements']} improvements")
        
        return results
    
    def _extract_baseline_scores(self, evaluation_data: List[Dict]) -> Dict[str, float]:
        """Extract baseline scores from evaluation data"""
        
        baseline = {}
        score_collections = {}
        
        for eval_data in evaluation_data:
            overall_scores = eval_data.get("overall_scores", {})
            for category, score in overall_scores.items():
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
            if 'presentation_overall' in iteration['baseline_scores']:
                score = iteration['baseline_scores']['presentation_overall']
                if score > best_score:
                    best_score = score
                    best_iteration = iteration
        
        return best_iteration
    
    def _calculate_total_improvement(self, iterations: List[Dict]) -> Optional[Dict]:
        """Calculate total improvement from first to last iteration"""
        
        if len(iterations) < 2:
            return None
        
        first = iterations[0]['baseline_scores']
        last = iterations[-1]['baseline_scores']
        
        return self._calculate_improvement(first, last)
    
    def _print_iteration_summary(self, iteration_result: Dict):
        """Print summary of iteration results"""
        
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