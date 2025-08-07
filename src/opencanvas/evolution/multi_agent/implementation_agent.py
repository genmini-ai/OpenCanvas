"""
Implementation Agent - Specialized in actually applying improvements to the generation system
"""

import json
import logging
import re
from typing import Dict, Any, List
from pathlib import Path
from opencanvas.evolution.multi_agent.base_agent import BaseEvolutionAgent
from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts

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

        prompt = EvolutionPrompts.get_prompt(
            'IMPLEMENTATION_MAIN',
            iteration_number=iteration_number,
            tool_context=tool_context,
            improvements_json=json.dumps(improvements, indent=2),
            system_config_json=json.dumps(current_system_config, indent=2)
        )
        
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
        
        # Prepare quality issues from baseline scores
        quality_issues = {
            "visual_issues": [] if baseline_scores.get("visual", 0) >= 4 else ["Low visual quality scores"],
            "content_issues": [] if baseline_scores.get("content", 0) >= 4 else ["Low content quality scores"]
        }
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPLEMENTATION_PROMPT_ENHANCEMENTS',
            improvements_json=json.dumps(improvements, indent=2),
            quality_issues_json=json.dumps(quality_issues, indent=2),
            current_prompts_json=json.dumps(current_prompts, indent=2)
        )
        
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
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPLEMENTATION_VALIDATION_RULES',
            improvements_json=json.dumps(improvements, indent=2),
            quality_issues_json=json.dumps(quality_issues, indent=2)
        )
        
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
        
        prompt = EvolutionPrompts.get_prompt(
            'IMPLEMENTATION_TESTING_APPROACH',
            implementations_json=json.dumps(implementation_package, indent=2),
            improvements_json=json.dumps(improvements, indent=2)
        )
        
        result = self.call_claude(prompt)
        
        # Add to history
        self.add_to_history(
            "test_implementation",
            f"Created testing strategy for {len(improvements)} improvements",
            {"improvements": len(improvements)}
        )
        
        return result