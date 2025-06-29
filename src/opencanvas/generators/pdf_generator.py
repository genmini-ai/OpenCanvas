import os
import json
import webbrowser
import requests
import base64
from pathlib import Path
from anthropic import Anthropic
from datetime import datetime
from urllib.parse import urlparse
import mimetypes
import logging

from .base import BaseGenerator
from opencanvas.utils.validation import InputValidator

logger = logging.getLogger(__name__)

class PDFGenerator(BaseGenerator):
    """
    A class to generate HTML slide presentations from PDF documents using the Anthropic API.
    """
    def __init__(self, api_key):
        """Initialize the PDF slide generator with Anthropic API key"""
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)
        self.presentation_focus = None

    def validate_pdf_url(self, url):
        """Validate if the URL points to a PDF file"""
        return InputValidator.validate_pdf_url(url)

    def validate_pdf_file(self, file_path):
        """Validate if the file is a PDF"""
        return InputValidator.validate_pdf_file(file_path)

    def encode_pdf_from_file(self, file_path):
        """Encode a local PDF file to base64"""
        try:
            with open(file_path, "rb") as f:
                pdf_data = base64.b64encode(f.read()).decode("utf-8")
            return pdf_data, None
        except Exception as e:
            return None, f"Error encoding PDF: {str(e)}"

    def encode_pdf_from_url(self, url):
        """Download and encode a PDF from URL to base64"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            pdf_data = base64.b64encode(response.content).decode("utf-8")
            return pdf_data, None
        except Exception as e:
            return None, f"Error downloading and encoding PDF: {str(e)}"

    def generate_slides_html(self, pdf_data, presentation_focus, theme="professional"):
        """Generate HTML slides directly from PDF content in a single step."""
        
        self.presentation_focus = presentation_focus
        
        # Updated academic generation prompt
        academic_gen_prompt = f'''<presentation_task>
Create a stunning, visually captivating HTML presentation that makes viewers stop and say "wow" based on this PDF document.

**Purpose of presentation:** {presentation_focus}
**Visual theme:** {theme}
</presentation_task>

<design_philosophy>
CREATE EMOTIONAL IMPACT:
- Prioritize the "wow factor" over conventional academic design
- Make every slide feel alive and dynamic with subtle animations
- Choose bold, vibrant colors over muted, safe academic palettes
- Use cutting-edge web design trends (glassmorphism, gradient overlays, micro-animations)
- Push the boundaries of what's possible with modern CSS and JavaScript
- Create a premium, cutting-edge experience that feels expensive and engaging
</design_philosophy>

<visual_requirements>
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use modern slide transitions with easing and physics-based animations (not basic reveals)
3. Implement a sophisticated color scheme with gradients and depth for the "{theme}" theme
4. Include micro-interactions: hover effects, animated reveals, parallax scrolling
5. Use expressive, modern typography with varied font weights and dynamic sizing
6. Add glassmorphism effects, subtle shadows, and layered visual depth
7. Target ~100 words per slide maximum with animated text reveals
8. Create navigation with smooth, delightful interactions and visual feedback
9. CRITICAL: Use fixed width: 1280px; min-height: 720px; for all slides - use horizontal layouts for diagrams
10. Add subtle background animations or patterns that enhance without distracting
11. Ensure responsive content: Use horizontal layouts and optimize for the fixed 1280px width
12. **HEIGHT-AWARE LAYOUT: Ensure all content fit within the 720px height by adjusting complexity**
</visual_requirements>

<motion_design>
- Everything should have subtle movement and life
- Use staggered animations for mathematical formulas and diagrams
- Implement smooth cursor tracking effects on interactive elements
- Add entrance animations for each slide element with proper timing
- Create seamless transitions that maintain visual flow between concepts
</motion_design>

<academic_math_support>
### LaTeX Formula Support:
- Enhanced styling: Add beautiful animations and hover effects to formulas
- Example with delightful styling:
```html
<script>
MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']]
  }},
  options: {{
    processHtmlClass: 'mathjax-enabled'
  }}
}};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
<div class="code mathjax-enabled animate-reveal" style="white-space: pre-line; backdrop-filter: blur(10px); background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px;">
Algorithm with $f_θ$ and loss $L_t = \\frac{{1}}{{t}} \\delta_{{x_t,m}}$
Next line preserved
</div>
```
- Animated reveals: Use CSS animations to reveal formulas progressively
- Interactive math: Add hover effects and smooth transitions to mathematical expressions
- When to use: Any mathematical expressions, equations, statistical notation, scientific formulas, research calculations
</academic_math_support>

<diagram_support>
### Mermaid Diagram Support:
- Always include: `<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>`
- CRITICAL: Use horizontal, landscape-optimized layouts for fixed width: 1280px; min-height: 720px;
- Enhanced structure with modern styling:
```html
<div class="mermaid diagram-container" style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border-radius: 16px; padding: 24px; backdrop-filter: blur(10px); width: 1200px; margin: 0 auto;">
    graph LR
        A[Start] --> B[Process 1] --> C[Process 2] --> D[End]
        E[Input] --> B
        F[Config] --> C
        style A fill:#667eea,stroke:#fff,stroke-width:3px,color:#fff,rx:12,ry:12
        style B fill:#764ba2,stroke:#fff,stroke-width:2px,color:#fff,rx:12,ry:12
        style C fill:#f39c12,stroke:#fff,stroke-width:2px,color:#fff,rx:12,ry:12
        style D fill:#27ae60,stroke:#fff,stroke-width:3px,color:#fff,rx:12,ry:12
</div>
```
- Diagram orientation priority: Always use `graph LR` (left-to-right) or `graph RL` (right-to-left) instead of `graph TD` (top-down)
- Flowchart layouts: Use horizontal flows: `flowchart LR` for process flows, timelines, and sequential steps
- Network diagrams: Spread nodes horizontally with compact vertical spacing
- Modern colors with gradients: Primary: #667eea to #764ba2, Success: #27ae60 to #2ecc71, Process: #f39c12 to #e67e22, Warning: #f5576c to #e74c3c
- Container sizing: Use `width: 1200px; margin: 0 auto;` for diagram containers to center within 1280px slide width
- Animated diagrams: Add CSS animations to make diagram elements appear with staggered timing
</diagram_support>

<academic_guidelines>
- Show problems visually: Use dynamic before/after comparisons with smooth transitions
- Explain solutions beautifully: Present ideas with elegant diagrams and animated mathematical expressions
- Break down algorithms elegantly: Provide step-by-step walkthroughs with smooth reveals and visual flow
- Prove effectiveness dramatically: Use animated charts and graphs with stunning visual impact
- Explain intuitively: Use beautiful analogies with visual metaphors and smooth transitions
- Present limitations honestly: Use elegant visual indicators for constraints and future possibilities
</academic_guidelines>

<content_presentation>
- Transform academic content into visually engaging elements with icons and graphics
- Use progressive disclosure with smooth animations
- Create visual hierarchy through dynamic sizing, vibrant colors, and spatial relationships
- Include elegant progress indicators and slide counters with smooth animations
- Break up dense content with beautiful visual elements and breathing room
</content_presentation>

<technical_excellence>
- Use advanced CSS features: backdrop-filter, clip-path, CSS Grid, Flexbox, custom properties
- Implement smooth JavaScript animations with requestAnimationFrame
- Add keyboard navigation with delightful visual feedback and sound design
- Include beautiful preloaders and seamless state transitions
- Ensure the presentation feels responsive, premium, and engaging
</technical_excellence>

<slide_structure>
- Stunning title slide with animated value proposition and visual hierarchy
- 8-15 content slides (each with one key message beautifully presented)
- Elegant conclusion slide with animated key takeaways summary
</slide_structure>

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser and immediately impresses with its sophisticated visual design and smooth interactions.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
</output_requirements>
'''
        try:
            logger.info("🔍 Analyzing PDF and generating slides in one step...")
            
            message = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=15000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": academic_gen_prompt
                            }
                        ],
                    }
                ],
            )
            
            # The response is expected to be HTML code, so we clean it up if needed
            html_content = message.content[0].text
            return self.clean_html_content(html_content), None

        except Exception as e:
            return None, f"Error generating slides directly: {str(e)}"
    
    def generate_presentation(self, pdf_source, presentation_focus="A comprehensive overview", theme="professional", slide_count=12, output_dir="output"):
        """
        One-step function to generate a presentation from a PDF source with organized file structure.
        
        Args:
            pdf_source: Either a URL to a PDF or a local file path
            presentation_focus: The main focus or theme of the presentation
            theme: Visual theme for the presentation ("professional", "academic", "modern", etc.)
            slide_count: Target number of slides
            output_dir: Output directory for organized files
            
        Returns:
            Dict with result information or None if process failed
        """
        from opencanvas.utils.file_utils import generate_topic_slug, organize_pipeline_outputs
        
        logger.info(f"🚀 Starting PDF presentation generation...")
        logger.info(f"📄 Source: {pdf_source}")
        logger.info(f"🎯 Focus: {presentation_focus}")
        logger.info(f"🎨 Theme: {theme}")
        
        # Generate topic slug and timestamp for organized naming
        topic_slug = generate_topic_slug(presentation_focus)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
        
        logger.info(f"📂 Topic slug: {topic_slug}")
        logger.info(f"📁 Output directory: {output_path}")
        
        # Determine if source is URL or file path
        if pdf_source.startswith(('http://', 'https://')):
            # Validate URL
            is_valid, msg = self.validate_pdf_url(pdf_source)
            logger.info(f"1. Validating source... {msg}")
            if not is_valid:
                logger.error(f"Invalid PDF URL: {msg}")
                return None
                
            # Download and encode PDF
            pdf_data, error = self.encode_pdf_from_url(pdf_source)
            if error:
                logger.error(f"❌ {error}")
                return None
        else:
            # Validate file
            is_valid, msg = self.validate_pdf_file(pdf_source)
            logger.info(f"1. Validating source... {msg}")
            if not is_valid:
                logger.error(f"Invalid PDF file: {msg}")
                return None
                
            # Encode PDF
            pdf_data, error = self.encode_pdf_from_file(pdf_source)
            if error:
                logger.error(f"❌ {error}")
                return None
        
        logger.info("2. PDF encoded successfully.")
        
        # Generate slides directly in one step
        html_content, error = self.generate_slides_html(
            pdf_data, 
            presentation_focus,
            theme
        )
        
        if error:
            logger.error(f"❌ {error}")
            return None
            
        logger.info("3. Slides generated successfully.")
        
        # Organize outputs with proper file structure
        logger.info("📁 Organizing output files...")
        organized_files = organize_pipeline_outputs(
            output_dir=output_path,
            topic_slug=topic_slug,
            timestamp=timestamp,
            html_content=html_content,
            source_pdf=pdf_source if not pdf_source.startswith(('http://', 'https://')) else None
        )
        
        # Open in browser (use the organized HTML file)
        if 'html' in organized_files:
            logger.info(f"🌐 Opening slides in browser...")
            self.open_in_browser(str(organized_files['html']))
        
        # Print organized file summary
        from opencanvas.utils.file_utils import get_file_summary
        logger.info(f"\n✅ PDF presentation generation complete!")
        logger.info(f"\n📁 Organized files:")
        logger.info(get_file_summary(organized_files))
        
        return {
            'pdf_source': pdf_source,
            'html_file': str(organized_files.get('html', '')),
            'html_content': html_content,
            'presentation_focus': presentation_focus,
            'theme': theme,
            'slide_count': slide_count,
            'organized_files': organized_files,
            'topic_slug': topic_slug,
            'timestamp': timestamp
        }
