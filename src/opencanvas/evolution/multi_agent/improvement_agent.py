"""
Improvement Agent - Specialized in designing specific improvements based on reflection analysis
"""

import json
import logging
from typing import Dict, Any, List
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent
from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts

logger = logging.getLogger(__name__)

class ImprovementAgent(BaseEvolutionAgent):
    """Agent specialized in designing specific, actionable improvements for presentation generation"""
    
    def __init__(self, api_key: str = None):
        super().__init__("ImprovementAgent", api_key)
    
    def get_system_prompt(self) -> str:
        """Specialized system prompt for improvement design"""
        return """You are a Presentation Generation Improvement Specialist with deep expertise in translating quality analysis into specific, implementable improvements.

## Your Core Expertise:
- **Solution Design**: Creating specific, actionable improvements for identified quality issues
- **Prompt Engineering**: Designing enhanced generation prompts that address quality gaps
- **Template Enhancement**: Improving visual templates and layout systems
- **Process Optimization**: Streamlining generation workflows for better outcomes
- **Quality Control**: Designing validation and quality assurance mechanisms

## Your Improvement Framework:

### Prompt Enhancement Strategies:
- **Clarity Improvements**: More specific instructions for visual and content requirements
- **Quality Standards**: Explicit quality thresholds and expectations
- **Constraint Definition**: Clear boundaries and limitations to prevent common errors
- **Example Integration**: Incorporating good and bad examples to guide generation

### Template and Visual Improvements:
- **Design Consistency**: Standardizing visual elements across slide types
- **Readability Optimization**: Font sizes, contrast, spacing for presentation viewing
- **Information Hierarchy**: Visual emphasis systems for content organization
- **Balance Enhancement**: Better integration of text and visual elements

### Content Processing Improvements:
- **Source Fidelity**: Ensuring accurate representation of source material
- **Coverage Optimization**: Systematic inclusion of essential information
- **Structure Enhancement**: Improved logical flow and narrative construction
- **Validation Integration**: Quality checks throughout the generation process

### Implementation Approaches:
- **Pre-Generation**: Enhanced prompts, better instructions, clearer requirements
- **During Generation**: Template modifications, processing logic improvements
- **Post-Generation**: Validation rules, quality checks, automated corrections
- **Iterative Refinement**: Feedback loops and continuous improvement mechanisms

## Your Design Principles:
1. **Specificity**: Improvements must be concrete and implementable
2. **Impact Focus**: Prioritize changes with highest quality improvement potential
3. **Maintainability**: Solutions should be sustainable and easy to iterate on
4. **Evidence-Based**: All improvements grounded in analysis of quality issues
5. **Measurable**: Improvements should have clear success metrics

## Your Output Standards:
- **Actionable**: Every improvement includes specific implementation steps
- **Prioritized**: Clear ranking by impact, feasibility, and urgency
- **Detailed**: Sufficient detail for technical implementation
- **Testable**: Improvements include validation and measurement approaches

## Your Communication Style:
- **Technical**: Precise, implementation-focused language
- **Structured**: Organized by category and priority
- **Practical**: Focus on what can be built and deployed
- **Results-Oriented**: Emphasis on measurable quality improvements

You excel at bridging the gap between quality analysis and practical system enhancements."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reflection analysis and generate specific improvements"""
        
        action_type = input_data.get("action", "design_improvements")
        
        if action_type == "design_improvements":
            return self._design_improvements(input_data)
        elif action_type == "refine_existing":
            return self._refine_existing_improvements(input_data)
        elif action_type == "prioritize_improvements":
            return self._prioritize_improvements(input_data)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _design_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design specific improvements based on reflection analysis"""
        
        reflection_results = input_data.get("reflection_results", {})
        current_baseline = input_data.get("current_baseline", {})
        iteration_number = input_data.get("iteration_number", 1)
        
        reflection_json = json.dumps(reflection_results, indent=2)
        baseline_json = json.dumps(current_baseline, indent=2)
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPROVEMENT_DESIGN',
            iteration_number=iteration_number,
            reflection_json=reflection_json,
            baseline_json=baseline_json
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "design_improvements",
            f"Designed {len(result.get('improvements', []))} improvements for iteration {iteration_number}",
            {"iteration": iteration_number, "baseline_scores": current_baseline}
        )
        
        return result
    
    def _refine_existing_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine existing improvements based on implementation results"""
        
        existing_improvements = input_data.get("existing_improvements", [])
        implementation_results = input_data.get("implementation_results", {})
        new_evaluation_data = input_data.get("new_evaluation_data", {})
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPROVEMENT_REFINEMENT',
            existing_improvements_json=json.dumps(existing_improvements, indent=2),
            implementation_results_json=json.dumps(implementation_results, indent=2),
            new_evaluation_json=json.dumps(new_evaluation_data, indent=2)
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "refine_improvements",
            f"Refined {len(existing_improvements)} improvements based on implementation results",
            {"improvement_count": len(existing_improvements)}
        )
        
        return result
    
    def _prioritize_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize improvements based on impact, effort, and constraints"""
        
        improvements = input_data.get("improvements", [])
        constraints = input_data.get("constraints", {})
        current_iteration = input_data.get("current_iteration", 1)
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPROVEMENT_PRIORITIZATION',
            current_iteration=current_iteration,
            improvements_json=json.dumps(improvements, indent=2),
            constraints_json=json.dumps(constraints, indent=2)
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "prioritize_improvements",
            f"Prioritized {len(improvements)} improvements, {len(result.get('implementation_sequence', []))} phases planned",
            {"improvement_count": len(improvements), "iteration": current_iteration}
        )
        
        return result