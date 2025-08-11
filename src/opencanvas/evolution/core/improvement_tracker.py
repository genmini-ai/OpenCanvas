"""
Improvement Tracker - Fine-grained traceability for evolution improvements
Links specific improvements (prompts/tools) to score deltas with attribution
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ImprovementType(Enum):
    """Types of improvements that can be made"""
    PROMPT_EVOLUTION = "prompt_evolution"
    TOOL_CREATION = "tool_creation"
    TOOL_MODIFICATION = "tool_modification"
    PARAMETER_TUNING = "parameter_tuning"
    PIPELINE_OPTIMIZATION = "pipeline_optimization"

@dataclass
class ScoreDelta:
    """Represents change in scores"""
    category: str  # e.g., "visual_design", "content_accuracy"
    subcategory: Optional[str]  # e.g., "slide_consistency", "factual_accuracy"
    before_score: float
    after_score: float
    delta: float
    percentage_change: float
    
    @classmethod
    def from_scores(cls, category: str, before: float, after: float, subcategory: Optional[str] = None):
        """Create ScoreDelta from before/after scores"""
        delta = after - before
        percentage = (delta / before * 100) if before > 0 else 0
        return cls(
            category=category,
            subcategory=subcategory,
            before_score=before,
            after_score=after,
            delta=delta,
            percentage_change=percentage
        )

@dataclass
class Improvement:
    """Represents a single improvement made during evolution"""
    id: str  # Unique identifier
    iteration: int
    type: ImprovementType
    name: str
    description: str
    implementation_details: Dict[str, Any]
    timestamp: str
    
    # Attribution
    target_weakness: str  # What weakness this addresses
    expected_impact: str  # What we expect to improve
    
    # Results
    actual_impact: Optional[List[ScoreDelta]] = None
    success: Optional[bool] = None
    failure_reason: Optional[str] = None
    
    # Metadata
    parent_improvements: List[str] = None  # IDs of improvements this builds on
    child_improvements: List[str] = None  # IDs of improvements that build on this
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['type'] = self.type.value
        return data

class ImprovementTracker:
    """
    Tracks all improvements made during evolution with fine-grained attribution
    Links improvements to specific score changes and maintains dependency graph
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize tracker with optional output directory"""
        self.output_dir = Path(output_dir) if output_dir else Path("evolution_tracking")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.improvements: Dict[str, Improvement] = {}
        self.iteration_scores: Dict[int, Dict[str, Any]] = {}
        self.improvement_timeline: List[str] = []  # Ordered list of improvement IDs
        
        # Load existing tracking data if available
        self._load_existing_data()
        
        logger.info(f"📊 Improvement Tracker initialized at {self.output_dir}")
    
    def _load_existing_data(self):
        """Load existing tracking data from disk"""
        tracking_file = self.output_dir / "improvement_tracking.json"
        
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct improvements
                for imp_data in data.get('improvements', []):
                    imp = Improvement(
                        id=imp_data['id'],
                        iteration=imp_data['iteration'],
                        type=ImprovementType(imp_data['type']),
                        name=imp_data['name'],
                        description=imp_data['description'],
                        implementation_details=imp_data['implementation_details'],
                        timestamp=imp_data['timestamp'],
                        target_weakness=imp_data['target_weakness'],
                        expected_impact=imp_data['expected_impact'],
                        actual_impact=[ScoreDelta(**sd) for sd in imp_data.get('actual_impact', [])] if imp_data.get('actual_impact') else None,
                        success=imp_data.get('success'),
                        failure_reason=imp_data.get('failure_reason'),
                        parent_improvements=imp_data.get('parent_improvements', []),
                        child_improvements=imp_data.get('child_improvements', [])
                    )
                    self.improvements[imp.id] = imp
                
                self.iteration_scores = data.get('iteration_scores', {})
                self.improvement_timeline = data.get('improvement_timeline', [])
                
                logger.info(f"📚 Loaded {len(self.improvements)} existing improvements")
                
            except Exception as e:
                logger.error(f"❌ Failed to load existing tracking data: {e}")
    
    def register_improvement(self, 
                           iteration: int,
                           type: ImprovementType,
                           name: str,
                           description: str,
                           target_weakness: str,
                           expected_impact: str,
                           implementation_details: Dict[str, Any],
                           parent_improvements: Optional[List[str]] = None) -> str:
        """
        Register a new improvement attempt
        
        Returns:
            Improvement ID for tracking
        """
        # Generate unique ID
        timestamp = datetime.now().isoformat()
        imp_id = f"{iteration:03d}_{type.value}_{name.replace(' ', '_')}_{timestamp}"
        
        improvement = Improvement(
            id=imp_id,
            iteration=iteration,
            type=type,
            name=name,
            description=description,
            implementation_details=implementation_details,
            timestamp=timestamp,
            target_weakness=target_weakness,
            expected_impact=expected_impact,
            parent_improvements=parent_improvements or []
        )
        
        self.improvements[imp_id] = improvement
        self.improvement_timeline.append(imp_id)
        
        # Update parent improvements to add this as child
        if parent_improvements:
            for parent_id in parent_improvements:
                if parent_id in self.improvements:
                    if not self.improvements[parent_id].child_improvements:
                        self.improvements[parent_id].child_improvements = []
                    self.improvements[parent_id].child_improvements.append(imp_id)
        
        logger.info(f"✅ Registered improvement: {name} (ID: {imp_id})")
        self._save_data()
        
        return imp_id
    
    def record_iteration_scores(self, iteration: int, scores: Dict[str, Any]):
        """Record evaluation scores for an iteration"""
        # Convert scores to serializable format
        self.iteration_scores[str(iteration)] = scores
        
        logger.info(f"📊 Recorded scores for iteration {iteration}")
        self._save_data()
    
    def attribute_score_changes(self, improvement_id: str, iteration: int) -> List[ScoreDelta]:
        """
        Attribute score changes to a specific improvement
        
        Args:
            improvement_id: ID of the improvement to attribute
            iteration: Current iteration number
        
        Returns:
            List of ScoreDelta objects showing attributed changes
        """
        if improvement_id not in self.improvements:
            logger.error(f"❌ Unknown improvement ID: {improvement_id}")
            return []
        
        improvement = self.improvements[improvement_id]
        
        # Get before/after scores
        before_scores = self.iteration_scores.get(str(iteration - 1), {})
        after_scores = self.iteration_scores.get(str(iteration), {})
        
        if not before_scores or not after_scores:
            logger.warning(f"⚠️ Missing scores for attribution (iter {iteration-1} -> {iteration})")
            return []
        
        score_deltas = []
        
        # Analyze score changes based on improvement type and target
        if improvement.type == ImprovementType.PROMPT_EVOLUTION:
            # Prompt changes typically affect content quality and coherence
            categories = ['content_accuracy', 'information_completeness', 'slide_coherence']
        elif improvement.type == ImprovementType.TOOL_CREATION:
            # Tools can affect various aspects depending on their purpose
            if 'citation' in improvement.name.lower():
                categories = ['content_accuracy', 'source_credibility']
            elif 'layout' in improvement.name.lower() or 'visual' in improvement.name.lower():
                categories = ['visual_design', 'slide_consistency']
            else:
                categories = ['overall_quality']  # Generic attribution
        else:
            categories = ['overall_quality']
        
        # Calculate deltas for relevant categories
        for category in categories:
            # Handle nested score structures
            before_val = self._extract_score_value(before_scores, category)
            after_val = self._extract_score_value(after_scores, category)
            
            if before_val is not None and after_val is not None:
                delta = ScoreDelta.from_scores(category, before_val, after_val)
                score_deltas.append(delta)
        
        # Update improvement with actual impact
        improvement.actual_impact = score_deltas
        
        # Determine success based on deltas
        if score_deltas:
            avg_delta = sum(d.delta for d in score_deltas) / len(score_deltas)
            improvement.success = avg_delta > 0
            
            if not improvement.success:
                improvement.failure_reason = f"Negative impact: avg delta {avg_delta:.2f}"
        
        self._save_data()
        return score_deltas
    
    def _extract_score_value(self, scores: Dict[str, Any], category: str) -> Optional[float]:
        """Extract a score value from potentially nested structure"""
        # Check top-level
        if category in scores:
            val = scores[category]
            if isinstance(val, (int, float)):
                return float(val)
            elif isinstance(val, dict) and 'score' in val:
                return float(val['score'])
        
        # Check in nested structures (visual_scores, content_scores, etc.)
        for key in ['visual_scores', 'content_free_scores', 'content_required_scores', 'overall_scores']:
            if key in scores and isinstance(scores[key], dict):
                if category in scores[key]:
                    val = scores[key][category]
                    if isinstance(val, (int, float)):
                        return float(val)
                    elif isinstance(val, dict) and 'score' in val:
                        return float(val['score'])
        
        return None
    
    def get_improvement_report(self, iteration: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate comprehensive improvement report
        
        Args:
            iteration: Specific iteration to report on (None for all)
        
        Returns:
            Detailed report of improvements and their impacts
        """
        if iteration is not None:
            improvements = [imp for imp in self.improvements.values() if imp.iteration == iteration]
        else:
            improvements = list(self.improvements.values())
        
        successful = [imp for imp in improvements if imp.success is True]
        failed = [imp for imp in improvements if imp.success is False]
        pending = [imp for imp in improvements if imp.success is None]
        
        # Calculate aggregate impact
        total_delta = 0
        category_impacts = {}
        
        for imp in improvements:
            if imp.actual_impact:
                for delta in imp.actual_impact:
                    total_delta += delta.delta
                    if delta.category not in category_impacts:
                        category_impacts[delta.category] = []
                    category_impacts[delta.category].append(delta.delta)
        
        # Average impacts by category
        category_avg = {cat: sum(deltas)/len(deltas) for cat, deltas in category_impacts.items() if deltas}
        
        report = {
            'iteration': iteration,
            'summary': {
                'total_improvements': len(improvements),
                'successful': len(successful),
                'failed': len(failed),
                'pending': len(pending),
                'success_rate': len(successful) / len(improvements) * 100 if improvements else 0
            },
            'impact': {
                'total_score_delta': total_delta,
                'average_delta_per_improvement': total_delta / len(improvements) if improvements else 0,
                'category_impacts': category_avg
            },
            'improvements': [imp.to_dict() for imp in improvements],
            'dependency_graph': self._build_dependency_graph(improvements)
        }
        
        return report
    
    def _build_dependency_graph(self, improvements: List[Improvement]) -> Dict[str, Any]:
        """Build a dependency graph showing improvement relationships"""
        graph = {
            'nodes': [],
            'edges': []
        }
        
        imp_ids = {imp.id for imp in improvements}
        
        for imp in improvements:
            # Add node
            graph['nodes'].append({
                'id': imp.id,
                'name': imp.name,
                'type': imp.type.value,
                'success': imp.success
            })
            
            # Add edges for parent relationships
            for parent_id in imp.parent_improvements:
                if parent_id in imp_ids:
                    graph['edges'].append({
                        'from': parent_id,
                        'to': imp.id,
                        'type': 'parent'
                    })
        
        return graph
    
    def _save_data(self):
        """Save tracking data to disk"""
        tracking_file = self.output_dir / "improvement_tracking.json"
        
        data = {
            'improvements': [imp.to_dict() for imp in self.improvements.values()],
            'iteration_scores': self.iteration_scores,
            'improvement_timeline': self.improvement_timeline,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(tracking_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_detailed_report(self, output_file: Optional[Path] = None):
        """Export detailed tracking report to file"""
        if not output_file:
            output_file = self.output_dir / f"improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'tracking_summary': self.get_improvement_report(),
            'iteration_details': {},
            'improvement_timeline': []
        }
        
        # Add per-iteration details
        for iteration in sorted(set(imp.iteration for imp in self.improvements.values())):
            report['iteration_details'][iteration] = self.get_improvement_report(iteration)
        
        # Add timeline with full details
        for imp_id in self.improvement_timeline:
            if imp_id in self.improvements:
                report['improvement_timeline'].append(self.improvements[imp_id].to_dict())
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Exported detailed report to {output_file}")
        
        # Also update TOOLS_REGISTRY.md with lessons learned
        self.update_tools_registry_lessons()
        
        return output_file
    
    def update_tools_registry_lessons(self):
        """Update TOOLS_REGISTRY.md with lessons learned from this tracking session"""
        registry_path = Path("TOOLS_REGISTRY.md")
        
        # Read existing content if file exists
        existing_content = ""
        if registry_path.exists():
            existing_content = registry_path.read_text()
            # Find where to insert lessons (before the end or after a specific section)
            if "## 📚 Lessons Learned" not in existing_content:
                existing_content += "\n\n## 📚 Lessons Learned\n\n"
        else:
            # Create new file with header
            existing_content = """# 🛠️ Tools Registry & Lessons Learned

This document tracks all tools (active, proposed, failed) and lessons learned from evolution runs.

## 📚 Lessons Learned

"""
        
        # Generate lessons content
        lessons_content = f"\n### Evolution Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Add successful improvements
        successful = [imp for imp in self.improvements.values() if imp.success is True]
        if successful:
            lessons_content += "#### ✅ Successful Improvements\n\n"
            for imp in successful[:5]:  # Top 5 successful
                if imp.actual_impact:
                    avg_delta = sum(d.delta for d in imp.actual_impact) / len(imp.actual_impact)
                    lessons_content += f"**{imp.name}**\n"
                    lessons_content += f"- **Target**: {imp.target_weakness}\n"
                    lessons_content += f"- **Impact**: {avg_delta:+.3f} avg score change\n"
                    lessons_content += f"- **Categories affected**: {', '.join(set(d.category for d in imp.actual_impact))}\n"
                    lessons_content += f"- **Lesson**: {imp.expected_impact} → "
                    if avg_delta > 0:
                        lessons_content += "✅ Confirmed effective\n"
                    else:
                        lessons_content += "⚠️ Mixed results\n"
                    lessons_content += "\n"
        
        # Add failed improvements
        failed = [imp for imp in self.improvements.values() if imp.success is False]
        if failed:
            lessons_content += "#### ❌ Failed Improvements\n\n"
            for imp in failed[:5]:  # Top 5 failures
                lessons_content += f"**{imp.name}**\n"
                lessons_content += f"- **Target**: {imp.target_weakness}\n"
                lessons_content += f"- **Failure reason**: {imp.failure_reason or 'Unknown'}\n"
                if imp.actual_impact:
                    avg_delta = sum(d.delta for d in imp.actual_impact) / len(imp.actual_impact)
                    lessons_content += f"- **Actual impact**: {avg_delta:+.3f} (negative)\n"
                lessons_content += f"- **Lesson learned**: Avoid {imp.type.value} for {imp.target_weakness}\n\n"
        
        # Add score attribution summary
        report = self.get_improvement_report()
        if report['impact']['category_impacts']:
            lessons_content += "#### 📊 Category Impact Summary\n\n"
            for category, impact in sorted(report['impact']['category_impacts'].items(), key=lambda x: x[1], reverse=True):
                emoji = "📈" if impact > 0 else "📉"
                lessons_content += f"- **{category}**: {emoji} {impact:+.3f} avg change\n"
            lessons_content += "\n"
        
        # Add recommendations
        lessons_content += "#### 💡 Recommendations for Next Run\n\n"
        if successful:
            lessons_content += f"1. **Continue using**: {', '.join(s.name for s in successful[:3])}\n"
        if failed:
            lessons_content += f"2. **Avoid or revise**: {', '.join(f.name for f in failed[:3])}\n"
        
        success_rate = report['summary']['success_rate']
        if success_rate < 50:
            lessons_content += "3. **Low success rate** - Consider smaller, more targeted improvements\n"
        elif success_rate > 80:
            lessons_content += "3. **High success rate** - Can attempt more ambitious improvements\n"
        
        lessons_content += "\n---\n"
        
        # Update the file
        if "## 📚 Lessons Learned" in existing_content:
            # Insert after the header
            parts = existing_content.split("## 📚 Lessons Learned")
            updated_content = parts[0] + "## 📚 Lessons Learned\n" + lessons_content + parts[1]
        else:
            updated_content = existing_content + lessons_content
        
        # Write back
        registry_path.write_text(updated_content)
        logger.info(f"📝 Updated {registry_path} with lessons learned")


# Global tracker instance
_tracker_instance = None

def get_improvement_tracker(output_dir: Optional[Path] = None) -> ImprovementTracker:
    """Get or create the global improvement tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ImprovementTracker(output_dir)
    return _tracker_instance