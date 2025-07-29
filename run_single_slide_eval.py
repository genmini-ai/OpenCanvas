#!/usr/bin/env python3
"""
Single Slide Evaluation - Add new slide to existing results
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from opencanvas.evaluation.evaluator import PresentationEvaluator
from opencanvas.config import Config

def evaluate_single_slide(slide_name: str):
    """Evaluate a single slide and add to existing results"""
    
    dataset_dir = Path("test_output/visual_comparison_dataset")
    slide_path = dataset_dir / "slides" / slide_name
    ai_results_file = dataset_dir / "ai_scores" / "ai_evaluation_results.json"
    
    if not slide_path.exists():
        print(f"❌ Slide not found: {slide_path}")
        return
    
    # Load existing results
    existing_results = {}
    if ai_results_file.exists():
        with open(ai_results_file, 'r') as f:
            existing_results = json.load(f)
    
    # Skip if already evaluated
    if slide_name in existing_results and "error" not in existing_results[slide_name]:
        print(f"⚠️ {slide_name} already evaluated. Skipping...")
        return
    
    # Initialize evaluator
    eval_config = Config.get_evaluation_config()
    evaluator = PresentationEvaluator(
        api_key=eval_config['api_key'],
        model=eval_config['model'],
        provider=eval_config['provider']
    )
    
    print(f"🤖 Evaluating {slide_name}...")
    
    try:
        # Extract PDF as base64
        pdf_data = evaluator.extract_pdf_as_base64(str(slide_path))
        
        if not pdf_data:
            print(f"❌ Failed to extract PDF data from {slide_name}")
            return
        
        # Run evaluations
        visual_scores = evaluator.evaluate_visual(pdf_data)
        content_scores = evaluator.evaluate_content_free(pdf_data)
        
        # Calculate overall scores
        overall_visual = visual_scores.get("overall_visual_score", 0)
        overall_content = content_scores.get("overall_content_score", 0)
        overall_presentation = (overall_visual + overall_content) / 2
        
        # Add to results
        existing_results[slide_name] = {
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
        
        print(f"✅ Visual: {overall_visual:.2f}")
        print(f"✅ Content-Free: {overall_content:.2f}")
        print(f"✅ Overall: {overall_presentation:.2f}")
        
        # Save updated results
        with open(ai_results_file, 'w') as f:
            json.dump(existing_results, f, indent=2)
        
        print(f"💾 Results updated in: {ai_results_file}")
        
        # Also update the human scores template
        template_file = dataset_dir / "human_scores" / "human_evaluation_template.json"
        if template_file.exists():
            with open(template_file, 'r') as f:
                template = json.load(f)
            
            if slide_name not in template:
                template[slide_name] = {
                    "visual_scores": {
                        "professional_design": {"score": 0, "reasoning": ""},
                        "information_hierarchy": {"score": 0, "reasoning": ""},
                        "clarity_readability": {"score": 0, "reasoning": ""},
                        "visual_textual_balance": {"score": 0, "reasoning": ""},
                        "overall_visual_score": 0
                    },
                    "content_free_scores": {
                        "logical_structure": {"score": 0, "reasoning": ""},
                        "narrative_quality": {"score": 0, "reasoning": ""},
                        "overall_content_score": 0
                    },
                    "content_required_scores": {
                        "accuracy": {"score": 0, "reasoning": ""},
                        "essential_coverage": {"score": 0, "reasoning": ""},
                        "overall_accuracy_coverage_score": 0
                    },
                    "overall_scores": {
                        "visual": 0,
                        "content_reference_free": 0,
                        "content_reference_required": 0,
                        "presentation_overall": 0
                    }
                }
                
                with open(template_file, 'w') as f:
                    json.dump(template, f, indent=2)
                
                print(f"📝 Added {slide_name} to human evaluation template")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        existing_results[slide_name] = {"error": str(e)}

if __name__ == "__main__":
    evaluate_single_slide("openai_slide1.pdf")