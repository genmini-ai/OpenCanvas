"""
Centralized prompts for the evolution system.
All prompts are stored as regular strings to avoid f-string formatting issues.
Use .format() method to insert variables when needed.

This file contains ALL prompts used throughout the evolution system:
- Agent system prompts
- Agent action prompts
- Analysis prompts
- Improvement prompts
- Implementation prompts
- Generation prompts
- Fallback prompts
"""

class EvolutionPrompts:
    """Centralized storage for all evolution system prompts"""
    
    # ============================================================================
    # IMPROVEMENT AGENT PROMPTS
    # ============================================================================
    
    IMPROVEMENT_DESIGN = """Design specific, implementable improvements based on the following reflection analysis for evolution iteration {iteration_number}.

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

Return a JSON object with the following structure:
{{
  "improvement_iteration": {{
    "iteration_number": ITERATION_NUMBER,
    "target_baseline": {{
      "visual_target": X.X,
      "content_target": X.X,
      "accuracy_target": X.X,
      "overall_target": X.X
    }},
    "expected_impact": "Description of overall expected improvement"
  }},
  "improvements": [
    {{
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
    }}
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
}}

Focus on creating specific, actionable improvements that can be immediately implemented and tested."""

    IMPROVEMENT_REFINEMENT = """Refine and optimize existing improvements based on their implementation results and new evaluation data.

EXISTING IMPROVEMENTS:
{existing_improvements_json}

IMPLEMENTATION RESULTS:
{implementation_results_json}

NEW EVALUATION DATA:
{new_evaluation_json}

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

Return a JSON object with the following structure:
{{
  "refinement_analysis": [
    {{
      "improvement_id": "existing_id",
      "effectiveness_rating": "high|medium|low",
      "achieved_impact": "Actual impact achieved",
      "issues_identified": ["Issue1", "Issue2"],
      "refinement_recommendations": [
        {{
          "type": "optimize|replace|remove|enhance",
          "description": "What to change",
          "implementation": "How to implement the change",
          "expected_improvement": "Expected benefit"
        }}
      ]
    }}
  ],
  "optimized_improvements": [
    "Same format as original improvements but refined"
  ],
  "new_insights": [
    "New understanding about what works/doesn't work"
  ]
}}

Focus on learning from implementation results to make improvements more effective."""

    IMPROVEMENT_PRIORITIZATION = """Prioritize the following improvements for implementation in iteration {current_iteration}, considering impact, effort, and constraints.

IMPROVEMENTS TO PRIORITIZE:
{improvements_json}

CONSTRAINTS:
{constraints_json}

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

Return a JSON object with the following structure:
{{
  "prioritization_analysis": [
    {{
      "improvement_id": "id",
      "priority_score": X.X,
      "impact_ratings": {{
        "quality_impact": X,
        "coverage": X,
        "strategic_value": X
      }},
      "feasibility_ratings": {{
        "implementation_effort": X,
        "risk_level": X,  
        "resource_requirements": X
      }},
      "recommendation": "implement_immediately|implement_next|implement_later|skip"
    }}
  ],
  "implementation_sequence": [
    {{
      "phase": "immediate|short_term|medium_term|long_term",
      "improvements": ["id1", "id2"],
      "rationale": "Why these improvements in this phase",
      "estimated_effort": "low|medium|high",
      "success_probability": "high|medium|low"
    }}
  ],
  "trade_offs": [
    {{
      "decision": "Description of trade-off decision",
      "alternatives": ["Option1", "Option2"],
      "chosen_approach": "Selected option",
      "rationale": "Why this choice was made"
    }}
  ]
}}

Focus on creating an optimal implementation plan that maximizes improvement while managing risks and constraints."""

    # ============================================================================
    # REFLECTION AGENT PROMPTS
    # ============================================================================
    
    REFLECTION_ANALYSIS = """Analyze the following presentation evaluation data to identify systematic patterns, weaknesses, and improvement opportunities for evolution iteration {iteration_number}.

EVALUATION DATA:
{evaluation_json}

BASELINE PERFORMANCE:
{baseline_json}

## Analysis Requirements:

### 1. QUALITY DIMENSION ANALYSIS
For each dimension (visual, content, accuracy):
- **Current Performance**: Average scores, variance, trends
- **Weakness Patterns**: Common failure modes, recurring issues
- **Root Causes**: Underlying reasons for quality gaps
- **Improvement Potential**: Realistic improvement targets

### 2. SYSTEMATIC PATTERN IDENTIFICATION
Identify patterns across presentations:
- **Consistent Failures**: Issues that appear in >50% of presentations
- **Context-Dependent Issues**: Problems linked to specific topics/purposes
- **Edge Cases**: Unusual failures that indicate system limitations
- **Emergent Behaviors**: Unexpected patterns in generation

### 3. PRIORITIZED WEAKNESS AREAS
Rank weaknesses by:
- **Impact**: How much they affect overall quality (1-5 scale)
- **Frequency**: How often they occur (percentage)
- **Fixability**: How tractable the solution is (easy/medium/hard)
- **Strategic Value**: Long-term importance for system improvement

### 4. IMPROVEMENT OPPORTUNITIES
For each major weakness:
- **Specific Issue**: Clear description of the problem
- **Evidence**: Examples from evaluation data
- **Root Cause**: Why this issue occurs
- **Improvement Direction**: High-level approach to fixing it

## Output Format:

Return a JSON object with the following structure:
{{
  "analysis_summary": {{
    "iteration_number": {iteration_number},
    "presentations_analyzed": X,
    "average_scores": {{
      "visual": X.X,
      "content": X.X,
      "overall": X.X
    }},
    "score_variance": {{
      "visual": X.X,
      "content": X.X
    }},
    "improvement_potential": {{
      "visual": X.X,
      "content": X.X,
      "overall": X.X
    }}
  }},
  "weakness_patterns": [
    {{
      "weakness_id": "unique_identifier",
      "name": "Clear weakness name",
      "category": "visual|content|structural|accuracy",
      "frequency": "percentage of affected presentations",
      "severity": "high|medium|low",
      "impact_score": X.X,
      "examples": ["Specific examples from evaluations"],
      "root_causes": ["Underlying reasons"],
      "affected_dimensions": ["dimension1", "dimension2"],
      "improvement_priority": "high|medium|low"
    }}
  ],
  "improvement_opportunities": [
    {{
      "opportunity_id": "unique_id",
      "target_weakness": "weakness_id",
      "improvement_type": "prompt|template|processing|validation",
      "description": "What can be improved",
      "expected_impact": "Potential quality improvement",
      "implementation_complexity": "low|medium|high",
      "success_probability": "high|medium|low"
    }}
  ],
  "strategic_recommendations": [
    {{
      "recommendation": "High-level strategic advice",
      "rationale": "Why this is important",
      "priority": "immediate|short_term|long_term"
    }}
  ]
}}

Focus on actionable insights that can drive measurable quality improvements."""

    # ============================================================================
    # IMPLEMENTATION AGENT PROMPTS
    # ============================================================================
    
    IMPLEMENTATION_PROMPT = """Convert the following improvement specifications into concrete implementation artifacts for evolution iteration {iteration_number}.

IMPROVEMENTS TO IMPLEMENT:
{improvements_json}

CURRENT SYSTEM STATE:
{system_state_json}

## Implementation Requirements:

### 1. PROMPT ENHANCEMENTS
For prompt improvements, create:
- **Enhanced Generation Prompts**: Detailed, specific instructions
- **Quality Guidelines**: Explicit standards and expectations
- **Validation Rules**: Built-in quality checks
- **Example Templates**: Good/bad examples for guidance

### 2. TEMPLATE MODIFICATIONS
For visual improvements, specify:
- **CSS/Style Changes**: Specific styling modifications
- **Layout Adjustments**: Structure and spacing changes
- **Component Updates**: New or modified visual elements
- **Responsive Behaviors**: Adaptation for different contexts

### 3. PROCESSING LOGIC
For processing improvements, define:
- **Algorithm Changes**: Modified generation logic
- **Validation Steps**: Quality gates and checks
- **Error Handling**: Recovery from common issues
- **Performance Optimizations**: Efficiency improvements

### 4. CONFIGURATION UPDATES
Specify all configuration changes:
- **Parameters**: New or modified configuration values
- **Feature Flags**: Enable/disable functionality
- **Thresholds**: Quality and validation thresholds
- **Defaults**: Updated default behaviors

## Output Format:

Return a JSON object with the following structure:
{{
  "implementation_package": {{
    "iteration": {iteration_number},
    "timestamp": "ISO timestamp",
    "improvements_count": X
  }},
  "prompt_artifacts": [
    {{
      "artifact_id": "unique_id",
      "improvement_id": "source_improvement_id",
      "type": "generation|validation|example",
      "name": "Descriptive name",
      "content": "The actual prompt text or template",
      "usage_context": "Where/how to use this",
      "expected_impact": "What this will improve"
    }}
  ],
  "template_artifacts": [
    {{
      "artifact_id": "unique_id",
      "improvement_id": "source_improvement_id",
      "type": "css|html|component",
      "name": "Template name",
      "modifications": {{
        "selectors": ["CSS selectors affected"],
        "properties": {{"property": "value"}},
        "description": "What this changes visually"
      }}
    }}
  ],
  "configuration_artifacts": [
    {{
      "artifact_id": "unique_id",
      "improvement_id": "source_improvement_id",
      "config_path": "path.to.config",
      "old_value": "previous value",
      "new_value": "updated value",
      "rationale": "Why this change"
    }}
  ],
  "validation_rules": [
    {{
      "rule_id": "unique_id",
      "improvement_id": "source_improvement_id",
      "type": "pre_generation|post_generation",
      "condition": "What triggers this rule",
      "action": "What happens when triggered",
      "severity": "error|warning|info"
    }}
  ],
  "testing_plan": {{
    "unit_tests": ["Test descriptions"],
    "integration_tests": ["Test scenarios"],
    "validation_criteria": ["Success metrics"]
  }}
}}

Focus on creating deployable artifacts that can be immediately integrated into the system."""

    IMPLEMENTATION_MAIN = """Implement the following improvements as specific, deployable system changes for evolution iteration {iteration_number}.

CURRENT TOOL ECOSYSTEM:
{tool_context}

IMPROVEMENTS TO IMPLEMENT:
{improvements_json}

CURRENT SYSTEM CONFIGURATION:
{system_config_json}

## Implementation Requirements:

### 1. ENHANCED PROMPT GENERATION
For prompt enhancement improvements, create:
- **Complete Prompt Templates**: Full prompt text with all enhancements
- **Variable Placeholders**: Clear variable substitution points ({{{{topic}}}}, {{{{purpose}}}}, etc.)
- **Quality Requirements**: Embedded quality standards and validation criteria
- **Instruction Hierarchy**: Organized from most to least important requirements

### 2. SYSTEM CONFIGURATION CHANGES
For configuration improvements, create:
- **Parameter Updates**: Specific parameter changes with values
- **Template Modifications**: Updated visual templates and styling
- **Processing Rules**: Modified content processing logic
- **Quality Thresholds**: Updated quality control standards

### 3. VALIDATION RULE IMPLEMENTATION
For quality control improvements, create:
- **Pre-Generation Checks**: Input validation rules and requirements
- **Generation Monitoring**: Quality gates and checkpoints
- **Post-Generation Validation**: Automated quality assessment rules
- **Error Handling**: Response to quality failures and corrections

### 4. INTEGRATION SPECIFICATIONS
For each implementation:
- **Integration Points**: Where in the system to apply changes
- **Dependency Management**: How changes interact with existing system
- **Rollback Procedures**: How to undo changes if needed
- **Testing Approach**: How to validate the implementation works

## Output Format:

Return a JSON object with implementation details including prompt_enhancements, configuration_changes, validation_rules, integration_plan, and proposed_tools.

Focus on creating complete, deployable implementations AND innovative tools that expand system capabilities."""

    IMPLEMENTATION_PROMPT_ENHANCEMENTS = """Generate enhanced generation prompts that implement the specified improvements and address identified quality issues.

IMPROVEMENTS TO IMPLEMENT:
{improvements_json}

QUALITY ISSUES TO ADDRESS:
{quality_issues_json}

CURRENT PROMPTS:
{current_prompts_json}

## Enhancement Requirements:

### 1. PROMPT STRUCTURE
Create complete, enhanced prompts with:
- **Clear Instructions**: Specific, unambiguous generation requirements
- **Quality Standards**: Explicit quality thresholds and expectations
- **Variable Placeholders**: Marked with {{{{variable_name}}}} format
- **Priority Hierarchy**: Most important requirements first

### 2. QUALITY IMPROVEMENTS
Address identified issues by:
- **Adding Constraints**: Rules that prevent common quality problems
- **Clarifying Requirements**: More specific instructions for weak areas
- **Including Examples**: Good and bad examples where helpful
- **Validation Criteria**: Built-in quality checks

## Output Format:

Return a JSON object with enhanced_prompts array containing prompt_id, prompt_type, content, improvements_addressed, and usage_instructions.

Focus on creating prompts that directly address identified quality issues."""

    IMPLEMENTATION_VALIDATION_RULES = """Create specific validation rules and quality control mechanisms based on the improvements and identified quality issues.

IMPROVEMENTS TO IMPLEMENT:
{improvements_json}

QUALITY ISSUES TO ADDRESS:
{quality_issues_json}

## Validation Requirements:

### 1. PRE-GENERATION VALIDATION
Create rules that check:
- **Input Quality**: Validate input completeness and appropriateness
- **Requirements Met**: Ensure necessary conditions are satisfied
- **Resource Availability**: Check required resources are accessible
- **Parameter Validity**: Validate configuration parameters

### 2. DURING-GENERATION MONITORING
Create rules that:
- **Monitor Progress**: Track generation quality as it proceeds
- **Apply Quality Gates**: Stop or adjust if quality drops
- **Resource Management**: Monitor and limit resource usage
- **Error Detection**: Catch issues early in the process

### 3. POST-GENERATION VALIDATION
Create rules that:
- **Quality Assessment**: Evaluate final output quality
- **Completeness Checks**: Ensure all requirements were met
- **Consistency Validation**: Check for internal contradictions
- **Format Verification**: Validate output structure and format

## Output Format:

Return a JSON object with validation_rules array containing rule_id, rule_type, condition, action, severity, and implementation details.

Focus on creating practical validation that prevents quality issues without being overly restrictive."""

    IMPLEMENTATION_TESTING_APPROACH = """Create a comprehensive testing approach for the implemented improvements to validate they work correctly and achieve expected quality gains.

IMPLEMENTATIONS TO TEST:
{implementations_json}

ORIGINAL IMPROVEMENTS:
{improvements_json}

## Testing Requirements:

### 1. UNIT TESTS
Design tests for individual components:
- **Prompt Tests**: Validate enhanced prompts generate better content
- **Validation Tests**: Ensure validation rules work correctly
- **Configuration Tests**: Verify configuration changes apply properly
- **Tool Tests**: Test proposed tools function as expected

### 2. INTEGRATION TESTS
Design tests for system integration:
- **End-to-End Tests**: Full generation pipeline with improvements
- **Compatibility Tests**: Ensure changes work with existing system
- **Performance Tests**: Measure impact on generation speed
- **Resource Tests**: Monitor resource usage changes

### 3. QUALITY TESTS
Design tests for quality improvements:
- **A/B Comparisons**: Compare before/after quality scores
- **Edge Case Tests**: Test with challenging inputs
- **Regression Tests**: Ensure no quality degradation
- **Metric Validation**: Verify improvement metrics are met

## Output Format:

Return a JSON object with test_suite containing unit_tests, integration_tests, quality_tests, test_data, and success_criteria.

Focus on practical tests that validate improvements work correctly and achieve quality goals."""

    # ============================================================================
    # ORCHESTRATOR AGENT PROMPTS
    # ============================================================================
    
    ORCHESTRATION_PLANNING = """Create an evolution cycle plan for iteration {iteration_number} based on current system state and evaluation results.

CURRENT STATE:
{current_state_json}

EVALUATION RESULTS:
{evaluation_results_json}

PREVIOUS ITERATIONS:
{previous_iterations_json}

## Planning Requirements:

### 1. CYCLE OBJECTIVES
Define clear objectives for this evolution cycle:
- **Quality Targets**: Specific score improvements to achieve
- **Focus Areas**: Priority dimensions to improve
- **Success Metrics**: How to measure cycle success
- **Risk Constraints**: Acceptable risk levels

### 2. AGENT COORDINATION
Plan the multi-agent workflow:
- **Reflection Phase**: Analysis scope and depth
- **Improvement Phase**: Number and types of improvements
- **Implementation Phase**: Artifacts to generate
- **Validation Phase**: Testing and verification approach

### 3. RESOURCE ALLOCATION
Estimate resource requirements:
- **Time Budget**: Expected duration for each phase
- **Complexity Points**: Effort allocation across improvements
- **Parallelization**: What can be done concurrently
- **Dependencies**: Sequential requirements

### 4. RISK MANAGEMENT
Identify and mitigate risks:
- **Rollback Points**: Where we can safely revert
- **Validation Gates**: Quality checks between phases
- **Failure Modes**: What could go wrong
- **Contingency Plans**: Alternative approaches

## Output Format:

Return a JSON object with the following structure:
{{
  "evolution_plan": {{
    "iteration": {iteration_number},
    "objectives": {{
      "primary_goal": "Main objective",
      "quality_targets": {{"visual": X.X, "content": X.X}},
      "focus_areas": ["Area1", "Area2"],
      "success_criteria": ["Criterion1", "Criterion2"]
    }},
    "phase_plan": [
      {{
        "phase": "reflection|improvement|implementation|validation",
        "agent": "agent_name",
        "inputs": ["Required inputs"],
        "expected_outputs": ["Expected results"],
        "duration_estimate": "time estimate",
        "success_metrics": ["How to measure success"]
      }}
    ],
    "resource_plan": {{
      "total_duration": "estimated time",
      "complexity_budget": X,
      "parallel_tasks": ["Task1", "Task2"],
      "sequential_dependencies": ["Dep1 -> Dep2"]
    }},
    "risk_plan": {{
      "identified_risks": ["Risk1", "Risk2"],
      "mitigation_strategies": ["Strategy1", "Strategy2"],
      "rollback_triggers": ["Condition1", "Condition2"],
      "validation_gates": ["Gate1", "Gate2"]
    }}
  }}
}}

Create a comprehensive plan that maximizes improvement while managing complexity and risk."""

    @classmethod
    def get_prompt(cls, prompt_name: str, **kwargs) -> str:
        """
        Get a prompt by name and format it with provided kwargs.
        
        Args:
            prompt_name: Name of the prompt (e.g., 'IMPROVEMENT_DESIGN')
            **kwargs: Variables to format into the prompt
            
        Returns:
            Formatted prompt string
        """
        if not hasattr(cls, prompt_name):
            raise ValueError(f"Prompt '{prompt_name}' not found in EvolutionPrompts")
        
        prompt_template = getattr(cls, prompt_name)
        return prompt_template.format(**kwargs)
    
    # ============================================================================
    # CORE AGENT PROMPTS (from core/agents.py)
    # ============================================================================
    
    CORE_ANALYZE_EVALUATIONS = """Analyze the following presentation evaluation results to identify ALL improvement opportunities. IMPORTANT: We aim for excellence (5.0/5.0), not just adequacy. Find gaps even in areas scoring 4.0/5.0.

EVALUATION DATA:
{evaluations_json}

TOPICS EVALUATED:
{topics_str}

REGISTRY CONTEXT (existing tools and lessons learned):
{registry_context}

## CRITICAL INSTRUCTION: ALWAYS IDENTIFY GAPS
Even if overall scores seem acceptable, you MUST identify at least 3-5 improvement opportunities. Any score below 4.5/5.0 represents a significant gap. Even 4.5+ scores can be improved.

## Analysis Requirements:

1. **Gap Identification**
   Identify ALL areas for improvement (target: 5.0/5.0 excellence):
   - **Priority 1**: Any dimension scoring below 4.0/5.0 (major gaps)
   - **Priority 2**: Dimensions scoring 4.0-4.5/5.0 (moderate gaps)  
   - **Priority 3**: Dimensions scoring 4.5-4.9/5.0 (refinement opportunities)
   
   For each gap provide:
   - Gap Description: Clear statement of what is lacking
   - Current Score: X.X/5.0 (average across evaluations)
   - Target Score: Y.Y/5.0 (aim for 4.8+ minimum)
   - Examples: Specific instances from the evaluations

2. **Solution Reasoning**
   For EACH identified gap, analyze:
   - Can prompt improvements fix this?
     * Would better instructions resolve it? [Yes/No]
     * Would format/structure changes help? [Yes/No]
     * Would additional constraints work? [Yes/No]
   - Does this need new capabilities?
     * Missing data processing? [Yes/No - What kind?]
     * Missing external resources? [Yes/No - Which APIs?]
     * Missing validation/checking? [Yes/No - What type?]
   - Check registry: Has this been tried before and failed?

3. **Solution Type Decision**
   Based on the reasoning above, classify each gap:
   - "prompt": Can be fixed with better generation instructions
     * Examples: slide structure, content organization, formatting rules
   - "tool": Requires new processing capabilities or external resources
     * Examples: image enhancement, citation verification, data visualization
   - "both": Complex issue needing multiple approaches
   
   Provide clear decision rationale for each classification.

4. **Priority Assessment**
   - Rank gaps by impact (score improvement potential)
   - Consider implementation complexity
   - Account for dependencies between gaps

## CRITICAL: JSON OUTPUT REQUIRED

You MUST respond with ONLY a valid JSON object. Do not include any text before or after the JSON. No explanations, no markdown code blocks, no additional commentary.

## Output Format:

Return EXACTLY this JSON structure:
{{
  "baseline_performance": {{
    "visual": X.X,
    "content_free": X.X,
    "content_required": X.X,
    "overall": X.X
  }},
  "identified_gaps": [
    {{
      "gap_id": "gap_001",
      "description": "Clear description of the weakness",
      "dimension": "visual|content|accuracy|etc",
      "current_score": X.X,
      "target_score": Y.Y,
      "examples": ["Example 1", "Example 2"],
      "solution_reasoning": {{
        "prompt_can_fix": {{
          "better_instructions": true/false,
          "format_changes": true/false,
          "additional_constraints": true/false,
          "reasoning": "Why prompt changes would/wouldn't work"
        }},
        "needs_new_capability": {{
          "data_processing": true/false,
          "external_resources": true/false,
          "validation_checking": true/false,
          "reasoning": "What capabilities are missing and why needed"
        }},
        "registry_check": "Previous attempts or similar tools that failed"
      }},
      "solution_type": "prompt|tool|both",
      "solution_rationale": "Clear explanation of why this solution type was chosen",
      "priority": "high|medium|low",
      "expected_impact": X.X
    }}
  ],
  "routing_summary": {{
    "prompt_gaps": ["gap_ids that need prompt solutions"],
    "tool_gaps": ["gap_ids that need tool solutions"],
    "both_gaps": ["gap_ids that need both approaches"]
  }},
  "minimum_gaps_check": {{
    "gaps_found": <number>,
    "message": "If < 3 gaps found, analyzed lowest-scoring dimensions to ensure progress"
  }}
}}

IMPORTANT REQUIREMENTS:
1. You MUST identify at least 3 gaps, even if scores seem good
2. Any dimension below 4.5/5.0 should be considered a gap
3. If all dimensions are above 4.5, identify the 3 lowest-scoring areas as gaps
4. Target scores should be ambitious (4.8-5.0 range)
5. Never return empty identified_gaps array

Focus on continuous improvement - there's ALWAYS room to enhance quality."""

    CORE_DESIGN_IMPROVEMENTS = """Design specific, systematic improvements based on the reflection analysis for evolution iteration {iteration_number}.

REFLECTION RESULTS:
{reflection_json}

CURRENT BASELINE:
{baseline_json}

## Improvement Design Requirements:

1. **Systematic Approaches**
   - Design improvements that address root causes, not symptoms
   - Create scalable solutions that work across different content types
   - Ensure improvements integrate with existing system

2. **Prioritization**
   - Focus on high-impact, low-complexity improvements first
   - Balance quick wins with strategic enhancements
   - Consider dependencies between improvements

3. **Measurability**
   - Define clear success metrics for each improvement
   - Specify expected impact on quality scores
   - Include validation approaches

## Output Format:

Return a JSON object with:
- improvements: array with id, name, description, category, priority, expected_impact
- implementation_plan: phased approach with dependencies
- success_criteria: measurable outcomes and thresholds

Focus on practical, implementable improvements with clear impact."""

    CORE_IMPLEMENT_IMPROVEMENTS = """Implement the following improvements as specific, deployable system changes for evolution iteration {iteration_number}.

IMPROVEMENTS:
{improvements_json}

CURRENT SYSTEM CONFIG:
{config_json}

## Implementation Requirements:

1. **Concrete Artifacts**
   - Generate complete, deployable implementations
   - Include all necessary configurations and code
   - Provide clear integration instructions

2. **Quality Assurance**
   - Include validation rules and checks
   - Define testing approaches
   - Specify rollback procedures

3. **Documentation**
   - Clear usage instructions
   - Integration points and dependencies
   - Expected behavior and impact

## Output Format:

Return a JSON object with implementation artifacts including:
- prompt_enhancements: enhanced generation prompts
- configuration_changes: system configuration updates
- validation_rules: quality control mechanisms
- integration_plan: deployment sequence and testing

Focus on creating immediately deployable implementations."""

    # Generic action prompts for core agents
    CORE_GENERIC_REFLECTION = """As a reflection specialist, perform the following action: {action}

Input data: {input_json}

Provide your analysis and insights."""

    CORE_GENERIC_IMPROVEMENT = """As an improvement specialist, perform the following action: {action}

Input data: {input_json}

Design specific improvements based on the input."""

    CORE_GENERIC_IMPLEMENTATION = """As an implementation specialist, perform the following action: {action}

Input data: {input_json}

Create concrete implementations based on the requirements."""

    CORE_GENERIC_ORCHESTRATION = """As an orchestration specialist, perform the following action: {action}

Input data: {input_json}

Coordinate the evolution process based on the input."""

    # ============================================================================
    # GENERATION PROMPTS (from evolved_generator.py, prompt_evolution_manager.py, core/prompts.py)
    # ============================================================================
    
    TOPIC_GENERATION_BASE = """You are an expert presentation generator with enhanced quality standards. Create a comprehensive HTML presentation based on the given topic.

TOPIC: {topic}
PURPOSE: {purpose}
THEME: {theme}"""

    PDF_GENERATION_BASE = """You are an expert presentation generator with enhanced fidelity standards. Create a comprehensive HTML presentation based on the provided PDF content.

PDF CONTENT: {pdf_content}
PURPOSE: {purpose}
THEME: {theme}"""

    FALLBACK_GENERATION = """Create a presentation about: {content}
Purpose: {purpose}
Theme: {theme}

Generate a comprehensive HTML presentation with proper structure and styling."""

    # ============================================================================
    # AGENT SYSTEM PROMPTS (from config/agent_prompts.py)
    # ============================================================================
    
    AGENT_SYSTEM_REFLECTION = """You are a Presentation Quality Reflection Specialist with deep expertise in analyzing presentation evaluation results and identifying systematic improvement opportunities.

## Your Core Expertise:
- **Pattern Recognition**: Identifying recurring quality issues across multiple presentations
- **Root Cause Analysis**: Understanding why presentations fail in specific dimensions
- **Systematic Analysis**: Converting evaluation data into actionable insights
- **Comparative Analysis**: Benchmarking against quality standards

## Your Analysis Framework:
1. **Data Processing**: Extract patterns from evaluation results
2. **Weakness Identification**: Identify systematic failure points
3. **Impact Assessment**: Prioritize issues by frequency and severity
4. **Improvement Opportunities**: Suggest specific areas for enhancement

## Your Output Standards:
- **Evidence-Based**: All conclusions supported by evaluation data
- **Quantitative**: Include specific scores, percentages, and metrics
- **Prioritized**: Rank issues by impact potential
- **Actionable**: Focus on problems that can be systematically addressed

## Your Communication Style:
- **Analytical**: Data-driven insights with supporting evidence
- **Systematic**: Organized analysis with clear categorization
- **Precise**: Specific metrics and concrete examples
- **Strategic**: Focus on high-impact improvement opportunities

You excel at transforming raw evaluation data into strategic insights that guide systematic quality improvements."""

    AGENT_SYSTEM_IMPROVEMENT = """You are a Presentation Generation Improvement Specialist with expertise in designing systematic enhancements to presentation quality based on analytical insights.

## Your Core Expertise:
- **Solution Design**: Creating targeted improvements for identified weaknesses
- **System Understanding**: Deep knowledge of presentation generation architecture
- **Quality Engineering**: Designing measurable quality improvements
- **Strategic Planning**: Prioritizing improvements by impact and feasibility

## Your Design Framework:
1. **Problem Analysis**: Understanding root causes from reflection insights
2. **Solution Architecture**: Designing systematic approaches to improvements
3. **Impact Modeling**: Estimating improvement potential and implementation effort
4. **Integration Planning**: Ensuring improvements work within existing system

## Your Output Standards:
- **Systematic**: Improvements that address root causes, not just symptoms
- **Measurable**: Clear success criteria and expected impact metrics
- **Feasible**: Realistic improvements within system constraints
- **Comprehensive**: Address multiple aspects of identified problems

## Your Communication Style:
- **Strategic**: Focus on high-impact, systematic improvements
- **Technical**: Precise understanding of system capabilities and constraints
- **Organized**: Structured improvement plans with clear priorities
- **Practical**: Emphasis on implementable solutions

You excel at transforming analytical insights into concrete improvement strategies that systematically enhance presentation generation quality."""

    AGENT_SYSTEM_IMPLEMENTATION = """You are a Presentation Generation Implementation Specialist with deep expertise in translating improvement strategies into concrete, deployable implementations AND discovering new tools to expand system capabilities.

## Your Core Expertise:
- **System Implementation**: Converting designs into deployable code and configurations
- **Tool Discovery**: Identifying gaps that require new tools beyond prompt improvements
- **Architecture Integration**: Ensuring implementations work within existing system
- **Quality Assurance**: Building validation and testing approaches

## Your Implementation Framework:
1. **Gap Analysis**: Determine if improvements need prompts, tools, or system changes
2. **Tool Discovery**: When gaps can't be solved by prompts, propose new tools
3. **Implementation Design**: Create complete, deployable solutions
4. **Integration Planning**: Ensure smooth deployment with existing system
5. **Validation Strategy**: Design testing approaches for all changes

## Your Output Standards:
- **Executable**: All code and configurations ready for immediate deployment
- **Complete**: No missing pieces or undefined references
- **Tool-Aware**: Propose new tools when prompt changes aren't sufficient
- **Validated**: Include testing approach for each change

## Your Communication Style:
- **Technical**: Precise, implementation-focused language
- **Innovative**: Propose new tools to solve systematic problems
- **Detailed**: Complete specifications for all changes
- **Practical**: Focus on what needs to be built and deployed

IMPORTANT: When analysis shows quality gaps that can't be solved by prompt changes alone, propose new TOOLS that can systematically address those gaps. Tools should be:
- Modular and independent
- Fast (minimal generation speed impact)
- Measurable (clear A/B testing capability) 
- Cost-effective

You excel at turning improvement designs into working system enhancements AND discovering the missing tools needed for systematic quality improvements."""

    AGENT_SYSTEM_ORCHESTRATOR = """You are an Evolution Orchestration Specialist responsible for coordinating multiple specialized agents through systematic presentation quality improvement cycles.

## Your Core Expertise:
- **Multi-Agent Coordination**: Managing complex interactions between specialized agents
- **Evolution Planning**: Designing improvement cycles with clear objectives
- **Resource Management**: Optimizing agent utilization and system resources
- **Progress Tracking**: Monitoring improvement metrics across iterations

## Your Orchestration Framework:
1. **Cycle Planning**: Design evolution iterations with specific goals
2. **Agent Coordination**: Route tasks to appropriate specialists
3. **Result Integration**: Combine outputs from multiple agents
4. **Progress Monitoring**: Track improvements and adjust strategies

## Your Output Standards:
- **Comprehensive**: Complete evolution plans with all phases covered
- **Coordinated**: Clear task allocation and dependencies
- **Measurable**: Specific success metrics and validation approaches
- **Adaptive**: Ability to adjust based on results

## Your Communication Style:
- **Executive**: High-level oversight with strategic focus
- **Structured**: Clear phases, milestones, and deliverables
- **Collaborative**: Effective coordination between agents
- **Results-Oriented**: Focus on achieving quality improvements

You excel at orchestrating complex evolution cycles that systematically improve presentation quality through coordinated agent collaboration."""

    @classmethod
    def get_prompt(cls, prompt_name: str, **kwargs) -> str:
        """
        Get a prompt by name and format it with provided kwargs.
        
        Args:
            prompt_name: Name of the prompt (e.g., 'IMPROVEMENT_DESIGN')
            **kwargs: Variables to format into the prompt
            
        Returns:
            Formatted prompt string
        """
        if not hasattr(cls, prompt_name):
            raise ValueError(f"Prompt '{prompt_name}' not found in EvolutionPrompts")
        
        prompt_template = getattr(cls, prompt_name)
        return prompt_template.format(**kwargs)
    
    @classmethod
    def list_prompts(cls) -> list:
        """List all available prompt names"""
        return [
            attr for attr in dir(cls) 
            if not attr.startswith('_') 
            and isinstance(getattr(cls, attr), str)
            and attr.isupper()
        ]