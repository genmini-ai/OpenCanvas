"""
Improvement Agent - Specialized in designing specific improvements based on reflection analysis
"""

import json
import logging
from typing import Dict, Any, List
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent

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
        
        prompt = f"""Design specific, implementable improvements based on the following reflection analysis for evolution iteration {iteration_number}.

REFLECTION ANALYSIS:
{reflection_json}

CURRENT BASELINE SCORES:
{baseline_json}

## Improvement Design Requirements:

### 1. PROMPT ENHANCEMENT DESIGN
For each identified weakness, design specific prompt improvements:
- **Enhanced Instructions**: More detailed and specific generation requirements
- **Quality Standards**: Explicit quality thresholds and expectations
- **Constraint Definition**: Clear rules to prevent identified issues
- **Validation Criteria**: Built-in quality checks within prompts

### 2. TEMPLATE AND VISUAL IMPROVEMENTS
Design improvements for visual quality issues:
- **Chart Readability**: Specific requirements for readable charts and graphs
- **Visual Hierarchy**: Enhanced title sizing, bullet formatting, emphasis
- **Design Consistency**: Standardized color schemes, typography, spacing
- **Element Integration**: Better visual-text balance and purposeful visuals

### 3. CONTENT PROCESSING ENHANCEMENTS
Improve content accuracy and coverage:
- **Source Fidelity**: Stricter adherence to source material
- **Coverage Validation**: Systematic inclusion of essential information
- **Fact Checking**: Built-in plausibility and consistency checks
- **Attribution Standards**: Proper citation and reference handling

### 4. QUALITY CONTROL MECHANISMS
Design validation and quality assurance improvements:
- **Pre-Generation Checks**: Input validation and requirement verification
- **During-Generation Monitoring**: Quality gates during creation process
- **Post-Generation Validation**: Automated quality assessment and correction
- **Feedback Integration**: Learning from evaluation results

## Output Format:

```json
{
  "improvement_iteration": {
    "iteration_number": ITERATION_NUMBER,
    "target_baseline": {{
      "visual_target": X.X,
      "content_target": X.X,
      "accuracy_target": X.X,
      "overall_target": X.X
    }},
    "expected_impact": "Description of overall expected improvement"
  },
  "improvements": [
    {
      "improvement_id": "unique_id",
      "name": "Clear improvement name",
      "category": "prompt|template|processing|validation",
      "priority": "high|medium|low",
      "target_weaknesses": ["weakness1", "weakness2"],
      "target_dimensions": ["dimension1", "dimension2"],
      "description": "Clear description of what this improvement does",
      "implementation": {{
        "type": "prompt_enhancement|template_modification|process_change|validation_rule",
        "details": "Specific implementation instructions",
        "code_changes": "Required code modifications if applicable",
        "configuration": "Configuration changes needed"
      }},
      "expected_impact": {{
        "dimensions_affected": ["dim1", "dim2"],
        "score_improvement": "Expected score increase",
        "success_metrics": ["How to measure success"]
      }},
      "implementation_effort": "low|medium|high",
      "dependencies": ["Other improvements this depends on"],
      "validation_approach": "How to test this improvement"
    }
  ],
  "implementation_plan": {{
    "phase_1_quick_wins": ["improvement_id1", "improvement_id2"],
    "phase_2_medium_effort": ["improvement_id3"],
    "phase_3_complex_changes": ["improvement_id4"],
    "rollback_strategy": "How to undo changes if needed"
  }},
  "success_criteria": {{
    "minimum_acceptable_improvement": X.X,
    "target_improvement": X.X,
    "key_metrics": ["Metric1", "Metric2"],
    "validation_requirements": ["Requirement1", "Requirement2"]
  }}
}
```

Focus on creating specific, actionable improvements that can be immediately implemented and tested."""
        
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
        
        prompt = f"""Refine and optimize existing improvements based on their implementation results and new evaluation data.

EXISTING IMPROVEMENTS:
{json.dumps(existing_improvements, indent=2)}

IMPLEMENTATION RESULTS:
{json.dumps(implementation_results, indent=2)}

NEW EVALUATION DATA:
{json.dumps(new_evaluation_data, indent=2)}

## Refinement Analysis Required:

### 1. EFFECTIVENESS ASSESSMENT
For each existing improvement:
- Did it achieve the expected impact?
- Which aspects worked well vs poorly?
- What unintended consequences occurred?
- How can it be optimized further?

### 2. IMPROVEMENT OPTIMIZATION
Design refinements for:
- **Underperforming Improvements**: Enhance or replace ineffective changes
- **Partially Successful**: Amplify successful aspects, fix issues
- **Successful Improvements**: Minor optimizations and extensions
- **Conflicting Improvements**: Resolve conflicts between improvements

### 3. NEW IMPROVEMENT OPPORTUNITIES
Based on implementation learnings:
- What new weaknesses were revealed?
- What improvement approaches work best?
- What implementation patterns are most effective?

## Output Format:

```json
{
  "refinement_analysis": [
    {
      "improvement_id": "existing_id",
      "effectiveness_rating": "high|medium|low",
      "achieved_impact": "Actual impact achieved",
      "issues_identified": ["Issue1", "Issue2"],
      "refinement_recommendations": [
        {
          "type": "optimize|replace|remove|enhance",
          "description": "What to change",
          "implementation": "How to implement the change",
          "expected_improvement": "Expected benefit"
        }
      ]
    }
  ],
  "optimized_improvements": [
    "Same format as original improvements but refined"
  ],
  "new_insights": [
    "New understanding about what works/doesn't work"
  ]
}
```

Focus on learning from implementation results to make improvements more effective."""
        
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
        
        prompt = f"""Prioritize the following improvements for implementation in iteration {current_iteration}, considering impact, effort, and constraints.

IMPROVEMENTS TO PRIORITIZE:
{json.dumps(improvements, indent=2)}

CONSTRAINTS:
{json.dumps(constraints, indent=2)}

## Prioritization Criteria:

### 1. IMPACT ASSESSMENT
Rate each improvement on:
- **Quality Impact**: Potential score improvement (1-5 scale)
- **Coverage**: How many presentations benefit (1-5 scale) 
- **Strategic Value**: Long-term system improvement (1-5 scale)

### 2. FEASIBILITY ASSESSMENT
Rate each improvement on:
- **Implementation Effort**: Development complexity (1-5 scale, 1=easy)
- **Risk Level**: Potential for unintended consequences (1-5 scale, 1=safe)
- **Resource Requirements**: Time and skill needed (1-5 scale, 1=minimal)

### 3. DEPENDENCY ANALYSIS
Identify:
- **Prerequisites**: Improvements that must be done first
- **Synergies**: Improvements that work better together
- **Conflicts**: Improvements that interfere with each other

### 4. OPTIMAL SEQUENCING
Design implementation sequence considering:
- **Quick Wins**: High impact, low effort improvements first
- **Foundation Building**: Prerequisites for other improvements
- **Risk Management**: Safer changes before riskier ones
- **Learning Optimization**: Improvements that provide learning for future iterations

## Output Format:

```json
{
  "prioritization_analysis": [
    {
      "improvement_id": "id",
      "priority_score": X.X,
      "impact_ratings": {
        "quality_impact": X,
        "coverage": X,
        "strategic_value": X
      },
      "feasibility_ratings": {
        "implementation_effort": X,
        "risk_level": X,  
        "resource_requirements": X
      },
      "recommendation": "implement_immediately|implement_next|implement_later|skip"
    }
  ],
  "implementation_sequence": [
    {
      "phase": "immediate|short_term|medium_term|long_term",
      "improvements": ["id1", "id2"],
      "rationale": "Why these improvements in this phase",
      "estimated_effort": "low|medium|high",
      "success_probability": "high|medium|low"
    }
  ],
  "trade_offs": [
    {
      "decision": "Description of trade-off decision",
      "alternatives": ["Option1", "Option2"],
      "chosen_approach": "Selected option",
      "rationale": "Why this choice was made"
    }
  ]
}
```

Focus on creating an optimal implementation plan that maximizes improvement while managing risks and constraints."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "prioritize_improvements",
            f"Prioritized {len(improvements)} improvements, {len(result.get('implementation_sequence', []))} phases planned",
            {"improvement_count": len(improvements), "iteration": current_iteration}
        )
        
        return result