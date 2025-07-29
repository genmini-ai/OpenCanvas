#!/usr/bin/env python3
"""
Visual Comparison Dataset Evaluation

Runs AI evaluation on competitor slides and compares with human scores.
Tests all three evaluation dimensions (visual, content-free, content-required)
with primary focus on validating visual evaluation quality.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from opencanvas.evaluation.evaluator import PresentationEvaluator
from opencanvas.config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class VisualComparisonEvaluator:
    """Evaluates competitor slides and compares AI vs human scores"""
    
    def __init__(self):
        self.dataset_dir = Path("test_output/visual_comparison_dataset")
        self.slides_dir = self.dataset_dir / "slides"
        self.human_scores_dir = self.dataset_dir / "human_scores"
        self.ai_scores_dir = self.dataset_dir / "ai_scores"
        self.analysis_dir = self.dataset_dir / "comparison_analysis"
        
        # Create directories
        self.ai_scores_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize evaluator
        eval_config = Config.get_evaluation_config()
        self.evaluator = PresentationEvaluator(
            api_key=eval_config['api_key'],
            model=eval_config['model'],
            provider=eval_config['provider']
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_ai_evaluation(self) -> Dict[str, Any]:
        """Run AI evaluation on all slides"""
        print("🤖 Running AI Evaluation on Competitor Slides")
        print("=" * 60)
        
        ai_results = {}
        slide_files = list(self.slides_dir.glob("*.pdf"))
        
        for i, slide_path in enumerate(slide_files, 1):
            slide_name = slide_path.name
            print(f"\n📄 Evaluating {i}/{len(slide_files)}: {slide_name}")
            
            try:
                # Use the same method that worked in our earlier tests
                # Extract PDF as base64 first
                pdf_data = self.evaluator.extract_pdf_as_base64(str(slide_path))
                
                if not pdf_data:
                    print(f"  ❌ Failed to extract PDF data from {slide_name}")
                    continue
                
                # Run all three evaluation dimensions
                visual_scores = self.evaluator.evaluate_visual(pdf_data)
                content_scores = self.evaluator.evaluate_content_free(pdf_data)
                
                # Note: Content-required would need source material, 
                # so we'll skip it for competitor slides
                
                # Calculate overall scores
                overall_visual = visual_scores.get("overall_visual_score", 0)
                overall_content = content_scores.get("overall_content_score", 0)
                overall_presentation = (overall_visual + overall_content) / 2
                
                ai_results[slide_name] = {
                    "visual_scores": visual_scores,
                    "content_free_scores": content_scores,
                    "content_required_scores": {"note": "Not available - no source material"},
                    "overall_scores": {
                        "visual": overall_visual,
                        "content_reference_free": overall_content,
                        "content_reference_required": 0,
                        "presentation_overall": overall_presentation
                    },
                    "evaluation_timestamp": datetime.now().isoformat()
                }
                
                print(f"  ✅ Visual: {overall_visual:.2f}")
                print(f"  ✅ Content-Free: {overall_content:.2f}")
                print(f"  ✅ Overall: {overall_presentation:.2f}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                ai_results[slide_name] = {"error": str(e)}
        
        # Save AI results
        ai_results_file = self.ai_scores_dir / "ai_evaluation_results.json"
        with open(ai_results_file, 'w') as f:
            json.dump(ai_results, f, indent=2)
        
        print(f"\n💾 AI evaluation results saved to: {ai_results_file}")
        return ai_results
    
    def load_human_scores(self) -> Dict[str, Any]:
        """Load human evaluation scores"""
        human_file = self.human_scores_dir / "human_evaluation_scores.json"
        
        if not human_file.exists():
            print(f"⚠️ Human scores not found at: {human_file}")
            print("Please fill in the template at:")
            print(f"  {self.human_scores_dir / 'human_evaluation_template.json'}")
            return {}
        
        with open(human_file, 'r') as f:
            return json.load(f)
    
    def compare_scores(self, ai_results: Dict, human_results: Dict) -> Dict[str, Any]:
        """Compare AI and human evaluation scores"""
        print("\n📊 Comparing AI vs Human Scores")
        print("=" * 60)
        
        comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "slide_comparisons": {},
            "dimension_analysis": {
                "visual": {"correlations": [], "differences": []},
                "content_free": {"correlations": [], "differences": []},
                "overall": {"correlations": [], "differences": []}
            },
            "summary_stats": {}
        }
        
        for slide_name in ai_results.keys():
            if slide_name not in human_results or "error" in ai_results[slide_name]:
                continue
            
            ai_slide = ai_results[slide_name]
            human_slide = human_results[slide_name]
            
            # Extract scores for comparison
            ai_visual = ai_slide["overall_scores"]["visual"]
            human_visual = human_slide["overall_scores"]["visual"]
            
            ai_content = ai_slide["overall_scores"]["content_reference_free"]
            human_content = human_slide["overall_scores"]["content_reference_free"]
            
            ai_overall = ai_slide["overall_scores"]["presentation_overall"]
            human_overall = human_slide["overall_scores"]["presentation_overall"]
            
            # Calculate differences
            visual_diff = ai_visual - human_visual
            content_diff = ai_content - human_content
            overall_diff = ai_overall - human_overall
            
            comparison_results["slide_comparisons"][slide_name] = {
                "visual": {"ai": ai_visual, "human": human_visual, "difference": visual_diff},
                "content_free": {"ai": ai_content, "human": human_content, "difference": content_diff},
                "overall": {"ai": ai_overall, "human": human_overall, "difference": overall_diff}
            }
            
            # Store for dimension analysis
            comparison_results["dimension_analysis"]["visual"]["correlations"].append([ai_visual, human_visual])
            comparison_results["dimension_analysis"]["visual"]["differences"].append(visual_diff)
            
            comparison_results["dimension_analysis"]["content_free"]["correlations"].append([ai_content, human_content])
            comparison_results["dimension_analysis"]["content_free"]["differences"].append(content_diff)
            
            comparison_results["dimension_analysis"]["overall"]["correlations"].append([ai_overall, human_overall])
            comparison_results["dimension_analysis"]["overall"]["differences"].append(overall_diff)
            
            print(f"\n{slide_name}:")
            print(f"  Visual:      AI={ai_visual:.2f}, Human={human_visual:.2f}, Diff={visual_diff:+.2f}")
            print(f"  Content-Free: AI={ai_content:.2f}, Human={human_content:.2f}, Diff={content_diff:+.2f}")
            print(f"  Overall:     AI={ai_overall:.2f}, Human={human_overall:.2f}, Diff={overall_diff:+.2f}")
        
        # Calculate summary statistics
        for dimension in ["visual", "content_free", "overall"]:
            diffs = comparison_results["dimension_analysis"][dimension]["differences"]
            if diffs:
                comparison_results["summary_stats"][dimension] = {
                    "mean_difference": sum(diffs) / len(diffs),
                    "abs_mean_difference": sum(abs(d) for d in diffs) / len(diffs),
                    "max_difference": max(diffs),
                    "min_difference": min(diffs),
                    "agreement_within_1": sum(1 for d in diffs if abs(d) <= 1.0) / len(diffs)
                }
        
        return comparison_results
    
    def generate_analysis_report(self, comparison_results: Dict):
        """Generate and print analysis report"""
        print("\n🎯 ANALYSIS SUMMARY")
        print("=" * 60)
        
        stats = comparison_results["summary_stats"]
        
        for dimension in ["visual", "content_free", "overall"]:
            if dimension in stats:
                dim_stats = stats[dimension]
                print(f"\n{dimension.upper()} DIMENSION:")
                print(f"  Mean AI-Human Difference: {dim_stats['mean_difference']:+.2f}")
                print(f"  Mean Absolute Difference: {dim_stats['abs_mean_difference']:.2f}")
                print(f"  Agreement within ±1.0: {dim_stats['agreement_within_1']:.1%}")
                print(f"  Range: {dim_stats['min_difference']:+.2f} to {dim_stats['max_difference']:+.2f}")
        
        # Save detailed comparison results
        comparison_file = self.analysis_dir / "ai_vs_human_comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison_results, f, indent=2)
        
        print(f"\n💾 Detailed comparison saved to: {comparison_file}")
    
    def run_full_evaluation(self):
        """Run complete evaluation pipeline"""
        print("🚀 Starting Visual Comparison Dataset Evaluation")
        print("=" * 80)
        
        # Step 1: Run AI evaluation
        ai_results = self.run_ai_evaluation()
        
        # Step 2: Load human scores
        human_results = self.load_human_scores()
        
        if not human_results:
            print("\n⏸️ Stopping here - please fill in human scores first")
            return
        
        # Step 3: Compare scores
        comparison_results = self.compare_scores(ai_results, human_results)
        
        # Step 4: Generate analysis
        self.generate_analysis_report(comparison_results)
        
        print("\n✅ Visual comparison evaluation completed!")
        print(f"📁 Results saved in: {self.dataset_dir}")

def main():
    """Main entry point"""
    setup_logging()
    
    evaluator = VisualComparisonEvaluator()
    evaluator.run_full_evaluation()

if __name__ == "__main__":
    main()