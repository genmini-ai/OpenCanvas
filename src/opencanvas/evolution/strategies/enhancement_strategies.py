"""
Prompt Enhancement Strategies Library - Temperature-adaptive enhancement patterns
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import random

logger = logging.getLogger(__name__)

class PromptEnhancementStrategies:
    """Temperature-adaptive enhancement strategies library"""
    
    @staticmethod
    def get_strategy(gap_type: str, temperature: float, previous_attempts: List[str] = None) -> Dict[str, Any]:
        """Get enhancement strategy based on gap type and temperature"""
        
        previous_attempts = previous_attempts or []
        
        if temperature >= 0.7:
            return PromptEnhancementStrategies._get_exploration_strategy(gap_type, previous_attempts)
        elif temperature >= 0.4:
            return PromptEnhancementStrategies._get_balanced_strategy(gap_type, previous_attempts)
        else:
            return PromptEnhancementStrategies._get_exploitation_strategy(gap_type, previous_attempts)
    
    @staticmethod
    def _get_exploration_strategy(gap_type: str, previous_attempts: List[str]) -> Dict[str, Any]:
        """High-temperature exploration strategies"""
        
        strategies = {
            "accuracy": [
                {
                    "name": "comprehensive_source_verification",
                    "approach": "protocol_addition",
                    "content": [
                        "\n## COMPREHENSIVE SOURCE VERIFICATION PROTOCOL:",
                        "BEFORE generating each slide:",
                        "1. Re-read the specific source section being used",
                        "2. Extract ONLY factual statements from source",
                        "3. Mark each claim with [SOURCE LINE: X] reference",
                        "4. Flag any interpretations with [INTERPRETATION] tag",
                        "",
                        "DURING generation:",
                        "- Quote source material directly when possible",
                        "- Use source terminology exactly as written",
                        "- Preserve numerical values and statistics precisely",
                        "",
                        "AFTER each slide:",
                        "- Review against source for accuracy",
                        "- List any creative additions made",
                        "- Score accuracy confidence: [HIGH|MEDIUM|LOW]"
                    ]
                },
                {
                    "name": "fact_checking_framework",
                    "approach": "validation_layer",
                    "content": [
                        "\n## MULTI-LAYER FACT CHECKING FRAMEWORK:",
                        "Layer 1 - Source Alignment Check:",
                        "□ Every claim traceable to source material",
                        "□ No contradictions with source information",
                        "□ Numerical data matches source exactly",
                        "",
                        "Layer 2 - Completeness Verification:",
                        "□ All key facts from source included",
                        "□ Context preserved for all statements",
                        "□ Relationships between facts maintained",
                        "",
                        "Layer 3 - Creative Addition Audit:",
                        "□ Mark all non-source content as [ADDED]",
                        "□ Justify necessity of additions",
                        "□ Ensure additions don't contradict source"
                    ]
                },
                {
                    "name": "source_quotation_system",
                    "approach": "direct_citation",
                    "content": [
                        "\n## DIRECT SOURCE QUOTATION SYSTEM:",
                        "For HIGH ACCURACY (target: 4.8+/5.0):",
                        "- Use [QUOTE: \"exact text\"] for key statements",
                        "- Paraphrase minimally: [PARAPHRASE: original → rephrased]",
                        "- Include source confidence tags: [CERTAIN|LIKELY|UNCLEAR]",
                        "- End each slide with accuracy self-assessment",
                        "",
                        "Strict Rules:",
                        "• NEVER add statistics not in source",
                        "• NEVER combine facts from different contexts",
                        "• NEVER use superlatives not in source",
                        "• ALWAYS preserve source terminology"
                    ]
                }
            ],
            
            "coverage": [
                {
                    "name": "exhaustive_content_mining",
                    "approach": "systematic_extraction",
                    "content": [
                        "\n## EXHAUSTIVE CONTENT MINING PROTOCOL:",
                        "Phase 1 - Complete Source Mapping:",
                        "1. List ALL main topics mentioned in source",
                        "2. Identify ALL subtopics and supporting details",
                        "3. Extract ALL examples, case studies, statistics",
                        "4. Note ALL terminology and definitions",
                        "",
                        "Phase 2 - Systematic Inclusion:",
                        "□ Primary concepts: 100% coverage required",
                        "□ Supporting details: Include ALL relevant examples",
                        "□ Quantitative data: Preserve ALL numbers/percentages",
                        "□ Qualitative insights: Include ALL key observations",
                        "",
                        "Phase 3 - Completeness Verification:",
                        "- Cross-reference each slide against source sections",
                        "- Ensure NO essential information omitted",
                        "- Verify proper context for all included information"
                    ]
                },
                {
                    "name": "comprehensive_detail_framework",
                    "approach": "detail_extraction",
                    "content": [
                        "\n## COMPREHENSIVE DETAIL EXTRACTION FRAMEWORK:",
                        "Level 1 - Core Information (MUST INCLUDE):",
                        "• Main arguments and conclusions",
                        "• Key findings and results", 
                        "• Essential definitions and concepts",
                        "• Critical statistics and data points",
                        "",
                        "Level 2 - Supporting Information (SHOULD INCLUDE):",
                        "• Examples and case studies",
                        "• Background context and rationale",
                        "• Methodology and approach details",
                        "• Comparative information and contrasts",
                        "",
                        "Level 3 - Enhancement Information (MAY INCLUDE):",
                        "• Additional context for clarity",
                        "• Relevant implications and connections",
                        "• Complementary supporting details",
                        "",
                        "COVERAGE TARGET: Include 95%+ of Level 1, 80%+ of Level 2"
                    ]
                }
            ],
            
            "visual": [
                {
                    "name": "advanced_visual_excellence",
                    "approach": "comprehensive_design",
                    "content": [
                        "\n## ADVANCED VISUAL EXCELLENCE FRAMEWORK:",
                        "Design Hierarchy Requirements:",
                        "1. Title slides: Bold, prominent, memorable design",
                        "2. Content slides: Clear information hierarchy",
                        "3. Data slides: Professional charts with clear labels",
                        "4. Summary slides: Visual impact with key takeaways",
                        "",
                        "Visual Consistency Standards:",
                        "• Color palette: Maintain consistent theme throughout",
                        "• Typography: Professional fonts, consistent sizing",
                        "• Layout: Balanced white space, aligned elements",
                        "• Graphics: High-quality, purposeful imagery",
                        "",
                        "Quality Checkpoints:",
                        "□ Every slide passes professional appearance test",
                        "□ Information is scannable at a glance",
                        "□ Visual elements enhance rather than distract",
                        "□ Overall aesthetic is conference-presentation ready"
                    ]
                }
            ],
            
            "quality": [
                {
                    "name": "multi_dimensional_excellence", 
                    "approach": "holistic_quality",
                    "content": [
                        "\n## MULTI-DIMENSIONAL EXCELLENCE PROTOCOL:",
                        "Dimension 1 - Content Excellence:",
                        "• Logical flow and clear narrative structure",
                        "• Comprehensive coverage of all essential topics", 
                        "• Accurate representation of source material",
                        "• Engaging and accessible presentation style",
                        "",
                        "Dimension 2 - Visual Excellence:",
                        "• Professional design meeting conference standards",
                        "• Clear information hierarchy and readability",
                        "• Effective use of visual elements and styling",
                        "• Consistent and polished appearance",
                        "",
                        "Dimension 3 - Technical Excellence:",
                        "• Proper HTML structure and valid formatting",
                        "• Responsive design elements",
                        "• Clean, semantic markup",
                        "• Error-free rendering",
                        "",
                        "QUALITY TARGET: 4.8+/5.0 in all dimensions",
                        "VALIDATION: Each slide must pass multi-dimensional review"
                    ]
                }
            ]
        }
        
        # Get strategies for gap type
        gap_strategies = strategies.get(gap_type, strategies["quality"])
        
        # Filter out previously attempted strategies
        available_strategies = []
        for strategy in gap_strategies:
            strategy_name = strategy["name"]
            if not any(attempt.lower() in strategy_name.lower() for attempt in previous_attempts):
                available_strategies.append(strategy)
        
        # If no strategies available, return the first one with modifications
        if not available_strategies:
            logger.warning(f"All exploration strategies attempted for {gap_type}, using modified version")
            base_strategy = gap_strategies[0].copy()
            base_strategy["name"] = f"modified_{base_strategy['name']}"
            return base_strategy
        
        # Return a random strategy for exploration
        return random.choice(available_strategies)
    
    @staticmethod
    def _get_balanced_strategy(gap_type: str, previous_attempts: List[str]) -> Dict[str, Any]:
        """Medium-temperature balanced strategies"""
        
        strategies = {
            "accuracy": {
                "name": "targeted_accuracy_enhancement",
                "approach": "selective_modification",
                "modifications": [
                    ("Generate", "Generate with strict source adherence"),
                    ("comprehensive", "comprehensive and source-verified"),
                    ("include", "include and verify against source"),
                    ("accurate", "precisely accurate to source material"),
                    ("information", "source-authenticated information"),
                    ("content", "source-validated content"),
                    ("ensure", "rigorously ensure")
                ]
            },
            
            "coverage": {
                "name": "systematic_coverage_improvement",
                "approach": "selective_modification", 
                "modifications": [
                    ("key points", "ALL key points with comprehensive details"),
                    ("main concepts", "main concepts with supporting information"),
                    ("include", "systematically include and elaborate"),
                    ("cover", "thoroughly cover with full context"),
                    ("essential", "ALL essential information"),
                    ("important", "ALL important details and examples"),
                    ("comprehensive", "exhaustively comprehensive")
                ]
            },
            
            "visual": {
                "name": "professional_visual_enhancement",
                "approach": "selective_modification",
                "modifications": [
                    ("professional", "exceptionally professional and polished"),
                    ("clear", "crystal clear with excellent readability"),
                    ("consistent", "perfectly consistent throughout"),
                    ("design", "award-worthy design quality"),
                    ("layout", "expertly balanced layout"),
                    ("visual", "visually stunning and effective"),
                    ("formatting", "flawless formatting")
                ]
            },
            
            "quality": {
                "name": "comprehensive_quality_boost",
                "approach": "selective_modification",
                "modifications": [
                    ("high-quality", "exceptional quality meeting conference standards"),
                    ("ensure", "meticulously ensure"),
                    ("excellent", "truly outstanding"),
                    ("effective", "highly effective and impactful"),
                    ("engaging", "deeply engaging and memorable"),
                    ("well-structured", "expertly structured"),
                    ("quality", "premium quality")
                ]
            }
        }
        
        return strategies.get(gap_type, strategies["quality"])
    
    @staticmethod
    def _get_exploitation_strategy(gap_type: str, previous_attempts: List[str]) -> Dict[str, Any]:
        """Low-temperature exploitation strategies (fine-tuning)"""
        
        strategies = {
            "accuracy": {
                "name": "precision_accuracy_tuning",
                "approach": "word_level_refinement",
                "tweaks": [
                    ("must", "MUST"),
                    ("should", "must"),
                    ("approximately", "exactly"),
                    ("ensure", "strictly ensure"),
                    ("accurate", "perfectly accurate"),
                    ("verify", "rigorously verify"),
                    ("check", "carefully validate"),
                    ("include", "precisely include"),
                    ("based on", "directly from"),
                    ("according to", "exactly as stated in")
                ]
            },
            
            "coverage": {
                "name": "completeness_fine_tuning",
                "approach": "word_level_refinement",
                "tweaks": [
                    ("include", "thoroughly include"),
                    ("cover", "comprehensively cover"),
                    ("mention", "detail extensively"),
                    ("describe", "fully describe"),
                    ("explain", "completely explain"),
                    ("discuss", "thoroughly discuss"),
                    ("address", "comprehensively address"),
                    ("complete", "exhaustively complete"),
                    ("all", "ALL"),
                    ("every", "EVERY")
                ]
            },
            
            "visual": {
                "name": "visual_polish_refinement",
                "approach": "word_level_refinement",
                "tweaks": [
                    ("professional", "highly professional"),
                    ("clean", "exceptionally clean"),
                    ("clear", "crystal clear"),
                    ("consistent", "perfectly consistent"),
                    ("attractive", "visually striking"),
                    ("effective", "highly effective"),
                    ("good", "excellent"),
                    ("nice", "outstanding"),
                    ("well", "exceptionally well")
                ]
            },
            
            "quality": {
                "name": "overall_quality_refinement",
                "approach": "word_level_refinement", 
                "tweaks": [
                    ("quality", "exceptional quality"),
                    ("good", "excellent"),
                    ("well", "exceptionally well"),
                    ("effective", "highly effective"),
                    ("engaging", "deeply engaging"),
                    ("clear", "crystal clear"),
                    ("comprehensive", "thoroughly comprehensive"),
                    ("structured", "expertly structured"),
                    ("organized", "meticulously organized"),
                    ("polished", "professionally polished")
                ]
            }
        }
        
        return strategies.get(gap_type, strategies["quality"])
    
    @staticmethod
    def get_fallback_strategy(gap_type: str, all_previous_attempts: List[str]) -> Dict[str, Any]:
        """Get fallback strategy when all standard approaches have been tried"""
        
        fallback_strategies = {
            "accuracy": {
                "name": "creative_accuracy_approach",
                "approach": "novel_technique",
                "content": [
                    "\n## CREATIVE ACCURACY ENHANCEMENT:",
                    "Novel Approach - Source Dialogue Method:",
                    "1. Before writing, ask: 'What would the source author say?'",
                    "2. Write each claim as if quoting the source directly",
                    "3. Use source author's perspective and terminology",
                    "4. Imagine presenting to the source author for approval",
                    "",
                    "Quality Gate: Would the original source author approve this slide?"
                ]
            },
            
            "coverage": {
                "name": "creative_coverage_approach",
                "approach": "novel_technique", 
                "content": [
                    "\n## CREATIVE COVERAGE ENHANCEMENT:",
                    "Novel Approach - Completeness Visualization:",
                    "1. Mentally map ALL source sections as puzzle pieces",
                    "2. Ensure each 'piece' appears somewhere in presentation",
                    "3. Use connecting language to link related pieces",
                    "4. Create coverage inventory: what's in, what's out, why",
                    "",
                    "Quality Gate: Does this presentation tell the COMPLETE story?"
                ]
            },
            
            "visual": {
                "name": "creative_visual_approach",
                "approach": "novel_technique",
                "content": [
                    "\n## CREATIVE VISUAL ENHANCEMENT:",
                    "Novel Approach - Conference Ready Standard:",
                    "1. Imagine presenting at a top-tier conference",
                    "2. Design each slide to impress industry experts",
                    "3. Use visual storytelling to enhance content flow",
                    "4. Apply 'magazine quality' visual standards",
                    "",
                    "Quality Gate: Would this slide look good on a conference main stage?"
                ]
            },
            
            "quality": {
                "name": "creative_quality_approach",
                "approach": "novel_technique",
                "content": [
                    "\n## CREATIVE QUALITY ENHANCEMENT:",
                    "Novel Approach - Excellence Mindset:",
                    "1. Adopt mindset: 'This will be evaluated by experts'",
                    "2. Apply graduate thesis-level attention to detail",
                    "3. Ensure every element serves a clear purpose",
                    "4. Review with fresh eyes: 'What would impress me?'",
                    "",
                    "Quality Gate: Is this the best possible version of this presentation?"
                ]
            }
        }
        
        base_strategy = fallback_strategies.get(gap_type, fallback_strategies["quality"])
        base_strategy["is_fallback"] = True
        base_strategy["previous_attempts_count"] = len(all_previous_attempts)
        
        logger.info(f"Using fallback strategy for {gap_type} after {len(all_previous_attempts)} previous attempts")
        
        return base_strategy
    
    @staticmethod
    def validate_strategy_effectiveness(strategy: Dict, actual_improvement: float) -> Dict[str, Any]:
        """Validate and learn from strategy effectiveness"""
        
        effectiveness = {
            "strategy_name": strategy.get("name", "unknown"),
            "approach": strategy.get("approach", "unknown"),
            "temperature_level": strategy.get("temperature_level", "unknown"),
            "actual_improvement": actual_improvement,
            "effectiveness_rating": "low"
        }
        
        # Rate effectiveness based on improvement
        if actual_improvement > 0.3:
            effectiveness["effectiveness_rating"] = "high"
        elif actual_improvement > 0.1:
            effectiveness["effectiveness_rating"] = "medium"
        elif actual_improvement > 0:
            effectiveness["effectiveness_rating"] = "low"
        else:
            effectiveness["effectiveness_rating"] = "negative"
        
        # Add learning insights
        if effectiveness["effectiveness_rating"] == "high":
            effectiveness["lesson"] = f"Strategy '{strategy.get('name')}' with approach '{strategy.get('approach')}' was highly effective"
        elif effectiveness["effectiveness_rating"] == "negative":
            effectiveness["lesson"] = f"Strategy '{strategy.get('name')}' caused degradation - avoid similar approaches"
        
        return effectiveness