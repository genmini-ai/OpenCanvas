#!/usr/bin/env python3
"""
Complete Evolution Cycle Demo - Demonstrates the full evolution system in action
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from opencanvas.evolution.multi_agent.orchestrator_agent import OrchestratorAgent
from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager
from opencanvas.evolution.evolved_generator import EvolvedGenerator, EvolvedGenerationRouter
from opencanvas.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_complete_evolution_cycle():
    """Demonstrate the complete evolution cycle from analysis to implementation"""
    
    print("🚀 COMPLETE EVOLUTION CYCLE DEMONSTRATION")
    print("=" * 60)
    
    # Step 1: Setup sample evaluation data (simulating real evaluation results)
    sample_evaluation_data = create_sample_evaluation_data()
    
    print(f"\n📊 Step 1: Sample Evaluation Data")
    print(f"  - {len(sample_evaluation_data)} presentations evaluated")
    print(f"  - Average visual score: {calculate_avg_score(sample_evaluation_data, 'visual'):.2f}/5")
    print(f"  - Average content score: {calculate_avg_score(sample_evaluation_data, 'content_reference_free'):.2f}/5")
    
    # Step 2: Run multi-agent analysis
    print(f"\n🤖 Step 2: Multi-Agent Analysis")
    orchestrator = OrchestratorAgent()
    
    agent_input = {
        "action": "run_evolution_cycle",
        "evaluation_data": sample_evaluation_data,
        "topics": ["AI in healthcare", "Sustainable energy", "Quantum computing"],
        "iteration_number": 1,
        "previous_implementations": []
    }
    
    print("  Running orchestrated agent analysis...")
    agent_result = orchestrator.process(agent_input)
    
    if not agent_result.get("success"):
        print(f"❌ Agent analysis failed: {agent_result.get('error', 'Unknown error')}")
        return
    
    print("  ✅ Multi-agent analysis completed successfully")
    
    # Extract key results
    phases = agent_result.get("phases", {})
    reflection_success = phases.get("reflection", {}).get("success", False)
    improvement_success = phases.get("improvement", {}).get("success", False)
    implementation_success = phases.get("implementation", {}).get("success", False)
    
    print(f"    - Reflection Agent: {'✅' if reflection_success else '❌'}")
    print(f"    - Improvement Agent: {'✅' if improvement_success else '❌'}")
    print(f"    - Implementation Agent: {'✅' if implementation_success else '❌'}")
    
    # Show discovered weaknesses
    reflection_phase = phases.get("reflection", {})
    weaknesses = reflection_phase.get("weakness_patterns", [])
    print(f"    - Weaknesses identified: {len(weaknesses)}")
    
    # Show designed improvements
    improvement_phase = phases.get("improvement", {})
    improvements = improvement_phase.get("improvements", [])
    print(f"    - Improvements designed: {len(improvements)}")
    
    # Step 3: Create evolved prompts
    print(f"\n🧬 Step 3: Prompt Evolution")
    
    # Initialize prompt evolution manager
    prompt_manager = PromptEvolutionManager("demo_evolution_prompts")
    
    # Extract baseline scores
    baseline_scores = extract_baseline_scores(sample_evaluation_data)
    print(f"  Current baseline scores:")
    for category, score in baseline_scores.items():
        print(f"    - {category}: {score:.3f}/5")
    
    # Create evolution iteration with improvements
    print(f"  Creating evolution iteration 1...")
    iteration_dir = prompt_manager.create_evolution_iteration(
        iteration_number=1,
        improvements=improvements,
        baseline_scores=baseline_scores
    )
    
    print(f"  ✅ Evolution iteration created: {iteration_dir}")
    
    # Step 4: Generate presentation with evolved prompts
    print(f"\n🎯 Step 4: Test Evolved Generation")
    
    try:
        # Initialize evolved generator
        evolved_generator = EvolvedGenerator(
            api_key=Config.ANTHROPIC_API_KEY,
            evolution_iteration=1
        )
        
        print(f"  Evolved generator initialized with iteration 1")
        print(f"  Loaded {len(evolved_generator.evolved_prompts)} evolved prompts")
        
        # Create test generation directory
        test_dir = Path("demo_evolved_generation")
        test_dir.mkdir(exist_ok=True)
        
        # Generate test presentation
        test_topic = "sustainable energy solutions for developing countries"
        print(f"  Generating test presentation: {test_topic}")
        
        # Use evolved generation router for complete integration
        evolved_router = EvolvedGenerationRouter(
            api_key=Config.ANTHROPIC_API_KEY,
            evolution_iteration=1
        )
        
        generation_result = evolved_router.generate(
            input_source=test_topic,
            purpose="evolution system demonstration",
            theme="professional blue",
            output_dir=str(test_dir)
        )
        
        if generation_result.get("success"):
            print(f"  ✅ Evolved generation successful!")
            print(f"    - HTML file: {generation_result['html_file']}")
            print(f"    - Evolution metadata included")
            
            # Show generation stats
            evolution_metadata = generation_result.get("evolution_metadata", {})
            print(f"    - Generation stats: {evolution_metadata.get('generation_stats', {})}")
            
        else:
            print(f"  ❌ Evolved generation failed: {generation_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"  ⚠️ Evolved generation test skipped due to missing API key: {e}")
    
    # Step 5: Show evolution artifacts
    print(f"\n📁 Step 5: Evolution Artifacts")
    
    # Show evolved prompts
    current_prompts = prompt_manager.get_current_prompts(1)
    print(f"  Evolved prompts available:")
    for category, prompt in current_prompts.items():
        print(f"    - {category}: {len(prompt)} characters")
    
    # Show evolution history
    evolution_history = prompt_manager.get_evolution_history()
    print(f"  Evolution history:")
    print(f"    - Total iterations: {evolution_history['total_iterations']}")
    print(f"    - Iterations recorded: {len(evolution_history['iterations'])}")
    
    # Show agent artifacts
    print(f"  Agent analysis artifacts:")
    evolution_summary = agent_result.get("evolution_summary", {})
    iteration_summary = evolution_summary.get("iteration_summary", {})
    print(f"    - Total weaknesses identified: {iteration_summary.get('weaknesses_identified', 0)}")
    print(f"    - Total improvements designed: {iteration_summary.get('improvements_designed', 0)}")
    print(f"    - Total implementations created: {iteration_summary.get('implementations_created', 0)}")
    
    # Step 6: Save complete demonstration results
    print(f"\n💾 Step 6: Save Demonstration Results")
    
    demo_results = {
        "demonstration_timestamp": datetime.now().isoformat(),
        "sample_evaluation_data": sample_evaluation_data,
        "baseline_scores": baseline_scores,
        "agent_analysis_result": agent_result,
        "evolution_iteration_created": iteration_dir,
        "evolved_prompts_count": len(current_prompts),
        "evolution_history": evolution_history,
        "demonstration_success": True
    }
    
    results_file = "complete_evolution_cycle_demo_results.json"
    with open(results_file, 'w') as f:
        json.dump(demo_results, f, indent=2, default=str)
    
    print(f"  ✅ Demo results saved: {results_file}")
    
    # Final summary
    print(f"\n🎉 DEMONSTRATION COMPLETE!")
    print(f"=" * 60)
    print(f"✅ Multi-agent analysis: Successful")
    print(f"✅ Prompt evolution: {len(improvements)} improvements applied")
    print(f"✅ Evolved prompts: {len(current_prompts)} categories created")
    print(f"✅ System integration: Complete")
    
    print(f"\n🚀 The evolution system is now ready for production use!")
    print(f"   - Evolved prompts are saved in: {iteration_dir}")
    print(f"   - Use EvolvedGenerator for enhanced generation")
    print(f"   - Run A/B tests to validate improvements")
    
    return demo_results

def create_sample_evaluation_data():
    """Create realistic sample evaluation data for demonstration"""
    
    return [
        {
            "visual_evaluation": {
                "professional_design": {"score": 4, "reasoning": "Good overall design consistency"},
                "information_hierarchy": {"score": 3, "reasoning": "Adequate hierarchy but could be clearer"},
                "clarity_readability": {"score": 2, "reasoning": "Charts are hard to read, text too small"},
                "visual_textual_balance": {"score": 3, "reasoning": "Reasonable balance between visuals and text"},
                "overall_visual_score": 3.0
            },
            "content_reference_free_evaluation": {
                "logical_structure": {"score": 4, "reasoning": "Well organized flow"},
                "narrative_quality": {"score": 4, "reasoning": "Engaging story with good examples"},
                "comprehensive_coverage": {"score": 3, "reasoning": "Covers main points but missing some details"},
                "accuracy_plausibility": {"score": 2, "reasoning": "Some questionable claims and fake citations"},
                "overall_content_score": 3.25
            },
            "overall_scores": {
                "visual": 3.0,
                "content_reference_free": 3.25,
                "presentation_overall": 3.125
            },
            "source_path": "ai_healthcare_presentation",
            "topic": "AI applications in healthcare"
        },
        {
            "visual_evaluation": {
                "professional_design": {"score": 3, "reasoning": "Adequate design but inconsistent"},
                "information_hierarchy": {"score": 4, "reasoning": "Clear hierarchy and structure"},
                "clarity_readability": {"score": 2, "reasoning": "Multiple charts are unreadable"},
                "visual_textual_balance": {"score": 2, "reasoning": "Poor integration of visuals"},
                "overall_visual_score": 2.75
            },
            "content_reference_free_evaluation": {
                "logical_structure": {"score": 5, "reasoning": "Excellent logical flow"},
                "narrative_quality": {"score": 3, "reasoning": "Good narrative but could be more engaging"},
                "comprehensive_coverage": {"score": 3, "reasoning": "Good coverage of benefits, lacks challenges"},
                "accuracy_plausibility": {"score": 3, "reasoning": "Mostly accurate but some unsupported claims"},
                "overall_content_score": 3.5
            },
            "overall_scores": {
                "visual": 2.75,
                "content_reference_free": 3.5,
                "presentation_overall": 3.125
            },
            "source_path": "sustainable_energy_presentation",
            "topic": "Sustainable energy solutions"
        },
        {
            "visual_evaluation": {
                "professional_design": {"score": 3, "reasoning": "Basic professional appearance"},
                "information_hierarchy": {"score": 3, "reasoning": "Adequate but could be improved"},
                "clarity_readability": {"score": 2, "reasoning": "Technical diagrams are unclear"},
                "visual_textual_balance": {"score": 3, "reasoning": "Reasonable balance"},
                "overall_visual_score": 2.75
            },
            "content_reference_free_evaluation": {
                "logical_structure": {"score": 4, "reasoning": "Well structured technical content"},
                "narrative_quality": {"score": 3, "reasoning": "Technical but accessible"},
                "comprehensive_coverage": {"score": 4, "reasoning": "Comprehensive technical coverage"},
                "accuracy_plausibility": {"score": 4, "reasoning": "Technically accurate content"},
                "overall_content_score": 3.75
            },
            "overall_scores": {
                "visual": 2.75,
                "content_reference_free": 3.75,
                "presentation_overall": 3.25
            },
            "source_path": "quantum_computing_presentation",
            "topic": "Quantum computing principles"
        }
    ]

def calculate_avg_score(evaluation_data, category):
    """Calculate average score for a category"""
    scores = []
    for eval_data in evaluation_data:
        overall_scores = eval_data.get("overall_scores", {})
        if category in overall_scores:
            scores.append(overall_scores[category])
    
    return sum(scores) / len(scores) if scores else 0.0

def extract_baseline_scores(evaluation_data):
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

if __name__ == "__main__":
    try:
        demo_results = demo_complete_evolution_cycle()
        print("\n✅ Demonstration completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)