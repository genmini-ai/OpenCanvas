"""
Checkpoint Management for Evolution System

This module manages different versions/checkpoints of the generation system,
starting with the production baseline and evolving through iterations.
"""

from pathlib import Path
import shutil
import json
from datetime import datetime
from typing import Dict, Any, Optional

class CheckpointManager:
    """Manages generation system checkpoints for evolution"""
    
    def __init__(self, checkpoints_dir: str = None):
        """Initialize checkpoint manager"""
        if checkpoints_dir:
            self.checkpoints_dir = Path(checkpoints_dir)
        else:
            # Default to evolution/checkpoints directory
            self.checkpoints_dir = Path(__file__).parent
        
        self.baseline_dir = self.checkpoints_dir / "baseline"
        self.iterations_dir = self.checkpoints_dir / "iterations"
        self.iterations_dir.mkdir(exist_ok=True)
        
        # Track current active checkpoint
        self.current_checkpoint = "baseline"
        
    def get_baseline_generators(self) -> Dict[str, Path]:
        """Get paths to baseline (production) generator files"""
        return {
            "topic_generator": self.baseline_dir / "topic_generator.py",
            "pdf_generator": self.baseline_dir / "pdf_generator.py"
        }
    
    def create_iteration_checkpoint(self, iteration_num: int, modifications: Dict[str, Any]) -> Path:
        """Create a new checkpoint for an evolution iteration"""
        
        iteration_dir = self.iterations_dir / f"iteration_{iteration_num:03d}"
        iteration_dir.mkdir(exist_ok=True)
        
        # Copy baseline files to iteration directory
        for name, baseline_path in self.get_baseline_generators().items():
            if baseline_path.exists():
                shutil.copy2(baseline_path, iteration_dir / baseline_path.name)
        
        # Save metadata about modifications
        metadata = {
            "iteration": iteration_num,
            "created_at": datetime.now().isoformat(),
            "base_checkpoint": self.current_checkpoint,
            "modifications": modifications,
            "performance_metrics": {}
        }
        
        with open(iteration_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return iteration_dir
    
    def load_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Load a specific checkpoint"""
        
        if checkpoint_name == "baseline":
            return {
                "name": "baseline",
                "path": self.baseline_dir,
                "generators": self.get_baseline_generators(),
                "is_production": True
            }
        else:
            # Load iteration checkpoint
            iteration_dir = self.iterations_dir / checkpoint_name
            if not iteration_dir.exists():
                raise ValueError(f"Checkpoint {checkpoint_name} not found")
            
            # Load metadata
            with open(iteration_dir / "metadata.json", 'r') as f:
                metadata = json.load(f)
            
            return {
                "name": checkpoint_name,
                "path": iteration_dir,
                "generators": {
                    "topic_generator": iteration_dir / "topic_generator.py",
                    "pdf_generator": iteration_dir / "pdf_generator.py"
                },
                "metadata": metadata,
                "is_production": False
            }
    
    def get_best_checkpoint(self) -> Optional[str]:
        """Get the best performing checkpoint based on metrics"""
        
        best_score = 0
        best_checkpoint = "baseline"
        
        # Check all iteration checkpoints
        for iteration_dir in self.iterations_dir.glob("iteration_*"):
            metadata_file = iteration_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                metrics = metadata.get("performance_metrics", {})
                overall_score = metrics.get("overall_score", 0)
                
                if overall_score > best_score:
                    best_score = overall_score
                    best_checkpoint = iteration_dir.name
        
        return best_checkpoint
    
    def set_active_checkpoint(self, checkpoint_name: str):
        """Set the active checkpoint for generation"""
        self.current_checkpoint = checkpoint_name
        
    def get_checkpoint_history(self) -> list:
        """Get history of all checkpoints"""
        
        history = [{"name": "baseline", "type": "production"}]
        
        # Add all iterations
        for iteration_dir in sorted(self.iterations_dir.glob("iteration_*")):
            metadata_file = iteration_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    history.append({
                        "name": iteration_dir.name,
                        "type": "iteration",
                        "created_at": metadata.get("created_at"),
                        "metrics": metadata.get("performance_metrics", {})
                    })
        
        return history