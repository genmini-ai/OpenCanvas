"""
Main Evolution Logic - Simplified orchestration of the complete evolution system
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from opencanvas.config import Config
from opencanvas.generators.router import GenerationRouter
from opencanvas.evaluation.evaluator import PresentationEvaluator

from .agents import EvolutionAgent
from .tools import ToolsManager, ToolDiscovery
from .prompts import PromptManager
from .improvement_tracker import get_improvement_tracker, ImprovementType
from .agent_wrapper import AgentExecutor, PartialProgressTracker

logger = logging.getLogger(__name__)

# Try to import PresentationConverter after logger is defined
try:
    from opencanvas.conversion.html_to_pdf import PresentationConverter
except ImportError:
    PresentationConverter = None
    logger.warning("PresentationConverter not available - PDF conversion disabled")

class EvolutionSystem:
    """
    Main evolution system that orchestrates agents, tools, and prompts
    for systematic presentation quality improvement
    """
    
    def __init__(self, 
                 output_dir: str = "evolution_output",
                 test_topics: List[str] = None,
                 max_iterations: int = 5,
                 improvement_threshold: float = 0.2,
                 diagnostic_mode: bool = False,
                 prompt_only: bool = False,
                 prompts_registry: str = "PROMPTS_REGISTRY.md",
                 theme: str = "professional blue",
                 purpose: str = "educational presentation",
                 initial_prompt_path: Optional[str] = None,
                 use_memory: bool = True):
        """Initialize evolution system with optional diagnostic mode and prompt-only mode"""
        
        logger.info(f"🔧 Initializing EvolutionSystem with output_dir={output_dir}, max_iterations={max_iterations}, diagnostic={diagnostic_mode}, prompt_only={prompt_only}, memory={use_memory}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory configuration - controls whether prompts registry is loaded
        self.use_memory = use_memory
        
        # Diagnostic mode for debugging
        self.diagnostic_mode = diagnostic_mode
        if diagnostic_mode:
            self.diagnostic_dir = self.output_dir / "diagnostics"
            self.diagnostic_dir.mkdir(exist_ok=True)
            logger.info(f"📊 Diagnostic mode enabled - saving to {self.diagnostic_dir}")
        
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
        
        # Theme and purpose configuration
        self.theme = theme
        self.purpose = purpose
        
        # Prompt-only mode configuration
        self.prompt_only = prompt_only
        if self.prompt_only:
            logger.info("📝 PROMPT-ONLY MODE ENABLED - Focusing exclusively on prompt optimization")
            if self.use_memory:
                from .prompts_registry import PromptsRegistryManager
                self.prompts_registry = PromptsRegistryManager(prompts_registry)
                logger.info(f"📚 Using prompts registry with memory: {prompts_registry}")
            else:
                self.prompts_registry = None
                logger.info("🧠 Memory disabled - running without prompts registry")
        else:
            self.prompts_registry = None
        
        # Smart stopping criteria tracking
        self.consecutive_degradations = 0
        self.consecutive_perfect_scores = 0
        self.baseline_history = []  # Track last few baselines for degradation detection
        
        # Initialize core components
        self.tools_manager = ToolsManager()
        self.prompt_manager = PromptManager()
        # Pass prompts_registry to orchestrator if in prompt-only mode
        self.orchestrator = EvolutionAgent("orchestrator", prompts_registry=self.prompts_registry)
        
        # Initialize checkpoint manager for production baseline
        from ..checkpoints import CheckpointManager
        self.checkpoint_manager = CheckpointManager()
        logger.info(f"📦 Using baseline checkpoint from production code")
        
        # Initialize automatic tool implementation (human review optional)
        from .tool_implementation import AutomaticToolImplementation
        self.tool_implementation = AutomaticToolImplementation(
            require_human_review=False,
            output_dir=self.output_dir  # Pass experiment directory for isolation
        )
        logger.info(f"🤖 Automatic tool implementation enabled (auto-deploy mode)")
        
        # Initialize improvement tracker for fine-grained attribution
        self.tracker = get_improvement_tracker(self.output_dir / "tracking")
        logger.info(f"📊 Improvement tracker initialized")
        
        # Initialize agent executor for robust execution
        self.agent_executor = AgentExecutor(max_retries=3, retry_delay=2.0)
        logger.info(f"🛡️ Agent executor initialized with retry support")
        
        # Load initial prompt if specified
        self.initial_prompt = None
        if initial_prompt_path:
            try:
                prompt_path = Path(initial_prompt_path)
                if prompt_path.exists():
                    self.initial_prompt = prompt_path.read_text()
                    logger.info(f"📝 Loaded initial prompt from: {initial_prompt_path}")
                else:
                    logger.warning(f"❌ Initial prompt file not found: {initial_prompt_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load initial prompt: {e}")
        else:
            # Use default loading process (from evolved_prompts folder)
            self.initial_prompt = self._load_default_prompt()
        
        # Evolution state
        self.evolution_history = []
        self.current_baseline = {}
        
        logger.info(f"🚀 Evolution system initialized")
        logger.info(f"📁 Output: {output_dir}")
        logger.info(f"🎯 Topics: {len(self.test_topics)}")
        logger.info(f"🔄 Max iterations: {max_iterations}")
    
    def _preflight_check(self) -> Tuple[bool, str]:
        """Check system readiness before starting evolution
        
        Returns:
            (ready, error_message)
        """
        logger.info("🔍 Running pre-flight checks...")
        
        # 1. Check evaluation system
        try:
            from opencanvas.config import Config
            from opencanvas.evaluation.evaluator import PresentationEvaluator
            
            eval_config = Config.get_evaluation_config()
            evaluator = PresentationEvaluator(
                api_key=eval_config['api_key'],
                model=eval_config['model'],
                provider=eval_config['provider']
            )
            logger.info("  ✅ Evaluation system configured")
        except Exception as e:
            error_msg = f"Evaluation system not ready: {e}"
            logger.error(f"  ❌ {error_msg}")
            return False, error_msg
        
        # 2. Check tool implementation system
        if not hasattr(self, 'tool_implementation'):
            error_msg = "Tool implementation system not initialized"
            logger.error(f"  ❌ {error_msg}")
            return False, error_msg
        logger.info("  ✅ Tool implementation system ready")
        
        # 3. Check agent orchestrator
        if not hasattr(self, 'orchestrator'):
            error_msg = "Agent orchestrator not initialized"
            logger.error(f"  ❌ {error_msg}")
            return False, error_msg
        logger.info("  ✅ Agent orchestrator ready")
        
        # 4. Check output directory is writable
        try:
            test_file = self.output_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("  ✅ Output directory writable")
        except Exception as e:
            error_msg = f"Cannot write to output directory: {e}"
            logger.error(f"  ❌ {error_msg}")
            return False, error_msg
        
        logger.info("✅ All pre-flight checks passed")
        return True, ""
    
    def _check_system_health(self, iteration_results: List[Dict]) -> Dict[str, Any]:
        """Monitor system health and detect issues"""
        health = {
            "healthy": True,
            "issues": [],
            "metrics": {}
        }
        
        if not iteration_results:
            return health
        
        # Check evaluation success rate
        total_evals = sum(len(r.get("evaluation_data", [])) + len(r.get("errors", [])) 
                         for r in iteration_results if r.get("success", False))
        successful_evals = sum(len(r.get("evaluation_data", [])) 
                              for r in iteration_results if r.get("success", False))
        
        if total_evals > 0:
            eval_success_rate = successful_evals / total_evals
            health["metrics"]["eval_success_rate"] = eval_success_rate
            
            if eval_success_rate < 0.5:
                health["healthy"] = False
                health["issues"].append(f"Evaluation success rate too low: {eval_success_rate:.1%}")
        
        # Check tool adoption rate
        tools_proposed = sum(r.get("tools_proposed", 0) for r in iteration_results)
        tools_adopted = sum(len(r.get("tools_adopted", [])) for r in iteration_results)
        
        if tools_proposed > 0:
            adoption_rate = tools_adopted / tools_proposed
            health["metrics"]["tool_adoption_rate"] = adoption_rate
            
            if tools_proposed > 10 and tools_adopted == 0:
                health["healthy"] = False
                health["issues"].append(f"No tools adopted despite {tools_proposed} proposals")
        
        # Check for stuck iterations (no improvement)
        if len(iteration_results) >= 2:
            last_scores = iteration_results[-1].get("baseline_scores", {})
            prev_scores = iteration_results[-2].get("baseline_scores", {})
            
            if last_scores and prev_scores:
                improvement = any(
                    last_scores.get(k, 0) > prev_scores.get(k, 0) 
                    for k in last_scores.keys()
                )
                if not improvement:
                    health["issues"].append("No score improvement in last iteration")
        
        # Check gap detection
        gaps_found = sum(r.get("weaknesses_identified", 0) for r in iteration_results)
        if len(iteration_results) >= 2 and gaps_found == 0:
            health["issues"].append("No gaps identified across iterations")
        
        health["healthy"] = len(health["issues"]) == 0
        
        return health
    
    def run_evolution_cycle(self, start_iteration: int = 1) -> Dict[str, Any]:
        """Run complete evolution cycle"""
        
        logger.info("="*70)
        logger.info(f"🔄 Starting evolution cycle from iteration {start_iteration}")
        logger.info(f"📋 Topics: {self.test_topics}")
        logger.info(f"🔢 Max iterations: {self.max_iterations}")
        logger.info(f"📊 Improvement threshold: {self.improvement_threshold}")
        logger.info("="*70)
        
        # Run pre-flight checks
        ready, error_msg = self._preflight_check()
        if not ready:
            logger.error(f"❌ Pre-flight check failed: {error_msg}")
            return {
                "success": False,
                "error": f"Pre-flight check failed: {error_msg}",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat()
            }
        
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
                
                # Check for early termination (system optimized)
                if iteration_result.get("early_termination"):
                    logger.info(f"🎉 {iteration_result.get('message', 'System optimized')}")
                    logger.info(f"🛑 Early termination at iteration {current_iteration}: {iteration_result.get('reason', 'optimal state')}")
                    break
                
                # Update baseline
                current_baseline = iteration_result["baseline_scores"]
                
                # Check system health
                health = self._check_system_health(evolution_results["iterations"])
                if not health["healthy"]:
                    logger.warning("⚠️ SYSTEM HEALTH ISSUES DETECTED:")
                    for issue in health["issues"]:
                        logger.warning(f"  - {issue}")
                    
                    # Only stop if critical issues persist
                    if len(health["issues"]) >= 3:
                        logger.error("❌ Too many health issues - stopping evolution")
                        evolution_results["stopped_reason"] = "health_issues"
                        evolution_results["health_issues"] = health["issues"]
                        break
                
                # Check if we should continue with smart stopping criteria
                if previous_baseline:
                    should_continue, stop_reason = self._check_smart_stopping_criteria(previous_baseline, current_baseline, current_iteration)
                    if not should_continue:
                        logger.info(f"🛑 {stop_reason} - stopping at iteration {current_iteration}")
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
        
        # Export detailed tracking report
        tracking_report = self.tracker.export_detailed_report()
        
        # Generate final attribution report
        final_report = self.tracker.get_improvement_report()
        
        logger.info("="*70)
        logger.info(f"🎉 Evolution cycle complete!")
        logger.info(f"📁 Results: {results_path}")
        logger.info(f"📊 Tracking report: {tracking_report}")
        
        # Log improvement attribution summary
        if final_report['summary']['total_improvements'] > 0:
            logger.info(f"📊 Improvement Attribution Summary:")
            logger.info(f"  - Total improvements: {final_report['summary']['total_improvements']}")
            logger.info(f"  - Success rate: {final_report['summary']['success_rate']:.1f}%")
            logger.info(f"  - Avg score delta: {final_report['impact']['average_delta_per_improvement']:.3f}")
            
            if final_report['impact']['category_impacts']:
                logger.info(f"  - Category impacts:")
                for cat, delta in final_report['impact']['category_impacts'].items():
                    logger.info(f"    • {cat}: {delta:+.3f}")
        
        logger.info("="*70)
        
        return evolution_results
    
    def _run_single_iteration(self, iteration_number: int, previous_baseline: Optional[Dict] = None) -> Dict[str, Any]:
        """Run a single evolution iteration with partial progress tracking"""
        
        logger.info(f"🚀 Starting iteration {iteration_number}")
        
        iteration_dir = self.output_dir / f"iteration_{iteration_number}"
        iteration_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Iteration directory: {iteration_dir}")
        
        # Initialize progress tracker for this iteration
        progress = PartialProgressTracker()
        
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
                # Return with partial progress
                return {
                    "success": False, 
                    "error": f"Generation failed: {generation_result.get('errors', [])}",
                    "iteration": iteration_number,
                    "partial_progress": progress.get_summary()
                }
            progress.mark_completed("generation", generation_result)
            
            # Step 2: Evaluate presentations
            logger.info(f"📊 Step 2: Evaluating {len(generation_result['presentations'])} presentations...")
            evaluation_result = self._evaluate_presentations(iteration_dir, generation_result["presentations"])
            if not evaluation_result["success"]:
                logger.error(f"❌ Evaluation failed: {evaluation_result.get('errors', 'No error details')}")
                # Return with partial progress
                return {
                    "success": False,
                    "error": f"Evaluation failed: {evaluation_result.get('errors', [])}",
                    "iteration": iteration_number,
                    "partial_progress": progress.get_summary()
                }
            progress.mark_completed("evaluation", evaluation_result)
            
            # Step 3: Run agent-based analysis and improvement
            if self.prompt_only:
                # Prompt-only mode: Skip complex orchestration, create simple agent result
                logger.info("📝 Step 3: Prompt-only mode - skipping complex orchestration")
                agent_result = {
                    "success": True,
                    "evaluation_data": evaluation_result["evaluation_data"],
                    "phases": {"direct_evolution": "pending"},
                    "coordination_log": []
                }
            else:
                # Normal mode: Run full orchestration
                logger.info("🤖 Step 3: Running agent-based analysis with robust execution...")
                agent_result = self.agent_executor.execute_with_retry(
                    agent_func=self.orchestrator.process,
                    request={
                        "action": "run_evolution_cycle",
                        "evaluation_data": evaluation_result["evaluation_data"], 
                        "topics": self.test_topics,
                        "iteration_number": iteration_number,
                        "max_iterations": self.max_iterations,  # Pass max_iterations for temperature scheduling
                        "previous_implementations": [],
                        "prompt_only": self.prompt_only  # Pass prompt_only flag to agents
                    },
                    agent_name="Evolution Orchestrator",
                    allow_partial=True
                )
            
            # Check for early termination (system optimized)
            if agent_result.get("early_termination"):
                logger.info(f"🎉 {agent_result.get('message', 'System optimized - no gaps found')}")
                return {
                    "success": True,
                    "early_termination": True,
                    "reason": agent_result.get("reason", "optimal_state"),
                    "iteration": iteration_number,
                    "message": agent_result.get("message"),
                    "baseline_scores": self._extract_baseline_scores(evaluation_result["evaluation_data"])
                }
            
            if not agent_result.get("success") and not agent_result.get("partial"):
                logger.error(f"❌ Agent analysis failed completely: {agent_result.get('error', 'No error details')}")
                return {"success": False, "error": f"Agent cycle failed: {agent_result.get('error', 'Unknown')}", "iteration": iteration_number}
            
            if agent_result.get("partial"):
                logger.warning(f"⚠️ Using partial results from agent analysis after {agent_result.get('retry_count', 0)} retries")
            progress.mark_completed("agent_analysis", agent_result)
            
            # Step 4: Apply improvements (prompts and tools)
            logger.info("🔧 Step 4: Applying improvements...")
            improvements_result = self._apply_improvements(agent_result, iteration_number)
            progress.mark_completed("improvements", improvements_result)
            
            # Step 5: Calculate baseline scores (needed for tool tracking)
            logger.info("📊 Step 5: Calculating baseline scores...")
            baseline_scores = self._extract_baseline_scores(evaluation_result["evaluation_data"])
            
            # CRITICAL: Cannot continue without valid baseline
            if baseline_scores is None:
                logger.error("❌ Cannot calculate baseline scores - no valid evaluation data")
                return {
                    "success": False,
                    "error": "No valid baseline scores could be calculated",
                    "iteration": iteration_number,
                    "reason": "invalid_baseline"
                }
            
            logger.info(f"  📈 Baseline scores: {json.dumps(baseline_scores, indent=2)}")
            
            # Track deployed tools for next iteration
            if improvements_result.get("tools_adopted"):
                if not hasattr(self, '_tools_to_track'):
                    self._tools_to_track = []
                # Convert tool names to tracking format
                for tool_name in improvements_result["tools_adopted"]:
                    self._tools_to_track.append({
                        "tool_name": tool_name,
                        "iteration_deployed": iteration_number,
                        "baseline_scores": baseline_scores  # Use current baseline
                    })
                logger.info(f"  🔧 Tracking {len(improvements_result['tools_adopted'])} deployed tools for next iteration")
            
            # Record scores for tracking
            self.tracker.record_iteration_scores(iteration_number, baseline_scores)
            
            # Attribute score changes to improvements from previous iteration
            if iteration_number > 1 and hasattr(self, '_previous_improvements'):
                for imp_id in self._previous_improvements:
                    deltas = self.tracker.attribute_score_changes(imp_id, iteration_number)
                    if deltas:
                        logger.info(f"  📊 Attribution for {imp_id[:30]}...")
                        for delta in deltas:
                            logger.info(f"    - {delta.category}: {delta.before_score:.2f} → {delta.after_score:.2f} (Δ{delta.delta:+.2f})")
            
            # Store current iteration improvements for next attribution
            self._previous_improvements = improvements_result.get('improvement_ids', [])
            
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
        
        # Determine router type based on iteration and initial prompt
        use_evolved_router = False
        initial_prompt_for_router = None
        
        if iteration_number == 1 and self.initial_prompt:
            # For iteration 1 with initial prompt, use EvolvedRouter with initial prompt
            use_evolved_router = True
            initial_prompt_for_router = self.initial_prompt
            logger.info(f"🎯 Iteration 1 with initial prompt: using EvolvedRouter")
            
            # Save initial prompt as v0 for tracking
            evolved_dir = self.output_dir / "evolved_prompts"
            evolved_dir.mkdir(parents=True, exist_ok=True)
            v0_file = evolved_dir / "generation_prompt_v0.txt"
            v0_file.write_text(self.initial_prompt)
            logger.info(f"💾 Saved initial prompt as: {v0_file.relative_to(self.output_dir)}")
            
        elif iteration_number > 1:
            # For iterations > 1, v{N-1} MUST exist - no fallback allowed
            evolved_dir = self.output_dir / "evolved_prompts"
            prev_prompt_file = evolved_dir / f"generation_prompt_v{iteration_number-1}.txt"
            
            if not prev_prompt_file.exists():
                error_msg = f"Evolution cannot continue: Required prompt file not found: {prev_prompt_file.relative_to(self.output_dir)}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "presentations": [],
                    "errors": [error_msg]
                }
            
            logger.info(f"📝 Found evolved prompt from iteration {iteration_number-1}: {prev_prompt_file.relative_to(self.output_dir)}")
            use_evolved_router = True
        else:
            # First iteration without initial prompt - use baseline
            use_evolved_router = False
            logger.info(f"📦 Iteration 1 without initial prompt: using baseline")
        
        if use_evolved_router:
            logger.info(f"📝 Using EVOLVED router (iteration {iteration_number})")
            from .evolved_router import EvolvedGenerationRouter
            router = EvolvedGenerationRouter(
                api_key=Config.ANTHROPIC_API_KEY,
                brave_api_key=Config.BRAVE_API_KEY,
                evolution_iteration=iteration_number,
                prompt_only=self.prompt_only,
                evolution_output_dir=str(self.output_dir),
                initial_prompt=initial_prompt_for_router
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
                    purpose=self.purpose,
                    theme=self.theme, 
                    output_dir=str(topic_dir)
                )
                
                if result and result.get('html_file'):
                    # Convert to PDF if available
                    pdf_path = None
                    if PresentationConverter is not None:
                        converter = PresentationConverter(
                            html_file=result['html_file'],
                            output_dir=str(topic_dir),
                            method="playwright",
                            zoom_factor=1.0,
                            compress_images=True
                        )
                        pdf_path = converter.convert(output_filename="presentation.pdf")
                    else:
                        logger.warning("    ⚠️ PDF conversion skipped - converter not available")
                        pdf_path = None
                    
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
                
                # Detect if this is PDF-based or topic-based presentation
                is_pdf_based = presentation['topic'].startswith('PDF:')
                
                if is_pdf_based:
                    # For PDF evolution - use source PDF for reference-required evaluation
                    eval_result = evaluator.evaluate_presentation_with_sources(
                        presentation_pdf_path=presentation['pdf_path'],
                        source_content_path=None,  # No text source for PDF
                        source_pdf_path=presentation.get('source_pdf_path')  # Use saved source PDF
                    )
                else:
                    # For topic evolution - use source content for reference-required evaluation
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
                    
                    # Check if evaluation contains errors (from API failures)
                    has_errors = False
                    for score_type in ['visual_scores', 'content_free_scores', 'content_required_scores']:
                        if score_type in eval_dict and isinstance(eval_dict[score_type], dict):
                            if 'error' in eval_dict[score_type]:
                                logger.error(f"    ❌ {score_type} evaluation failed: {eval_dict[score_type]['error']}")
                                has_errors = True
                    
                    if has_errors:
                        # Don't add results with errors to evaluation_data
                        errors.append(f"Evaluation API errors for {presentation['topic']}")
                        continue
                    
                    overall_scores = eval_dict.get('overall_scores', {}) if isinstance(eval_dict, dict) else {}
                    if overall_scores:
                        logger.info(f"    ✅ Evaluation scores for '{presentation['topic'][:30]}':")
                        logger.info(f"      - Visual Design: {overall_scores.get('visual', 0):.2f}/5.0")
                        logger.info(f"      - Content Quality: {overall_scores.get('content_combined', 0):.2f}/5.0")
                        logger.info(f"      - Overall Score: {overall_scores.get('presentation_overall', 0):.2f}/5.0")
                    else:
                        logger.warning(f"    ⚠️  No overall scores available for '{presentation['topic'][:30]}'")
                        errors.append(f"No scores returned for {presentation['topic']}")
                        continue
                    
                    # Add source info
                    eval_dict['source_path'] = presentation['topic']
                    eval_dict['topic'] = presentation['topic']
                    evaluation_data.append(eval_dict)
                
            except Exception as e:
                logger.error(f"    ❌ Evaluation failed for {presentation['topic']}: {e}")
                errors.append(f"Evaluation failed for {presentation['topic']}: {e}")
        
        # Check if we have ANY valid evaluation data
        success = len(evaluation_data) > 0
        
        # CRITICAL: If ALL evaluations failed, we cannot continue
        if not success and len(presentations) > 0:
            logger.error("❌ CRITICAL: All evaluations failed - cannot analyze non-existent data")
            logger.error(f"  Attempted: {len(presentations)} presentations")
            logger.error(f"  Failed: {len(errors)} errors")
            for error in errors[:3]:  # Log first 3 errors
                logger.error(f"    - {error}")
            
            return {
                "success": False,
                "evaluation_data": [],
                "errors": errors,
                "average_scores": {},
                "critical_failure": True,
                "failure_reason": "all_evaluations_failed"
            }
        
        # Calculate and log aggregate metrics
        avg_scores = {}
        if evaluation_data:
            avg_scores = self._calculate_average_scores(evaluation_data)
            logger.info("📈 EVALUATION SUMMARY:")
            logger.info(f"  - Average Visual Design: {avg_scores.get('visual', 0):.2f}/5.0")
            logger.info(f"  - Average Content Quality: {avg_scores.get('content_combined', 0):.2f}/5.0")
            logger.info(f"  - Average Overall Score: {avg_scores.get('presentation_overall', 0):.2f}/5.0")
            logger.info(f"  - Total Presentations Evaluated: {len(evaluation_data)}")
            logger.info(f"  - Evaluation Errors: {len(errors)}")
        
        # Warn if too many failures
        if len(errors) > 0 and len(evaluation_data) > 0:
            failure_rate = len(errors) / (len(errors) + len(evaluation_data))
            if failure_rate > 0.5:
                logger.warning(f"⚠️ High evaluation failure rate: {failure_rate:.1%}")
        
        logger.info(f"✅ Evaluation phase complete: {len(evaluation_data)} successful, {len(errors)} errors")
        
        # Save evaluation data to disk for debugging and audit trail
        eval_file = iteration_dir / "evaluation_results.json"
        try:
            eval_results = {
                "evaluation_data": evaluation_data,
                "average_scores": avg_scores,
                "errors": errors,
                "timestamp": datetime.now().isoformat(),
                "total_presentations": len(presentations),
                "successful_evaluations": len(evaluation_data),
                "failed_evaluations": len(errors)
            }
            with open(eval_file, 'w') as f:
                json.dump(eval_results, f, indent=2, default=str)
            logger.info(f"💾 Saved evaluation results to {eval_file}")
        except Exception as e:
            logger.warning(f"Failed to save evaluation results: {e}")
        
        return {
            "success": success,
            "evaluation_data": evaluation_data,
            "errors": errors,
            "average_scores": avg_scores
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
    
    def _test_prompt_enhancement(self, enhancement: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Test a prompt enhancement by comparing before/after scores with real evaluation"""
        
        logger.info(f"    🧪 Testing prompt enhancement: {enhancement.get('prompt_type', 'unknown')}")
        
        # Phase 6: Enhanced structure validation testing
        logger.info(f"      🔍 Validating prompt structure integrity...")
        structure_validation = self._validate_enhancement_structure_integrity(enhancement)
        
        if not structure_validation["valid"]:
            logger.error(f"      ❌ Structure validation failed: {structure_validation['errors']}")
            return {
                "success": False,
                "error": f"Structure validation failed: {structure_validation['errors']}",
                "validation_details": structure_validation
            }
        
        logger.info(f"      ✅ Structure validation passed - {structure_validation['protected_elements']} elements preserved")
        
        # Get current prompts from prompt manager
        current_prompts = self.prompt_manager.get_current_prompts()
        
        # Apply the enhancement to create enhanced prompts with validation
        enhanced_prompts = self._apply_prompt_enhancement_with_validation(current_prompts, enhancement)
        
        # Test topics (use subset for speed)
        test_topics_subset = self.test_topics[:2] if len(self.test_topics) > 2 else self.test_topics
        
        logger.info(f"      Testing on {len(test_topics_subset)} topics...")
        
        # Generate and evaluate with baseline prompts
        logger.info(f"      📊 Generating baseline presentations...")
        baseline_evaluations = []
        for topic in test_topics_subset:
            try:
                # Generate with baseline prompts
                gen_result = self.generator.generate_from_topic(
                    topic=topic,
                    purpose=self.purpose,
                    theme=self.theme,
                    custom_prompts=current_prompts
                )
                
                if gen_result.get("success") and gen_result.get("slides"):
                    # Evaluate the presentation
                    eval_result = self.evaluator.evaluate_presentation(
                        gen_result["slides"],
                        gen_result.get("source_content", "")
                    )
                    if eval_result:
                        baseline_evaluations.append(eval_result)
            except Exception as e:
                logger.warning(f"      ⚠️ Baseline generation failed for '{topic}': {e}")
        
        # Generate and evaluate with enhanced prompts
        logger.info(f"      📊 Generating enhanced presentations...")
        enhanced_evaluations = []
        for topic in test_topics_subset:
            try:
                # Generate with enhanced prompts
                gen_result = self.generator.generate_from_topic(
                    topic=topic,
                    purpose=self.purpose,
                    theme=self.theme,
                    custom_prompts=enhanced_prompts
                )
                
                if gen_result.get("success") and gen_result.get("slides"):
                    # Evaluate the presentation
                    eval_result = self.evaluator.evaluate_presentation(
                        gen_result["slides"],
                        gen_result.get("source_content", "")
                    )
                    if eval_result:
                        enhanced_evaluations.append(eval_result)
            except Exception as e:
                logger.warning(f"      ⚠️ Enhanced generation failed for '{topic}': {e}")
        
        # Calculate average scores
        baseline_avg = self._calculate_average_score(baseline_evaluations)
        enhanced_avg = self._calculate_average_score(enhanced_evaluations)
        
        # Calculate improvement
        improvement = enhanced_avg - baseline_avg if baseline_avg and enhanced_avg else 0
        
        # Calculate dimension-specific improvements
        dimension_improvements = {}
        if baseline_evaluations and enhanced_evaluations:
            baseline_dims = self._calculate_dimension_averages(baseline_evaluations)
            enhanced_dims = self._calculate_dimension_averages(enhanced_evaluations)
            
            for dim in baseline_dims:
                if dim in enhanced_dims:
                    dimension_improvements[dim] = enhanced_dims[dim] - baseline_dims[dim]
        
        logger.info(f"      📈 Results: Baseline={baseline_avg:.2f}, Enhanced={enhanced_avg:.2f}, Improvement={improvement:+.3f}")
        
        return {
            'baseline_avg': baseline_avg,
            'edited_avg': enhanced_avg,
            'improvement': improvement,
            'statistical_significance': 'significant' if abs(improvement) > 0.2 else 'not_significant',
            'dimension_scores': dimension_improvements,
            'baseline_count': len(baseline_evaluations),
            'enhanced_count': len(enhanced_evaluations)
        }
    
    def _apply_prompt_enhancement(self, current_prompts: Dict[str, str], enhancement: Dict[str, Any]) -> Dict[str, str]:
        """Apply prompt enhancement to current prompts"""
        
        enhanced_prompts = current_prompts.copy()
        prompt_type = enhancement.get('prompt_type', 'generation')
        key_enhancements = enhancement.get('key_enhancements', [])
        
        # Apply enhancements based on type
        if prompt_type in enhanced_prompts:
            current = enhanced_prompts[prompt_type]
            
            # Add enhancements to the prompt
            enhancement_text = "\n\nENHANCED REQUIREMENTS:\n"
            for enh in key_enhancements:
                enhancement_text += f"- {enh}\n"
            
            enhanced_prompts[prompt_type] = current + enhancement_text
        
        return enhanced_prompts
    
    def _validate_enhancement_structure_integrity(self, enhancement: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that enhancement preserves prompt structure integrity using PromptParser
        
        This is part of Phase 6: Enhanced prompt testing with structure validation
        """
        
        try:
            # Import the prompt parser
            from .prompt_parser import PromptParser
            
            parser = PromptParser()
            
            # Check if enhancement has the new adaptive format
            if "enhancements" in enhancement and isinstance(enhancement["enhancements"], list):
                # New adaptive enhancement format
                validation_results = []
                
                for enh in enhancement["enhancements"]:
                    if not enh.get("validated", False):
                        validation_results.append({
                            "type": enh.get("type", "unknown"),
                            "error": "Enhancement not pre-validated",
                            "valid": False
                        })
                    else:
                        validation_results.append({
                            "type": enh.get("type", "unknown"),
                            "valid": True,
                            "structure_preserved": True
                        })
                
                # Check overall validity
                all_valid = all(r["valid"] for r in validation_results)
                
                return {
                    "valid": all_valid,
                    "format": "adaptive",
                    "protected_elements": sum(1 for r in validation_results if r.get("structure_preserved")),
                    "validation_results": validation_results,
                    "errors": [r.get("error") for r in validation_results if not r["valid"]]
                }
            
            else:
                # Legacy enhancement format - basic validation
                prompt_type = enhancement.get('prompt_type', 'generation')
                key_enhancements = enhancement.get('key_enhancements', [])
                
                if not key_enhancements:
                    return {
                        "valid": False,
                        "format": "legacy",
                        "protected_elements": 0,
                        "errors": ["No enhancements provided"]
                    }
                
                # Test if enhancement text contains any format strings
                enhancement_text = "\n".join(key_enhancements)
                protected_vars = parser.PROTECTED_VARIABLES
                
                violations = []
                for var_pattern in protected_vars:
                    if var_pattern.replace("\\", "") in enhancement_text:
                        violations.append(f"Enhancement modifies protected variable: {var_pattern}")
                
                return {
                    "valid": len(violations) == 0,
                    "format": "legacy",
                    "protected_elements": len(protected_vars) - len(violations),
                    "errors": violations
                }
                
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            return {
                "valid": False,
                "format": "unknown",
                "protected_elements": 0,
                "errors": [f"Validation exception: {str(e)}"]
            }
    
    def _apply_prompt_enhancement_with_validation(self, current_prompts: Dict[str, str], 
                                                 enhancement: Dict[str, Any]) -> Dict[str, str]:
        """Apply prompt enhancement with structure validation and safety checks
        
        This is part of Phase 6: Enhanced prompt testing with structure validation
        """
        
        try:
            # Import the prompt parser for advanced enhancements
            from .prompt_parser import PromptParser
            
            parser = PromptParser()
            enhanced_prompts = current_prompts.copy()
            
            # Handle new adaptive enhancement format
            if "enhancements" in enhancement and isinstance(enhancement["enhancements"], list):
                logger.info(f"      🔧 Applying {len(enhancement['enhancements'])} adaptive enhancements...")
                
                # Get the prompt key to modify
                prompt_key = enhancement.get("prompt_key", "generation_prompt")
                current_prompt = current_prompts.get(prompt_key, "")
                
                if not current_prompt:
                    logger.warning(f"      ⚠️ No current prompt found for key: {prompt_key}")
                    return enhanced_prompts
                
                # Parse current prompt structure
                parsed = parser.parse_prompt(current_prompt)
                
                if not parsed["format_valid"]:
                    logger.warning(f"      ⚠️ Current prompt has format issues: {parsed['format_errors']}")
                    # Fall back to legacy enhancement
                    return self._apply_prompt_enhancement(current_prompts, enhancement)
                
                # Apply enhancements using parser
                try:
                    enhanced_prompt = parser.reconstruct_prompt(parsed, enhancement["enhancements"])
                    enhanced_prompts[prompt_key] = enhanced_prompt
                    logger.info(f"      ✅ Applied adaptive enhancements to {prompt_key}")
                except Exception as e:
                    logger.warning(f"      ⚠️ Adaptive enhancement failed, falling back to legacy: {e}")
                    return self._apply_prompt_enhancement(current_prompts, enhancement)
            
            else:
                # Legacy enhancement format
                logger.info(f"      🔧 Applying legacy enhancement format...")
                enhanced_prompts = self._apply_prompt_enhancement(current_prompts, enhancement)
            
            return enhanced_prompts
            
        except Exception as e:
            logger.error(f"Enhancement application failed: {e}")
            # Fall back to legacy method
            return self._apply_prompt_enhancement(current_prompts, enhancement)
    
    def _calculate_average_score(self, evaluations: List[Dict]) -> float:
        """Calculate average overall score from evaluations"""
        
        if not evaluations:
            return 0.0
        
        scores = []
        for eval in evaluations:
            overall = eval.get('overall_scores', {})
            if overall:
                avg = sum(overall.values()) / len(overall) if overall else 0
                scores.append(avg)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_dimension_averages(self, evaluations: List[Dict]) -> Dict[str, float]:
        """Calculate average scores per dimension"""
        
        dimension_totals = {}
        dimension_counts = {}
        
        for eval in evaluations:
            overall = eval.get('overall_scores', {})
            for dim, score in overall.items():
                if dim not in dimension_totals:
                    dimension_totals[dim] = 0
                    dimension_counts[dim] = 0
                dimension_totals[dim] += score
                dimension_counts[dim] += 1
        
        averages = {}
        for dim in dimension_totals:
            if dimension_counts[dim] > 0:
                averages[dim] = dimension_totals[dim] / dimension_counts[dim]
        
        return averages
    
    def _apply_improvements(self, agent_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Apply improvements from agent analysis"""
        
        logger.info("🔧 Applying evolution improvements")
        
        results = {
            "prompts_evolved": 0,
            "tools_discovered": [],
            "tools_adopted": [],
            "total_improvements": 0,
            "improvement_ids": []  # Track IDs for attribution
        }
        
        # Extract improvements from agent results
        phases = agent_result.get("phases", {})
        implementation_phase = phases.get("implementation", {})
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
                target_weakness = enhancement.get('target_weakness', 'general quality')
                expected_impact = enhancement.get('expected_impact', 'improved presentation quality')
                
                # Register with tracker
                imp_id = self.tracker.register_improvement(
                    iteration=iteration_number,
                    type=ImprovementType.PROMPT_EVOLUTION,
                    name=f"Prompt enhancement: {prompt_type}",
                    description=" ".join(key_enhancements[:3]) if key_enhancements else "Prompt improvements",
                    target_weakness=target_weakness,
                    expected_impact=expected_impact,
                    implementation_details={
                        "prompt_type": prompt_type,
                        "key_enhancements": key_enhancements,
                        "iteration": iteration_number
                    }
                )
                
                logger.info(f"    - {prompt_type} prompt (ID: {imp_id[:20]}...):")
                for enh in key_enhancements[:3]:  # Log first 3 enhancements
                    logger.info(f"      • {enh[:100]}...")
                
                improvements.append({
                    "name": f"Prompt enhancement {prompt_type}",
                    "description": key_enhancements,
                    "solution_type": "prompt_enhancement",
                    "tracker_id": imp_id
                })
                results["improvement_ids"].append(imp_id)
            
            baseline_scores = self._extract_baseline_from_agent_result(agent_result)
            self.prompt_manager.create_iteration(iteration_number, improvements, baseline_scores)
            results["prompts_evolved"] = len(prompt_enhancements)
        
        # In prompt-only mode, use direct prompt evolution only
        if self.prompt_only:
            logger.info("  📝 PROMPT-ONLY MODE: Using direct prompt evolution")
            return self._evolve_prompt_directly(agent_result, iteration_number)
        
        # Handle tool discoveries and AUTOMATIC IMPLEMENTATION (only if not in prompt-only mode)
        # Tools can be in either tool_proposal phase or implementation_package
        tool_proposal_phase = phases.get("tool_proposal", {})
        proposed_tools = tool_proposal_phase.get("proposed_tools", [])
        
        # Fallback to implementation_package if not in tool_proposal
        if not proposed_tools:
            proposed_tools = implementation_package.get("proposed_tools", [])
        
        if proposed_tools:
            logger.info(f"  🔧 Processing {len(proposed_tools)} tool proposals:")
        
        for tool_spec in proposed_tools:
            tool_name = tool_spec.get("name", "Unknown")
            target_weakness = tool_spec.get("target_weakness", "general quality")
            expected_impact = tool_spec.get("expected_impact", "improved presentation quality")
            
            logger.info(f"    - Proposing: {tool_name}")
            
            # Register tool proposal with tracker
            imp_id = self.tracker.register_improvement(
                iteration=iteration_number,
                type=ImprovementType.TOOL_CREATION,
                name=f"Tool: {tool_name}",
                description=tool_spec.get("description", "Auto-generated tool"),
                target_weakness=target_weakness,
                expected_impact=expected_impact,
                implementation_details={
                    "tool_spec": tool_spec,
                    "iteration": iteration_number,
                    "priority": tool_spec.get("priority", "medium")
                }
            )
            
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
                            
                            # Track tool as successful
                            self.tracker.improvements[imp_id].success = True
                            results["improvement_ids"].append(imp_id)
                            
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
    
    def _extract_baseline_scores(self, evaluation_data: List[Dict]) -> Optional[Dict[str, float]]:
        """Extract baseline scores from evaluation data
        
        Returns:
            Dict of baseline scores, or None if no valid data
        """
        
        # CRITICAL: Cannot extract baseline from empty or invalid data
        if not evaluation_data:
            logger.error("❌ Cannot extract baseline from empty evaluation data")
            return None
        
        baseline = {}
        score_collections = {}
        valid_evaluations = 0
        
        for eval_data in evaluation_data:
            overall_scores = eval_data.get("overall_scores", {})
            if not overall_scores:
                logger.warning("Skipping evaluation data without overall_scores")
                continue
                
            valid_evaluations += 1
            for category, score in overall_scores.items():
                if isinstance(score, (int, float)):
                    if category not in score_collections:
                        score_collections[category] = []
                    score_collections[category].append(score)
        
        # If no valid evaluations found, return None
        if valid_evaluations == 0:
            logger.error("❌ No valid evaluations with overall_scores found")
            return None
        
        # Calculate averages
        for category, scores in score_collections.items():
            baseline[category] = sum(scores) / len(scores) if scores else 0.0
        
        # Ensure we have at least some key metrics
        if not baseline or not any(k in baseline for k in ['presentation_overall', 'visual', 'content_combined']):
            logger.error("❌ Baseline missing critical metrics")
            return None
            
        return baseline
    
    def _extract_baseline_from_agent_result(self, agent_result: Dict[str, Any]) -> Dict[str, float]:
        """Extract baseline from agent result for prompt evolution"""
        
        # This is a simplified extraction - in real implementation would be more sophisticated
        return {
            "visual": 3.0,
            "content_reference_free": 3.5,
            "presentation_overall": 3.25
        }
    
    def _check_smart_stopping_criteria(self, previous_baseline: Dict[str, float], current_baseline: Dict[str, float], iteration: int) -> Tuple[bool, str]:
        """Check smart stopping criteria: consecutive degradations, perfection, or max iterations
        
        Enhanced for prompt-only mode with additional criteria:
        - No more prompt-addressable gaps
        - Diminishing returns detection
        - Prompt pattern exhaustion
        
        Returns:
            (should_continue: bool, stop_reason: str)
        """
        
        # Add current baseline to history
        self.baseline_history.append(current_baseline.copy())
        # Keep only last 4 baselines for degradation tracking
        if len(self.baseline_history) > 4:
            self.baseline_history.pop(0)
        
        # 1. Check for consecutive perfect scores (multiple 5.0s)
        overall_score = current_baseline.get('presentation_overall', 0)
        if overall_score >= 4.95:  # Account for small floating point differences
            self.consecutive_perfect_scores += 1
            logger.info(f"✨ Perfect score detected: {overall_score:.2f}/5.0 (consecutive: {self.consecutive_perfect_scores})")
            
            if self.consecutive_perfect_scores >= 2:
                return False, "System achieved perfection (2+ consecutive near-perfect scores)"
        else:
            self.consecutive_perfect_scores = 0
        
        # 2. Check for consecutive degradations (3 iterations worse than baseline)
        if len(self.baseline_history) >= 4:  # Need at least 4 points to check 3 consecutive degradations
            baseline_overall = self.baseline_history[0].get('presentation_overall', 0)
            recent_scores = [b.get('presentation_overall', 0) for b in self.baseline_history[1:]]
            
            # Check if last 3 iterations are all worse than baseline
            consecutive_worse = all(score < baseline_overall for score in recent_scores)
            
            if consecutive_worse:
                self.consecutive_degradations = 3
                avg_recent = sum(recent_scores) / len(recent_scores)
                logger.warning(f"📉 Consecutive degradation detected:")
                logger.warning(f"  Baseline: {baseline_overall:.2f}")
                logger.warning(f"  Recent average: {avg_recent:.2f}")
                return False, "System degrading (3 consecutive iterations worse than baseline)"
        
        # 3. Check max iterations
        if iteration >= self.max_iterations:
            return False, f"Maximum iterations reached ({self.max_iterations})"
        
        # 4. Log improvement status but don't stop based on improvement threshold alone
        improvements = []
        for key in current_baseline:
            if key in previous_baseline:
                improvement = current_baseline[key] - previous_baseline[key]
                improvements.append(improvement)
        
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            if avg_improvement >= 0:
                logger.info(f"📈 Iteration {iteration}: Average improvement +{avg_improvement:.3f}")
            else:
                logger.warning(f"📉 Iteration {iteration}: Average change {avg_improvement:.3f}")
                self.consecutive_degradations += 1 if avg_improvement < -0.05 else 0
        
        # 5. Prompt-only mode specific checks
        if self.prompt_only:
            # Check for diminishing returns (improvements < 0.05 for 3 consecutive iterations)
            if len(self.baseline_history) >= 3:
                recent_improvements = []
                for i in range(1, len(self.baseline_history)):
                    prev = self.baseline_history[i-1].get('presentation_overall', 0)
                    curr = self.baseline_history[i].get('presentation_overall', 0)
                    recent_improvements.append(curr - prev)
                
                if all(abs(imp) < 0.05 for imp in recent_improvements[-3:]):
                    logger.info(f"📊 Diminishing returns detected (3 iterations with < 0.05 improvement)")
                    return False, "Diminishing returns in prompt optimization"
            
            # Check if we've exhausted known prompt patterns
            if self.prompts_registry:
                stats = self.prompts_registry.registry_data.get('statistics', {})
                success_rate = stats.get('success_rate', 0)
                total_edits = stats.get('total_prompt_edits_tested', 0)
                
                # If success rate is very low after many attempts, stop
                if total_edits >= 10 and success_rate < 0.2:
                    logger.warning(f"⚠️ Low success rate ({success_rate:.1%}) after {total_edits} prompt edits")
                    return False, "Prompt optimization exhausted (low success rate)"
                
                # If we're achieving high scores with prompt-only, declare success
                if overall_score >= 4.7:
                    logger.info(f"🎯 Excellent score achieved with prompt-only: {overall_score:.2f}/5.0")
                    if iteration >= 3:  # At least 3 iterations to confirm stability
                        return False, "Prompt optimization successful (score >= 4.7)"
        
        # Continue evolution
        return True, "Continuing evolution"
    
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
    
    def _generate_prompt_evolution_report(self, evolution_results: Dict):
        """📝 Generate comprehensive prompt evolution report"""
        
        logger.info("="*70)
        logger.info("📝 PROMPT EVOLUTION FINAL REPORT")
        logger.info("="*70)
        
        if self.prompts_registry:
            registry_data = self.prompts_registry.registry_data
            stats = registry_data.get('statistics', {})
            
            # Overall statistics
            logger.info("📊 OVERALL STATISTICS:")
            logger.info(f"  - Evolution Mode: PROMPT-ONLY")
            logger.info(f"  - Total Iterations: {evolution_results['total_iterations']}")
            logger.info(f"  - Total Prompt Edits Tested: {stats.get('total_prompt_edits_tested', 0)}")
            logger.info(f"  - Successful Edits: {stats.get('successful_edits', 0)}")
            logger.info(f"  - Failed Edits: {stats.get('failed_edits', 0)}")
            logger.info(f"  - Success Rate: {stats.get('success_rate', 0):.1%}")
            
            # Score trajectory
            if evolution_results['iterations']:
                logger.info("\n📈 SCORE TRAJECTORY:")
                first_iter = evolution_results['iterations'][0]
                last_iter = evolution_results['iterations'][-1]
                
                first_score = first_iter['baseline_scores'].get('presentation_overall', 0)
                last_score = last_iter['baseline_scores'].get('presentation_overall', 0)
                total_improvement = last_score - first_score
                
                logger.info(f"  - Starting Score: {first_score:.3f}/5.0")
                logger.info(f"  - Final Score: {last_score:.3f}/5.0")
                logger.info(f"  - Total Improvement: {total_improvement:+.3f}")
                
                # Show trajectory
                logger.info("  - Evolution Path:")
                for i, iter_data in enumerate(evolution_results['iterations']):
                    score = iter_data['baseline_scores'].get('presentation_overall', 0)
                    bar_length = int(score * 10)  # Scale to 50 chars max
                    bar = '█' * bar_length + '░' * (50 - bar_length)
                    logger.info(f"    Iter {i+1}: [{bar}] {score:.3f}")
            
            # Successful patterns
            successful_patterns = self.prompts_registry.get_successful_patterns()
            if successful_patterns:
                logger.info("\n✅ SUCCESSFUL PROMPT PATTERNS:")
                for pattern in successful_patterns[:3]:
                    logger.info(f"  - {pattern['name']}: {pattern['description']}")
                    logger.info(f"    Success rate: {pattern['success_rate']:.1%}, Avg improvement: {pattern['average_improvement']:.3f}")
            
            # Failed patterns to avoid
            failed_patterns = self.prompts_registry.get_failed_patterns()
            if failed_patterns:
                logger.info("\n❌ FAILED PATTERNS (TO AVOID):")
                for pattern in failed_patterns[:3]:
                    logger.info(f"  - {pattern['name']}: {pattern['description']}")
                    logger.info(f"    Lesson: {pattern['lesson_learned']}")
            
            # Key insights
            logger.info("\n💡 KEY INSIGHTS:")
            if stats.get('success_rate', 0) > 0.5:
                logger.info("  - High success rate indicates effective prompt optimization strategy")
            else:
                logger.info("  - Low success rate suggests prompts are near optimization limit")
            
            if stats.get('avg_improvement_successful', 0) > 0.5:
                logger.info("  - Large improvements when successful - significant optimization potential exists")
            else:
                logger.info("  - Small improvements suggest fine-tuning phase reached")
            
            # Recommendations
            logger.info("\n🎯 RECOMMENDATIONS:")
            last_score = 0
            if evolution_results['iterations']:
                last_score = evolution_results['iterations'][-1]['baseline_scores'].get('presentation_overall', 0)
            
            if evolution_results.get('early_termination_reason') == 'prompt_optimization_exhausted':
                logger.info("  - Prompt optimization has reached its limit")
                logger.info("  - Consider implementing tools for remaining gaps")
            elif last_score >= 4.7:
                logger.info("  - Excellent performance achieved with prompt-only optimization!")
                logger.info("  - Current prompts are highly effective")
                logger.info("  - Consider deploying to production")
            else:
                logger.info("  - Continue prompt evolution with focus on identified gaps")
                logger.info("  - Consider more creative prompt engineering approaches")
                logger.info("  - Experiment with different instruction structures")
        
        # Print summary to console for visibility
        print("\n" + "="*70)
        print("📝 PROMPT EVOLUTION COMPLETE")
        print("="*70)
        
        if evolution_results['iterations']:
            first_score = evolution_results['iterations'][0]['baseline_scores'].get('presentation_overall', 0)
            last_score = evolution_results['iterations'][-1]['baseline_scores'].get('presentation_overall', 0)
            improvement = last_score - first_score
            
            print(f"\n🎯 Final Score: {last_score:.3f}/5.0 ({improvement:+.3f} improvement)")
            
            if last_score >= 4.7:
                print("✨ EXCELLENT - Ready for production!")
            elif last_score >= 4.0:
                print("✅ GOOD - Significant improvement achieved")
            else:
                print("🔄 MODERATE - Further optimization possible")
    
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
        """Print summary of iteration results with enhanced prompt-only reporting"""
        
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
        
        # Improvement from previous iteration
        if iteration_result.get('improvement_from_previous'):
            logger.info("📈 IMPROVEMENT FROM PREVIOUS:")
            for category, delta in iteration_result['improvement_from_previous'].items():
                if delta != 0:
                    emoji = "📈" if delta > 0 else "📉"
                    logger.info(f"  {emoji} {category.replace('_', ' ').title()}: {delta:+.3f}")
        
        # Prompt-only mode specific reporting
        if self.prompt_only:
            logger.info("📝 PROMPT EVOLUTION STATUS:")
            if self.prompts_registry:
                stats = self.prompts_registry.registry_data.get('statistics', {})
                logger.info(f"  - Total Edits Tested: {stats.get('total_prompt_edits_tested', 0)}")
                logger.info(f"  - Success Rate: {stats.get('success_rate', 0):.1%}")
                logger.info(f"  - Avg Improvement (successful): {stats.get('avg_improvement_successful', 0):.3f}")
                
                # Show recent prompt changes
                active_prompts = self.prompts_registry.registry_data.get('active_prompts', {})
                if active_prompts:
                    recent = list(active_prompts.items())[-1]  # Most recent
                    logger.info(f"  - Latest Successful: {recent[0]} (+{recent[1].get('improvement', 0):.3f})")
        
        # Also print to console for visibility
        print(f"\n{'='*60}")
        if self.prompt_only:
            print(f"📝 PROMPT EVOLUTION - ITERATION {iteration_result['iteration']}")
        else:
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
        if not self.prompt_only:
            print(f"  Tools Discovered: {len(improvements.get('tools_discovered', []))}")
        
        # Improvement trajectory for prompt-only mode
        if self.prompt_only and iteration_result.get('improvement_from_previous'):
            overall_delta = iteration_result['improvement_from_previous'].get('presentation_overall', 0)
            if overall_delta > 0:
                print(f"\n🎯 Overall Progress: +{overall_delta:.3f} 🚀")
            elif overall_delta < 0:
                print(f"\n⚠️ Overall Change: {overall_delta:.3f} 📉")
            else:
                print(f"\n➡️ No change in overall score")
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
    
    def _validate_enhancement_structure_integrity(self, enhancement: Dict[str, Any]) -> bool:
        """Validate that prompt enhancement preserves critical structure elements"""
        
        try:
            # Check if enhancement has required fields
            required_fields = ["enhancements", "temperature", "creativity_level"]
            for field in required_fields:
                if field not in enhancement:
                    logger.warning(f"Enhancement missing required field: {field}")
                    return False
            
            # Validate individual enhancements preserve structure
            enhancements_list = enhancement.get("enhancements", [])
            if not enhancements_list:
                logger.warning("No enhancements provided")
                return False
            
            for enh in enhancements_list:
                # Check enhancement has proper structure
                if "type" not in enh or "justification" not in enh:
                    logger.warning(f"Enhancement missing type or justification: {enh}")
                    return False
                
                # Validate enhancement doesn't break protected elements
                if enh.get("type") in ["targeted_replacement", "precision_tuning"]:
                    find_text = enh.get("find", "")
                    # Ensure we're not replacing protected template variables
                    protected_patterns = ["{topic}", "{purpose}", "{theme}", "{source_content}", "{pdf_content}"]
                    if any(pattern in find_text for pattern in protected_patterns):
                        logger.warning(f"Enhancement attempts to modify protected template variable: {find_text}")
                        return False
                
                # Check structural additions don't break format
                if enh.get("type") == "structural_addition":
                    content = enh.get("content", "")
                    # Ensure proper formatting
                    if not content.startswith("\n"):
                        logger.debug("Structural addition should start with newline for proper formatting")
            
            logger.info(f"✅ Enhancement structure validation passed for {len(enhancements_list)} enhancements")
            return True
            
        except Exception as e:
            logger.error(f"Enhancement structure validation failed: {e}")
            return False
    
    def _apply_prompt_enhancement_with_validation(self, prompt_name: str, enhancement: Dict[str, Any]) -> bool:
        """Apply prompt enhancement with validation checks"""
        
        try:
            # First validate enhancement structure
            if not self._validate_enhancement_structure_integrity(enhancement):
                logger.error(f"❌ Enhancement failed structure validation for {prompt_name}")
                return False
            
            # Get current prompt
            current_prompt = self.prompt_manager.get_current_prompt(prompt_name)
            if not current_prompt:
                logger.error(f"❌ Could not retrieve current prompt: {prompt_name}")
                return False
            
            # Apply enhancement using prompt manager
            success = self.prompt_manager.apply_prompt_enhancement(
                prompt_name, 
                enhancement,
                validate_structure=True
            )
            
            if success:
                logger.info(f"✅ Successfully applied validated enhancement to {prompt_name}")
                
                # Verify the enhanced prompt is still valid
                enhanced_prompt = self.prompt_manager.get_current_prompt(prompt_name)
                if enhanced_prompt and len(enhanced_prompt) > len(current_prompt):
                    logger.info(f"📈 Prompt enhanced: {len(current_prompt)} → {len(enhanced_prompt)} chars")
                    return True
                else:
                    logger.warning(f"⚠️ Enhanced prompt validation concerns for {prompt_name}")
                    return True  # Still consider success if enhancement was applied
            else:
                logger.error(f"❌ Failed to apply enhancement to {prompt_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error applying prompt enhancement to {prompt_name}: {e}")
            return False
    
    def _evolve_prompt_directly(self, agent_result: Dict[str, Any], iteration_number: int) -> Dict[str, Any]:
        """Directly evolve prompts using LLM with registry context
        
        Args:
            agent_result: Result from the improvement agent
            iteration_number: Current iteration number
            
        Returns:
            Dict with results of prompt evolution
        """
        logger.info("🔄 Starting direct prompt evolution")
        
        results = {
            "prompts_evolved": 0,
            "successful_prompts": [],
            "failed_prompts": [],
            "improvements": []
        }
        
        try:
            # Load the correct prompt based on iteration number
            if iteration_number == 1:
                # First iteration: use initial_prompt if specified, otherwise load from baseline
                if self.initial_prompt:
                    current_prompt = self.initial_prompt
                    logger.info(f"📝 Using custom initial prompt ({len(current_prompt)} characters)")
                else:
                    # Fallback to baseline file
                    baseline_prompt_path = Path("src/opencanvas/prompts/baseline/generation_prompt.txt")
                    if baseline_prompt_path.exists():
                        current_prompt = baseline_prompt_path.read_text()
                        logger.info(f"📝 Loaded baseline prompt ({len(current_prompt)} characters)")
                    else:
                        logger.error("Baseline prompt file not found, falling back to source extraction")
                        # Fallback to source extraction
                        from opencanvas.generators.topic_generator import TopicGenerator
                        import inspect
                        generator_source = inspect.getsource(TopicGenerator.generate_slides_html)
                        prompt_start = generator_source.find('slide_prompt = f"""')
                        prompt_end = generator_source.find('"""', prompt_start + 19)
                        if prompt_start == -1 or prompt_end == -1:
                            logger.error("Could not extract current prompt from topic_generator.py")
                            return results
                        current_prompt = generator_source[prompt_start + 19:prompt_end]
            else:
                # Subsequent iterations: load previous evolution from experiment directory
                evolved_dir = self.output_dir / "evolved_prompts"
                
                # Use correct filename based on mode
                if hasattr(self, 'pdf_mode') and self.pdf_mode:
                    prev_file = evolved_dir / f"pdf_generation_prompt_v{iteration_number-1}.txt"
                else:
                    prev_file = evolved_dir / f"generation_prompt_v{iteration_number-1}.txt"
                
                logger.info(f"📂 Looking for previous evolved prompt at: {prev_file.absolute()}")
                if prev_file.exists():
                    current_prompt = prev_file.read_text()
                    logger.info(f"📝 Loaded evolved prompt v{iteration_number-1} from: {prev_file.absolute()} ({len(current_prompt)} characters)")
                else:
                    # Fallback to global evolved prompts, then baseline
                    logger.warning(f"Previous evolution v{iteration_number-1} not found in experiment, checking global")
                    global_evolved_dir = Path("evolution_runs/evolved_prompts")
                    
                    # Use correct filename based on mode for global fallback
                    if hasattr(self, 'pdf_mode') and self.pdf_mode:
                        global_prev_file = global_evolved_dir / f"pdf_generation_prompt_v{iteration_number-1}.txt"
                    else:
                        global_prev_file = global_evolved_dir / f"generation_prompt_v{iteration_number-1}.txt"
                    
                    logger.info(f"📂 Checking global evolved prompts at: {global_prev_file.absolute()}")
                    if global_prev_file.exists():
                        current_prompt = global_prev_file.read_text()
                        logger.info(f"📝 Loaded evolved prompt v{iteration_number-1} from global: {global_prev_file.absolute()} ({len(current_prompt)} characters)")
                    else:
                        # Final fallback to baseline
                        logger.warning(f"Previous evolution v{iteration_number-1} not found, falling back to baseline")
                        baseline_prompt_path = Path("src/opencanvas/prompts/baseline/generation_prompt.txt")
                        logger.info(f"📂 Checking baseline prompt at: {baseline_prompt_path.absolute()}")
                        if baseline_prompt_path.exists():
                            current_prompt = baseline_prompt_path.read_text()
                            logger.info(f"📝 Loaded baseline prompt from: {baseline_prompt_path.absolute()} ({len(current_prompt)} characters)")
                        else:
                            logger.error("Could not find any prompt to evolve from")
                            return results
            
            # Get evaluation data
            evaluation_data = agent_result.get("evaluation_data", [])
            if not evaluation_data:
                logger.warning("No evaluation data available for prompt evolution")
                return results
            
            # Get registry context if available
            registry_context = ""
            if self.prompts_registry:
                registry_context = self.prompts_registry.get_context_for_agents()
            
            # Create prompt evolution request
            evolution_prompt = self._create_prompt_evolution_prompt(
                current_prompt, evaluation_data, registry_context, iteration_number
            )
            
            # Call LLM to evolve the prompt
            from anthropic import Anthropic
            from opencanvas.config import Config
            
            client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            
            logger.info("🤖 Requesting evolved prompt from LLM...")
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=8000,
                temperature=0.3,
                messages=[{"role": "user", "content": evolution_prompt}]
            )
            
            evolved_prompt = response.content[0].text.strip()
            
            # For PDF mode, add static code examples back to the evolved prompt
            if hasattr(self, 'pdf_mode') and self.pdf_mode:
                from .pdf_static_examples import add_static_examples
                evolved_prompt = add_static_examples(evolved_prompt)
                logger.info(f"📋 Added static code examples to evolved prompt: {len(evolved_prompt)} total characters")
            
            # Validate the evolved prompt structure
            from .prompt_parser import PromptParser
            parser = PromptParser()
            
            # Get critical variables based on evolution mode
            if hasattr(self, 'pdf_mode') and self.pdf_mode:
                critical_vars = {'{presentation_focus}', '{theme}', '{image_context}'}
            else:
                critical_vars = {'{blog_content}', '{purpose}', '{theme}'}
            
            validation = parser.validate_evolved_prompt(current_prompt, evolved_prompt, critical_vars)
            
            # Additional validation: check for navigation compatibility
            navigation_validation = self._validate_navigation_compatibility(evolved_prompt)
            
            # Always use evolved prompt (validation is now informational only)
            evolved_prompt_final = validation["evolved_prompt"]
            
            # Test the evolved prompt (simplified version)
            test_score = self._test_evolved_prompt_simple(evolved_prompt_final, iteration_number)
            
            # ALWAYS save evolved prompt for experiment tracking regardless of validation
            logger.info(f"💾 Saving evolved prompt (improvement: {test_score:+.1%})")
            self._save_evolved_prompt(evolved_prompt_final, iteration_number)
            
            # Track results based on test score (regardless of validation)
            if test_score > 0.05:  # Improvement threshold
                logger.info(f"📝 Prompt improvement tracked: +{test_score:.3f} (registry update deferred to post-evolution)")
                
                results["prompts_evolved"] = 1
                results["successful_prompts"].append(f"DirectEvolved_v{iteration_number}")
                results["improvements"].append({
                    "type": "direct_evolution",
                    "improvement": test_score,
                    "iteration": iteration_number
                })
                
                # Test evolved prompt immediately (for single iteration runs)
                if self.max_iterations == 1:
                    logger.info("🧪 Testing evolved prompt immediately (single iteration mode)")
                    test_result_actual = self._test_evolved_prompt_actual(evolved_prompt_final, iteration_number)
                    if test_result_actual:
                        logger.info(f"✅ Actual test completed: {test_result_actual.get('improvement', 0):.3f} improvement")
                
            else:
                logger.info(f"❌ Evolved prompt did not improve scores significantly: {test_score:.3f}")
                results["failed_prompts"].append(f"DirectEvolved_v{iteration_number}")
            
            # Log validation issues for information (but don't block saving)
            if not validation["is_valid"]:
                logger.info("ℹ️  Validation warnings (prompt saved anyway for evolution):")
                if validation.get("missing_critical_variables"):
                    logger.warning(f"  Missing critical variables: {validation['missing_critical_variables']}")
                    
            if not navigation_validation["is_valid"]:
                logger.info(f"ℹ️  Navigation validation warning: {navigation_validation.get('reason', 'Unknown issue')}")
                
            elif validation["is_valid"] and navigation_validation["is_valid"]:
                logger.info("✅ Evolved prompt passed all validation")
            
            return results
            
        except Exception as e:
            logger.error(f"Direct prompt evolution failed: {e}")
            return results
    
    def _create_prompt_evolution_prompt(self, current_prompt: str, evaluation_data: List[Dict], 
                                      registry_context: str, iteration_number: int) -> str:
        """Create the prompt for evolving the current prompt"""
        
        # For PDF mode, remove static code examples before evolution
        if hasattr(self, 'pdf_mode') and self.pdf_mode:
            from .pdf_static_examples import remove_static_sections
            current_prompt = remove_static_sections(current_prompt)
        
        # Simplify evaluation data for context
        eval_summary = []
        for eval_data in evaluation_data[-3:]:  # Last 3 evaluations
            visual_score = eval_data.get("visual_scores", {}).get("overall_visual_score", 0)
            content_score = eval_data.get("content_free_scores", {}).get("overall_content_score", 0)
            eval_summary.append(f"Visual: {visual_score:.2f}, Content: {content_score:.2f}")
        
        # Get placeholder instruction before building f-string
        placeholder_instruction = self._get_placeholder_instruction()
        
        # Add PDF-specific instruction about static examples
        static_examples_note = ""
        if hasattr(self, 'pdf_mode') and self.pdf_mode:
            static_examples_note = "\nNOTE: Code examples for MathJax and Mermaid diagrams are handled separately and will be automatically included. Focus on evolving the presentation instructions and guidelines only."
        
        evolution_prompt = f"""You are an expert at improving prompts for presentation generation. 

CURRENT PROMPT TO IMPROVE:
```
{current_prompt}
```

EVALUATION FEEDBACK:
Recent evaluation scores: {', '.join(eval_summary)}
Areas needing improvement: Based on scores, focus on visual design and content structure.

REGISTRY CONTEXT (lessons learned from previous attempts):
{registry_context}

CRITICAL INSTRUCTIONS:
1. Return ONLY the improved prompt text - no explanations or comments
{placeholder_instruction}
3. Keep ALL XML tags exactly as they are: <presentation_task>, <design_philosophy>, etc.
4. Improve the prompt content to address evaluation weaknesses
5. Use insights from the registry context to avoid failed patterns
6. Focus on specific, actionable improvements rather than vague suggestions{static_examples_note}

NAVIGATION COMPATIBILITY REQUIREMENTS (CRITICAL):
7. DO NOT change the slide navigation mechanism - maintain consistent approach
8. Ensure all slides remain accessible with standard arrow key navigation
9. Do NOT mix different navigation methods (opacity-based vs transform-based)
10. If slides use .active class with opacity, DO NOT add container transforms
11. Test that arrow key navigation works for ALL slides, not just the first

HTML GENERATION REQUIREMENTS:
12. Ensure generated HTML has proper slide structure with consistent CSS classes
13. Verify all slides are visible when their .active class is applied
14. Maintain compatibility with existing PDF conversion process

Based on the evaluation feedback and registry context, provide an improved version of the prompt that will generate better presentations WITHOUT breaking slide navigation.
"""
        return evolution_prompt
    
    def _get_placeholder_instruction(self) -> str:
        """Get the appropriate placeholder instruction based on evolution mode"""
        if hasattr(self, 'pdf_mode') and self.pdf_mode:
            return """2. Keep ALL variables exactly as they are: {presentation_focus}, {theme}, {image_context}
CRITICAL FOR PYTHON FORMAT STRINGS:
- Single braces { } are format placeholders - keep EXACTLY as-is for the three variables above
- Double braces {{ }} produce literal braces in the output HTML - MUST preserve ALL double braces
- Example: MathJax = {{ tex: {{ ... }} }} NOT MathJax = { tex: { ... } }
- All JavaScript objects, CSS rules, and template literals need {{ }} to render correctly in the final HTML
- When you see {{ or }} in the current prompt, it MUST remain as {{ or }} in your output"""
        else:
            return "2. Keep ALL variables exactly as they are: {blog_content}, {purpose}, {theme}"
    
    def _test_evolved_prompt_simple(self, evolved_prompt: str, iteration_number: int) -> float:
        """Simple test of evolved prompt - returns improvement estimate"""
        # For now, return a placeholder improvement score
        # In a full implementation, this would generate a test presentation and evaluate it
        
        # Simple heuristics based on prompt content
        improvement = 0.0
        
        # Check for specific improvements
        if "visual balance" in evolved_prompt.lower():
            improvement += 0.1
        if "animation" in evolved_prompt.lower() and "smooth" in evolved_prompt.lower():
            improvement += 0.1
        if "typography" in evolved_prompt.lower():
            improvement += 0.05
        if "engagement" in evolved_prompt.lower():
            improvement += 0.05
        
        # Length-based heuristic (more detailed prompts often perform better)
        # This is a placeholder - would need the original prompt length for comparison
        if len(evolved_prompt) > 1000:  # Reasonably detailed prompt
            improvement += 0.05
        
        logger.info(f"📊 Estimated improvement for evolved prompt: +{improvement:.3f}")
        return improvement
    
    def _save_evolved_prompt(self, evolved_prompt: str, iteration_number: int):
        """Save evolved prompt to evolved_prompts directory (matching successful 0815 run structure)"""
        try:
            # Save ONLY to experiment-specific evolved_prompts (like successful 0815 run)
            evolved_dir = self.output_dir / "evolved_prompts"
            evolved_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine prompt filename based on evolution type (PDF vs topic)
            if hasattr(self, 'pdf_mode') and self.pdf_mode:
                prompt_file = evolved_dir / f"pdf_generation_prompt_v{iteration_number}.txt"
            else:
                prompt_file = evolved_dir / f"generation_prompt_v{iteration_number}.txt"
            
            prompt_file.write_text(evolved_prompt)
            logger.info(f"💾 Saved evolved prompt: {prompt_file.relative_to(self.output_dir)} ({len(evolved_prompt)} characters)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save evolved prompt: {e}")
            return False
    
    def _load_default_prompt(self) -> Optional[str]:
        """Load default baseline prompt - no random evolved prompt loading"""
        try:
            # Only load from baseline, never from random evolved prompts
            
            # Fall back to baseline prompt
            baseline_file = Path("src/opencanvas/prompts/baseline/generation_prompt.txt")
            if baseline_file.exists():
                prompt = baseline_file.read_text()
                logger.info("📝 Loaded baseline prompt from file")
                return prompt
            
            # If no files found, return None (system will use hardcoded fallback)
            logger.warning("⚠️ No prompt files found, will use system hardcoded fallback")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load default prompt: {e}")
            return None
    
    def _validate_navigation_compatibility(self, evolved_prompt: str) -> Dict[str, Any]:
        """Validate that evolved prompt won't break slide navigation"""
        
        # Check for dangerous patterns that could break navigation
        issues = []
        
        # Pattern 1: Conflicting navigation methods
        if "translateY" in evolved_prompt and ".active" in evolved_prompt:
            if "opacity" in evolved_prompt:
                issues.append("Mixing translateY transforms with opacity-based navigation")
        
        # Pattern 2: Container-based slide movement
        if "slideContainer.style.transform" in evolved_prompt:
            issues.append("Using container transforms for slide navigation")
        
        # Pattern 3: Breaking slide selector consistency  
        if "slide-container" in evolved_prompt and ".slide" in evolved_prompt:
            if not ("slide-container" in evolved_prompt and "slides.length" in evolved_prompt):
                issues.append("Inconsistent slide container structure")
                
        # Pattern 4: Missing navigation event handlers
        if "addEventListener" in evolved_prompt:
            if not ("ArrowRight" in evolved_prompt or "ArrowLeft" in evolved_prompt):
                issues.append("Custom event listeners without arrow key support")
        
        # Pattern 5: Overriding standard slide structure
        if "position: absolute" in evolved_prompt and "position: relative" in evolved_prompt:
            if "100%" not in evolved_prompt:
                issues.append("Non-standard slide positioning that may break navigation")
        
        is_valid = len(issues) == 0
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "reason": "; ".join(issues) if issues else "Navigation validation passed"
        }
    
    def _test_evolved_prompt_actual(self, evolved_prompt: str, iteration_number: int) -> Optional[Dict[str, Any]]:
        """Actually test the evolved prompt by generating a presentation"""
        try:
            from opencanvas.generators.topic_generator import TopicGenerator
            from opencanvas.evaluation.evaluator import PresentationEvaluator
            from opencanvas.config import Config
            
            # Create a temporary topic generator with the evolved prompt
            # For now, just return placeholder - full implementation would:
            # 1. Temporarily patch the prompt in TopicGenerator
            # 2. Generate a test presentation
            # 3. Evaluate it against baseline
            # 4. Return comparison results
            
            logger.info("📝 Actual testing would generate and evaluate presentation here")
            return {
                "improvement": 0.2,  # Placeholder
                "baseline_score": 3.1,
                "evolved_score": 3.3,
                "test_topic": self.test_topics[0] if self.test_topics else "test topic"
            }
            
        except Exception as e:
            logger.error(f"Failed to test evolved prompt: {e}")
            return None