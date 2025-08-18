"""
Adaptive Prompt Enhancer - Temperature-controlled prompt evolution
Uses exploration/exploitation strategy with temperature scheduling
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .prompt_parser import PromptParser

logger = logging.getLogger(__name__)

class AdaptivePromptEnhancer:
    """Generate prompt enhancements with temperature-based creativity control"""
    
    def __init__(self, iteration: int, max_iterations: int = 10, temperature_schedule: str = "adaptive"):
        """Initialize adaptive enhancer
        
        Args:
            iteration: Current iteration number (1-based)
            max_iterations: Total expected iterations
            temperature_schedule: "adaptive", "aggressive", "conservative", or "linear"
        """
        self.iteration = iteration
        self.max_iterations = max_iterations
        self.temperature_schedule = temperature_schedule
        self.temperature = self._calculate_temperature()
        self.parser = PromptParser()
        
        # Track enhancement attempts for learning
        self.enhancement_history = []
        
        logger.info(f"🌡️ AdaptivePromptEnhancer initialized: iteration {iteration}/{max_iterations}, temperature={self.temperature:.3f}")
    
    def _calculate_temperature(self) -> float:
        """Calculate temperature based on iteration progress and schedule"""
        
        # Ensure iteration is at least 1
        iteration = max(1, self.iteration)
        max_iter = max(1, self.max_iterations)
        
        # Calculate progress (0.0 to 1.0)
        progress = (iteration - 1) / max(max_iter - 1, 1)
        progress = max(0.0, min(1.0, progress))  # Clamp to [0, 1]
        
        if self.temperature_schedule == "aggressive":
            # Start very high, decrease slowly
            return 0.95 - (progress * 0.25)  # 0.95 -> 0.70
        
        elif self.temperature_schedule == "conservative":
            # Start moderate, decrease quickly
            return 0.6 - (progress * 0.4)  # 0.6 -> 0.2
        
        elif self.temperature_schedule == "linear":
            # Linear decrease
            return 0.8 - (progress * 0.6)  # 0.8 -> 0.2
            
        else:  # adaptive (default)
            # Adaptive schedule with three phases
            if progress < 0.3:  # Early stage - exploration
                # Exponential decay from high temp
                decay_factor = progress / 0.3  # 0 to 1 within first 30%
                return 0.9 - (decay_factor * 0.2)  # 0.9 -> 0.7
                
            elif progress < 0.7:  # Mid stage - balanced
                # Linear decay through middle range
                mid_progress = (progress - 0.3) / 0.4  # 0 to 1 within middle 40%
                return 0.7 - (mid_progress * 0.3)  # 0.7 -> 0.4
                
            else:  # Late stage - exploitation
                # Rapid decay to fine-tuning
                late_progress = (progress - 0.7) / 0.3  # 0 to 1 within last 30%
                return 0.4 - (late_progress * 0.25)  # 0.4 -> 0.15
    
    def get_creativity_level(self) -> str:
        """Get current creativity level description"""
        if self.temperature > 0.7:
            return "high"
        elif self.temperature > 0.4:
            return "medium"
        else:
            return "low"
    
    def generate_enhancement(self, gap: Dict[str, Any], current_prompt: str, 
                           prompt_registry = None) -> Dict[str, Any]:
        """Generate enhancement for a specific gap with temperature control
        
        Args:
            gap: Gap to address with enhancement
            current_prompt: Current prompt to enhance
            prompt_registry: Registry to check previous attempts
            
        Returns:
            Enhancement specification with temperature-appropriate creativity
        """
        
        try:
            # Parse current prompt structure
            parsed = self.parser.parse_prompt(current_prompt)
            
            if not parsed["format_valid"]:
                logger.warning(f"Current prompt has format issues: {parsed['format_errors']}")
                return self._create_failed_enhancement(gap, "Invalid format in current prompt")
            
            # Check registry for previous attempts
            similar_attempts = []
            if prompt_registry:
                try:
                    gap_description = gap.get("description", "")
                    similar_attempts = prompt_registry.check_similar_edits([gap_description])
                except Exception as e:
                    logger.debug(f"Could not check prompt registry: {e}")
            
            # Generate enhancement strategy based on temperature
            strategy = self._select_enhancement_strategy(gap, parsed, similar_attempts)
            
            # Generate actual enhancements using the strategy
            enhancements = self._generate_enhancements(strategy, parsed, gap)
            
            # Validate enhancements preserve structure
            validated_enhancements = self._validate_enhancements(enhancements, parsed)
            
            if not validated_enhancements:
                logger.warning(f"All enhancements failed validation for gap: {gap.get('gap_id', 'unknown')}")
                return self._create_failed_enhancement(gap, "Validation failed")
            
            enhancement_result = {
                "success": True,
                "gap_id": gap.get("gap_id"),
                "gap_type": gap.get("dimension", "unknown"),
                "temperature": self.temperature,
                "creativity_level": self.get_creativity_level(),
                "strategy": strategy,
                "enhancements": validated_enhancements,
                "preserved_elements": len(parsed["all_protected"]),
                "modification_zones": len(parsed["editable_sections"]),
                "timestamp": datetime.now().isoformat()
            }
            
            # Track this attempt
            self.enhancement_history.append(enhancement_result)
            
            return enhancement_result
            
        except Exception as e:
            logger.error(f"Failed to generate enhancement for gap {gap.get('gap_id', 'unknown')}: {e}")
            return self._create_failed_enhancement(gap, str(e))
    
    def _select_enhancement_strategy(self, gap: Dict, parsed: Dict, similar_attempts: List) -> Dict[str, Any]:
        """Select enhancement strategy based on temperature and context"""
        
        gap_type = gap.get("dimension", "unknown").lower()
        creativity = self.get_creativity_level()
        
        # Check if we should avoid certain approaches based on similar attempts
        avoid_patterns = []
        if similar_attempts:
            for attempt in similar_attempts.get("exact_matches", []):
                avoid_patterns.append(attempt.get("change", ""))
            for attempt in similar_attempts.get("pattern_warnings", []):
                avoid_patterns.append(attempt.get("pattern", ""))
        
        strategy = {
            "creativity_level": creativity,
            "gap_type": gap_type,
            "gap_description": gap.get("description", ""),
            "current_score": gap.get("current_score", 0),
            "target_score": gap.get("target_score", 5),
            "avoid_patterns": avoid_patterns,
            "enhancement_types": self._get_enhancement_types_for_temperature(creativity),
            "focus_areas": self._get_focus_areas(gap_type),
            "modification_intensity": self._get_modification_intensity(creativity)
        }
        
        return strategy
    
    def _get_enhancement_types_for_temperature(self, creativity: str) -> List[str]:
        """Get appropriate enhancement types for current temperature"""
        
        if creativity == "high":
            return [
                "structural_addition",  # Add new sections/requirements
                "protocol_insertion",  # Insert verification protocols
                "constraint_amplification",  # Strengthen existing constraints
                "instruction_expansion",  # Expand instruction detail
                "validation_injection"  # Add self-validation steps
            ]
        
        elif creativity == "medium":
            return [
                "targeted_replacement",  # Replace specific words/phrases
                "emphasis_modification",  # Change emphasis (should -> MUST)
                "constraint_strengthening",  # Moderate constraint changes
                "instruction_clarification",  # Clarify existing instructions
                "format_improvement"  # Improve formatting/structure
            ]
        
        else:  # low creativity
            return [
                "precision_tuning",  # Fine word choice adjustments
                "emphasis_adjustment",  # Minor emphasis changes
                "constraint_refinement",  # Small constraint tweaks
                "clarity_improvement",  # Minor clarity enhancements
                "formatting_polish"  # Small formatting improvements
            ]
    
    def _get_focus_areas(self, gap_type: str) -> List[str]:
        """Get focus areas based on gap type"""
        
        focus_map = {
            "accuracy": [
                "source_adherence",
                "fact_verification", 
                "citation_requirements",
                "creative_addition_prevention",
                "reference_validation"
            ],
            "content": [
                "coverage_completeness",
                "detail_extraction",
                "example_inclusion",
                "supporting_evidence",
                "systematic_processing"
            ],
            "visual": [
                "design_consistency",
                "hierarchy_clarity",
                "readability_optimization",
                "visual_balance",
                "formatting_precision"
            ],
            "overall": [
                "quality_assurance",
                "systematic_improvement",
                "multi_dimensional_optimization",
                "coherence_enhancement",
                "excellence_targeting"
            ]
        }
        
        return focus_map.get(gap_type, focus_map["overall"])
    
    def _get_modification_intensity(self, creativity: str) -> str:
        """Get modification intensity level"""
        intensity_map = {
            "high": "aggressive",
            "medium": "moderate", 
            "low": "conservative"
        }
        return intensity_map.get(creativity, "moderate")
    
    def _generate_enhancements(self, strategy: Dict, parsed: Dict, gap: Dict) -> List[Dict]:
        """Generate actual prompt enhancements based on strategy"""
        
        enhancements = []
        enhancement_types = strategy["enhancement_types"]
        focus_areas = strategy["focus_areas"]
        intensity = strategy["modification_intensity"]
        
        # Get safe modification zones
        safe_zones = self.parser.get_safe_modification_zones(parsed)
        
        if not safe_zones:
            logger.warning("No safe modification zones found")
            return enhancements
        
        # Generate enhancements for each type
        for enhancement_type in enhancement_types[:3]:  # Limit to top 3 types
            try:
                enhancement = self._create_specific_enhancement(
                    enhancement_type, focus_areas, intensity, safe_zones, gap, parsed
                )
                if enhancement:
                    enhancements.append(enhancement)
            except Exception as e:
                logger.debug(f"Failed to create {enhancement_type} enhancement: {e}")
        
        return enhancements
    
    def _create_specific_enhancement(self, enhancement_type: str, focus_areas: List[str], 
                                   intensity: str, safe_zones: List[Dict], gap: Dict, 
                                   parsed: Dict) -> Optional[Dict]:
        """Create a specific type of enhancement"""
        
        gap_type = gap.get("dimension", "unknown").lower()
        
        if enhancement_type == "structural_addition" and intensity == "aggressive":
            return self._create_structural_addition(gap_type, focus_areas, safe_zones)
        
        elif enhancement_type == "targeted_replacement" and intensity in ["aggressive", "moderate"]:
            return self._create_targeted_replacement(gap_type, focus_areas, safe_zones, parsed)
        
        elif enhancement_type == "precision_tuning" and intensity == "conservative":
            return self._create_precision_tuning(gap_type, focus_areas, safe_zones, parsed)
        
        elif enhancement_type == "constraint_amplification":
            return self._create_constraint_amplification(gap_type, intensity, safe_zones)
        
        elif enhancement_type == "validation_injection":
            return self._create_validation_injection(gap_type, intensity, safe_zones)
        
        # Add more enhancement types as needed
        return None
    
    def _create_structural_addition(self, gap_type: str, focus_areas: List[str], safe_zones: List[Dict]) -> Dict:
        """Create structural addition enhancement"""
        
        if gap_type == "accuracy":
            additions = [
                "\n\n## STRICT SOURCE VERIFICATION PROTOCOL:",
                "1. EVERY factual claim must reference the source explicitly",
                "2. Mark any inference or interpretation with [INFERRED]",
                "3. Include source line/section references where possible",
                "4. Flag uncertainty with confidence levels: [HIGH|MEDIUM|LOW]",
                "5. Self-audit: List any unsupported claims at the end"
            ]
        elif gap_type == "content":
            additions = [
                "\n\n## COMPREHENSIVE COVERAGE CHECKLIST:",
                "□ All main concepts from source included",
                "□ Supporting examples and data preserved", 
                "□ Key relationships between ideas mapped",
                "□ Important terminology defined",
                "□ Statistical/quantitative information transferred",
                "□ Completeness verification: Re-read source after generation"
            ]
        else:
            additions = [
                "\n\n## ENHANCED QUALITY REQUIREMENTS:",
                "- Systematic approach to excellence",
                "- Multi-pass quality verification", 
                "- Consistency checks across all elements",
                "- Performance optimization for target metrics"
            ]
        
        # Find best position to add (end of first safe zone or end of prompt)
        position = len(safe_zones[0]["content"]) if safe_zones else 0
        
        return {
            "type": "structural_addition",
            "content": "\n".join(additions),
            "position": position,
            "justification": f"Adding verification protocol for {gap_type} gap improvement"
        }
    
    def _create_targeted_replacement(self, gap_type: str, focus_areas: List[str], 
                                   safe_zones: List[Dict], parsed: Dict) -> Optional[Dict]:
        """Create targeted replacement enhancement"""
        
        # Find common weak phrases to strengthen
        replacements = []
        
        if gap_type == "accuracy":
            replacements = [
                ("generate", "generate with strict source adherence"),
                ("include", "include ONLY from source material"),
                ("create", "create based exclusively on provided content"),
                ("comprehensive", "source-faithful comprehensive"),
                ("should", "MUST"),
                ("try to", "")
            ]
        elif gap_type == "content":
            replacements = [
                ("key points", "ALL key points with supporting details"),
                ("important", "essential and comprehensive"),
                ("include", "systematically include"),
                ("cover", "exhaustively cover"),
                ("mention", "thoroughly explain")
            ]
        else:
            replacements = [
                ("good", "excellent"),
                ("appropriate", "optimal"),
                ("should", "must"),
                ("try", "ensure")
            ]
        
        # Find the first applicable replacement in safe zones
        for find_text, replace_text in replacements:
            for zone in safe_zones:
                if find_text in zone["content"]:
                    return {
                        "type": "targeted_replacement",
                        "find": find_text,
                        "replace": replace_text,
                        "zone_id": zone["zone_id"],
                        "justification": f"Strengthening language for {gap_type} improvement"
                    }
        
        return None
    
    def _create_precision_tuning(self, gap_type: str, focus_areas: List[str], 
                               safe_zones: List[Dict], parsed: Dict) -> Optional[Dict]:
        """Create precision tuning enhancement"""
        
        # Conservative word-level adjustments
        precision_adjustments = [
            ("approximately", "exactly"),
            ("generally", "specifically"), 
            ("often", "consistently"),
            ("usually", "always"),
            ("might", "will"),
            ("could", "should"),
            ("may", "must")
        ]
        
        for find_text, replace_text in precision_adjustments:
            for zone in safe_zones:
                if find_text in zone["content"]:
                    return {
                        "type": "precision_tuning",
                        "find": find_text,
                        "replace": replace_text,
                        "zone_id": zone["zone_id"],
                        "justification": f"Precision improvement for {gap_type}"
                    }
        
        return None
    
    def _create_constraint_amplification(self, gap_type: str, intensity: str, safe_zones: List[Dict]) -> Dict:
        """Create constraint amplification enhancement"""
        
        if intensity == "aggressive":
            constraint_text = f"\n\nCRITICAL {gap_type.upper()} CONSTRAINT: This requirement is NON-NEGOTIABLE and must be verified before output."
        elif intensity == "moderate":
            constraint_text = f"\n\nIMPORTANT: {gap_type.title()} requirements must be carefully verified."
        else:
            constraint_text = f"\n\nNote: Pay special attention to {gap_type} requirements."
        
        position = len(safe_zones[0]["content"]) if safe_zones else 0
        
        return {
            "type": "constraint_amplification",
            "content": constraint_text,
            "position": position,
            "justification": f"Amplifying {gap_type} constraints at {intensity} intensity"
        }
    
    def _create_validation_injection(self, gap_type: str, intensity: str, safe_zones: List[Dict]) -> Dict:
        """Create validation injection enhancement"""
        
        if intensity == "aggressive":
            validation_text = f"\n\n## MANDATORY {gap_type.upper()} VALIDATION:\nBefore finalizing output, verify: [List specific {gap_type} criteria and check each one]"
        elif intensity == "moderate":
            validation_text = f"\n\n## {gap_type.title()} Validation:\nPlease verify {gap_type} requirements are met before output."
        else:
            validation_text = f"\n\nValidation note: Review {gap_type} quality before completion."
        
        position = len(safe_zones[0]["content"]) if safe_zones else 0
        
        return {
            "type": "validation_injection",
            "content": validation_text,
            "position": position,
            "justification": f"Adding {gap_type} validation at {intensity} level"
        }
    
    def _validate_enhancements(self, enhancements: List[Dict], parsed: Dict) -> List[Dict]:
        """Validate that enhancements preserve prompt structure"""
        
        validated = []
        
        for enhancement in enhancements:
            try:
                # Create a test modification list
                test_modifications = [enhancement]
                
                # Try to reconstruct with this enhancement
                reconstructed = self.parser.reconstruct_prompt(parsed, test_modifications)
                
                # Validate the reconstructed prompt
                validation_result = self.parser.parse_prompt(reconstructed)
                
                if validation_result["format_valid"]:
                    enhancement["validated"] = True
                    enhancement["reconstructed_preview"] = reconstructed[:200] + "..." if len(reconstructed) > 200 else reconstructed
                    validated.append(enhancement)
                else:
                    logger.warning(f"Enhancement validation failed: {validation_result['format_errors']}")
                    
            except Exception as e:
                logger.warning(f"Enhancement validation error: {e}")
        
        return validated
    
    def _create_failed_enhancement(self, gap: Dict, error_reason: str) -> Dict[str, Any]:
        """Create a failed enhancement result"""
        return {
            "success": False,
            "gap_id": gap.get("gap_id"),
            "error": error_reason,
            "temperature": self.temperature,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """Get summary of enhancement attempts"""
        
        successful = [e for e in self.enhancement_history if e.get("success")]
        failed = [e for e in self.enhancement_history if not e.get("success")]
        
        return {
            "total_attempts": len(self.enhancement_history),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / max(len(self.enhancement_history), 1),
            "current_temperature": self.temperature,
            "creativity_level": self.get_creativity_level(),
            "iteration": self.iteration
        }
    
    def get_creativity_level(self) -> str:
        """Get human-readable creativity level"""
        if self.temperature >= 0.7:
            return "high"
        elif self.temperature >= 0.4:
            return "medium"
        else:
            return "low"