"""
Prompt Parser - Structure preservation during prompt evolution
Identifies and protects critical elements to ensure prompt functionality
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class PromptParser:
    """Parse and preserve prompt structure during evolution"""
    
    # Note: Variable protection is now handled by LLM instructions
    # instead of complex parsing. The LLM is instructed to preserve
    # all {variables} and <tags> when evolving prompts.
    
    # Structural markers that define prompt sections
    STRUCTURE_MARKERS = [
        "## Requirements:",
        "## Output Format:",
        "## Quality Standards:",
        "## Constraints:",
        "## Analysis Requirements:",
        "## Implementation Requirements:",
        "## Enhancement Requirements:",
        "## Planning Requirements:",
        "IMPORTANT:",
        "NOTE:",
        "WARNING:",
        "CRITICAL:",
        "You MUST respond with ONLY a valid JSON object",
        "Return EXACTLY this JSON structure:",
        "Return a JSON object with",
        "Focus on",
        "CRITICAL INSTRUCTION:",
        "CRITICAL: JSON OUTPUT REQUIRED"
    ]
    
    # Format string patterns (both old and new style)
    FORMAT_PATTERNS = [
        r'\{[^}]+\}',  # {variable} style
        r'\{\{[^}]+\}\}',  # {{variable}} style for nested
        r'%\([^)]+\)s'  # %(variable)s style
    ]
    
    def __init__(self):
        """Initialize the prompt parser"""
        self.logger = logger
    
    def parse_prompt(self, prompt_text: str) -> Dict[str, Any]:
        """Simple prompt validation - most logic moved to LLM instructions
        
        Args:
            prompt_text: The prompt to parse
            
        Returns:
            Dict containing basic prompt info for validation
        """
        if not prompt_text:
            return self._empty_parse_result()
        
        try:
            # Simple validation - just check if it's a valid string
            variables = re.findall(r'\{[^}]+\}', prompt_text)
            xml_tags = re.findall(r'<[^>]+>', prompt_text)
            
            result = {
                "original_prompt": prompt_text,
                "variables_found": variables,
                "xml_tags_found": xml_tags,
                "format_valid": True,
                "format_errors": [],
                "ready_for_evolution": True
            }
            
            self.logger.debug(f"Parsed prompt: {len(variables)} variables, {len(xml_tags)} XML tags")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to parse prompt: {e}")
            return self._empty_parse_result()
    
    def _extract_variables(self, text: str) -> List[Dict]:
        """Extract variable placeholders that must be preserved"""
        variables = []
        
        for pattern in self.PROTECTED_VARIABLES:
            for match in re.finditer(pattern, text):
                variables.append({
                    "type": "variable",
                    "content": match.group(),
                    "position": match.span(),
                    "pattern": pattern
                })
        
        # Also find any other format variables we might have missed
        for pattern in self.FORMAT_PATTERNS:
            for match in re.finditer(pattern, text):
                content = match.group()
                # Only add if not already captured
                if not any(var["content"] == content for var in variables):
                    variables.append({
                        "type": "format_variable", 
                        "content": content,
                        "position": match.span(),
                        "pattern": pattern
                    })
        
        return sorted(variables, key=lambda x: x["position"][0])
    
    def _extract_structures(self, text: str) -> List[Dict]:
        """Extract structural markers that should be preserved"""
        structures = []
        
        for marker in self.STRUCTURE_MARKERS:
            # Use case-insensitive search for some markers
            if marker.upper() in ["IMPORTANT:", "NOTE:", "WARNING:", "CRITICAL:"]:
                pattern = re.compile(re.escape(marker), re.IGNORECASE)
                for match in pattern.finditer(text):
                    structures.append({
                        "type": "structure",
                        "content": match.group(),
                        "position": match.span(),
                        "marker_type": marker.lower().replace(":", "")
                    })
            else:
                # Exact match for specific structural elements
                if marker in text:
                    idx = text.find(marker)
                    structures.append({
                        "type": "structure",
                        "content": marker,
                        "position": (idx, idx + len(marker)),
                        "marker_type": "section_header"
                    })
        
        return sorted(structures, key=lambda x: x["position"][0])
    
    def _extract_format_strings(self, text: str) -> List[Dict]:
        """Extract format string patterns"""
        formats = []
        
        for pattern in self.FORMAT_PATTERNS:
            for match in re.finditer(pattern, text):
                content = match.group()
                formats.append({
                    "type": "format_string",
                    "content": content, 
                    "position": match.span(),
                    "pattern": pattern
                })
        
        return sorted(formats, key=lambda x: x["position"][0])
    
    def _identify_editable_sections(self, text: str, protected_elements: List[Dict]) -> List[Dict]:
        """Identify sections that can be safely edited"""
        editable = []
        
        if not protected_elements:
            # Entire text is editable if no protected elements
            return [{
                "type": "editable",
                "content": text,
                "position": (0, len(text)),
                "safe_to_edit": True
            }]
        
        # Sort protected elements by position
        protected_sorted = sorted(protected_elements, key=lambda x: x["position"][0])
        
        # Find gaps between protected elements
        current_pos = 0
        
        for protected in protected_sorted:
            start_pos = protected["position"][0]
            
            # Add editable section before this protected element
            if current_pos < start_pos:
                section_content = text[current_pos:start_pos]
                if section_content.strip():  # Only add non-empty sections
                    editable.append({
                        "type": "editable",
                        "content": section_content,
                        "position": (current_pos, start_pos),
                        "safe_to_edit": True
                    })
            
            current_pos = protected["position"][1]
        
        # Add final editable section after last protected element
        if current_pos < len(text):
            section_content = text[current_pos:]
            if section_content.strip():
                editable.append({
                    "type": "editable",
                    "content": section_content,
                    "position": (current_pos, len(text)),
                    "safe_to_edit": True
                })
        
        return editable
    
    def _create_structure_map(self, text: str) -> Dict[str, Any]:
        """Create a map of the prompt structure for reconstruction"""
        lines = text.split('\n')
        
        return {
            "total_lines": len(lines),
            "total_chars": len(text),
            "has_json_requirements": "JSON object" in text,
            "has_format_requirements": "format" in text.lower(),
            "has_constraints": any(marker in text for marker in ["IMPORTANT:", "CRITICAL:", "WARNING:"]),
            "line_structure": [
                {
                    "line_num": i,
                    "content": line,
                    "is_header": line.strip().startswith("##"),
                    "is_constraint": any(marker in line for marker in ["IMPORTANT:", "CRITICAL:", "WARNING:"]),
                    "has_variables": bool(re.search(r'\{[^}]+\}', line))
                }
                for i, line in enumerate(lines)
            ]
        }
    
    def _validate_format_strings(self, text: str) -> Tuple[bool, List[str]]:
        """Validate that format strings are syntactically correct"""
        errors = []
        
        try:
            # Create dummy values for common variables
            test_values = {
                'topic': 'test_topic',
                'purpose': 'test_purpose', 
                'theme': 'test_theme',
                'source_content': 'test_content',
                'pdf_content': 'test_pdf',
                'evaluation_json': '{}',
                'topics_str': 'test_topics',
                'registry_context': 'test_context',
                'reflection_json': '{}',
                'baseline_json': '{}',
                'iteration_number': 1,
                'improvements_json': '{}',
                'config_json': '{}',
                'evaluations_json': '{}',
                'current_state_json': '{}',
                'system_state_json': '{}',
                'enhancement': 'test_enhancement',
                'content': 'test_content'
            }
            
            # Try to format the string
            text.format(**test_values)
            return True, []
            
        except KeyError as e:
            errors.append(f"Missing variable: {e}")
        except ValueError as e:
            errors.append(f"Format error: {e}")
        except Exception as e:
            errors.append(f"Unknown format error: {e}")
        
        return len(errors) == 0, errors
    
    def _empty_parse_result(self) -> Dict[str, Any]:
        """Return empty parse result structure"""
        return {
            "original_prompt": "",
            "variables_found": [],
            "xml_tags_found": [],
            "format_valid": False,
            "format_errors": ["Empty or invalid prompt"],
            "ready_for_evolution": False
        }
    
    def reconstruct_prompt(self, parsed: Dict[str, Any], modifications: List[Dict]) -> str:
        """Reconstruct prompt with modifications while preserving structure
        
        Args:
            parsed: Result from parse_prompt()
            modifications: List of modifications to apply
            
        Returns:
            Modified prompt with structure preserved
        """
        if not parsed.get("original_prompt"):
            return ""
        
        try:
            # Start with original prompt
            result = parsed["original_prompt"]
            
            # Apply modifications in reverse position order to preserve indices
            modifications_sorted = sorted(modifications, key=lambda x: x.get("position", (0, 0))[0], reverse=True)
            
            for mod in modifications_sorted:
                if mod.get("type") == "replacement" and "position" in mod:
                    start, end = mod["position"]
                    new_content = mod.get("new_content", "")
                    
                    # Verify we're not modifying protected content
                    if self._is_position_safe(start, end, parsed["all_protected"]):
                        result = result[:start] + new_content + result[end:]
                    else:
                        self.logger.warning(f"Skipped unsafe modification at position {start}-{end}")
                
                elif mod.get("type") == "addition":
                    position = mod.get("position", len(result))
                    new_content = mod.get("content", "")
                    
                    if isinstance(position, int):
                        result = result[:position] + new_content + result[position:]
                    
                elif mod.get("type") == "find_replace":
                    find_text = mod.get("find", "")
                    replace_text = mod.get("replace", "")
                    
                    if find_text:  # Simplified - no complex protection check
                        result = result.replace(find_text, replace_text)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reconstruct prompt: {e}")
            return parsed["original_prompt"]
    
    def _is_position_safe(self, start: int, end: int, protected_elements: List[Dict]) -> bool:
        """Check if a position range is safe to modify"""
        for element in protected_elements:
            element_start, element_end = element["position"]
            
            # Check for overlap
            if not (end <= element_start or start >= element_end):
                return False
        
        return True
    
    def _is_safe_to_replace(self, find_text: str, protected_elements: List[Dict]) -> bool:
        """Check if text is safe to replace (not in protected elements)"""
        for element in protected_elements:
            if find_text in element["content"]:
                return False
        return True
    
    def get_safe_modification_zones(self, parsed: Dict[str, Any]) -> List[Dict]:
        """Get zones where modifications are safe to make"""
        return [
            {
                "zone_id": i,
                "content": section["content"],
                "position": section["position"],
                "length": section["position"][1] - section["position"][0],
                "modification_types": ["addition", "replacement", "find_replace"]
            }
            for i, section in enumerate(parsed["editable_sections"])
        ]
    
    def validate_evolved_prompt(self, original_prompt: str, evolved_prompt: str) -> Dict[str, Any]:
        """Validate that evolved prompt preserves critical variables only
        
        Args:
            original_prompt: The original prompt
            evolved_prompt: The evolved prompt from LLM
            
        Returns:
            Dict with validation results
        """
        try:
            # Get variables from both prompts
            orig_vars = set(re.findall(r'\{[^}]+\}', original_prompt))
            evolved_vars = set(re.findall(r'\{[^}]+\}', evolved_prompt))
            
            # Only check critical variables needed for template substitution
            critical_vars = {'{blog_content}', '{purpose}', '{theme}'}
            missing_critical = critical_vars - evolved_vars
            
            # Check if all critical elements are preserved (tags can evolve freely)
            missing_vars = orig_vars - evolved_vars
            
            # Validation passes if critical variables are present
            is_valid = len(missing_critical) == 0
            
            validation_result = {
                "is_valid": is_valid,
                "missing_variables": list(missing_vars),
                "missing_critical_variables": list(missing_critical),
                "variables_preserved": len(missing_vars) == 0,
                "critical_variables_preserved": len(missing_critical) == 0,
                "evolved_prompt": evolved_prompt,  # Always use evolved prompt
                "fallback_used": False  # Never use fallback - let evolution happen
            }
            
            if not is_valid:
                self.logger.warning(f"Evolved prompt validation failed:")
                if missing_critical:
                    self.logger.warning(f"  Missing critical variables: {missing_critical}")
                if missing_vars:
                    self.logger.info(f"  Other missing variables (non-critical): {missing_vars}")
                self.logger.warning("  Proceeding with evolved prompt anyway to allow evolution")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Failed to validate evolved prompt: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "evolved_prompt": original_prompt,
                "fallback_used": True
            }