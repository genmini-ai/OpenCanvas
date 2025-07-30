"""
Reflection Agent - Specialized in analyzing evaluation results and identifying patterns
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent

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

### Visual Quality Analysis:
- **Professional Design**: Consistency, color schemes, typography, visual identity
- **Information Hierarchy**: Title sizing, bullet formatting, visual emphasis
- **Clarity & Readability**: Font sizes, contrast, chart readability, element visibility
- **Visual-Text Balance**: Integration of visuals with content, purposeful visual elements

### Content Quality Analysis:
- **Logical Structure**: Flow between slides, coherent progression, factual consistency
- **Narrative Quality**: Storytelling effectiveness, significance communication, engagement
- **Accuracy**: Fidelity to source material, factual correctness, proper attribution
- **Coverage**: Completeness of essential information, methodological context

### Pattern Identification:
- **Severity Assessment**: High/Medium/Low impact classification
- **Frequency Analysis**: How often patterns appear across presentations
- **Correlation Detection**: Relationships between different quality dimensions
- **Root Cause Inference**: Why certain issues consistently occur

## Your Analytical Approach:
1. **Quantitative Analysis**: Statistical patterns in scores across dimensions
2. **Qualitative Assessment**: Reasoning patterns and specific feedback analysis
3. **Comparative Evaluation**: Performance differences between topics/presentations
4. **Systematic Diagnosis**: Identifying underlying generation process issues

## Your Output Standards:
- **Evidence-Based**: All conclusions supported by evaluation data
- **Actionable**: Insights that can drive specific improvements
- **Prioritized**: Clear ranking of issues by impact and frequency
- **Specific**: Concrete examples and targeted recommendations

## Your Communication Style:
- **Analytical**: Data-driven conclusions with supporting evidence
- **Clear**: Accessible explanations of complex patterns
- **Structured**: Organized findings with logical progression
- **Constructive**: Focus on improvement opportunities rather than just problems

You excel at transforming raw evaluation data into actionable insights that drive systematic quality improvements."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process evaluation results and generate reflection analysis"""
        
        action_type = input_data.get("action", "analyze_evaluations")
        
        if action_type == "analyze_evaluations":
            return self._analyze_evaluation_batch(input_data)
        elif action_type == "compare_iterations":
            return self._compare_iterations(input_data)
        elif action_type == "identify_root_causes":
            return self._identify_root_causes(input_data)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _analyze_evaluation_batch(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a batch of evaluation results"""
        
        evaluation_data = input_data.get("evaluations", [])
        topics = input_data.get("topics", [])
        
        if not evaluation_data:
            return {"error": "No evaluation data provided"}
        
        prompt = f"""Analyze the following {len(evaluation_data)} presentation evaluation results to identify systematic quality patterns and improvement opportunities.

EVALUATION DATA:
{json.dumps(evaluation_data, indent=2)}

TOPICS ANALYZED:
{', '.join(topics)}

## Analysis Required:

### 1. WEAKNESS PATTERN IDENTIFICATION
Identify recurring weaknesses across presentations:
- Which dimensions consistently score below 3.5?
- What specific issues appear in multiple presentations?
- How frequently does each weakness pattern occur?
- What is the severity impact of each pattern?

### 2. PERFORMANCE BASELINE CALCULATION
Calculate current performance baseline:
- Average scores for each evaluation dimension
- Overall presentation quality baseline
- Performance variation across topics
- Identification of best and worst performing areas

### 3. ROOT CAUSE HYPOTHESIS
For each major weakness pattern, hypothesize why it occurs:
- Is it a prompt/instruction issue?
- Is it a template/design limitation?
- Is it a content processing problem?
- Is it a validation/quality control gap?

### 4. STRENGTH IDENTIFICATION
Identify consistent strengths to preserve:
- Which dimensions consistently score well (4.0+)?
- What aspects of the generation process are working effectively?
- Which presentation elements should be maintained?

### 5. IMPROVEMENT OPPORTUNITY RANKING
Rank improvement opportunities by:
- **Impact**: How much score improvement is possible?
- **Frequency**: How many presentations would benefit?
- **Feasibility**: How implementable is the fix?

## Output Format:

```json
{
  "analysis_summary": {
    "total_presentations": X,
    "topics_analyzed": ["topic1", "topic2"],
    "baseline_performance": {
      "visual_average": X.X,
      "content_average": X.X,
      "accuracy_average": X.X,
      "overall_average": X.X
    }
  },
  "weakness_patterns": [
    {
      "category": "visual|content_free|content_required",
      "dimension": "specific_dimension_name",
      "frequency": X,
      "avg_score": X.X,
      "severity": "high|medium|low",
      "description": "Clear description of the pattern",
      "examples": ["Example 1", "Example 2"],
      "root_cause_hypothesis": "Why this pattern occurs"
    }
  ],
  "strengths": [
    "Dimension or aspect that consistently performs well"
  ],
  "improvement_opportunities": [
    {
      "priority": "high|medium|low",
      "description": "Specific improvement opportunity",
      "expected_impact": "Expected score improvement",
      "affected_dimensions": ["dim1", "dim2"],
      "implementation_approach": "How to implement this improvement"
    }
  ],
  "key_insights": [
    "Major insight about presentation quality patterns"
  ]
}
```

Provide thorough analysis with specific examples and actionable recommendations."""
        
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
        
        prompt = f"""Compare presentation quality across {len(iterations)} evolution iterations to assess improvement patterns and identify trends.

ITERATION DATA:
{json.dumps(iterations, indent=2)}

## Comparison Analysis Required:

### 1. PERFORMANCE PROGRESSION
Track how each dimension has improved or declined:
- Score changes for visual dimensions
- Score changes for content dimensions  
- Overall presentation quality trend
- Identify best and worst performing iterations

### 2. IMPROVEMENT EFFECTIVENESS
Assess which improvements were most effective:
- Which applied improvements led to score increases?
- Which improvements had no impact or negative impact?
- What patterns emerge in successful vs unsuccessful improvements?

### 3. PLATEAU DETECTION
Identify if improvement has plateaued:
- Are recent iterations showing diminishing returns?
- Which dimensions have stopped improving?
- Is the system reaching optimal performance limits?

### 4. TREND ANALYSIS
Identify broader trends:
- Which quality aspects improve fastest?
- Are there trade-offs between different dimensions?
- What is the typical improvement trajectory?

## Output Format:

```json
{
  "comparison_summary": {
    "iterations_compared": X,
    "improvement_trend": "improving|plateauing|declining",
    "best_iteration": X,
    "total_improvement": X.X,
    "avg_improvement_per_iteration": X.X
  },
  "dimension_trends": {
    "visual": {
      "trend": "improving|stable|declining",
      "total_change": X.X,
      "best_iteration": X,
      "plateau_detected": true/false
    }
  },
  "effective_improvements": [
    {
      "improvement": "Description of improvement",
      "iteration_applied": X,
      "score_impact": X.X,
      "dimensions_affected": ["dim1", "dim2"]
    }
  ],
  "recommendations": [
    "Recommendation based on iteration comparison"
  ]
}
```

Focus on identifying which improvements are most effective and whether continued evolution is worthwhile."""
        
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
        
        prompt = f"""Perform deep root cause analysis for the identified presentation quality weakness patterns.

WEAKNESS PATTERNS:
{json.dumps(weakness_patterns, indent=2)}

GENERATION CONTEXT:
{json.dumps(generation_context, indent=2)}

## Root Cause Analysis Required:

### 1. GENERATION PROCESS DIAGNOSIS
For each weakness pattern, analyze potential causes in:
- **Prompt Design**: Are instructions clear and specific enough?
- **Template System**: Are visual templates adequate for requirements?
- **Content Processing**: Is information extraction and organization effective?
- **Quality Control**: Are validation steps catching issues?

### 2. SYSTEMATIC VS RANDOM ISSUES
Classify each issue:
- **Systematic**: Affects all/most presentations consistently
- **Topic-Specific**: Only affects certain types of content
- **Random**: Inconsistent occurrence patterns

### 3. INTERVENTION POINT IDENTIFICATION
For each root cause, identify where in the process to intervene:
- **Pre-Generation**: Prompt enhancement, better instructions
- **During Generation**: Template improvements, processing changes
- **Post-Generation**: Validation, quality checks, corrections
- **Evaluation**: Better feedback loops, refined criteria

### 4. SOLUTION DIFFICULTY ASSESSMENT
Rate each potential intervention:
- **Easy**: Simple prompt changes or parameter adjustments
- **Medium**: Template modifications or processing logic changes
- **Hard**: Fundamental architecture changes or new capabilities

## Output Format:

```json
{
  "root_cause_analysis": [
    {
      "weakness_pattern": "Pattern description",
      "primary_root_cause": "Main underlying cause",
      "contributing_factors": ["Factor 1", "Factor 2"],
      "issue_type": "systematic|topic_specific|random",
      "intervention_points": [
        {
          "stage": "pre_generation|during_generation|post_generation|evaluation",
          "intervention": "Specific intervention description",
          "difficulty": "easy|medium|hard",
          "expected_impact": "high|medium|low"
        }
      ]
    }
  ],
  "systemic_issues": [
    "Issues that affect the overall generation system"
  ],
  "quick_wins": [
    "Easy improvements with high impact"
  ],
  "strategic_improvements": [
    "More complex improvements for long-term gains"
  ]
}
```

Focus on actionable insights that can drive specific system improvements."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "identify_root_causes",
            f"Analyzed root causes for {len(weakness_patterns)} patterns",
            {"pattern_count": len(weakness_patterns)}
        )
        
        return result