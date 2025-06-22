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
        academic_gen_prompt = f'''Create a beautiful HTML presentation based on this PDF document.

**Purpose of presentation:** {presentation_focus}
**Visual theme:** {theme}

Instructions:
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library)
3. Include elegant transitions between slides
4. Use a color scheme appropriate for the "{theme}" theme
5. Optimize typography for readability
6. Target ~100 words per slide maximum - avoid dense text blocks
7. Use the navigation button to switch pages
8. Avoid embedding base64-encoded content in the HTML file. Do not use base64 for images—instead, use external icons, diagrams, or vector graphics.

## Academic Math & Diagrams Integration:

### LaTeX Formula Support:
- **Example:**
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
<div class="code mathjax-enabled" style="white-space: pre-line;">
Algorithm with $f_θ$ and loss $L_t = \\frac{{1}}{{t}} \\delta_{{x_t,m}}$
Next line preserved
</div>
```
- **Inline formulas:** Use `$E = mc^2$` within text
- **Display equations:** Use `$$\\frac{{d}}{{dx}}f(x) = f'(x)$$` for centered equations
- **Multi-line equations:** Use `\\begin{{align}}` for step-by-step mathematical derivations
- **Code with math:** ALWAYS Use `class="mathjax-enabled"` AND `white-space: pre-line` for pseudocode
- **When to use:** Any mathematical expressions, equations, statistical notation, scientific formulas, research calculations

### Mermaid Diagram Support:
- **Always include:** `<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>`
- **Structure format:**
```html
<div class="mermaid">
    graph TD
        A[Start] --> B[Process] --> C[End]
        style A fill:#667eea,stroke:#fff,stroke-width:3px,color:#fff
</div>
```
- **When to use:** Process flows, system architecture, research methodology, decision trees, conceptual frameworks
- **Standard colors:** Primary: #667eea, Success: #27ae60, Process: #f39c12, Warning: #f5576c

### Academic Enhancement Guidelines:
- **Show the problem clearly:** Use concrete examples and visual comparisons to demonstrate what's broken with current approaches
- **Explain the solution simply:** Present the main idea with clear diagrams and math, then explain in plain language what it means
- **Break down complex algorithms:** Provide step-by-step walkthroughs with code examples and explain each step's purpose
- **Prove it works visually:** Do not generate images. Use charts and graphs to show dramatic before/after improvements that anyone can understand at a glance
- **Explain the magic:** Help readers understand why the approach succeeds where others fail, using intuitive analogies
- **Be honest about limits:** Clearly state what doesn't work yet and what exciting possibilities this opens up

SLIDE STRUCTURE TEMPLATE:
- Title slide with clear value proposition
- 8-15 content slides (each with one key message)
- Conclusion slide summarizing key takeaways

IMPORTANT: The HTML must be a complete, self-contained file that can be opened directly in a browser.
Do not include any explanations, just output the complete HTML code.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.'''

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
    
    def generate_presentation(self, pdf_source, presentation_focus="A comprehensive overview", theme="professional", slide_count=12):
        """
        One-step function to generate a presentation from a PDF source.
        
        Args:
            pdf_source: Either a URL to a PDF or a local file path
            presentation_focus: The main focus or theme of the presentation
            theme: Visual theme for the presentation ("professional", "academic", "modern", etc.)
            slide_count: Target number of slides
            
        Returns:
            Dict with result information or None if process failed
        """
        logger.info(f"🚀 Starting PDF presentation generation...")
        logger.info(f"📄 Source: {pdf_source}")
        logger.info(f"🎯 Focus: {presentation_focus}")
        logger.info(f"🎨 Theme: {theme}")
        
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
        
        # Save to file and open
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"pdf_slides_{timestamp}.html"
        
        saved_html = self.save_html_file(html_content, html_filename)
        if not saved_html:
            logger.error("❌ Failed to save HTML file")
            return None
            
        logger.info(f"4. Presentation saved to {html_filename}")
        
        # Open in browser
        self.open_in_browser(html_filename)
        logger.info("5. Opening slides in browser...")
        
        logger.info(f"\n✅ PDF presentation generation complete!")
        
        return {
            'pdf_source': pdf_source,
            'html_file': html_filename,
            'html_content': html_content,
            'presentation_focus': presentation_focus,
            'theme': theme,
            'slide_count': slide_count,
            'timestamp': timestamp
        }