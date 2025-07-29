#!/usr/bin/env python3
"""
Main script to run the complete visual adversarial testing pipeline

Usage:
    python examples/run_visual_adversarial_test.py --mode full
    python examples/run_visual_adversarial_test.py --mode generate
    python examples/run_visual_adversarial_test.py --mode test
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from visual_adversarial_generator import VisualAdversarialGenerator
from visual_adversarial_tester import VisualPromptTester

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_generation(source_dir: str, output_dir: str, skip_pdf: bool = False):
    """Run the adversarial generation phase"""
    logger.info("="*80)
    logger.info("PHASE 1: GENERATING ADVERSARIAL ATTACKS")
    logger.info("="*80)
    
    generator = VisualAdversarialGenerator(source_dir, output_dir)
    
    if skip_pdf:
        logger.info("Skipping PDF conversion for faster testing")
        # Modified run without PDF conversion
        source_slides = generator.find_source_slides()
        if not source_slides:
            logger.error("No source slides found!")
            return False
            
        original_slides = generator.copy_original_slides(source_slides)
        attacked_slides = generator.generate_all_attacks(original_slides)
        generator.save_metadata(original_slides, attacked_slides, {})
    else:
        generator.run()
    
    return True

def run_testing(test_dir: str):
    """Run the evaluation testing phase"""
    logger.info("="*80)
    logger.info("PHASE 2: TESTING VISUAL EVALUATION PROMPTS")
    logger.info("="*80)
    
    tester = VisualPromptTester(test_dir)
    tester.run_analysis()
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Run visual adversarial testing for presentation evaluation prompts"
    )
    
    parser.add_argument(
        "--mode",
        choices=["full", "generate", "test"],
        default="full",
        help="Execution mode: full (both phases), generate (only create attacks), test (only run evaluation)"
    )
    
    parser.add_argument(
        "--source",
        default="/Users/christineh./Downloads/slidebee/OpenCanvas/evolution_runs/pdf_tracked_evolution_20250826_102641",
        help="Path to evolution run directory with source slides"
    )
    
    parser.add_argument(
        "--output",
        default="test_output/visual_adversarial_testing",
        help="Output directory for adversarial testing"
    )
    
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF conversion in generation phase (faster for HTML-only testing)"
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("VISUAL ADVERSARIAL TESTING PIPELINE")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Source: {args.source}")
    logger.info(f"Output: {args.output}")
    logger.info("="*80)
    
    success = True
    
    # Run appropriate phases based on mode
    if args.mode in ["full", "generate"]:
        success = run_generation(args.source, args.output, args.skip_pdf)
        if not success:
            logger.error("Generation phase failed!")
            sys.exit(1)
    
    if args.mode in ["full", "test"]:
        if not Path(args.output).exists():
            logger.error(f"Test data directory {args.output} does not exist! Run generation first.")
            sys.exit(1)
            
        success = run_testing(args.output)
        if not success:
            logger.error("Testing phase failed!")
            sys.exit(1)
    
    # Final summary
    if success:
        logger.info("\n" + "="*80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        
        if args.mode == "full":
            # Try to read and display best prompt
            results_file = Path(args.output) / "evaluation_results" / "alignment_scores.json"
            if results_file.exists():
                import json
                with open(results_file) as f:
                    scores = json.load(f)
                best_prompt = max(scores, key=scores.get)
                logger.info(f"BEST VISUAL EVALUATION PROMPT: {best_prompt}")
                logger.info(f"Alignment Score: {scores[best_prompt]:.3f}")
        
        logger.info(f"Results saved to: {args.output}")
        logger.info("="*80)
    else:
        logger.error("Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()