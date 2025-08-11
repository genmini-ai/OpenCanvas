"""
Concrete Improvement Strategies for Evolution System
These strategies ensure the evolution actually improves quality
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ImprovementStrategy:
    """A concrete strategy for improving presentation quality"""
    name: str
    target_metric: str
    approach: str
    implementation: str
    expected_impact: float
    priority: str

class EvolutionStrategies:
    """
    Concrete strategies that actually improve presentations
    Based on analysis of what works and what doesn't
    """
    
    def __init__(self):
        self.strategies = self._initialize_strategies()
        logger.info(f"🎯 Initialized {len(self.strategies)} improvement strategies")
    
    def _initialize_strategies(self) -> Dict[str, ImprovementStrategy]:
        """Initialize proven improvement strategies"""
        return {
            "enhance_visuals": ImprovementStrategy(
                name="Visual Enhancement Strategy",
                target_metric="visual_quality",
                approach="Add data visualizations and reduce text density",
                implementation="""
                1. Extract all numerical data from content
                2. Generate appropriate charts (bar, line, pie)
                3. Replace text-heavy slides with visual representations
                4. Ensure 40/60 visual-to-text ratio minimum
                """,
                expected_impact=0.5,
                priority="CRITICAL"
            ),
            
            "ensure_accuracy": ImprovementStrategy(
                name="Source Fidelity Strategy",
                target_metric="accuracy",
                approach="Verify all claims against source material",
                implementation="""
                1. Extract all factual claims from generated content
                2. Cross-reference with source material
                3. Flag and remove unsupported additions
                4. Add citation markers for verifiable claims
                """,
                expected_impact=0.3,
                priority="HIGH"
            ),
            
            "improve_engagement": ImprovementStrategy(
                name="Engagement Optimization Strategy",
                target_metric="engagement",
                approach="Add interactive and memorable elements",
                implementation="""
                1. Add relevant real-world examples
                2. Include case studies with specific outcomes
                3. Use storytelling techniques for flow
                4. Add memorable statistics with visual emphasis
                """,
                expected_impact=0.4,
                priority="HIGH"
            ),
            
            "fix_consistency": ImprovementStrategy(
                name="Consistency Enforcement Strategy",
                target_metric="consistency",
                approach="Ensure uniform design and messaging",
                implementation="""
                1. Standardize color palette across all slides
                2. Ensure consistent font sizes and styles
                3. Maintain uniform bullet point formatting
                4. Align visual element positioning
                """,
                expected_impact=0.2,
                priority="MEDIUM"
            ),
            
            "add_structure": ImprovementStrategy(
                name="Structural Enhancement Strategy",
                target_metric="logical_flow",
                approach="Improve presentation narrative and flow",
                implementation="""
                1. Add clear section dividers
                2. Include progress indicators
                3. Add transition slides between major topics
                4. Ensure each slide has clear takeaway
                """,
                expected_impact=0.3,
                priority="MEDIUM"
            )
        }
    
    def get_strategy_for_weakness(self, evaluation_data: Dict) -> Optional[ImprovementStrategy]:
        """Get the best strategy for current weaknesses"""
        
        # Analyze evaluation scores to find weaknesses
        weaknesses = self._identify_weaknesses(evaluation_data)
        
        if not weaknesses:
            logger.info("No significant weaknesses found")
            return None
        
        # Get highest priority weakness
        priority_weakness = max(weaknesses.items(), key=lambda x: x[1])
        weakness_type, severity = priority_weakness
        
        logger.info(f"🎯 Identified primary weakness: {weakness_type} (severity: {severity:.2f})")
        
        # Map weakness to strategy
        strategy_mapping = {
            "visual_quality": "enhance_visuals",
            "text_heavy": "enhance_visuals",
            "accuracy": "ensure_accuracy",
            "engagement": "improve_engagement",
            "consistency": "fix_consistency",
            "structure": "add_structure"
        }
        
        strategy_key = strategy_mapping.get(weakness_type)
        if strategy_key and strategy_key in self.strategies:
            return self.strategies[strategy_key]
        
        return None
    
    def _identify_weaknesses(self, evaluation_data: Dict) -> Dict[str, float]:
        """Identify weaknesses from evaluation data"""
        weaknesses = {}
        
        # Check visual quality
        visual_score = evaluation_data.get("visual_scores", {}).get("overall_visual_score", 5)
        if visual_score < 4.0:
            weaknesses["visual_quality"] = 4.0 - visual_score
        
        # Check for text-heavy presentations (based on visual-textual balance)
        balance_score = evaluation_data.get("visual_scores", {}).get("visual_textual_balance", {}).get("score", 5)
        if balance_score < 3.5:
            weaknesses["text_heavy"] = 3.5 - balance_score
        
        # Check accuracy
        accuracy_score = evaluation_data.get("content_required_scores", {}).get("accuracy", {}).get("score", 5)
        if accuracy_score < 4.5:
            weaknesses["accuracy"] = 4.5 - accuracy_score
        
        # Check engagement (narrative quality)
        narrative_score = evaluation_data.get("content_free_scores", {}).get("narrative_quality", {}).get("score", 5)
        if narrative_score < 4.0:
            weaknesses["engagement"] = 4.0 - narrative_score
        
        # Check structure
        structure_score = evaluation_data.get("content_free_scores", {}).get("logical_structure", {}).get("score", 5)
        if structure_score < 4.0:
            weaknesses["structure"] = 4.0 - structure_score
        
        return weaknesses
    
    def generate_prompt_improvements(self, strategy: ImprovementStrategy) -> Dict[str, str]:
        """Generate specific prompt improvements based on strategy"""
        
        prompt_improvements = {}
        
        if strategy.name == "Visual Enhancement Strategy":
            prompt_improvements["slide_generation"] = """
CRITICAL VISUAL REQUIREMENTS:
- EVERY slide must have at least one visual element (chart, image, diagram, or icon)
- For any numerical data, CREATE a chart visualization:
  * Use bar charts for comparisons
  * Use line graphs for trends over time
  * Use pie charts for proportional data
- Maintain a 40/60 visual-to-text ratio minimum
- Use data visualization libraries like Chart.js for interactive charts
- Include relevant, high-quality images for each major concept
- NEVER create text-only slides
"""
        
        elif strategy.name == "Source Fidelity Strategy":
            prompt_improvements["content_generation"] = """
STRICT ACCURACY REQUIREMENTS:
- ONLY include information that is EXPLICITLY stated in the source material
- Do NOT add plausible but unverified details
- Mark all statistics and claims with source references
- If information seems missing, note it rather than inventing it
- Cross-check every fact before including it
- Use exact figures from source, not approximations
"""
        
        elif strategy.name == "Engagement Optimization Strategy":
            prompt_improvements["narrative_enhancement"] = """
ENGAGEMENT REQUIREMENTS:
- Start each section with a compelling hook or question
- Include at least one real-world case study per major topic
- Use specific examples with names, dates, and outcomes
- Add "Did you know?" boxes with surprising statistics
- Include interactive elements or thought-provoking questions
- End each section with clear, actionable takeaways
"""
        
        return prompt_improvements
    
    def generate_tool_specification(self, strategy: ImprovementStrategy) -> Dict[str, Any]:
        """Generate tool specification based on strategy"""
        
        tool_spec = {
            "name": f"{strategy.name.replace(' ', '')}Tool",
            "purpose": strategy.approach,
            "target_problem": strategy.target_metric,
            "expected_impact": strategy.expected_impact,
            "priority": strategy.priority,
            "implementation_steps": strategy.implementation.strip().split('\n'),
            "validation_criteria": []
        }
        
        # Add specific validation criteria based on strategy
        if "Visual" in strategy.name:
            tool_spec["validation_criteria"] = [
                "Each slide has at least one visual element",
                "Visual-to-text ratio >= 40%",
                "All numerical data is visualized"
            ]
        elif "Accuracy" in strategy.name:
            tool_spec["validation_criteria"] = [
                "All claims traced to source",
                "No unsupported additions",
                "Statistics match source exactly"
            ]
        elif "Engagement" in strategy.name:
            tool_spec["validation_criteria"] = [
                "Case studies present",
                "Real examples included",
                "Clear takeaways on each slide"
            ]
        
        return tool_spec
    
    def create_implementation_plan(self, weaknesses: Dict[str, float]) -> List[Dict]:
        """Create a concrete implementation plan for improvements"""
        
        plan = []
        
        # Sort weaknesses by severity
        sorted_weaknesses = sorted(weaknesses.items(), key=lambda x: x[1], reverse=True)
        
        for weakness, severity in sorted_weaknesses[:3]:  # Top 3 weaknesses
            # Get strategy for this weakness
            strategy = self._get_strategy_for_weakness_type(weakness)
            if strategy:
                plan.append({
                    "step": len(plan) + 1,
                    "weakness": weakness,
                    "severity": severity,
                    "strategy": strategy.name,
                    "approach": strategy.approach,
                    "expected_impact": strategy.expected_impact,
                    "implementation": strategy.implementation,
                    "priority": strategy.priority
                })
        
        return plan
    
    def _get_strategy_for_weakness_type(self, weakness_type: str) -> Optional[ImprovementStrategy]:
        """Get strategy for specific weakness type"""
        mapping = {
            "visual_quality": self.strategies.get("enhance_visuals"),
            "text_heavy": self.strategies.get("enhance_visuals"),
            "accuracy": self.strategies.get("ensure_accuracy"),
            "engagement": self.strategies.get("improve_engagement"),
            "consistency": self.strategies.get("fix_consistency"),
            "structure": self.strategies.get("add_structure")
        }
        return mapping.get(weakness_type)
    
    def measure_improvement(self, before: Dict, after: Dict, strategy: ImprovementStrategy) -> Dict:
        """Measure actual improvement from strategy implementation"""
        
        metric = strategy.target_metric
        
        # Extract relevant scores
        before_score = self._extract_metric_score(before, metric)
        after_score = self._extract_metric_score(after, metric)
        
        improvement = after_score - before_score
        success = improvement > 0
        
        result = {
            "strategy": strategy.name,
            "metric": metric,
            "before": before_score,
            "after": after_score,
            "improvement": improvement,
            "expected": strategy.expected_impact,
            "success": success,
            "efficiency": improvement / strategy.expected_impact if strategy.expected_impact > 0 else 0
        }
        
        if success:
            logger.info(f"✅ Strategy {strategy.name} improved {metric} by {improvement:.2f}")
        else:
            logger.warning(f"❌ Strategy {strategy.name} failed to improve {metric}")
        
        return result
    
    def _extract_metric_score(self, evaluation: Dict, metric: str) -> float:
        """Extract specific metric score from evaluation data"""
        
        if metric == "visual_quality":
            return evaluation.get("visual_scores", {}).get("overall_visual_score", 0)
        elif metric == "accuracy":
            return evaluation.get("content_required_scores", {}).get("accuracy", {}).get("score", 0)
        elif metric == "engagement":
            return evaluation.get("content_free_scores", {}).get("narrative_quality", {}).get("score", 0)
        elif metric == "consistency":
            return evaluation.get("visual_scores", {}).get("professional_design", {}).get("score", 0)
        elif metric == "logical_flow":
            return evaluation.get("content_free_scores", {}).get("logical_structure", {}).get("score", 0)
        else:
            return 0