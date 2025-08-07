"""
Reflection Agent - Specialized in analyzing evaluation results and identifying patterns
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent
from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts

logger = logging.getLogger(__name__)

class ReflectionAgent(BaseEvolutionAgent):
    """Agent specialized in reflecting on evaluation results and identifying improvement patterns"""
    
    def __init__(self, api_key: str = None):
        super().__init__("ReflectionAgent", api_key)
    
    def get_system_prompt(self) -> str:
        """Specialized system prompt for reflection analysis"""
        return """You are a Presentation Quality Reflection Specialist with deep expertise in analyzing presentation evaluation data to identify systematic improvement opportunities.

## Your Core Expertise:
- **Pattern Recognition**: Identifying recurring weakness patterns across multiple presentations
- **Root Cause Analysis**: Understanding why certain dimensions consistently score poorly
- **Quality Assessment**: Evaluating presentation quality across visual, content, and structural dimensions
- **Systematic Thinking**: Connecting evaluation scores to underlying generation process issues

## Your Analytical Framework:
1. **Data Analysis**: Extract quantitative patterns from evaluation scores
2. **Weakness Identification**: Find recurring issues across multiple presentations
3. **Impact Assessment**: Prioritize issues by frequency and severity
4. **Root Cause Analysis**: Understand underlying causes of quality issues

## Your Output Standards:
- **Evidence-Based**: All findings supported by evaluation data
- **Quantitative**: Include specific metrics and percentages
- **Actionable**: Focus on issues that can be systematically addressed
- **Prioritized**: Rank issues by potential impact

You excel at transforming evaluation data into actionable insights for quality improvement."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reflection analysis requests"""
        
        action_type = input_data.get("action", "analyze_evaluations")
        
        if action_type == "analyze_evaluations":
            return self._analyze_evaluations(input_data)
        elif action_type == "compare_iterations":
            return self._compare_iterations(input_data)
        elif action_type == "identify_root_causes":
            return self._identify_root_causes(input_data)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _analyze_evaluations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze presentation evaluations to identify patterns"""
        
        evaluation_data = input_data.get("evaluation_data", [])
        topics = input_data.get("topics", [])
        
        if not evaluation_data:
            return {"error": "No evaluation data provided"}
        
        evaluation_json = json.dumps(evaluation_data, indent=2)
        topics_str = ', '.join(topics)
        
        # Use centralized prompt
        baseline_json = json.dumps({}, indent=2)  # Empty baseline for initial analysis
        prompt = EvolutionPrompts.get_prompt(
            'REFLECTION_ANALYSIS', 
            iteration_number=1,
            evaluation_json=evaluation_json,
            baseline_json=baseline_json
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "analyze_evaluations",
            f"Analyzed {len(evaluation_data)} evaluations, identified {len(result.get('weakness_patterns', []))} patterns",
            {"evaluation_count": len(evaluation_data), "topics": topics}
        )
        
        return result
    
    def _compare_iterations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance across evolution iterations"""
        
        iterations = input_data.get("iterations", [])
        
        if len(iterations) < 2:
            return {"error": "Need at least 2 iterations for comparison"}
        
        iterations_json = json.dumps(iterations, indent=2)
        
        # Compare iterations - using reflection analysis prompt
        prompt = EvolutionPrompts.get_prompt(
            'REFLECTION_ANALYSIS',
            iteration_number=len(iterations),
            evaluation_json=json.dumps({"iterations": iterations}, indent=2),
            baseline_json=json.dumps({}, indent=2)
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "compare_iterations",
            f"Compared {len(iterations)} iterations, trend: {result.get('comparison_summary', {}).get('improvement_trend', 'unknown')}",
            {"iteration_count": len(iterations)}
        )
        
        return result
    
    def _identify_root_causes(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep analysis of root causes for quality issues"""
        
        weakness_patterns = input_data.get("weakness_patterns", [])
        generation_context = input_data.get("generation_context", {})
        
        weakness_json = json.dumps(weakness_patterns, indent=2)
        context_json = json.dumps(generation_context, indent=2)
        
        # Root cause analysis - using reflection analysis prompt
        prompt = EvolutionPrompts.get_prompt(
            'REFLECTION_ANALYSIS',
            iteration_number=1,
            evaluation_json=json.dumps(weakness_patterns, indent=2),
            baseline_json=json.dumps({}, indent=2)
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "identify_root_causes",
            f"Analyzed root causes for {len(weakness_patterns)} patterns",
            {"pattern_count": len(weakness_patterns)}
        )
        
        return result