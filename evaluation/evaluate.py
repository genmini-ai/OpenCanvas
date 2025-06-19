import asyncio
import argparse
import os
import time
from evaluation.evaluator import PPTQualityEvaluator
from typing import Optional

async def evaluate_presentation(
        html_file: str,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
):
    """
    Evaluate a pre-generated HTML presentation file for quality
    Args:
        html_file: Path to the HTML file containing the presentation slides
        anthropic_api_key: API key for Claude (evaluation)
        openai_api_key: API key for OpenAI GPT (if using GPT model)
    """
    evaluator = PPTQualityEvaluator(
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key
    )
    print(f"📄 Evaluating presentation: {html_file}")
    try:
        evaluation_results = await _evaluate(evaluator, html_filename=html_file)
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return {"status": "error", "error": str(e)}

    evaluation_results["generation_time"] = evaluation_results["evaluation_time"]
    _print_comprehensive_results(
        {"Test Case": evaluation_results},
        total_time=evaluation_results['evaluation_time'], 
        avg_gen_time=evaluation_results['evaluation_time'], 
        total_eval_time=evaluation_results['evaluation_time'], 
        avg_eval_time=evaluation_results['evaluation_time'])

async def run_comprehensive_test_suite(
        anthropic_api_key: str = None, brave_api_key: str = None, openai_api_key: str = None):
    """
    Run complete test suite: generate presentations + evaluate quality
    
    Args:
        anthropic_api_key: API key for Claude (generation + evaluation)
        brave_api_key: API key for Brave search (generation)
        model: 'sonnet' (Claude) or 'gpt' (OpenAI)
        openai_api_key: API key for OpenAI GPT (if model is 'gpt')
    """
    
    # Initialize components
    from generation.slide_generator import SlideGenerator
    
    generator = SlideGenerator(api_key=anthropic_api_key, brave_api_key=brave_api_key)
    evaluator = PPTQualityEvaluator(
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key
    )
    
    # Define test cases with mapped values (not keys)
    test_cases = [
        # Test Case 1: Startup Pitch Deck
        {
            "name": "Startup Pitch Deck",
            "user_text": "AI-powered fitness app that creates personalized workout plans using computer vision to analyze form and provide real-time feedback",
            "purpose": "pitch deck",
            "theme": "bold high contrast"
        },
        
        # Test Case 2: Corporate Training
        {
            "name": "Corporate Training",
            "user_text": "Cybersecurity best practices for remote workers including password management, phishing detection, and secure file sharing protocols",
            "purpose": "educational presentation",
            "theme": "cool professional"
        },
        
        # Test Case 3: Academic Conference
        {
            "name": "Academic Research Presentation",
            "user_text": "Climate change impacts on coral reef ecosystems: a longitudinal study of bleaching events in the Great Barrier Reef from 2010-2024",
            "purpose": "academic presentation",
            "theme": "clean minimalist"
        }
    ]
    
    # Run all test cases
    results = {}
    total_time = 0
    total_evaluation_time = 0
    
    print("🚀 Starting Comprehensive PPT Test Suite")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Topic: {test_case['user_text'][:80]}...")
        print(f"   Purpose: {test_case['purpose']} | Theme: {test_case['theme']}")
        
        # Phase 1: Generate presentation
        start_time = time.time()
        
        try:
            print("  🎨 Generating presentation...")
            result = generator.generate_complete_presentation(
                user_text=test_case['user_text'],
                purpose=test_case['purpose'],
                theme=test_case['theme']
            )
            generation_time = time.time() - start_time
            print(f"  ✅ Generated presentation in {generation_time:.2f}s")
            total_time += generation_time
            html_filename = result.get('html_file', f"test_case_{i}_{test_case['name'].replace(' ', '_').lower()}.html")
            
        except Exception as e:
            generation_time = time.time() - start_time
            total_time += generation_time
            
            results[test_case['name']] = {
                'status': 'error',
                'generation_time': generation_time,
                'error': str(e)
            }
            print(f"  ❌ Error after {generation_time:.2f}s: {e}")
            continue
    
        # Phase 2: Evaluate presentation
        try: 
            evaluation_results = await _evaluate(
                evaluator,
                html_filename=html_filename,
                topic=test_case['user_text'],
                theme=test_case['theme'],
                purpose=test_case['purpose']
            )
            evaluation_results["generation_time"] = generation_time
            results[test_case['name']] = evaluation_results            
        except Exception as e:
            evaluation_results["generation_time"] = generation_time
            results[test_case['name']] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"  ❌ Evaluation failed: {e}")
            continue

    # Calculate averages
    successful_tests = [r for r in results.values() if r['status'] == 'success']
    average_generation_time = total_time / len(test_cases) if test_cases else 0
    average_evaluation_time = total_evaluation_time / len(successful_tests) if successful_tests else 0
    
    _print_comprehensive_results(results, total_time, average_generation_time, total_evaluation_time, average_evaluation_time)
    
    return results, total_time, average_generation_time, total_evaluation_time, average_evaluation_time

async def _evaluate(
        evaluator: PPTQualityEvaluator,
        html_filename: str,
        topic: str = None,
        theme: str = None,
        purpose: str = None,
) -> dict:
    """
    Evaluate a pre-generated HTML presentation file for quality
    Args:
        html_filename: Path to the HTML file containing the presentation slides
    """
    eval_start_time = time.time()
    
    # Capture slides and evaluate
    slides_data = await evaluator.capture_all_slides(html_filename)
    evaluation_results = evaluator.evaluate_presentation(
        slides_data, 
        {
            'topic': topic,
            'theme': theme,
            'purpose': purpose
        }
    )
    
    evaluation_time = time.time() - eval_start_time
    
    # Calculate average score
    scores = evaluation_results.get('scores', {})
    avg_score = sum(scores.values()) / len(scores) if scores else 0
    
    print(f"  📊 Evaluation completed in {evaluation_time:.2f}s | Avg Score: {avg_score:.1f}/10")
    
    return {
        'status': 'success',
        'slides_count': len(slides_data) if slides_data else 0,
        'evaluation_time': evaluation_time,
        'evaluation_scores': scores,
        'average_score': avg_score,
        'html_file': html_filename,
        'full_evaluation': evaluation_results
    }


def _print_comprehensive_results(results, total_time, avg_gen_time, total_eval_time, avg_eval_time):
    """Print detailed results of the comprehensive test suite"""
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*80)
    
    # TODO: Calculate success rates and averages instead of using passing them
    # as arguments
    successful_results = [r for r in results.values() if r['status'] == 'success']
    successful = len(successful_results)
    total = len(results)
    
    # Basic stats
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"⏱️  Total Generation Time: {total_time:.2f}s")
    print(f"⏱️  Average Generation Time: {avg_gen_time:.2f}s per presentation")
    print(f"🤖 Total Evaluation Time: {total_eval_time:.2f}s")
    print(f"🤖 Average Evaluation Time: {avg_eval_time:.2f}s per evaluation")
    
    # Performance analysis
    if successful > 0:
        successful_results = [r for r in results.values() if r['status'] == 'success']
        generation_times = [r['generation_time'] for r in successful_results]
        evaluation_times = [r['evaluation_time'] for r in successful_results if 'evaluation_time' in r]
        avg_scores = [r['average_score'] for r in successful_results if 'average_score' in r]
        
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print("-" * 50)
        if generation_times:
            print(f"Fastest Generation: {min(generation_times):.2f}s")
            print(f"Slowest Generation: {max(generation_times):.2f}s")
        if evaluation_times:
            print(f"Fastest Evaluation: {min(evaluation_times):.2f}s")
            print(f"Slowest Evaluation: {max(evaluation_times):.2f}s")
        if avg_scores:
            print(f"Highest Quality Score: {max(avg_scores):.1f}/10")
            print(f"Lowest Quality Score: {min(avg_scores):.1f}/10")
            print(f"Average Quality Score: {sum(avg_scores)/len(avg_scores):.1f}/10")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 80)
    for name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        
        if result['status'] == 'success':
            gen_time = f"{result['generation_time']:.2f}s"
            eval_time = f"{result.get('evaluation_time', 0):.2f}s" if 'evaluation_time' in result else "N/A"
            avg_score = f"{result.get('average_score', 0):.1f}/10" if 'average_score' in result else "N/A"
            slides = result['slides_count']
            
            print(f"{status_icon} {name}:")
            print(f"    Slides: {slides} | Gen: {gen_time} | Eval: {eval_time} | Quality: {avg_score}")
            
            # Show top scores if available
            if 'evaluation_scores' in result and result['evaluation_scores']:
                scores = result['evaluation_scores']
                top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                print("    Top Scores:")
                for criteria, score in top_scores:
                    criteria_name = criteria.replace("_", " ").title()
                    print(f"      • {criteria_name}: {score}/10")
        else:
            print(f"{status_icon} {name}: ERROR - {result['error']}")
    
    # Quality insights
    successful_with_scores = [r for r in results.values() 
                             if r['status'] == 'success' and 'evaluation_scores' in r and r['evaluation_scores']]
    
    if successful_with_scores:
        print(f"\n🎨 QUALITY INSIGHTS:")
        print("-" * 50)
        
        # Aggregate scores by criteria
        criteria_scores = {}
        for result in successful_with_scores:
            for criteria, score in result['evaluation_scores'].items():
                if criteria not in criteria_scores:
                    criteria_scores[criteria] = []
                criteria_scores[criteria].append(score)
        
        # Calculate averages
        criteria_averages = {k: sum(v)/len(v) for k, v in criteria_scores.items()}
        sorted_criteria = sorted(criteria_averages.items(), key=lambda x: x[1], reverse=True)
        
        print("Strongest Areas:")
        for criteria, avg_score in sorted_criteria[:3]:
            print(f"  • {criteria.replace('_', ' ').title()}: {avg_score:.1f}/10")
        
        print("Areas for Improvement:")
        for criteria, avg_score in sorted_criteria[-3:]:
            print(f"  • {criteria.replace('_', ' ').title()}: {avg_score:.1f}/10")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run comprehensive test suite for OpenCanvas presentations.")
    parser.add_argument('--slides_path', type=str, default=None, help='Path to directory with pre-generated HTML slides (optional)')
    parser.add_argument('--model', type=str, choices=['sonnet', 'gpt'], default='sonnet', help='Model to use for evaluation: sonnet (Claude) or gpt (OpenAI)')
    args = parser.parse_args()

    # Get API keys from environment variables
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    brave_api_key = os.getenv('BRAVE_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    slides_path = args.slides_path
    model = args.model
    
    if model == 'sonnet' and not anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables for model 'sonnet'")
        exit(1)
    if model == 'gpt' and not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment variables for model 'gpt'")
        exit(1)

    if not slides_path:
        asyncio.run(run_comprehensive_test_suite(
            anthropic_api_key=anthropic_api_key,
            brave_api_key=brave_api_key,
            openai_api_key=openai_api_key
        ))
    else:
        asyncio.run(evaluate_presentation(
            html_file=slides_path,
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key,
        ))
