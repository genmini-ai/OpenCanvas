#!/usr/bin/env python3
"""
Quick Adversarial Evaluation Test Runner

This script provides a simple way to test evaluation robustness
and analyze the effectiveness of the evaluation prompts.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from tests.test_adversarial_evaluation import run_adversarial_evaluation_test
from opencanvas.evaluation.analysis import analyze_adversarial_results

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for adversarial evaluation testing"""
    parser = argparse.ArgumentParser(
        description="Test presentation evaluation robustness with adversarial attacks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with existing presentations (recommended for first run)
  python run_adversarial_eval_test.py

  # Generate fresh presentations and test
  python run_adversarial_eval_test.py --regenerate

  # Run only analysis on existing results
  python run_adversarial_eval_test.py --analysis-only

  # Specify custom output directory
  python run_adversarial_eval_test.py --output-dir custom_analysis
        """
    )
    
    parser.add_argument(
        "--regenerate", 
        action="store_true",
        help="Generate fresh presentations instead of using existing ones"
    )
    
    parser.add_argument(
        "--analysis-only",
        action="store_true", 
        help="Only run analysis on existing results, skip evaluation testing"
    )
    
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for results (default: {OUTPUT_DIR}/adversarial_analysis)"
    )
    
    parser.add_argument(
        "--original-dir",
        default=None,
        help="Directory containing original evaluation results (default: {OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Import config and set defaults
    from opencanvas.config import Config
    
    # Use config defaults if not specified
    if args.output_dir is None:
        args.output_dir = str(Config.OUTPUT_DIR / "adversarial_analysis")
    if args.original_dir is None:
        args.original_dir = str(Config.OUTPUT_DIR)
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if not args.analysis_only:
            # Run adversarial evaluation testing
            print("🚀 Starting Adversarial Evaluation Test")
            print("=" * 60)
            
            results = run_adversarial_evaluation_test(
                use_existing=not args.regenerate,
                output_dir=str(output_dir)
            )
            
            print(f"\n✅ Adversarial testing completed!")
            print(f"📊 Results saved to: {output_dir}")
        
        # Run analysis
        print(f"\n🔍 Starting Analysis of Results")
        print("=" * 60)
        
        analysis_report = analyze_adversarial_results(
            original_dir=args.original_dir,
            adversarial_dir=str(output_dir),
            output_dir=str(output_dir)
        )
        
        print(f"\n✅ Analysis completed!")
        print(f"📈 Analysis report saved to: {output_dir}/analysis_report.json")
        
        # Quick summary of key findings
        if analysis_report:
            print(f"\n🎯 KEY FINDINGS:")
            
            effectiveness = analysis_report.get("attack_effectiveness", {})
            if effectiveness:
                # Find most and least effective attacks
                attack_scores = {name: stats.get("mean_score_drop", 0) 
                               for name, stats in effectiveness.items()}
                
                most_effective = max(attack_scores.items(), key=lambda x: x[1])
                least_effective = min(attack_scores.items(), key=lambda x: x[1])
                
                print(f"  🔥 Most effective attack: {most_effective[0]} (avg drop: {most_effective[1]:.3f})")
                print(f"  🛡️ Least effective attack: {least_effective[0]} (avg drop: {least_effective[1]:.3f})")
            
            overall_stats = analysis_report.get("overall_statistics", {})
            if overall_stats:
                success_rate = overall_stats.get("attack_success_rate", 0)
                significant_rate = overall_stats.get("significant_impact_rate", 0)
                print(f"  📊 Attack success rate: {success_rate:.1%}")
                print(f"  💥 Significant impact rate: {significant_rate:.1%}")
            
            # Evaluation robustness interpretation
            mean_drop = overall_stats.get("mean_score_drop_all_attacks", 0)
            if mean_drop < 0.1:
                robustness = "🟢 HIGH (evaluation is robust to attacks)"
            elif mean_drop < 0.5:
                robustness = "🟡 MODERATE (evaluation shows some vulnerability)"
            else:
                robustness = "🔴 LOW (evaluation is vulnerable to attacks)"
            
            print(f"  🔒 Evaluation robustness: {robustness}")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"  1. Review detailed analysis in: {output_dir}/analysis_report.json")
        print(f"  2. Check visualizations in: {output_dir}/plots/")
        print(f"  3. Consider improving evaluation prompts based on vulnerabilities found")
        
    except Exception as e:
        logger.error(f"Adversarial evaluation test failed: {e}")
        print(f"\n❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"  1. Ensure you have run normal topic-based tests first")
        print(f"  2. Check that evaluation API keys are configured")
        print(f"  3. Verify that {Config.OUTPUT_DIR} directory exists with presentation files")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())