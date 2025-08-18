"""
Insights Extractor

Automatically extracts actionable insights from prompt evolution data,
identifying successful patterns, common failure modes, and optimization strategies.
"""

import re
import statistics
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class EvolutionInsight:
    """Represents a single insight from evolution analysis"""
    category: str
    insight_type: str  # 'success_pattern', 'failure_pattern', 'recommendation', 'observation'
    title: str
    description: str
    confidence: float  # 0-1 confidence score
    supporting_data: Dict[str, Any]
    actionable_recommendation: Optional[str] = None

class InsightsExtractor:
    """Extracts meaningful insights from prompt evolution analysis"""
    
    def __init__(self, analysis_summary: Dict[str, Any]):
        self.data = analysis_summary
        self.insights: List[EvolutionInsight] = []
        
    def extract_all_insights(self) -> List[EvolutionInsight]:
        """Extract all available insights from the analysis data"""
        self.insights = []
        
        # Extract different types of insights
        self._extract_performance_insights()
        self._extract_pattern_insights()
        self._extract_growth_insights()
        self._extract_optimization_insights()
        self._extract_strategic_insights()
        
        # Sort insights by confidence and importance
        self.insights.sort(key=lambda x: (x.confidence, self._get_importance_score(x)), reverse=True)
        
        logger.info(f"Extracted {len(self.insights)} insights from evolution data")
        return self.insights
    
    def _extract_performance_insights(self):
        """Extract insights about overall evolution performance"""
        overview = self.data.get('evolution_overview', {})
        score_progression = self.data.get('score_progression', {})
        
        success_rate = overview.get('success_rate', 0)
        total_iterations = overview.get('total_iterations', 0)
        
        # Success rate insights
        if success_rate >= 0.8:
            self.insights.append(EvolutionInsight(
                category='performance',
                insight_type='success_pattern',
                title='Highly Successful Evolution',
                description=f'Evolution achieved {success_rate:.1%} success rate across {total_iterations} iterations, indicating robust optimization strategy.',
                confidence=0.9,
                supporting_data={'success_rate': success_rate, 'iterations': total_iterations},
                actionable_recommendation='Current evolution approach is highly effective. Consider applying similar strategies to other prompt types.'
            ))
        elif success_rate >= 0.5:
            self.insights.append(EvolutionInsight(
                category='performance',
                insight_type='observation',
                title='Moderate Evolution Success',
                description=f'Evolution achieved {success_rate:.1%} success rate. There is room for improvement in optimization strategy.',
                confidence=0.7,
                supporting_data={'success_rate': success_rate, 'iterations': total_iterations},
                actionable_recommendation='Consider refining evaluation criteria or prompt modification strategies to improve success rate.'
            ))
        else:
            self.insights.append(EvolutionInsight(
                category='performance',
                insight_type='failure_pattern',
                title='Low Evolution Success Rate',
                description=f'Evolution only achieved {success_rate:.1%} success rate, indicating potential issues with optimization approach.',
                confidence=0.8,
                supporting_data={'success_rate': success_rate, 'iterations': total_iterations},
                actionable_recommendation='Review evolution strategy. Consider smaller, more targeted changes or different evaluation metrics.'
            ))
        
        # Score progression trends
        if score_progression:
            score_trends = self._analyze_score_trends(score_progression)
            for metric, trend in score_trends.items():
                if abs(trend['slope']) > 0.1:  # Significant trend
                    trend_type = 'improvement' if trend['slope'] > 0 else 'decline'
                    self.insights.append(EvolutionInsight(
                        category='performance',
                        insight_type='success_pattern' if trend['slope'] > 0 else 'failure_pattern',
                        title=f'{metric.replace("_", " ").title()} Shows Strong {trend_type.title()}',
                        description=f'{metric.replace("_", " ").title()} evolved with a {trend["slope"]:.3f} trend over iterations.',
                        confidence=min(0.9, abs(trend['r_squared'])),
                        supporting_data=trend,
                        actionable_recommendation=f'{"Continue" if trend["slope"] > 0 else "Revise"} strategies that affect {metric.replace("_", " ")} to {"maintain" if trend["slope"] > 0 else "reverse"} this trend.'
                    ))
    
    def _extract_pattern_insights(self):
        """Extract insights about successful and failed change patterns"""
        change_patterns = self.data.get('change_patterns', {})
        
        # Section change insights
        section_changes = change_patterns.get('section_changes', {})
        if section_changes:
            most_changed = max(section_changes.items(), key=lambda x: x[1])
            least_changed = min(section_changes.items(), key=lambda x: x[1])
            
            # Most frequently changed section
            self.insights.append(EvolutionInsight(
                category='patterns',
                insight_type='observation',
                title=f'{most_changed[0].replace("_", " ").title()} Section Most Frequently Modified',
                description=f'The {most_changed[0]} section was modified {most_changed[1]} times, indicating it may be a key area for optimization.',
                confidence=0.8,
                supporting_data={'section': most_changed[0], 'changes': most_changed[1]},
                actionable_recommendation=f'Focus quality control on {most_changed[0]} modifications as this section appears critical for performance.'
            ))
            
            # Stable sections
            if least_changed[1] == 0:
                self.insights.append(EvolutionInsight(
                    category='patterns',
                    insight_type='observation',
                    title=f'{least_changed[0].replace("_", " ").title()} Section Remained Stable',
                    description=f'The {least_changed[0]} section was never modified, suggesting it may already be well-optimized.',
                    confidence=0.6,
                    supporting_data={'section': least_changed[0], 'changes': least_changed[1]},
                    actionable_recommendation=f'Consider {least_changed[0]} section as a stable foundation. May serve as template for other sections.'
                ))
        
        # Successful vs failed patterns
        successful_patterns = change_patterns.get('successful_change_types', {})
        failed_patterns = change_patterns.get('failed_change_types', {})
        
        if successful_patterns:
            # Most successful pattern
            best_pattern = max(successful_patterns.items(), 
                             key=lambda x: (len(x[1]), statistics.mean(x[1]) if x[1] else 0))
            
            self.insights.append(EvolutionInsight(
                category='patterns',
                insight_type='success_pattern',
                title=f'Most Successful Pattern: {best_pattern[0].replace(":", " → ").title()}',
                description=f'This change pattern appeared {len(best_pattern[1])} times with average improvement of {statistics.mean(best_pattern[1]):.3f}.',
                confidence=min(0.9, len(best_pattern[1]) / 10),  # Higher confidence with more examples
                supporting_data={'pattern': best_pattern[0], 'occurrences': len(best_pattern[1]), 'avg_improvement': statistics.mean(best_pattern[1])},
                actionable_recommendation=f'Prioritize {best_pattern[0].split(":")[0]} modifications of type {best_pattern[0].split(":")[1]} in future evolutions.'
            ))
        
        if failed_patterns:
            # Most problematic pattern
            worst_pattern = min(failed_patterns.items(),
                              key=lambda x: statistics.mean(x[1]) if x[1] else 0)
            
            self.insights.append(EvolutionInsight(
                category='patterns',
                insight_type='failure_pattern',
                title=f'Most Problematic Pattern: {worst_pattern[0].replace(":", " → ").title()}',
                description=f'This change pattern appeared {len(worst_pattern[1])} times with average decline of {statistics.mean(worst_pattern[1]):.3f}.',
                confidence=min(0.9, len(worst_pattern[1]) / 5),
                supporting_data={'pattern': worst_pattern[0], 'occurrences': len(worst_pattern[1]), 'avg_decline': statistics.mean(worst_pattern[1])},
                actionable_recommendation=f'Avoid {worst_pattern[0].split(":")[0]} modifications of type {worst_pattern[0].split(":")[1]} or refine approach before applying.'
            ))
    
    def _extract_growth_insights(self):
        """Extract insights about prompt growth and complexity changes"""
        growth = self.data.get('prompt_growth', {})
        
        if not growth:
            return
            
        word_change = growth.get('word_count_change', 0)
        instruction_change = growth.get('instruction_count_change', 0)
        section_change = growth.get('section_count_change', 0)
        relative_growth = growth.get('relative_growth', 0)
        
        # Word count insights
        if abs(word_change) > 50:  # Significant word change
            change_type = 'expansion' if word_change > 0 else 'compression'
            self.insights.append(EvolutionInsight(
                category='growth',
                insight_type='observation',
                title=f'Significant Prompt {change_type.title()}',
                description=f'Prompt {"expanded" if word_change > 0 else "compressed"} by {abs(word_change)} words ({relative_growth:+.1f}%) during evolution.',
                confidence=0.8,
                supporting_data=growth,
                actionable_recommendation=f'Monitor if {"expansion" if word_change > 0 else "compression"} correlates with performance improvements. Consider optimal prompt length.'
            ))
        
        # Instruction density insights
        if instruction_change > 0 and word_change > 0:
            instruction_density_change = instruction_change / word_change
            if instruction_density_change > 0.1:  # Instructions added faster than words
                self.insights.append(EvolutionInsight(
                    category='growth',
                    insight_type='success_pattern',
                    title='Increased Instruction Density',
                    description=f'Added {instruction_change} instructions while only adding {word_change} words, increasing specificity.',
                    confidence=0.7,
                    supporting_data={'instruction_density_change': instruction_density_change, **growth},
                    actionable_recommendation='Focus on adding specific, actionable instructions rather than general guidance.'
                ))
        
        # Structure insights
        if section_change > 0:
            self.insights.append(EvolutionInsight(
                category='growth',
                insight_type='observation',
                title='Enhanced Prompt Structure',
                description=f'Added {section_change} new sections, improving organization and clarity.',
                confidence=0.6,
                supporting_data=growth,
                actionable_recommendation='Continue organizing prompt content into clear, distinct sections for better AI comprehension.'
            ))
    
    def _extract_optimization_insights(self):
        """Extract insights about optimization strategies and effectiveness"""
        overview = self.data.get('evolution_overview', {})
        change_patterns = self.data.get('change_patterns', {})
        
        total_changes = overview.get('total_changes', 0)
        successful_iterations = overview.get('successful_iterations', 0)
        
        # Change efficiency
        if total_changes > 0 and successful_iterations > 0:
            change_efficiency = successful_iterations / total_changes
            
            if change_efficiency > 0.7:
                self.insights.append(EvolutionInsight(
                    category='optimization',
                    insight_type='success_pattern',
                    title='Highly Efficient Change Strategy',
                    description=f'Achieved {change_efficiency:.1%} success rate per change, indicating precise optimization approach.',
                    confidence=0.8,
                    supporting_data={'change_efficiency': change_efficiency, 'total_changes': total_changes},
                    actionable_recommendation='Current change strategy is highly efficient. Document and replicate this approach.'
                ))
            elif change_efficiency < 0.3:
                self.insights.append(EvolutionInsight(
                    category='optimization',
                    insight_type='failure_pattern',
                    title='Low Change Efficiency',
                    description=f'Only {change_efficiency:.1%} of changes led to improvements, suggesting need for more targeted modifications.',
                    confidence=0.7,
                    supporting_data={'change_efficiency': change_efficiency, 'total_changes': total_changes},
                    actionable_recommendation='Reduce change frequency and focus on higher-confidence modifications based on evaluation feedback.'
                ))
        
        # Change type distribution insights
        change_types = change_patterns.get('change_types', {})
        if change_types:
            dominant_type = max(change_types.items(), key=lambda x: x[1])
            
            self.insights.append(EvolutionInsight(
                category='optimization',
                insight_type='observation',
                title=f'Primary Optimization Strategy: {dominant_type[0].title()}',
                description=f'{dominant_type[0].title()} changes comprised {dominant_type[1]}/{sum(change_types.values())} of all modifications.',
                confidence=0.6,
                supporting_data=change_types,
                actionable_recommendation=f'{"Continue focusing on" if dominant_type[0] == "addition" else "Balance"} {dominant_type[0]} strategies with other change types for comprehensive optimization.'
            ))
    
    def _extract_strategic_insights(self):
        """Extract high-level strategic insights for future evolution"""
        insights_data = self.data.get('key_insights', [])
        overview = self.data.get('evolution_overview', {})
        
        # Meta-insights about the evolution process
        if overview.get('total_iterations', 0) > 3:
            self.insights.append(EvolutionInsight(
                category='strategy',
                insight_type='recommendation',
                title='Multi-Iteration Evolution Strategy',
                description=f'Completed {overview.get("total_iterations")} iterations, demonstrating iterative refinement approach.',
                confidence=0.7,
                supporting_data=overview,
                actionable_recommendation='Continue multi-iteration approach but consider checkpoint evaluation every 2-3 iterations to prevent drift.'
            ))
        
        # Evolution maturity assessment
        success_rate = overview.get('success_rate', 0)
        total_changes = overview.get('total_changes', 0)
        
        if success_rate > 0.5 and total_changes < 10:
            self.insights.append(EvolutionInsight(
                category='strategy',
                insight_type='recommendation',
                title='Ready for Advanced Evolution',
                description='Good success rate with relatively few changes suggests readiness for more sophisticated evolution strategies.',
                confidence=0.6,
                supporting_data={'success_rate': success_rate, 'total_changes': total_changes},
                actionable_recommendation='Consider implementing multi-objective optimization or exploring different prompt architectures.'
            ))
        elif success_rate < 0.3 and total_changes > 20:
            self.insights.append(EvolutionInsight(
                category='strategy',
                insight_type='recommendation',
                title='Simplify Evolution Approach',
                description='High change volume with low success rate suggests overly complex modifications.',
                confidence=0.7,
                supporting_data={'success_rate': success_rate, 'total_changes': total_changes},
                actionable_recommendation='Reduce to single-aspect changes per iteration. Focus on understanding what works before combining strategies.'
            ))
    
    def _analyze_score_trends(self, score_progression: Dict[int, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Analyze trends in score progression"""
        trends = {}
        iterations = sorted(score_progression.keys())
        
        if len(iterations) < 3:  # Need at least 3 points for trend analysis
            return trends
            
        # Get all metrics
        all_metrics = set()
        for scores in score_progression.values():
            all_metrics.update(scores.keys())
        
        for metric in all_metrics:
            values = []
            x_values = []
            
            for iteration in iterations:
                if metric in score_progression[iteration]:
                    values.append(score_progression[iteration][metric])
                    x_values.append(iteration)
            
            if len(values) >= 3:  # Need at least 3 points
                # Calculate linear trend
                slope, r_squared = self._calculate_linear_trend(x_values, values)
                trends[metric] = {
                    'slope': slope,
                    'r_squared': r_squared,
                    'values': values,
                    'start_value': values[0],
                    'end_value': values[-1],
                    'total_change': values[-1] - values[0]
                }
        
        return trends
    
    def _calculate_linear_trend(self, x_values: List[float], y_values: List[float]) -> Tuple[float, float]:
        """Calculate linear trend slope and R-squared"""
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x * x for x in x_values)
        sum_y_squared = sum(y * y for y in y_values)
        
        # Calculate slope
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return 0.0, 0.0
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Calculate R-squared
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in y_values)
        
        if ss_tot == 0:
            r_squared = 1.0 if slope == 0 else 0.0
        else:
            predicted_y = [slope * (x - sum_x / n) + mean_y for x in x_values]
            ss_res = sum((actual - predicted) ** 2 for actual, predicted in zip(y_values, predicted_y))
            r_squared = max(0, 1 - (ss_res / ss_tot))
        
        return slope, r_squared
    
    def _get_importance_score(self, insight: EvolutionInsight) -> float:
        """Calculate importance score for insight prioritization"""
        importance = 0.5  # Base importance
        
        # Boost importance based on type
        if insight.insight_type == 'success_pattern':
            importance += 0.3
        elif insight.insight_type == 'failure_pattern':
            importance += 0.2
        elif insight.insight_type == 'recommendation':
            importance += 0.4
        
        # Boost importance based on category
        if insight.category == 'performance':
            importance += 0.2
        elif insight.category == 'strategy':
            importance += 0.1
        
        # Boost if actionable recommendation exists
        if insight.actionable_recommendation:
            importance += 0.1
        
        return min(1.0, importance)
    
    def get_insights_by_category(self) -> Dict[str, List[EvolutionInsight]]:
        """Group insights by category"""
        categorized = defaultdict(list)
        
        for insight in self.insights:
            categorized[insight.category].append(insight)
        
        return dict(categorized)
    
    def get_actionable_recommendations(self) -> List[str]:
        """Get list of actionable recommendations"""
        recommendations = []
        
        for insight in self.insights:
            if insight.actionable_recommendation and insight.confidence >= 0.6:
                recommendations.append(insight.actionable_recommendation)
        
        return recommendations
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """Get summary of insight confidence levels"""
        if not self.insights:
            return {'total': 0, 'high_confidence': 0, 'medium_confidence': 0, 'low_confidence': 0}
        
        high_confidence = len([i for i in self.insights if i.confidence >= 0.8])
        medium_confidence = len([i for i in self.insights if 0.5 <= i.confidence < 0.8])
        low_confidence = len([i for i in self.insights if i.confidence < 0.5])
        
        return {
            'total': len(self.insights),
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence,
            'avg_confidence': statistics.mean([i.confidence for i in self.insights])
        }