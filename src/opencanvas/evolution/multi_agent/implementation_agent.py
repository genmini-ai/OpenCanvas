"""
Implementation Agent - Specialized in actually applying improvements to the generation system
"""

import json
import logging
import re
from typing import Dict, Any, List
from pathlib import Path
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent

logger = logging.getLogger(__name__)

class ImplementationAgent(BaseEvolutionAgent):
    """Agent specialized in implementing specific improvements in the generation system"""
    
    def __init__(self, api_key: str = None):
        super().__init__("ImplementationAgent", api_key)
    
    def get_system_prompt(self) -> str:
        """Specialized system prompt for implementation"""
        return """You are a Presentation Generation Implementation Specialist with deep expertise in translating improvement designs into actual system changes.

## Your Core Expertise:
- **Code Generation**: Creating specific code changes for improvements
- **Prompt Engineering**: Crafting enhanced generation prompts with precise instructions
- **Configuration Management**: Updating system configurations and parameters
- **Validation Implementation**: Creating quality checks and validation rules
- **Integration Planning**: Ensuring improvements work together seamlessly

## Your Implementation Framework:

### Prompt Enhancement Implementation:
- **Instruction Crafting**: Writing clear, specific, actionable prompts
- **Constraint Integration**: Adding validation rules and quality requirements
- **Example Integration**: Including good/bad examples for guidance
- **Context Management**: Ensuring prompts work across different scenarios

### System Configuration Changes:
- **Parameter Tuning**: Adjusting generation parameters for better quality
- **Template Modifications**: Updating visual templates and layouts
- **Processing Logic**: Modifying content processing workflows
- **Quality Thresholds**: Setting appropriate quality control standards

### Validation and Quality Control:
- **Pre-Generation Checks**: Input validation and requirement verification
- **Generation Monitoring**: Quality gates during the creation process
- **Post-Generation Validation**: Automated quality assessment rules
- **Error Handling**: Graceful handling of quality issues

### Code and Configuration Generation:
- **Prompt Templates**: Structured prompt generation with variables
- **Configuration Files**: JSON/YAML configurations for system parameters
- **Validation Scripts**: Code for quality checking and validation
- **Integration Hooks**: Code to integrate improvements into existing system

## Your Implementation Principles:
1. **Precision**: Every change must be specific and unambiguous
2. **Compatibility**: Improvements must work with existing system
3. **Testability**: All changes must be verifiable and measurable
4. **Maintainability**: Code and configurations must be clean and documented
5. **Rollback-Ready**: All changes must be easily reversible

## Your Output Standards:
- **Executable**: All code and configurations ready for immediate deployment
- **Complete**: No missing pieces or undefined references
- **Documented**: Clear explanation of what each change does
- **Validated**: Include testing approach for each change

## Your Communication Style:
- **Technical**: Precise, implementation-focused language
- **Detailed**: Complete specifications for all changes
- **Organized**: Structured by implementation phase and component
- **Practical**: Focus on what needs to be built and deployed

You excel at turning improvement designs into working system enhancements that can be immediately deployed and tested."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process improvement designs and generate implementation artifacts"""
        
        action_type = input_data.get("action", "implement_improvements")
        
        if action_type == "implement_improvements":
            return self._implement_improvements(input_data)
        elif action_type == "generate_prompts":
            return self._generate_enhanced_prompts(input_data)
        elif action_type == "create_validation":
            return self._create_validation_rules(input_data)
        elif action_type == "test_implementation":
            return self._test_implementation(input_data)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _implement_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the designed improvements"""
        
        improvements = input_data.get("improvements", [])
        current_system_config = input_data.get("current_system_config", {})
        iteration_number = input_data.get("iteration_number", 1)
        
        # Get current tool ecosystem context
        from opencanvas.evolution.tools_registry_manager import ToolsRegistryManager
        try:
            registry_manager = ToolsRegistryManager()
            tool_context = registry_manager.get_tools_for_agent_context()
        except Exception as e:
            tool_context = "Tool context unavailable"

        prompt = f"""Implement the following improvements as specific, deployable system changes for evolution iteration {iteration_number}.

CURRENT TOOL ECOSYSTEM:
{tool_context}

IMPROVEMENTS TO IMPLEMENT:
{json.dumps(improvements, indent=2)}

CURRENT SYSTEM CONFIGURATION:
{json.dumps(current_system_config, indent=2)}

## Implementation Requirements:

### 1. ENHANCED PROMPT GENERATION
For prompt enhancement improvements, create:
- **Complete Prompt Templates**: Full prompt text with all enhancements
- **Variable Placeholders**: Clear variable substitution points ({{topic}}, {{purpose}}, etc.)
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

```json
{
  "implementation_package": {
    "iteration_number": {iteration_number},
    "total_changes": X,
    "implementation_date": "timestamp",
    "rollback_available": true
  },
  "prompt_enhancements": [
    {
      "improvement_id": "id",
      "prompt_type": "topic_generation|pdf_generation|validation",
      "enhanced_prompt": "Complete enhanced prompt text with {{variables}}",
      "key_enhancements": ["Enhancement1", "Enhancement2"],
      "quality_requirements": ["Requirement1", "Requirement2"],
      "usage_instructions": "How to use this prompt"
    }
  ],
  "configuration_changes": [
    {
      "improvement_id": "id", 
      "config_type": "parameters|templates|processing|validation",
      "changes": {
        "parameter_name": "new_value",
        "setting_name": "new_setting"
      },
      "file_locations": ["config/file1.json", "templates/template1.html"],
      "backup_required": true
    }
  ],
  "validation_rules": [
    {
      "improvement_id": "id",
      "rule_type": "pre_generation|during_generation|post_generation",
      "validation_logic": "Specific validation implementation",
      "error_handling": "What to do when validation fails",
      "integration_point": "Where in the process to apply this rule"
    }
  ],
  "integration_plan": {
    "deployment_sequence": [
      {
        "step": 1,
        "changes": ["improvement_id1", "improvement_id2"],
        "description": "What this step does",
        "validation": "How to test this step",
        "rollback": "How to undo this step"
      }
    ],
    "testing_checklist": [
      "Test item 1",
      "Test item 2"
    ],
    "success_criteria": [
      "Criteria 1",
      "Criteria 2"
    ]
  },
  "proposed_tools": [
    {
      "name": "Tool Name",
      "purpose": "What this tool does",
      "target_problem": "Specific problem it solves from evaluation data",
      "implementation": {
        "class_name": "ToolClassName",
        "main_method": "process",
        "params": "input_data",
        "description": "Process description",
        "logic": "Core implementation logic"
      },
      "expected_impact": "high|medium|low - estimate improvement to evaluation scores",
      "complexity": "low|medium|high - implementation difficulty",
      "integration_points": ["Where in generation pipeline to integrate"],
      "validation_method": "How to A/B test effectiveness",
      "cost_estimate": "API calls, processing time, etc.",
      "speed_impact": "Effect on generation time"
    }
  ],
  "implementation_artifacts": {
    "prompt_files": ["prompts/enhanced_topic_prompt.txt"],
    "config_files": ["config/evolution_iteration_{iteration_number}.json"],
    "validation_scripts": ["validation/quality_checks_{iteration_number}.py"],
    "tool_specifications": ["tools/proposed_tools_{iteration_number}.json"],
    "documentation": ["docs/iteration_{iteration_number}_changes.md"]
  }
}
```

IMPORTANT: When analysis shows quality gaps that can't be solved by prompt changes alone, propose new TOOLS that can systematically address those gaps. Tools should be:
- Modular and independent
- Fast (minimal generation speed impact)
- Measurable (clear A/B testing capability)
- Cost-effective

Examples of tools that could address common gaps:
- CitationVerificationTool for fake citation detection
- ChartValidationTool for unreadable visualizations
- ContentBalanceAnalyzer for text wall detection
- VisualConsistencyChecker for design inconsistencies

Focus on creating complete, deployable implementations AND innovative tools that expand system capabilities."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "implement_improvements",
            f"Generated implementation for {len(improvements)} improvements in iteration {iteration_number}",
            {"improvements": len(improvements), "iteration": iteration_number}
        )
        
        return result
    
    def _generate_enhanced_prompts(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific enhanced prompts based on improvements"""
        
        improvements = input_data.get("improvements", [])
        current_prompts = input_data.get("current_prompts", {})
        baseline_scores = input_data.get("baseline_scores", {})
        
        prompt = f"""Generate enhanced generation prompts that implement the specified improvements and address identified quality issues.

IMPROVEMENTS TO IMPLEMENT:
{json.dumps(improvements, indent=2)}

CURRENT PROMPTS:
{json.dumps(current_prompts, indent=2)}

BASELINE SCORES TO IMPROVE:
{json.dumps(baseline_scores, indent=2)}

## Enhanced Prompt Generation Requirements:

### 1. VISUAL QUALITY ENHANCEMENTS
If visual improvements are specified, include:
- **Chart Readability**: Explicit requirements for readable charts with proper axes, labels, and scaling
- **Design Consistency**: Clear color scheme, typography, and spacing standards
- **Information Hierarchy**: Specific requirements for title sizing, bullet formatting, visual emphasis
- **Visual-Text Integration**: Requirements for purposeful visual elements that enhance content

### 2. CONTENT QUALITY ENHANCEMENTS  
If content improvements are specified, include:
- **Source Fidelity**: Strict requirements for accuracy and faithful representation
- **Coverage Completeness**: Systematic inclusion of essential information and methodology
- **Logical Structure**: Requirements for clear flow, transitions, and narrative construction
- **Fact Validation**: Built-in plausibility checks and consistency requirements

### 3. QUALITY CONTROL INTEGRATION
For all enhanced prompts, include:
- **Validation Checkpoints**: Self-checking requirements within the generation process
- **Quality Standards**: Explicit quality thresholds and expectations
- **Error Prevention**: Specific constraints to prevent identified common issues
- **Success Criteria**: Clear requirements for successful completion

### 4. PROMPT STRUCTURE OPTIMIZATION
Structure each prompt with:
- **Priority Hierarchy**: Most critical requirements first
- **Clear Instructions**: Unambiguous, actionable directions
- **Context Awareness**: Adaptation to different topics and purposes
- **Variable Integration**: Proper use of {{topic}}, {{purpose}}, {{theme}} variables

## Output Format:

```json
{
  "enhanced_prompts": {
    "topic_generation_prompt": {
      "prompt_text": "Complete enhanced prompt for topic-based generation",
      "key_enhancements": ["Enhancement1", "Enhancement2"],
      "target_improvements": ["Dimension1", "Dimension2"],
      "usage_notes": "Special instructions for using this prompt"
    },
    "pdf_generation_prompt": {
      "prompt_text": "Complete enhanced prompt for PDF-based generation", 
      "key_enhancements": ["Enhancement1", "Enhancement2"],
      "target_improvements": ["Dimension1", "Dimension2"],
      "usage_notes": "Special instructions for using this prompt"
    },
    "validation_prompt": {
      "prompt_text": "Prompt for post-generation quality validation",
      "key_enhancements": ["Enhancement1", "Enhancement2"],
      "target_improvements": ["Dimension1", "Dimension2"],
      "usage_notes": "How to use for quality checking"
    }
  },
  "prompt_comparison": {
    "changes_made": ["Change1", "Change2"],
    "expected_impact": "Description of expected improvement",
    "backwards_compatibility": true/false,
    "migration_notes": "How to transition from old to new prompts"
  },
  "testing_prompts": [
    {
      "test_scenario": "Scenario description",
      "test_input": "Sample input for testing",
      "expected_behavior": "What the enhanced prompt should produce",
      "validation_criteria": "How to judge if the test passed"
    }
  ]
}
```

Create prompts that are immediately usable and address the specific quality issues identified in the analysis."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "generate_prompts",
            f"Generated enhanced prompts for {len(improvements)} improvements",
            {"improvements": len(improvements)}
        )
        
        return result
    
    def _create_validation_rules(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create specific validation rules for quality control"""
        
        improvements = input_data.get("improvements", [])
        quality_issues = input_data.get("quality_issues", [])
        
        prompt = f"""Create specific validation rules and quality control mechanisms based on the improvements and identified quality issues.

IMPROVEMENTS REQUIRING VALIDATION:
{json.dumps(improvements, indent=2)}

QUALITY ISSUES TO PREVENT:
{json.dumps(quality_issues, indent=2)}

## Validation Rule Creation Requirements:

### 1. PRE-GENERATION VALIDATION
Create rules that check before generation starts:
- **Input Validation**: Verify topic/PDF input quality and completeness
- **Requirement Verification**: Ensure all necessary parameters and context are available
- **Resource Checks**: Confirm system resources and capabilities for generation
- **Configuration Validation**: Verify system configuration is optimal for quality

### 2. DURING-GENERATION MONITORING
Create checkpoints during the generation process:
- **Progress Validation**: Verify generation is proceeding correctly
- **Quality Gates**: Check intermediate outputs meet minimum standards
- **Error Detection**: Identify issues early in the generation process
- **Correction Triggers**: When to apply mid-generation corrections

### 3. POST-GENERATION VALIDATION
Create comprehensive post-generation quality checks:
- **Visual Quality Checks**: Automated assessment of visual elements and readability
- **Content Quality Checks**: Verification of accuracy, completeness, and structure
- **Consistency Validation**: Check for internal contradictions and logical issues
- **Format Validation**: Ensure output meets technical and format requirements

### 4. AUTOMATED CORRECTION RULES
Create rules for automatic quality improvements:
- **Simple Fixes**: Automatic corrections for common, fixable issues
- **Enhancement Rules**: Automatic application of quality improvements
- **Escalation Rules**: When to flag issues for human review
- **Rollback Rules**: When to reject output and regenerate

## Output Format:

```json
{
  "validation_system": {
    "total_rules": X,
    "coverage_areas": ["visual", "content", "technical"],
    "automation_level": "high|medium|low",
    "integration_points": ["pre_gen", "during_gen", "post_gen"]
  },
  "validation_rules": [
    {
      "rule_id": "unique_id",
      "rule_name": "Descriptive rule name",
      "category": "visual|content|technical|format",
      "trigger": "pre_generation|during_generation|post_generation",
      "description": "What this rule checks",
      "validation_logic": "Specific implementation of the validation check",
      "pass_criteria": "When the validation passes",
      "fail_actions": ["action1", "action2"],
      "correction_logic": "How to fix issues when possible",
      "severity": "critical|important|minor"
    }
  ],
  "quality_gates": [
    {
      "gate_name": "Gate name",
      "trigger_point": "When this gate is checked",
      "checks": ["rule_id1", "rule_id2"],
      "pass_threshold": "Requirements to pass this gate",
      "fail_handling": "What happens if gate fails"
    }
  ],
  "automation_scripts": [
    {
      "script_name": "Script name",
      "purpose": "What this script does",
      "implementation": "Code or logic for the script",
      "usage": "How and when to use this script"
    }
  ],
  "integration_specifications": {
    "system_integration": "How to integrate these rules into the generation system",
    "configuration_files": ["Files that need to be created/updated"],
    "dependencies": ["Required system components"],
    "testing_approach": "How to test the validation system"
  }
}
```

Focus on creating practical, implementable validation rules that prevent identified quality issues."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "create_validation",
            f"Created validation rules for {len(improvements)} improvements and {len(quality_issues)} quality issues",
            {"improvements": len(improvements), "quality_issues": len(quality_issues)}
        )
        
        return result
    
    def _test_implementation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create testing approach for implemented improvements"""
        
        implementation_package = input_data.get("implementation_package", {})
        improvements = input_data.get("improvements", [])
        
        prompt = f"""Create a comprehensive testing approach for the implemented improvements to validate they work correctly and achieve expected quality gains.

IMPLEMENTATION PACKAGE:
{json.dumps(implementation_package, indent=2)}

IMPROVEMENTS TO TEST:
{json.dumps(improvements, indent=2)}

## Testing Strategy Requirements:

### 1. UNIT TESTING
For individual improvements:
- **Prompt Testing**: Verify enhanced prompts produce expected behavior
- **Configuration Testing**: Confirm configuration changes work correctly
- **Validation Testing**: Test that validation rules trigger appropriately
- **Integration Testing**: Ensure improvements work with existing system

### 2. QUALITY IMPACT TESTING
For quality improvements:
- **Before/After Comparison**: Test presentations generated before and after improvements
- **Dimension-Specific Testing**: Test specific quality dimensions targeted by improvements
- **Regression Testing**: Ensure improvements don't negatively impact other areas
- **Stress Testing**: Test improvements under various conditions

### 3. SYSTEM INTEGRATION TESTING
For system-level changes:
- **End-to-End Testing**: Full generation pipeline with improvements applied
- **Performance Testing**: Ensure improvements don't negatively impact performance
- **Compatibility Testing**: Verify compatibility with different input types and configurations
- **Error Handling Testing**: Test how system handles errors with improvements

### 4. SUCCESS VALIDATION
For measuring improvement effectiveness:
- **Baseline Comparison**: Compare against pre-improvement baselines
- **Target Achievement**: Verify improvements meet expected targets
- **Consistency Testing**: Ensure improvements work consistently across different scenarios
- **Long-term Stability**: Test that improvements maintain effectiveness over time

## Output Format:

```json
{
  "testing_strategy": {
    "total_tests": X,
    "testing_phases": ["unit", "integration", "quality", "system"],
    "estimated_duration": "Time estimate for complete testing",
    "success_criteria": "Overall criteria for successful implementation"
  },
  "test_plans": [
    {
      "test_category": "unit|integration|quality|system",
      "test_name": "Descriptive test name",
      "improvement_targets": ["improvement_id1", "improvement_id2"],
      "test_description": "What this test validates",
      "test_procedure": [
        "Step 1: Setup",
        "Step 2: Execute", 
        "Step 3: Validate"
      ],
      "test_inputs": "Required test inputs and scenarios",
      "expected_outputs": "Expected results and behaviors",
      "success_criteria": "How to determine if test passes",
      "failure_actions": "What to do if test fails"
    }
  ],
  "test_scenarios": [
    {
      "scenario_name": "Test scenario name",
      "description": "What this scenario tests",
      "test_data": "Specific test inputs",
      "expected_improvements": "Expected quality improvements",
      "validation_approach": "How to measure success"
    }
  ],
  "automation_tests": [
    {
      "test_name": "Automated test name",
      "test_script": "Implementation of automated test",
      "validation_logic": "How the test determines success/failure",
      "integration": "How to integrate into testing pipeline"
    }
  ],
  "rollback_tests": [
    {
      "test_name": "Rollback test name", 
      "description": "Test that rollback works correctly",
      "rollback_procedure": "Steps to rollback changes",
      "validation": "How to verify rollback was successful"
    }
  ]
}
```

Create comprehensive testing that validates both technical implementation and quality improvement effectiveness."""
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "test_implementation",
            f"Created testing strategy for {len(improvements)} improvements",
            {"improvements": len(improvements)}
        )
        
        return result