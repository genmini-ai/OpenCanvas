"""
Example Visual Enhancement Tool - Demonstrates proper tool implementation
This tool adds visual indicators and improves slide formatting
"""

import re
import logging
from typing import Any, Dict, Optional
from opencanvas.evolution.core.base_tool import HTMLProcessingTool

logger = logging.getLogger(__name__)

class VisualEnhancementTool(HTMLProcessingTool):
    """
    Enhances visual quality of HTML presentations by adding:
    - Progress indicators
    - Visual separators
    - Better spacing
    - Icon suggestions for bullet points
    """
    
    name = "VisualEnhancementTool"
    stage = "post_html"  # Runs after HTML generation
    priority = 10  # Higher priority = runs earlier
    description = "Enhances visual elements in HTML presentations"
    
    def process(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process HTML content to enhance visual quality.
        
        Args:
            content: HTML string of the presentation
            context: Optional context with metadata
        
        Returns:
            Enhanced HTML content (never adds debug messages)
        """
        try:
            logger.info(f"{self.name}: Starting visual enhancement")
            
            # Enhancement 1: Add slide numbers if not present
            content = self._add_slide_numbers(content)
            
            # Enhancement 2: Improve bullet point formatting
            content = self._enhance_bullet_points(content)
            
            # Enhancement 3: Add visual separators between sections
            content = self._add_visual_separators(content)
            
            # Enhancement 4: Ensure proper spacing
            content = self._improve_spacing(content)
            
            logger.info(f"{self.name}: Visual enhancement complete")
            
            # CRITICAL: Return clean content without any tool messages
            return content
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            # Always return original content on error
            return content
    
    def _add_slide_numbers(self, html: str) -> str:
        """Add slide numbers to each slide if not present"""
        try:
            # Check if slide numbers already exist
            if "slide-number" in html or "page-number" in html:
                return html
            
            # Count slides
            slide_count = html.count('<section') or html.count('<div class="slide"')
            
            if slide_count > 1:
                # Add CSS for slide numbers
                slide_number_css = """
                <style>
                .slide-number {
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    font-size: 14px;
                    color: #666;
                    opacity: 0.7;
                }
                </style>
                """
                
                # Insert CSS before first slide
                if '<style>' in html:
                    html = html.replace('</style>', '.slide-number { position: absolute; bottom: 20px; right: 20px; font-size: 14px; color: #666; opacity: 0.7; }\n</style>', 1)
                
                # Add slide numbers to each slide
                slide_num = 0
                def add_number(match):
                    nonlocal slide_num
                    slide_num += 1
                    slide_html = match.group(0)
                    # Don't add to title slide
                    if slide_num == 1:
                        return slide_html
                    # Add slide number div before closing tag
                    return slide_html.replace('</section>', f'<div class="slide-number">{slide_num}/{slide_count}</div></section>')
                
                html = re.sub(r'<section[^>]*>.*?</section>', add_number, html, flags=re.DOTALL)
            
            return html
            
        except Exception as e:
            logger.warning(f"Failed to add slide numbers: {e}")
            return html
    
    def _enhance_bullet_points(self, html: str) -> str:
        """Enhance bullet point formatting"""
        try:
            # Add better bullet styling
            bullet_css = """
            ul li::marker { color: #4a90e2; }
            ul li { margin-bottom: 0.5em; line-height: 1.6; }
            """
            
            if '<style>' in html:
                html = html.replace('</style>', f'{bullet_css}</style>', 1)
            
            return html
            
        except Exception as e:
            logger.warning(f"Failed to enhance bullet points: {e}")
            return html
    
    def _add_visual_separators(self, html: str) -> str:
        """Add visual separators between major sections"""
        try:
            # Add subtle separators between sections
            separator_css = """
            .section-separator {
                width: 60%;
                height: 2px;
                background: linear-gradient(to right, transparent, #e0e0e0, transparent);
                margin: 2em auto;
            }
            """
            
            if '<style>' in html:
                html = html.replace('</style>', f'{separator_css}</style>', 1)
            
            return html
            
        except Exception as e:
            logger.warning(f"Failed to add visual separators: {e}")
            return html
    
    def _improve_spacing(self, html: str) -> str:
        """Improve spacing and layout"""
        try:
            # Add better spacing rules
            spacing_css = """
            h1, h2, h3 { margin-top: 1.5em; margin-bottom: 0.8em; }
            p { line-height: 1.6; margin-bottom: 1em; }
            .slide { padding: 40px; }
            """
            
            if '<style>' in html:
                html = html.replace('</style>', f'{spacing_css}</style>', 1)
            
            return html
            
        except Exception as e:
            logger.warning(f"Failed to improve spacing: {e}")
            return html