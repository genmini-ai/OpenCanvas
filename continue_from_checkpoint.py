#!/usr/bin/env python
"""Continue evolution from a previous checkpoint"""

import json
import shutil
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from test_evolution_unified_final import UnifiedEvolutionRunner

def find_latest_checkpoint(base_dir="evolution_runs"):
    """Find the most recent checkpoint directory"""
    base_path = Path(base_dir)
    if not base_path.exists():
        return None
    
    # Find all experiment directories
    exp_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("ai_animal_care_")]
    
    if not exp_dirs:
        return None
    
    # Sort by modification time and get the most recent
    latest = max(exp_dirs, key=lambda d: d.stat().st_mtime)
    return latest

def analyze_checkpoint(checkpoint_dir):
    """Analyze checkpoint to determine last completed iteration"""
    checkpoint_path = Path(checkpoint_dir)
    
    # Read config
    config_file = checkpoint_path / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {}
    
    # Find last completed iteration
    iterations = [d for d in checkpoint_path.iterdir() 
                  if d.is_dir() and d.name.startswith("iteration_")]
    
    if not iterations:
        return 0, config
    
    # Get the highest iteration number
    last_iteration = max(int(d.name.split("_")[1]) for d in iterations)
    
    # Check if evolution results exist
    results_file = checkpoint_path / "output" / "evolution_results.json"
    if results_file.exists():
        with open(results_file) as f:
            results = json.load(f)
            successful_iterations = [i for i in results.get("iterations", []) 
                                    if i.get("success", False)]
            if successful_iterations:
                last_iteration = max(i["iteration"] for i in successful_iterations)
    
    return last_iteration, config

def continue_from_checkpoint(checkpoint_dir=None, additional_iterations=2):
    """Continue evolution from a checkpoint"""
    
    # Find checkpoint directory
    if checkpoint_dir:
        checkpoint_path = Path(checkpoint_dir)
    else:
        checkpoint_path = find_latest_checkpoint()
        if not checkpoint_path:
            print("❌ No checkpoint found. Please specify a checkpoint directory.")
            return
    
    print(f"📁 Loading checkpoint from: {checkpoint_path}")
    
    # Analyze checkpoint
    last_iteration, original_config = analyze_checkpoint(checkpoint_path)
    
    print(f"📊 Checkpoint Analysis:")
    print(f"  - Last completed iteration: {last_iteration}")
    print(f"  - Original topics: {original_config.get('test_topics', ['Unknown'])}")
    print(f"  - Original max iterations: {original_config.get('max_iterations', 'Unknown')}")
    
    # Create new experiment name for continuation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_experiment_name = f"ai_animal_care_continued_{timestamp}"
    
    print(f"\n🔄 Continuing Evolution:")
    print(f"  - New experiment: {new_experiment_name}")
    print(f"  - Starting from iteration: {last_iteration + 1}")
    print(f"  - Additional iterations: {additional_iterations}")
    
    # Copy evolved assets to new experiment
    print("\n📦 Copying evolved assets...")
    
    # Create new runner
    runner = UnifiedEvolutionRunner(experiment_name=new_experiment_name)
    
    # Copy evolved prompts if they exist
    prev_prompts_dir = checkpoint_path / "prompts"
    if prev_prompts_dir.exists():
        if runner.evolution_prompts.exists():
            shutil.rmtree(runner.evolution_prompts)
        shutil.copytree(prev_prompts_dir, runner.evolution_prompts)
        print(f"  ✅ Copied evolved prompts from iteration {last_iteration}")
    
    # Copy output directory structure if needed
    prev_output_dir = checkpoint_path / "output"
    if prev_output_dir.exists():
        # Copy previous iteration directories
        for iteration_dir in prev_output_dir.iterdir():
            if iteration_dir.is_dir() and iteration_dir.name.startswith("iteration_"):
                dest_dir = runner.evolution_output / iteration_dir.name
                if not dest_dir.exists():
                    shutil.copytree(iteration_dir, dest_dir)
                    print(f"  ✅ Copied {iteration_dir.name}")
    
    # Note about auto-generated tools
    print("\n🔧 Auto-generated tools check:")
    tools_dir = Path("src/opencanvas/evolution/tools")
    for i in range(1, last_iteration + 1):
        tool_dir = tools_dir / f"iteration_{i:03d}"
        if tool_dir.exists():
            print(f"  ✅ Tools from iteration {i} already available")
    
    # Update configuration for continuation
    print("\n🚀 Starting continued evolution...")
    
    # Run evolution continuing from next iteration
    try:
        results = runner.run_evolution(
            test_topics=original_config.get("test_topics", ["AI in animal care"]),
            max_iterations=last_iteration + additional_iterations,
            start_iteration=last_iteration + 1
        )
        
        print("\n✅ Continuation complete!")
        print(f"📁 Results saved to: evolution_runs/{new_experiment_name}/")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Continuation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main entry point for checkpoint continuation"""
    
    print("=" * 70)
    print("🔄 EVOLUTION CHECKPOINT CONTINUATION")
    print("=" * 70)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        checkpoint_dir = sys.argv[1]
        print(f"📁 Using specified checkpoint: {checkpoint_dir}")
    else:
        checkpoint_dir = None
        print("🔍 Looking for latest checkpoint...")
    
    # Additional iterations (can be customized)
    additional_iterations = 2
    if len(sys.argv) > 2:
        additional_iterations = int(sys.argv[2])
    
    # Find latest checkpoint if not specified
    if not checkpoint_dir:
        latest = find_latest_checkpoint()
        if latest:
            print(f"📁 Found latest checkpoint: {latest}")
            checkpoint_dir = str(latest)
        else:
            print("❌ No checkpoints found in evolution_runs/")
            print("\nUsage:")
            print("  python continue_from_checkpoint.py [checkpoint_dir] [additional_iterations]")
            print("\nExample:")
            print("  python continue_from_checkpoint.py evolution_runs/ai_animal_care_20250806_223814 2")
            return
    
    # Confirm before continuing
    print("\n" + "=" * 70)
    response = input("⚠️  Ready to continue evolution from checkpoint? (y/n): ")
    if response.lower() != 'y':
        print("Continuation cancelled.")
        return
    
    # Continue from checkpoint
    continue_from_checkpoint(checkpoint_dir, additional_iterations)

if __name__ == "__main__":
    main()