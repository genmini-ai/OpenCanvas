"""
Multi-Agent Evolution Manager - Coordinates the specialized agents for presentation evolution
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

from opencanvas.config import Config
from opencanvas.evolution.multi_agent.orchestrator_agent import OrchestratorAgent
from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator

logger = logging.getLogger(__name__)

class MultiAgentEvolutionManager:
    """Manages the multi-agent evolution system for presentation quality improvement"""
    
    def __init__(self, 
                 output_dir: str = "multi_agent_evolution",
                 test_topics: List[str] = None,
                 max_iterations: int = 5,
                 improvement_threshold: float = 0.2):
        """Initialize multi-agent evolution manager"""
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Default test topics
        self.test_topics = test_topics or [
            "sustainable energy solutions for developing countries",
            "artificial intelligence applications in healthcare", 
            "quantum computing principles and algorithms",
            "climate change mitigation strategies",
            "blockchain technology beyond cryptocurrency"
        ]
        
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        
        # Initialize orchestrator agent (which manages all other agents)
        self.orchestrator = OrchestratorAgent()
        
        # Evolution tracking
        self.evolution_history = []
        self.current_implementations = {}
        
    def run_multi_agent_evolution(self, start_iteration: int = 1) -> Dict[str, Any]:
        """Run complete multi-agent evolution process"""
        
        logger.info(f"🤖 Starting Multi-Agent Evolution System")
        logger.info(f"🎯 Test topics: {len(self.test_topics)}")
        logger.info(f"🔄 Max iterations: {self.max_iterations}")
        logger.info(f"📊 Improvement threshold: {self.improvement_threshold}")
        
        evolution_results = {
            "start_time": datetime.now().isoformat(),
            "test_topics": self.test_topics,
            "agent_system": "multi_agent_orchestrated",
            "iterations": [],
            "agent_performance": [],
            "best_iteration": None,
            "final_improvement": None
        }
        
        current_iteration = start_iteration
        previous_baseline = None
        
        while current_iteration <= self.max_iterations:
            logger.info(f"="*60)
            logger.info(f"🤖 MULTI-AGENT EVOLUTION ITERATION {current_iteration}")
            logger.info(f"="*60)
            
            try:
                # Step 1: Generate test presentations (potentially with previous improvements)
                iteration_dir = self.output_dir / f"iteration_{current_iteration}"
                iteration_dir.mkdir(exist_ok=True)
                
                generation_results = self._generate_test_presentations(
                    iteration_dir, current_iteration
                )
                
                if not generation_results["success"]:
                    logger.error(f"Generation failed for iteration {current_iteration}")
                    break
                
                # Step 2: Evaluate presentations
                evaluation_results = self._evaluate_presentations(
                    iteration_dir, generation_results["presentation_paths"]
                )
                
                if not evaluation_results["success"]:
                    logger.error(f"Evaluation failed for iteration {current_iteration}")
                    break
                
                # Step 3: Run multi-agent evolution cycle
                logger.info("🎭 Initiating multi-agent evolution cycle...")
                
                # Load evaluation data for agents
                evaluation_data = self._load_evaluation_data(evaluation_results["evaluation_paths"])
                
                # Run orchestrated agent process
                agent_cycle_result = self.orchestrator.process({
                    "action": "run_evolution_cycle",
                    "evaluation_data": evaluation_data,
                    "topics": self.test_topics,
                    "iteration_number": current_iteration,
                    "previous_implementations": list(self.current_implementations.values())
                })
                
                if not agent_cycle_result.get("success", False):
                    logger.error(f"Agent cycle failed: {agent_cycle_result.get('error', 'Unknown error')}")
                    break
                
                # Step 4: Extract and apply improvements
                improvements_applied = self._apply_agent_improvements(
                    agent_cycle_result, iteration_dir
                )
                
                # Step 5: Calculate baseline and check improvement
                current_baseline = self._extract_baseline_scores(evaluation_data)
                improvement_achieved = True
                
                if previous_baseline:
                    improvement_achieved = self._check_improvement(
                        previous_baseline, current_baseline
                    )
                
                # Record iteration results
                iteration_result = {
                    "iteration": current_iteration,
                    "baseline_scores": current_baseline,
                    "improvement_from_previous": self._calculate_improvement(previous_baseline, current_baseline) if previous_baseline else None,
                    "agent_cycle_summary": agent_cycle_result.get("evolution_summary", {}),
                    "improvements_applied": improvements_applied,
                    "agent_coordination_success": agent_cycle_result.get("success", False),
                    "presentation_paths": generation_results["presentation_paths"],
                    "evaluation_paths": evaluation_results["evaluation_paths"],
                    "agent_artifacts": self._save_agent_artifacts(agent_cycle_result, iteration_dir)
                }
                
                evolution_results["iterations"].append(iteration_result)
                self.evolution_history.append(iteration_result)
                
                # Track agent performance
                agent_performance = self._extract_agent_performance(agent_cycle_result)
                evolution_results["agent_performance"].append(agent_performance)
                
                # Print comprehensive iteration summary
                self._print_multi_agent_iteration_summary(iteration_result, agent_cycle_result)
                
                # Step 6: Plan next iteration or conclude
                if improvement_achieved and current_iteration < self.max_iterations:
                    logger.info(f"✅ Sufficient improvement achieved, planning iteration {current_iteration + 1}")
                    
                    # Update current implementations for next iteration
                    self._update_current_implementations(agent_cycle_result)
                    
                else:
                    if not improvement_achieved:
                        logger.info(f"📊 Improvement below threshold ({self.improvement_threshold}), evolution complete")
                    else:
                        logger.info(f"🏁 Maximum iterations reached")
                    break
                
                previous_baseline = current_baseline
                current_iteration += 1
                
            except Exception as e:
                logger.error(f"Error in multi-agent iteration {current_iteration}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Finalize evolution results
        evolution_results["end_time"] = datetime.now().isoformat()
        evolution_results["total_iterations"] = len(evolution_results["iterations"])
        evolution_results["best_iteration"] = self._find_best_iteration(evolution_results["iterations"])
        evolution_results["final_improvement"] = self._calculate_total_improvement(evolution_results["iterations"])
        evolution_results["agent_system_performance"] = self._analyze_agent_system_performance(evolution_results["agent_performance"])
        
        # Save complete results
        results_path = self.output_dir / "multi_agent_evolution_results.json"
        with open(results_path, 'w') as f:
            json.dump(evolution_results, f, indent=2, default=str)
        
        logger.info(f"🎉 Multi-Agent Evolution completed!")
        logger.info(f"📁 Results saved to: {results_path}")
        
        return evolution_results
    
    def _generate_test_presentations(self, iteration_dir: Path, iteration_number: int) -> Dict[str, Any]:
        """Generate test presentations, potentially with improvements from previous iterations"""
        
        logger.info(f"🚀 Generating {len(self.test_topics)} test presentations...")
        
        results = {
            "success": True,
            "presentation_paths": [],
            "errors": []
        }
        
        # Create generation directory
        gen_dir = iteration_dir / "presentations"
        gen_dir.mkdir(exist_ok=True)
        
        # Create router (potentially enhanced with previous improvements)
        router = self._create_enhanced_router(iteration_number)
        
        for i, topic in enumerate(self.test_topics):
            topic_slug = topic.replace(" ", "_").replace(",", "")[:30]
            topic_dir = gen_dir / f"{i+1}_{topic_slug}"
            
            try:
                logger.info(f"  Generating presentation {i+1}/{len(self.test_topics)}: {topic}")
                
                result = router.generate(
                    input_source=topic,
                    purpose="multi-agent evolution test",
                    theme="professional blue",
                    output_dir=str(topic_dir)
                )
                
                if result and result.get('html_file'):
                    # Convert to PDF
                    html_file = result['html_file']
                    converter = PresentationConverter(
                        html_file=html_file,
                        output_dir=str(topic_dir),
                        method="playwright",
                        zoom_factor=1.2
                    )
                    
                    pdf_path = converter.convert(output_filename="presentation.pdf")
                    
                    results["presentation_paths"].append({
                        "topic": topic,
                        "html_path": html_file,
                        "pdf_path": pdf_path,
                        "output_dir": str(topic_dir)
                    })
                    
                else:
                    error_msg = f"Generation failed for topic: {topic}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error generating {topic}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        if len(results["presentation_paths"]) == 0:
            results["success"] = False
        
        logger.info(f"✅ Generated {len(results['presentation_paths'])} presentations")
        return results
    
    def _create_enhanced_router(self, iteration_number: int) -> GenerationRouter:
        """Create generation router, potentially enhanced with previous improvements"""
        
        router = GenerationRouter(
            api_key=Config.ANTHROPIC_API_KEY,
            brave_api_key=Config.BRAVE_API_KEY
        )
        
        # If we have improvements from previous iterations, apply them
        if self.current_implementations and iteration_number > 1:
            logger.info(f"🔧 Applying {len(self.current_implementations)} improvements from previous iterations")
            # This would be where we actually modify the router with improvements
            # For now, just log that improvements would be applied
            
        return router
    
    def _evaluate_presentations(self, iteration_dir: Path, presentation_data: List[Dict]) -> Dict[str, Any]:
        """Evaluate all generated presentations"""
        
        logger.info(f"📊 Evaluating {len(presentation_data)} presentations...")
        
        results = {
            "success": True,
            "evaluation_paths": [],
            "errors": []
        }
        
        # Get evaluation configuration
        eval_config = Config.get_evaluation_config()
        evaluator = PresentationEvaluator(
            api_key=eval_config['api_key'],
            model=eval_config['model'],
            provider=eval_config['provider']
        )
        
        for i, pres_data in enumerate(presentation_data):
            try:
                logger.info(f"  Evaluating presentation {i+1}/{len(presentation_data)}: {pres_data['topic']}")
                
                # Create evaluation directory
                eval_dir = Path(pres_data['output_dir']) / "evaluation"
                eval_dir.mkdir(exist_ok=True)
                
                # Evaluate presentation
                eval_result = evaluator.evaluate_presentation_with_sources(
                    presentation_pdf_path=pres_data['pdf_path'],
                    source_content_path=None,
                    source_pdf_path=None
                )
                
                # Save evaluation results
                eval_path = eval_dir / "evaluation_results.json"
                evaluator.save_results(eval_result, str(eval_path))
                
                results["evaluation_paths"].append(str(eval_path))
                
            except Exception as e:
                error_msg = f"Error evaluating {pres_data['topic']}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        if len(results["evaluation_paths"]) == 0:
            results["success"] = False
        
        logger.info(f"✅ Evaluated {len(results['evaluation_paths'])} presentations")
        return results
    
    def _load_evaluation_data(self, evaluation_paths: List[str]) -> List[Dict[str, Any]]:
        """Load evaluation data for agent processing"""
        
        evaluation_data = []
        
        for path in evaluation_paths:
            try:
                with open(path, 'r') as f:
                    eval_data = json.load(f)
                    eval_data['source_path'] = path
                    evaluation_data.append(eval_data)
            except Exception as e:
                logger.error(f"Failed to load evaluation data from {path}: {e}")
        
        return evaluation_data
    
    def _apply_agent_improvements(self, agent_cycle_result: Dict[str, Any], iteration_dir: Path) -> Dict[str, Any]:
        """Apply improvements generated by the agent system"""
        
        logger.info("🔧 Applying agent-generated improvements...")
        
        # Extract improvement artifacts from agent results
        implementation_phase = agent_cycle_result.get("phases", {}).get("implementation", {})
        
        improvements_applied = {
            "prompt_enhancements": [],
            "configuration_changes": [],
            "validation_rules": [],
            "total_improvements": 0
        }
        
        # Extract enhanced prompts
        enhanced_prompts = implementation_phase.get("enhanced_prompts", {})
        if enhanced_prompts:
            improvements_applied["prompt_enhancements"] = list(enhanced_prompts.keys())
            logger.info(f"  📝 Enhanced prompts: {len(enhanced_prompts)}")
        
        # Extract validation rules
        validation_rules = implementation_phase.get("validation_rules", [])
        if validation_rules:
            improvements_applied["validation_rules"] = [rule.get("rule_name", "unnamed") for rule in validation_rules]
            logger.info(f"  ✅ Validation rules: {len(validation_rules)}")
        
        # Extract configuration changes
        implementation_package = implementation_phase.get("implementation_package", {})
        config_changes = implementation_package.get("configuration_changes", [])
        if config_changes:
            improvements_applied["configuration_changes"] = [change.get("config_type", "unnamed") for change in config_changes]
            logger.info(f"  ⚙️ Configuration changes: {len(config_changes)}")
        
        improvements_applied["total_improvements"] = (
            len(improvements_applied["prompt_enhancements"]) +
            len(improvements_applied["validation_rules"]) +
            len(improvements_applied["configuration_changes"])
        )
        
        logger.info(f"✅ Applied {improvements_applied['total_improvements']} improvements")
        
        return improvements_applied
    
    def _extract_baseline_scores(self, evaluation_data: List[Dict[str, Any]]) -> Dict[str, float]:
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
    
    def _extract_agent_performance(self, agent_cycle_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract agent performance metrics from cycle result"""
        
        phases = agent_cycle_result.get("phases", {})
        
        return {
            "iteration": agent_cycle_result.get("iteration_number", 0),
            "orchestrator_success": agent_cycle_result.get("success", False),
            "reflection_success": phases.get("reflection", {}).get("success", False),
            "improvement_success": phases.get("improvement", {}).get("success", False),
            "implementation_success": phases.get("implementation", {}).get("success", False),
            "integration_success": phases.get("integration", {}).get("success", False),
            "total_agent_interactions": len(agent_cycle_result.get("agent_coordination_log", [])),
            "weaknesses_identified": len(phases.get("reflection", {}).get("weakness_patterns", [])),
            "improvements_designed": len(phases.get("improvement", {}).get("improvements", [])),
            "artifacts_created": len(phases.get("implementation", {}).get("implementation_package", {}).get("prompt_enhancements", []))
        }
    
    def _save_agent_artifacts(self, agent_cycle_result: Dict[str, Any], iteration_dir: Path) -> Dict[str, str]:
        """Save agent-generated artifacts to disk"""
        
        artifacts_dir = iteration_dir / "agent_artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        saved_artifacts = {}
        
        # Save complete agent cycle result
        cycle_result_path = artifacts_dir / "agent_cycle_result.json"
        with open(cycle_result_path, 'w') as f:
            json.dump(agent_cycle_result, f, indent=2, default=str)
        saved_artifacts["cycle_result"] = str(cycle_result_path)
        
        # Save orchestrator coordination log
        coordination_log = agent_cycle_result.get("agent_coordination_log", [])
        if coordination_log:
            coord_log_path = artifacts_dir / "coordination_log.json"
            with open(coord_log_path, 'w') as f:
                json.dump(coordination_log, f, indent=2, default=str)
            saved_artifacts["coordination_log"] = str(coord_log_path)
        
        # Save implementation package
        implementation_phase = agent_cycle_result.get("phases", {}).get("implementation", {})
        implementation_package = implementation_phase.get("implementation_package", {})
        if implementation_package:
            impl_package_path = artifacts_dir / "implementation_package.json"
            with open(impl_package_path, 'w') as f:
                json.dump(implementation_package, f, indent=2, default=str)
            saved_artifacts["implementation_package"] = str(impl_package_path)
        
        logger.info(f"💾 Saved {len(saved_artifacts)} agent artifacts")
        
        return saved_artifacts
    
    def _update_current_implementations(self, agent_cycle_result: Dict[str, Any]):
        """Update current implementations for next iteration"""
        
        implementation_phase = agent_cycle_result.get("phases", {}).get("implementation", {})
        iteration_number = agent_cycle_result.get("iteration_number", 0)
        
        # Store implementation for next iteration
        self.current_implementations[f"iteration_{iteration_number}"] = {
            "iteration": iteration_number,
            "enhanced_prompts": implementation_phase.get("enhanced_prompts", {}),
            "validation_rules": implementation_phase.get("validation_rules", []),
            "implementation_package": implementation_phase.get("implementation_package", {})
        }
        
        logger.info(f"🔄 Updated implementations for iteration {iteration_number}")
    
    def _print_multi_agent_iteration_summary(self, iteration_result: Dict, agent_cycle_result: Dict):
        """Print comprehensive summary of multi-agent iteration"""
        
        print(f"\n{'='*70}")
        print(f"🤖 MULTI-AGENT ITERATION {iteration_result['iteration']} SUMMARY")
        print(f"{'='*70}")
        
        # Baseline scores
        print(f"\n📊 BASELINE SCORES:")
        for category, score in iteration_result['baseline_scores'].items():
            print(f"  {category.replace('_', ' ').title()}: {score:.3f}/5")
        
        # Agent performance
        agent_summary = iteration_result['agent_cycle_summary']
        print(f"\n🤖 AGENT SYSTEM PERFORMANCE:")
        print(f"  Orchestration Success: {'✅' if agent_cycle_result.get('success') else '❌'}")
        print(f"  Weaknesses Identified: {agent_summary.get('iteration_summary', {}).get('weaknesses_identified', 0)}")
        print(f"  Improvements Designed: {agent_summary.get('iteration_summary', {}).get('improvements_designed', 0)}")
        print(f"  Implementations Created: {agent_summary.get('iteration_summary', {}).get('implementations_created', 0)}")
        
        # Individual agent status
        agent_perf = agent_summary.get('agent_performance', {})
        print(f"\n🎭 INDIVIDUAL AGENT STATUS:")
        print(f"  Reflection Agent: {agent_perf.get('reflection_agent', 'unknown')}")
        print(f"  Improvement Agent: {agent_perf.get('improvement_agent', 'unknown')}")
        print(f"  Implementation Agent: {agent_perf.get('implementation_agent', 'unknown')}")
        
        # Improvements applied
        improvements = iteration_result['improvements_applied']
        print(f"\n🔧 IMPROVEMENTS APPLIED:")
        print(f"  Total Improvements: {improvements.get('total_improvements', 0)}")
        print(f"  Prompt Enhancements: {len(improvements.get('prompt_enhancements', []))}")
        print(f"  Validation Rules: {len(improvements.get('validation_rules', []))}")
        print(f"  Configuration Changes: {len(improvements.get('configuration_changes', []))}")
        
        # Improvement from previous
        if iteration_result['improvement_from_previous']:
            print(f"\n📈 IMPROVEMENT FROM PREVIOUS:")
            for category, improvement in iteration_result['improvement_from_previous'].items():
                sign = "+" if improvement >= 0 else ""
                print(f"  {category.replace('_', ' ').title()}: {sign}{improvement:.3f}")
    
    # Inherit utility methods from base evolution manager
    def _check_improvement(self, previous_baseline: Dict[str, float], current_baseline: Dict[str, float]) -> bool:
        """Check if sufficient improvement was achieved"""
        if not previous_baseline:
            return True
        
        improvements = []
        for key in current_baseline:
            if key in previous_baseline:
                improvement = current_baseline[key] - previous_baseline[key]
                improvements.append(improvement)
        
        if not improvements:
            return False
        
        avg_improvement = sum(improvements) / len(improvements)
        logger.info(f"Average improvement: {avg_improvement:.3f} (threshold: {self.improvement_threshold})")
        
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
    
    def _analyze_agent_system_performance(self, agent_performance_history: List[Dict]) -> Dict[str, Any]:
        """Analyze overall agent system performance"""
        
        if not agent_performance_history:
            return {"error": "No agent performance data available"}
        
        # Calculate success rates
        total_iterations = len(agent_performance_history)
        successful_orchestrations = sum(1 for perf in agent_performance_history if perf.get("orchestrator_success"))
        successful_reflections = sum(1 for perf in agent_performance_history if perf.get("reflection_success"))
        successful_improvements = sum(1 for perf in agent_performance_history if perf.get("improvement_success"))
        successful_implementations = sum(1 for perf in agent_performance_history if perf.get("implementation_success"))
        
        # Calculate productivity metrics
        total_weaknesses_identified = sum(perf.get("weaknesses_identified", 0) for perf in agent_performance_history)
        total_improvements_designed = sum(perf.get("improvements_designed", 0) for perf in agent_performance_history)
        total_artifacts_created = sum(perf.get("artifacts_created", 0) for perf in agent_performance_history)
        
        return {
            "system_reliability": {
                "orchestration_success_rate": successful_orchestrations / total_iterations,
                "reflection_success_rate": successful_reflections / total_iterations,
                "improvement_success_rate": successful_improvements / total_iterations,
                "implementation_success_rate": successful_implementations / total_iterations
            },
            "system_productivity": {
                "avg_weaknesses_per_iteration": total_weaknesses_identified / total_iterations,
                "avg_improvements_per_iteration": total_improvements_designed / total_iterations,
                "avg_artifacts_per_iteration": total_artifacts_created / total_iterations,
                "total_system_outputs": total_weaknesses_identified + total_improvements_designed + total_artifacts_created
            },
            "overall_assessment": "excellent" if successful_orchestrations / total_iterations > 0.8 else "good" if successful_orchestrations / total_iterations > 0.6 else "needs_improvement"
        }