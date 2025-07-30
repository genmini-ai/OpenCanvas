"""
Assist Mode Style Editor for OpenCanvas

This module implements the two-step assist mode for presentation style editing:
1. Analyze content and provide 3 diverse style recommendations
2. Implement the chosen style with professional CSS and animations
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import anthropic

from opencanvas.editing.prompts import EditingPrompts
from opencanvas.config import Config

logger = logging.getLogger(__name__)


class StyleRecommendation:
    """Data class for style recommendations"""
    
    def __init__(self, recommendation_data: Dict[str, Any]):
        self.style_name = recommendation_data.get("style_name", "")
        self.style_category = recommendation_data.get("style_category", "")
        self.color_palette = recommendation_data.get("color_palette", {})
        self.animation_philosophy = recommendation_data.get("animation_philosophy", "")
        self.animation_details = recommendation_data.get("animation_details", [])
        self.typography_approach = recommendation_data.get("typography_approach", "")
        self.font_suggestions = recommendation_data.get("font_suggestions", {})
        self.visual_rationale = recommendation_data.get("visual_rationale", "")
        self.mood_keywords = recommendation_data.get("mood_keywords", [])
        self.best_suited_for = recommendation_data.get("best_suited_for", "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "style_name": self.style_name,
            "style_category": self.style_category,
            "color_palette": self.color_palette,
            "animation_philosophy": self.animation_philosophy,
            "animation_details": self.animation_details,
            "typography_approach": self.typography_approach,
            "font_suggestions": self.font_suggestions,
            "visual_rationale": self.visual_rationale,
            "mood_keywords": self.mood_keywords,
            "best_suited_for": self.best_suited_for
        }


class AssistModeStyleEditor:
    """
    Two-step assist mode for presentation style editing
    
    Step 1: Analyze presentation and provide 3 diverse style recommendations
    Step 2: Implement chosen style with professional CSS and animations
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the style editor
        
        Args:
            anthropic_api_key: API key for Anthropic (uses config if not provided)
        """
        # Get API key
        if not anthropic_api_key:
            anthropic_api_key = Config.ANTHROPIC_API_KEY
        
        if not anthropic_api_key:
            raise ValueError("No Anthropic API key found. Check Config.ANTHROPIC_API_KEY or provide key directly.")
        
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.prompts = EditingPrompts()
        
        logger.info(f"AssistModeStyleEditor initialized with model: {self.prompts.EDITING_MODEL}")
    
    def get_style_recommendations(
        self, 
        html_content: str, 
        topic: str, 
        purpose: str = "general presentation", 
        audience: str = "professional audience"
    ) -> Tuple[Dict[str, Any], List[StyleRecommendation]]:
        """
        Step 1: Analyze presentation and get 3 diverse style recommendations
        
        Args:
            html_content: The original HTML presentation content
            topic: Topic or subject of the presentation
            purpose: Purpose of the presentation (e.g., "educational", "corporate")
            audience: Target audience description
            
        Returns:
            Tuple of (content_analysis, list_of_style_recommendations)
        """
        logger.info(f"Analyzing presentation for style recommendations - Topic: {topic}")
        
        # Get the step 1 prompt
        prompt_template = self.prompts.get_assist_mode_step1_prompt()
        
        # Format the user prompt
        user_prompt = prompt_template["user"].format(
            html_content=html_content,
            topic=topic,
            purpose=purpose,
            audience=audience
        )
        
        try:
            # Call Claude for style analysis and recommendations
            message = self.client.messages.create(
                model=self.prompts.EDITING_MODEL,
                max_tokens=4000,
                temperature=0.7,  # Higher temperature for creative style suggestions
                system=prompt_template["system"],
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response_text = message.content[0].text
            logger.debug(f"Claude response length: {len(response_text)} characters")
            
            # Parse the JSON response
            response_data = self._parse_style_recommendations_response(response_text)
            
            # Extract content analysis and recommendations
            content_analysis = response_data.get("content_analysis", {})
            recommendations_data = response_data.get("recommendations", [])
            
            # Convert to StyleRecommendation objects
            recommendations = [StyleRecommendation(rec) for rec in recommendations_data]
            
            logger.info(f"Successfully generated {len(recommendations)} style recommendations")
            
            return content_analysis, recommendations
            
        except Exception as e:
            logger.error(f"Error generating style recommendations: {e}")
            raise
    
    def implement_chosen_style(
        self, 
        original_html: str, 
        chosen_style: StyleRecommendation
    ) -> Tuple[str, str]:
        """
        Step 2: Implement the chosen style with professional CSS and animations
        
        Args:
            original_html: The original HTML presentation content
            chosen_style: The selected style recommendation to implement
            
        Returns:
            Tuple of (modified_html, implementation_summary)
        """
        logger.info(f"Implementing style: {chosen_style.style_name}")
        
        # Get the step 2 prompt
        prompt_template = self.prompts.get_assist_mode_step2_prompt()
        
        # Format the user prompt
        user_prompt = prompt_template["user"].format(
            original_html=original_html,
            style_name=chosen_style.style_name,
            style_category=chosen_style.style_category,
            style_details=json.dumps(chosen_style.to_dict(), indent=2)
        )
        
        try:
            # Call Claude for style implementation
            message = self.client.messages.create(
                model=self.prompts.EDITING_MODEL,
                max_tokens=20000,  # Larger token limit for full HTML output
                temperature=0.3,  # Lower temperature for consistent implementation
                system=prompt_template["system"],
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response_text = message.content[0].text
            logger.debug(f"Implementation response length: {len(response_text)} characters")
            
            # Parse the response to extract HTML and summary
            modified_html, implementation_summary = self._parse_implementation_response(response_text)
            
            logger.info(f"Successfully implemented style: {chosen_style.style_name}")
            
            return modified_html, implementation_summary
            
        except Exception as e:
            logger.error(f"Error implementing style: {e}")
            raise
    
    def _parse_style_recommendations_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the JSON response from step 1"""
        try:
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON in style recommendations response: {e}")
    
    def _parse_implementation_response(self, response_text: str) -> Tuple[str, str]:
        """Parse the implementation response to extract HTML and summary"""
        # Try to find HTML content (look for <!DOCTYPE or <html>)
        html_start = response_text.find('<!DOCTYPE')
        if html_start == -1:
            html_start = response_text.find('<html')
        
        if html_start == -1:
            # If no HTML found, treat entire response as HTML
            logger.warning("No HTML markers found, treating entire response as HTML")
            return response_text.strip(), "Implementation completed (no summary found)"
        
        # Find the end of HTML (look for </html>)
        html_end = response_text.rfind('</html>')
        if html_end != -1:
            html_end += 7  # Include </html>
            modified_html = response_text[html_start:html_end]
        else:
            # If no closing tag, take from start to end
            modified_html = response_text[html_start:]
        
        # Look for implementation summary after the HTML
        summary_start = response_text.find('## Style Implementation Summary', html_end if html_end != -1 else 0)
        if summary_start != -1:
            implementation_summary = response_text[summary_start:].strip()
        else:
            implementation_summary = "Style implementation completed successfully."
        
        return modified_html.strip(), implementation_summary
    
    def generate_style_previews(
        self,
        original_html: str,
        recommendations: List[StyleRecommendation]
    ) -> Dict[str, str]:
        """
        Generate preview HTML for all style recommendations (first slide only)
        
        Args:
            original_html: The original HTML presentation content
            recommendations: List of style recommendations to preview
            
        Returns:
            Dictionary mapping style names to preview HTML
        """
        logger.info(f"Generating previews for {len(recommendations)} style recommendations")
        
        previews = {}
        
        # Get the preview prompt template
        prompt_template = self.prompts.get_preview_mode_prompt()
        
        for i, style in enumerate(recommendations, 1):
            logger.info(f"Generating preview {i}/{len(recommendations)}: {style.style_name}")
            
            # Format the user prompt for preview
            user_prompt = prompt_template["user"].format(
                original_html=original_html,
                style_name=style.style_name,
                style_category=style.style_category,
                style_details=json.dumps(style.to_dict(), indent=2)
            )
            
            try:
                # Call Claude for preview generation (faster than full implementation)
                message = self.client.messages.create(
                    model=self.prompts.EDITING_MODEL,
                    max_tokens=6000,  # Smaller than full implementation
                    temperature=0.3,
                    system=prompt_template["system"],
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                response_text = message.content[0].text
                
                # Extract HTML from response
                preview_html = self._parse_preview_response(response_text, style.style_name)
                previews[style.style_name] = preview_html
                
                logger.info(f"Successfully generated preview for {style.style_name}")
                
            except Exception as e:
                logger.error(f"Error generating preview for {style.style_name}: {e}")
                # Create a fallback preview
                previews[style.style_name] = self._create_fallback_preview(style.style_name, str(e))
        
        return previews
    
    def _parse_preview_response(self, response_text: str, style_name: str) -> str:
        """Parse the preview response to extract HTML"""
        # Try to find HTML content
        html_start = response_text.find('<!DOCTYPE')
        if html_start == -1:
            html_start = response_text.find('<html')
        
        if html_start != -1:
            # Find the end of HTML
            html_end = response_text.rfind('</html>')
            if html_end != -1:
                html_end += 7
                return response_text[html_start:html_end]
            else:
                return response_text[html_start:]
        
        # If no HTML markers found, wrap the response
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Preview: {style_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .preview-header {{ background: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="preview-header">
        <h2>Style Preview: {style_name}</h2>
        <p>Preview generation in progress...</p>
    </div>
    <div class="preview-content">
        {response_text}
    </div>
</body>
</html>"""
    
    def _create_fallback_preview(self, style_name: str, error_msg: str) -> str:
        """Create a fallback preview when generation fails"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Preview Error: {style_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f9f9f9; }}
        .error-header {{ background: #ffebee; padding: 15px; margin-bottom: 20px; border-radius: 5px; border-left: 4px solid #f44336; }}
        .error-content {{ background: white; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error-header">
        <h2>Preview Generation Failed: {style_name}</h2>
        <p>Unable to generate preview for this style.</p>
    </div>
    <div class="error-content">
        <p><strong>Error:</strong> {error_msg}</p>
        <p>You can still proceed with full implementation of this style.</p>
    </div>
</body>
</html>"""

    def get_editing_stats(self) -> Dict[str, Any]:
        """Get statistics about editing operations"""
        return {
            "model_used": self.prompts.EDITING_MODEL,
            "assist_mode_available": True,
            "autonomy_mode_available": False,  # TODO: Implement autonomy mode
            "features": [
                "Style analysis and recommendations",
                "Style preview generation (first slide only)",
                "Professional CSS implementation", 
                "Animation integration",
                "Typography optimization",
                "Color system application"
            ]
        } 