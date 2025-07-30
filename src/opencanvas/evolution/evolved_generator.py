"""
Evolved Generator - Uses evolved prompts from prompt evolution manager
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from opencanvas.generators.base import BaseGenerator
from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager
from opencanvas.config import Config

logger = logging.getLogger(__name__)

class EvolvedGenerator(BaseGenerator):
    """
    Generator that uses evolved prompts from the evolution system
    instead of static prompts
    """
    
    def __init__(self, api_key: str, evolution_iteration: Optional[int] = None):
        """
        Initialize evolved generator
        
        Args:
            api_key: API key for generation
            evolution_iteration: Specific iteration to use, or None for latest
        """
        super().__init__(api_key)
        
        # Initialize prompt evolution manager
        self.prompt_manager = PromptEvolutionManager()
        
        # Set iteration to use
        self.evolution_iteration = evolution_iteration or self.prompt_manager.current_iteration
        
        # Load evolved prompts
        self.evolved_prompts = self.prompt_manager.get_current_prompts(self.evolution_iteration)
        
        logger.info(f"🧬 EvolvedGenerator initialized with iteration {self.evolution_iteration}")
        logger.info(f"📝 Loaded {len(self.evolved_prompts)} evolved prompts")
        
        # Track generation statistics
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "evolution_iteration_used": self.evolution_iteration,
            "prompt_categories_used": list(self.evolved_prompts.keys())
        }
    
    def generate_slides_html(self, content: str, purpose: str, theme: str) -> str:
        """
        Generate slides HTML using evolved prompts
        
        Args:
            content: Input content (topic or PDF content)
            purpose: Purpose of the presentation
            theme: Visual theme
            
        Returns:
            Generated HTML content
        """
        
        self.generation_stats["total_generations"] += 1
        
        try:
            # Determine if this is topic-based or PDF-based generation
            is_pdf_content = self._is_pdf_content(content)
            
            if is_pdf_content:
                html_result = self._generate_from_pdf_content(content, purpose, theme)
            else:
                html_result = self._generate_from_topic(content, purpose, theme)
            
            if html_result:
                # Apply post-generation enhancements
                enhanced_html = self._apply_post_generation_enhancements(html_result)
                
                # Validate against evolved quality standards
                if self._validate_evolved_quality(enhanced_html):
                    self.generation_stats["successful_generations"] += 1
                    return enhanced_html
                else:
                    logger.warning("Generated content failed evolved quality validation")
                    return enhanced_html  # Return anyway but log the issue
            
            return html_result
            
        except Exception as e:
            logger.error(f"Evolution-enhanced generation failed: {e}")
            # Fallback to basic generation if available
            return self._fallback_generation(content, purpose, theme)
    
    def _generate_from_topic(self, topic: str, purpose: str, theme: str) -> str:
        """Generate presentation from topic using evolved prompts"""
        
        logger.info(f"🎯 Generating from topic using evolution iteration {self.evolution_iteration}")
        
        # Get evolved topic generation prompt
        topic_prompt = self.evolved_prompts.get("topic_generation")
        
        if not topic_prompt:
            logger.error("No evolved topic generation prompt available")
            return ""
        
        # Format prompt with inputs
        formatted_prompt = topic_prompt.format(
            topic=topic,
            purpose=purpose,
            theme=theme
        )
        
        # Add evolution-specific instructions
        enhanced_prompt = self._add_evolution_context(formatted_prompt, "topic_generation")
        
        # Generate using Claude API
        html_result = self._call_generation_api(enhanced_prompt)
        
        logger.info("✅ Topic-based generation completed with evolved prompts")
        
        return html_result
    
    def _generate_from_pdf_content(self, pdf_content: str, purpose: str, theme: str) -> str:
        """Generate presentation from PDF content using evolved prompts"""
        
        logger.info(f"📄 Generating from PDF using evolution iteration {self.evolution_iteration}")
        
        # Get evolved PDF generation prompt
        pdf_prompt = self.evolved_prompts.get("pdf_generation")
        
        if not pdf_prompt:
            logger.error("No evolved PDF generation prompt available")
            return ""
        
        # Format prompt with inputs
        formatted_prompt = pdf_prompt.format(
            pdf_content=pdf_content,
            purpose=purpose,
            theme=theme
        )
        
        # Add evolution-specific instructions
        enhanced_prompt = self._add_evolution_context(formatted_prompt, "pdf_generation")
        
        # Generate using Claude API
        html_result = self._call_generation_api(enhanced_prompt)
        
        logger.info("✅ PDF-based generation completed with evolved prompts")
        
        return html_result
    
    def _add_evolution_context(self, base_prompt: str, prompt_type: str) -> str:
        """Add evolution-specific context and metadata to prompts"""
        
        evolution_context = f"""
EVOLUTION CONTEXT:
- Using Evolution Iteration: {self.evolution_iteration}
- Prompt Type: {prompt_type}
- Enhanced Quality Standards: ACTIVE
- This prompt has been evolved based on systematic quality analysis

EVOLUTION REMINDER:
This is an evolved prompt that incorporates specific improvements identified through systematic analysis of presentation quality. Follow all enhanced requirements carefully to achieve superior results.

---

{base_prompt}

---

EVOLUTION VALIDATION:
After generation, ensure the output meets all evolved quality standards specified above. The generated presentation should demonstrate clear improvements over baseline quality in the targeted dimensions.
"""
        
        return evolution_context
    
    def _apply_post_generation_enhancements(self, html_content: str) -> str:
        """Apply post-generation enhancements based on evolved standards"""
        
        logger.info("🔧 Applying post-generation enhancements...")
        
        enhanced_html = html_content
        
        # Apply visual enhancements if available
        if "visual_enhancement" in self.evolved_prompts:
            enhanced_html = self._apply_visual_enhancements(enhanced_html)
        
        # Apply content validation if available
        if "content_validation" in self.evolved_prompts:
            enhanced_html = self._apply_content_validation(enhanced_html)
        
        # Apply quality control if available
        if "quality_control" in self.evolved_prompts:
            enhanced_html = self._apply_quality_control(enhanced_html)
        
        logger.info("✅ Post-generation enhancements applied")
        
        return enhanced_html
    
    def _apply_visual_enhancements(self, html_content: str) -> str:
        """Apply visual enhancements based on evolved visual standards"""
        
        # Add CSS enhancements for better readability
        enhanced_css = """
<style>
/* Evolution-Enhanced Visual Standards */
.slide {
    font-size: 16px !important;
    line-height: 1.4 !important;
    padding: 20px !important;
}

.slide h1, .slide h2 {
    font-size: 28px !important;
    margin-bottom: 15px !important;
    color: #1a1a1a !important;
}

.slide h3 {
    font-size: 22px !important;
    margin-bottom: 10px !important;
}

.slide p, .slide li {
    font-size: 18px !important;
    margin-bottom: 8px !important;
}

/* Enhanced chart styles */
svg text {
    font-size: 14px !important;
    font-family: Arial, sans-serif !important;
}

/* Improved visual hierarchy */
.slide ul, .slide ol {
    margin-left: 20px !important;
}

.slide li {
    margin-bottom: 5px !important;
}
</style>
"""
        
        # Insert enhanced CSS into HTML
        if "<head>" in html_content:
            enhanced_html = html_content.replace("</head>", f"{enhanced_css}</head>")
        else:
            enhanced_html = enhanced_css + html_content
        
        return enhanced_html
    
    def _apply_content_validation(self, html_content: str) -> str:
        """Apply content validation enhancements"""
        
        # For now, just log validation - in a full implementation,
        # this would do content analysis and corrections
        logger.info("📋 Content validation applied (placeholder)")
        
        return html_content
    
    def _apply_quality_control(self, html_content: str) -> str:
        """Apply quality control enhancements"""
        
        # Add evolution metadata to HTML for tracking
        metadata_comment = f"""
<!-- Evolution Metadata -->
<!-- Generated with Evolution Iteration: {self.evolution_iteration} -->
<!-- Evolution Enhanced: {datetime.now().isoformat()} -->
<!-- Prompt Categories Used: {', '.join(self.evolved_prompts.keys())} -->
"""
        
        return metadata_comment + html_content
    
    def _validate_evolved_quality(self, html_content: str) -> bool:
        """Validate that generated content meets evolved quality standards"""
        
        # Basic validation checks
        validations = []
        
        # Check for minimum content length
        validations.append(len(html_content) > 500)
        
        # Check for proper slide structure
        validations.append('<div class="slide"' in html_content)
        
        # Check for multiple slides
        slide_count = html_content.count('<div class="slide"')
        validations.append(slide_count >= 4)
        
        # Check for titles/headers
        validations.append('<h1>' in html_content or '<h2>' in html_content)
        
        # All validations must pass
        validation_passed = all(validations)
        
        if validation_passed:
            logger.info("✅ Generated content passed evolved quality validation")
        else:
            logger.warning("⚠️ Generated content failed some evolved quality checks")
        
        return validation_passed
    
    def _is_pdf_content(self, content: str) -> bool:
        """Determine if content is from PDF extraction"""
        
        # Simple heuristics to detect PDF content
        pdf_indicators = [
            "abstract:",
            "introduction:",
            "methodology:",
            "results:",
            "conclusion:",
            "references:",
            len(content) > 5000,  # PDF content is typically longer
            content.count('.') > 50  # More sentences
        ]
        
        return sum(pdf_indicators) >= 3
    
    def _call_generation_api(self, prompt: str) -> str:
        """Call Claude API for generation"""
        
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Clean HTML content
            return self.clean_html_content(response_text)
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return ""
    
    def _fallback_generation(self, content: str, purpose: str, theme: str) -> str:
        """Fallback to basic generation if evolved generation fails"""
        
        logger.info("🔄 Falling back to basic generation")
        
        # Simple fallback prompt
        fallback_prompt = f"""Create a presentation about: {content}
Purpose: {purpose}
Theme: {theme}

Generate a simple HTML presentation with multiple slides."""
        
        return self._call_generation_api(fallback_prompt)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about generation performance"""
        
        success_rate = 0
        if self.generation_stats["total_generations"] > 0:
            success_rate = self.generation_stats["successful_generations"] / self.generation_stats["total_generations"]
        
        return {
            **self.generation_stats,
            "success_rate": success_rate,
            "evolution_prompts_loaded": len(self.evolved_prompts) > 0,
            "evolution_iteration_active": self.evolution_iteration > 0
        }
    
    def save_generation_report(self, output_dir: str):
        """Save generation report with evolution details"""
        
        report = {
            "evolution_generation_report": {
                "timestamp": datetime.now().isoformat(),
                "evolution_iteration": self.evolution_iteration,
                "generation_stats": self.get_generation_stats(),
                "evolved_prompts_used": list(self.evolved_prompts.keys()),
                "prompt_evolution_history": self.prompt_manager.get_evolution_history()
            }
        }
        
        report_path = Path(output_dir) / "evolution_generation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Evolution generation report saved to {report_path}")


class EvolvedGenerationRouter:
    """
    Router that uses evolved generators instead of basic generators
    """
    
    def __init__(self, api_key: str, brave_api_key: str = None, evolution_iteration: Optional[int] = None):
        """Initialize evolved generation router"""
        self.api_key = api_key
        self.brave_api_key = brave_api_key
        self.evolution_iteration = evolution_iteration
        
        # Initialize evolved generator
        self.evolved_generator = EvolvedGenerator(api_key, evolution_iteration)
        
        logger.info(f"🚀 EvolvedGenerationRouter initialized")
        logger.info(f"🧬 Using evolution iteration: {self.evolved_generator.evolution_iteration}")
    
    def generate(self, input_source: str, purpose: str, theme: str, output_dir: str) -> Dict[str, Any]:
        """
        Generate presentation using evolved prompts
        
        Args:
            input_source: Topic or PDF path/URL  
            purpose: Purpose of presentation
            theme: Visual theme
            output_dir: Output directory
            
        Returns:
            Generation result with evolution metadata
        """
        
        logger.info(f"🎯 Starting evolved generation...")
        logger.info(f"📁 Output directory: {output_dir}")
        
        # Determine input type and prepare content
        if input_source.endswith('.pdf') or input_source.startswith('http'):
            # PDF-based generation (would need PDF processing)
            content = f"PDF content from: {input_source}"
            generation_type = "pdf_based"
        else:
            # Topic-based generation
            content = input_source
            generation_type = "topic_based"
        
        # Generate using evolved prompts
        try:
            html_content = self.evolved_generator.generate_slides_html(content, purpose, theme)
            
            if not html_content:
                return {"success": False, "error": "Evolution generation failed"}
            
            # Save HTML file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            html_filename = f"evolved_presentation_iter_{self.evolved_generator.evolution_iteration}.html"
            html_file_path = output_path / html_filename
            
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save evolution generation report
            self.evolved_generator.save_generation_report(output_dir)
            
            # Return success result with evolution metadata
            result = {
                "success": True,
                "html_file": str(html_file_path),
                "generation_type": generation_type,
                "evolution_metadata": {
                    "iteration_used": self.evolved_generator.evolution_iteration,
                    "generation_stats": self.evolved_generator.get_generation_stats(),
                    "evolved_prompts_count": len(self.evolved_generator.evolved_prompts)
                },
                "output_dir": output_dir
            }
            
            logger.info(f"✅ Evolved generation completed successfully")
            logger.info(f"📄 HTML file: {html_file_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Evolved generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "evolution_iteration": self.evolved_generator.evolution_iteration
            }