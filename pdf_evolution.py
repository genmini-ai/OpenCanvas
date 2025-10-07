#!/usr/bin/env python3
"""
Test script for PDF-based evolution system

This script demonstrates the autonomous improvement of PDF presentation generation
through iterative prompt evolution and tool development.
"""

import sys
import logging
import argparse
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from opencanvas.evolution.core.pdf_evolution import PDFEvolutionSystem

def setup_logging(diagnostic_mode: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if diagnostic_mode else logging.INFO
    
    # Configure logging format
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pdf_evolution.log')
        ]
    )
    
    # Reduce noise from some modules
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def detect_last_completed_iteration(resume_dir: Path) -> int:
    """Detect the last completed iteration in an existing PDF evolution run"""
    evolution_dir = resume_dir / "evolution"
    if not evolution_dir.exists():
        return 0
    
    # Check for iteration directories with evaluation results
    completed_iterations = []
    for item in evolution_dir.iterdir():
        if item.is_dir() and item.name.startswith("iteration_"):
            try:
                iteration_num = int(item.name.split("_")[1])
                # Check if evaluation results exist (indicating completion)
                eval_file = item / "evaluation_results.json"
                if eval_file.exists():
                    completed_iterations.append(iteration_num)
            except (ValueError, IndexError):
                continue
    
    return max(completed_iterations) if completed_iterations else 0

def load_resume_configuration(resume_dir: Path) -> dict:
    """Load configuration from existing PDF evolution run"""
    # Try to load from config.json first, then test_configuration.json
    for config_name in ["config.json", "test_configuration.json"]:
        config_file = resume_dir / config_name
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load {config_name}: {e}")
                continue
    
    # If no config file found, return minimal default config
    print("⚠️ No configuration file found, using defaults")
    return {
        "test_pdf": "https://arxiv.org/pdf/2505.20286",
        "theme": "academic blue", 
        "purpose": "academic conference presentation"
    }

def main():
    """Run PDF evolution system"""
    parser = argparse.ArgumentParser(description="Run PDF-based evolution system")
    parser.add_argument('--max-iterations', type=int, default=2, 
                       help='Maximum number of evolution iterations (default: 2)')
    parser.add_argument('--test-pdf', type=str, 
                       default='https://arxiv.org/pdf/2505.20286',
                       help='PDF URL to use for testing (default: https://arxiv.org/pdf/2505.20286)')
    parser.add_argument('--test-pdfs', type=str, nargs='+',
                       help='Multiple PDF URLs/paths for testing (e.g., --test-pdfs url1.pdf url2.pdf /path/to/local.pdf)')
    parser.add_argument('--theme', type=str, default='academic blue',
                       help='Presentation theme (default: academic blue)')
    parser.add_argument('--purpose', type=str, default='academic conference presentation',
                       help='Presentation purpose (default: academic conference presentation)')
    parser.add_argument('--diagnostic', action='store_true',
                       help='Enable diagnostic mode with detailed logging')
    parser.add_argument('--prompt-only', action='store_true',
                       help='Focus on prompt evolution only (skip tool generation)')
    parser.add_argument('--output-dir', type=str,
                       help='Custom output directory (default: auto-generated)')
    parser.add_argument('--initial-prompt', type=str,
                       help='Path to initial PDF prompt file (e.g., evolution_runs/evolved_prompts/pdf_generation_prompt_v2.txt)')
    parser.add_argument('--memory', action='store_true',
                       help='Enable PDF prompts registry memory (lessons from previous PDF evolution attempts)')
    parser.add_argument('--resume', type=str,
                       help='Resume evolution from existing PDF experiment directory (e.g., evolution_runs/pdf_tracked_evolution_20250818_222957)')
    
    args = parser.parse_args()
    
    # Handle multiple PDFs vs single PDF
    if args.test_pdfs:
        # Multiple PDFs specified - strip quotes from each
        test_pdfs_input = [pdf.strip('"').strip("'") for pdf in args.test_pdfs]
        logger_msg = f"Multiple PDFs: {len(test_pdfs_input)} PDFs"
    else:
        # Single PDF (backward compatibility) - strip quotes
        test_pdfs_input = args.test_pdf.strip('"').strip("'")
        logger_msg = f"Single PDF: {test_pdfs_input}"
    
    # Setup logging
    setup_logging(args.diagnostic)
    logger = logging.getLogger(__name__)
    
    logger.info("="*70)
    logger.info("🚀 Starting PDF Evolution System Test")
    logger.info("="*70)
    
    # Handle resume mode or create new experiment
    start_iteration = 1
    resume_config = {}
    output_dir = args.output_dir
    
    if args.resume:
        logger.info(f"🔄 RESUME MODE: Continuing from {args.resume}")
        resume_dir = Path(args.resume)
        
        if not resume_dir.exists():
            logger.error(f"❌ Resume directory not found: {args.resume}")
            return
        
        # Load configuration from previous run
        try:
            resume_config = load_resume_configuration(resume_dir)
            logger.info(f"✅ Loaded configuration from previous run")
        except Exception as e:
            logger.error(f"❌ Failed to load resume configuration: {e}")
            return
        
        # Detect last completed iteration
        last_completed = detect_last_completed_iteration(resume_dir)
        start_iteration = last_completed + 1
        logger.info(f"📊 Last completed iteration: {last_completed}")
        logger.info(f"🚀 Will resume from iteration: {start_iteration}")
        
        if start_iteration > args.max_iterations:
            logger.info(f"✅ All iterations already completed (last: {last_completed}, max: {args.max_iterations})")
            return
        
        # Use existing directory
        output_dir = str(resume_dir)
    
    # Show current configuration (with resume values if applicable)
    # Handle backward compatibility for resume configs
    if "test_pdfs" in resume_config:
        test_pdfs_final = resume_config["test_pdfs"]
    elif "test_pdf" in resume_config:
        test_pdfs_final = resume_config["test_pdf"]  # Single PDF from old format
    else:
        test_pdfs_final = test_pdfs_input
    theme = resume_config.get("theme", args.theme)
    purpose = resume_config.get("purpose", args.purpose)
    
    # Display PDF configuration
    if isinstance(test_pdfs_final, list):
        logger.info(f"📄 Test PDFs: {len(test_pdfs_final)} PDFs")
        for i, pdf in enumerate(test_pdfs_final, 1):
            logger.info(f"   {i}. {pdf}")
    else:
        logger.info(f"📄 Test PDF: {test_pdfs_final}")
    logger.info(f"🔢 Max iterations: {args.max_iterations}")
    logger.info(f"🎨 Theme: {theme}")
    logger.info(f"🎯 Purpose: {purpose}")
    logger.info(f"🔍 Diagnostic mode: {args.diagnostic}")
    logger.info(f"📝 Prompt-only mode: {args.prompt_only}")
    if output_dir:
        logger.info(f"📁 Output directory: {output_dir}")
    if args.initial_prompt:
        logger.info(f"🎯 Initial prompt: {args.initial_prompt}")
    logger.info(f"🧠 Memory enabled: {args.memory}")
    if args.resume:
        logger.info(f"🔄 Resuming from iteration: {start_iteration}")
    logger.info("="*70)
    
    try:
        # Initialize PDF evolution system
        logger.info("🔧 Initializing PDFEvolutionSystem...")
        
        # Use PDF-specific prompts registry if memory is enabled
        prompts_registry = "PDF_PROMPTS_REGISTRY.md" if args.memory else "PROMPTS_REGISTRY.md"
        
        system = PDFEvolutionSystem(
            test_pdfs=test_pdfs_final,
            output_dir=output_dir,
            max_iterations=args.max_iterations,
            improvement_threshold=0.2,
            diagnostic_mode=args.diagnostic,
            prompt_only=args.prompt_only,
            prompts_registry=prompts_registry,
            theme=theme,
            purpose=purpose,
            initial_prompt_path=args.initial_prompt,
            use_memory=args.memory
        )
        
        logger.info(f"✅ PDFEvolutionSystem initialized")
        logger.info(f"📁 Evolution output directory: {system.output_dir}")
        
        # Run evolution cycle (with start_iteration if resuming)
        logger.info("🔄 Starting evolution cycle...")
        results = system.run_evolution_cycle(start_iteration=start_iteration)
        
        # Print results summary
        logger.info("="*70)
        logger.info("🎉 PDF Evolution Completed!")
        logger.info("="*70)
        
        if results.get("success", True):  # Assume success if not explicitly failed
            logger.info(f"✅ Evolution Status: SUCCESS")
            logger.info(f"📊 Total Iterations: {results.get('total_iterations', 'Unknown')}")
            logger.info(f"📁 Results Directory: {system.output_dir}")
            
            # Print iteration summary
            iterations = results.get("iterations", [])
            if iterations:
                logger.info(f"📋 Iteration Summary:")
                for i, iteration in enumerate(iterations, 1):
                    if iteration.get("success"):
                        baseline_scores = iteration.get("baseline_scores", {})
                        if baseline_scores:
                            avg_score = sum(baseline_scores.values()) / len(baseline_scores)
                            logger.info(f"  Iteration {i}: ✅ Average score: {avg_score:.3f}")
                        else:
                            logger.info(f"  Iteration {i}: ✅ Completed")
                    else:
                        error = iteration.get("error", "Unknown error")
                        logger.info(f"  Iteration {i}: ❌ Failed - {error}")
            
            # Print tools summary
            tools_discovered = results.get("tools_discovered", [])
            tools_adopted = results.get("tools_adopted", [])
            if tools_discovered:
                logger.info(f"🔧 Tools Discovered: {len(tools_discovered)}")
                for tool in tools_discovered[:3]:  # Show first 3
                    logger.info(f"  - {tool.get('name', 'Unknown')} ({tool.get('priority', 'unknown')} priority)")
            if tools_adopted:
                logger.info(f"🚀 Tools Adopted: {len(tools_adopted)}")
                for tool in tools_adopted[:3]:  # Show first 3
                    logger.info(f"  - {tool}")
            
            # Print final improvement
            final_improvement = results.get("final_improvement")
            if final_improvement:
                logger.info(f"📈 Final Improvement: {final_improvement}")
            
            # Print best iteration
            best_iteration = results.get("best_iteration")
            if best_iteration:
                logger.info(f"🏆 Best Iteration: {best_iteration}")
                
        else:
            logger.error(f"❌ Evolution Status: FAILED")
            error = results.get("error", "Unknown error")
            logger.error(f"💥 Error: {error}")
            
            # Print any partial results
            iterations = results.get("iterations", [])
            if iterations:
                logger.info(f"📋 Partial Results ({len(iterations)} iterations):")
                for i, iteration in enumerate(iterations, 1):
                    if iteration.get("success"):
                        logger.info(f"  Iteration {i}: ✅ Completed")
                    else:
                        error = iteration.get("error", "Unknown error")
                        logger.info(f"  Iteration {i}: ❌ {error}")
        
        logger.info("="*70)
        
        # Print file locations
        output_dir = Path(system.output_dir)
        if output_dir.exists():
            logger.info("📁 Generated Files:")
            
            # Evolution results
            results_file = output_dir / "evolution_results.json"
            if results_file.exists():
                logger.info(f"  📊 Results: {results_file}")
            
            # Evolved prompts
            evolved_prompts_dir = output_dir / "evolved_prompts"
            if evolved_prompts_dir.exists():
                prompt_files = list(evolved_prompts_dir.glob("pdf_generation_prompt_v*.txt"))
                if prompt_files:
                    logger.info(f"  📝 Evolved Prompts:")
                    for prompt_file in sorted(prompt_files):
                        logger.info(f"    - {prompt_file.name}")
            
            # Iteration outputs
            iteration_dirs = list(output_dir.glob("iteration_*"))
            if iteration_dirs:
                logger.info(f"  📂 Iteration Outputs:")
                for iteration_dir in sorted(iteration_dirs):
                    presentations_dir = iteration_dir / "presentations"
                    if presentations_dir.exists():
                        html_files = list(presentations_dir.glob("**/slides.html"))
                        pdf_files = list(presentations_dir.glob("**/presentation.pdf"))
                        logger.info(f"    - {iteration_dir.name}: {len(html_files)} HTML, {len(pdf_files)} PDF")
        
        logger.info("="*70)
        logger.info("🎯 PDF Evolution Test Complete!")
        
        return 0 if results.get("success", True) else 1
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Evolution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Evolution failed with error: {e}")
        if args.diagnostic:
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)