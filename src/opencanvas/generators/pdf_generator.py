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
import tempfile

from opencanvas.generators.base import BaseGenerator
from opencanvas.utils.validation import InputValidator
from opencanvas.config import Config
from opencanvas.utils.plot_caption_extractor import PDFPlotCaptionExtractor
from opencanvas.utils.docling_extractor import DoclingImageExtractor
from opencanvas.utils.file_utils import create_organized_output_structure

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
        self.plot_extractor = None
        self.docling_extractor = None

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

    def _extract_images_and_captions(self, pdf_data, output_dir):
        """
        Extract complete figures and captions from PDF using Docling
        
        This replaces the fragmented pdfplumber approach with Docling's semantic
        figure detection that maintains the integrity of complex diagrams.
        
        Args:
            pdf_data: Base64 encoded PDF data
            output_dir: Directory to save extracted images
            
        Returns:
            Tuple of (image_captions_dict, extracted_images_dir, plots_list)
        """
        try:
            # Try Docling extraction first (preferred method)
            if self._try_docling_extraction():
                logger.info("🔍 Using Docling for complete figure extraction...")
                
                # Initialize Docling extractor if not already done
                if self.docling_extractor is None:
                    self.docling_extractor = DoclingImageExtractor(dpi_scale=2.0)
                
                # Extract using Docling
                image_captions, extracted_images_dir, plots = self.docling_extractor.extract_from_pdf_data(
                    pdf_data, output_dir
                )
                
                if image_captions:
                    logger.info(f"✅ Docling extracted {len(image_captions)} complete figures")
                    return image_captions, extracted_images_dir, plots
                else:
                    logger.info("Docling found no figures, falling back to pdfplumber")
            
            # Fallback to original fragmented extraction
            logger.info("📋 Falling back to pdfplumber fragmented extraction...")
            return self._extract_with_pdfplumber_fallback(pdf_data, output_dir)
            
        except Exception as e:
            logger.error(f"Error in image extraction: {e}")
            # Always fallback to original method if there's any error
            logger.info("🔄 Error occurred, using pdfplumber fallback...")
            return self._extract_with_pdfplumber_fallback(pdf_data, output_dir)
    
    def _try_docling_extraction(self) -> bool:
        """
        Check if Docling extraction is available and should be used
        
        Returns:
            True if Docling should be used, False for fallback
        """
        try:
            from opencanvas.utils.docling_extractor import DOCLING_AVAILABLE
            return DOCLING_AVAILABLE
        except ImportError:
            return False
    
    def _extract_with_pdfplumber_fallback(self, pdf_data, output_dir):
        """
        Fallback extraction using the original pdfplumber method
        
        This preserves the original fragmented behavior for compatibility
        when Docling is not available or fails.
        """
        try:
            # Initialize plot extractor if not already done
            if self.plot_extractor is None:
                self.plot_extractor = PDFPlotCaptionExtractor(
                    api_key=self.api_key, 
                    provider="claude"
                )
            
            # Create temporary PDF file from base64 data
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                pdf_bytes = base64.b64decode(pdf_data)
                temp_pdf.write(pdf_bytes)
                temp_pdf_path = temp_pdf.name
            
            try:
                # Extract plots and captions
                plots = self.plot_extractor.extract_captions_from_pdf(temp_pdf_path)
                
                if not plots:
                    logger.info("No images/plots found in PDF")
                    return {}, None, []
                
                # Create extracted_images directory
                extracted_images_dir = output_dir / "extracted_images"
                extracted_images_dir.mkdir(exist_ok=True)
                
                # Save images and create caption mapping
                image_captions = {}
                for plot in plots:
                    if plot.image_data:
                        # Save image with plot_id as filename
                        image_filename = f"{plot.plot_id}.png"
                        image_path = extracted_images_dir / image_filename
                        
                        with open(image_path, "wb") as f:
                            f.write(plot.image_data)
                        
                        # Create relative path for HTML (go up one level from slides/ to parent directory)
                        relative_path = f"../extracted_images/{image_filename}"
                        image_captions[plot.plot_id] = {
                            'caption': plot.caption or "No caption found",
                            'path': relative_path,
                            'dimensions': plot.dimensions or "unknown",
                            'width': plot.width,
                            'height': plot.height,
                            'error': plot.error
                        }
                        
                        logger.info(f"Extracted image: {plot.plot_id} -> {image_path} ({plot.dimensions or 'unknown'})")
                
                logger.info(f"pdfplumber extracted {len(image_captions)} image fragments")

                return image_captions, extracted_images_dir, plots
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
                    
        except Exception as e:
            logger.error(f"Error in pdfplumber fallback extraction: {e}")
            return {}, None, []

    def generate_slides_html(self, pdf_data, presentation_focus, theme="professional", extract_images=True, output_dir=None):
        """Generate HTML slides directly from PDF content in a single step."""
        
        self.presentation_focus = presentation_focus
        
        # Extract images and captions if enabled
        image_captions = {}
        extracted_images_dir = None
        if extract_images and output_dir:
            logger.info("🔍 Extracting images and captions from PDF...")
            image_captions, extracted_images_dir, plots = self._extract_images_and_captions(pdf_data, output_dir)
            
            if image_captions:
                logger.info(f"📸 Found {len(image_captions)} images with captions")
            else:
                logger.info("📸 No images found in PDF")
        
        # Build image context for prompt - integrated format
        image_context = ""
        if image_captions:
            image_context = "\n**Visual Assets:** The following images have been extracted from the PDF with their captions and dimensions:\n"
            for image_id, info in image_captions.items():
                dimensions = info.get('dimensions', 'unknown')
                image_context += f"- {image_id}: {info['caption']} (file: {info['path']}, size: {dimensions})\n"
            image_context += "\n**Integration Instructions:**\n"
            image_context += "- Incorporate these images strategically throughout the presentation\n"
            image_context += "- Use format: `<img src='../extracted_images/image_id.png' alt='caption'>`\n"
            image_context += "- Consider image dimensions for proper layout and positioning\n"
            image_context += "- Place images where they enhance understanding and visual impact\n"
        else:
            image_context = "\n**Visual Assets:** No images were found in the source PDF."
        
        # Updated academic generation prompt
        academic_gen_prompt = f'''<presentation_task>
Create a stunning, visually captivating HTML presentation that makes viewers stop and say "wow" based on this PDF document.

**Purpose of presentation:** {presentation_focus}
**Visual theme:** {theme}
</presentation_task>

<source_materials>
**PDF Content:** The PDF document has been provided and analyzed for content extraction.{image_context}
</source_materials>

<design_philosophy>
CREATE EMOTIONAL IMPACT:
- Prioritize the "wow factor" through cohesive visual storytelling that enhances the core message
- Make every slide feel alive with purposeful, subtle animations that enhance comprehension
- Use a strategic color palette with 3-5 colors that reinforce the {theme} and create visual harmony
- Implement modern design techniques (glassmorphism, gradient overlays) with restraint and purpose
- Balance visual excitement with clarity and readability
- Create a premium experience through thoughtful spacing, alignment, and visual hierarchy
- Ensure every visual element directly supports and elevates the content narrative
- Use visual contrast strategically to create focal points that guide the viewer's attention
</design_philosophy>

<visual_requirements>
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use consistent slide transitions with natural easing (cubic-bezier) for predictable navigation
3. Implement a sophisticated color scheme with intentional contrast ratios (minimum 4.5:1 for text) for the "{theme}" theme
4. Include purposeful micro-interactions that guide attention to key content
5. Use no more than 2 complementary font families with clear hierarchy through weight and size
6. Add depth through subtle shadows and layering (max 3 layers) to create visual interest
7. Target 60-80 words per slide maximum with sequential text reveals
8. Create intuitive navigation with consistent visual feedback on all interactive elements
9. CRITICAL: Use fixed width: 1280px; min-height: 720px; for all slides - maintain horizontal layouts
10. Use background elements that reinforce the theme without competing with content
11. Ensure all content remains within the 1280px × 720px viewport without overflow
12. **HEIGHT-AWARE LAYOUT: Limit vertical content to 650px maximum to ensure visibility**
13. Apply the rule of thirds for content placement to create balanced, visually appealing compositions
14. Use whitespace strategically to create breathing room and highlight important elements
15. Implement a consistent visual grid system (12-column recommended) for alignment across all slides
16. Use visual contrast (size, color, position) to create clear focal points on each slide
17. CRITICAL: Ensure all slides use ONLY opacity-based transitions (.active class with opacity: 1) for navigation
18. Maintain consistent padding (40-60px) around content areas for visual breathing room
19. Use high-quality vector graphics or SVGs when possible for crisp rendering at any scale
20. Implement a cohesive visual language with consistent icon styles, button treatments, and UI elements
21. Create visual hierarchy with a 1.5:1 size ratio between importance levels (headings, body text, captions)
22. Use drop shadows sparingly (2-4px blur, 30-40% opacity) to create subtle depth perception
</visual_requirements>

<motion_design>
- Use consistent animation timing (300-500ms) and easing functions across all elements
- Implement sequential animations with 100-150ms delays between related elements
- Keep background animations subtle (opacity changes of 0.1-0.2 or 1-2px movements)
- Ensure all animations support the content narrative rather than distract from it
- Use entrance animations that build from the bottom up or left to right for natural reading flow
- Limit concurrent animations to 3 elements maximum to prevent visual overload
- Create a signature animation style that appears consistently throughout the presentation
- Use motion to create visual connections between related concepts across slides
- Apply the "less is more" principle: animate only what needs attention
- Use scale transforms (1.0 to 1.05) for subtle emphasis rather than dramatic movements
- CRITICAL: Avoid animations that interfere with slide navigation or content visibility
- Test all animations at different speeds to ensure they enhance rather than hinder comprehension
- Create "reveal" animations that build anticipation and highlight key information
- Use motion to guide the viewer's eye to the most important elements on each slide
</motion_design>

<academic_guidelines>
- Transform complex concepts into visual narratives with clear progression
- Use before/after comparisons with consistent visual language and clear delineation
- Present algorithms as visual flowcharts with consistent iconography and color coding
- Create data visualizations with meaningful color mapping and progressive build-up
- Use visual metaphors consistently throughout the presentation to reinforce key concepts
- Present limitations with balanced visual treatment that doesn't undermine achievements
- Incorporate visual evidence (charts, diagrams, images) to support every major claim
- Use consistent visual language for similar concepts across all slides
- Implement progressive complexity: start simple, then build detail as concepts develop
- Create visual anchors that connect related concepts across multiple slides
- Provide clear visual distinction between facts, hypotheses, and conclusions
- Use color consistently to categorize different types of information
- Create visual summaries that reinforce key takeaways at section endpoints
- Use diagrams to illustrate relationships between concepts rather than explaining them with text
</academic_guidelines>

<content_structure>
- Begin each slide with a clear, concise headline (5-7 words maximum)
- Structure content in digestible chunks with visual separation between concepts
- Use the 1-3-1 principle: one main idea, three supporting points, one conclusion per slide
- Create visual hierarchy through size (1.5:1 ratio between importance levels)
- Use consistent iconography (line weight, style) to represent similar concepts
- Implement progressive disclosure that reveals information in logical sequence
- Create clear visual distinctions between facts, interpretations, and implications
- Ensure every slide has a clear purpose that advances the overall narrative
- Use visual anchors (consistent icons, colors, or shapes) to help viewers track key themes
- Apply the "inverted pyramid" structure: most important information first, details later
- Create visual breadcrumbs that help viewers understand where they are in the narrative
- Use consistent formatting for similar content types (quotes, data, examples)
- Implement a clear information hierarchy with primary, secondary, and tertiary content levels
- Create meaningful transitions between major sections with visual cues
- Use "chunking" to group related information visually (max 3-5 items per group)
- Create visual signposts that indicate transitions between major topics or sections
</content_structure>

<technical_implementation>
- Use standardized CSS class naming convention (.slide, .active, .content, .title)
- Implement smooth opacity transitions (opacity: 0 to opacity: 1) for slide changes
- Ensure all slides use the SAME navigation mechanism for consistency
- Add keyboard navigation (arrow keys) with visual indicators for current slide position
- Implement consistent z-indexing strategy (background: 1-10, content: 11-50, overlays: 51-100)
- Test all animations at 60fps to ensure smooth performance
- CRITICAL: Maintain consistent slide visibility behavior across all slides
- Verify that all interactive elements work consistently throughout the presentation
- IMPORTANT: Use opacity-based transitions ONLY (.active class with opacity: 1) for slide navigation
- DO NOT mix transform-based and opacity-based slide transitions
- CRITICAL: Ensure all slides have position: absolute and are contained within the same parent
- Test navigation with keyboard, mouse clicks, and touch events to ensure universal accessibility
- Implement consistent event listeners for all interactive elements
- Verify that all slides have the same base CSS structure to prevent navigation inconsistencies
- Use CSS variables for consistent theming across all slides (--primary-color, --accent-color, etc.)
- Implement proper event delegation for efficient event handling across all slides
</technical_implementation>

<slide_structure>
- Opening slide: Bold headline, subtle animation revealing key visual, clear purpose statement
- Content progression: Each slide builds on previous knowledge with visual callbacks
- Section dividers: Clear visual breaks between major topic transitions with distinct visual treatment
- Data slides: Maximum of 5 data points per visualization with clear labeling and progressive reveal
- Conclusion slide: 3 key takeaways with visual reinforcement and call to action
- Create a visual thread that connects the opening to the conclusion for narrative coherence
- Use consistent visual language for similar slide types (data, concept, transition)
- Include a visual progress indicator that shows current position in the presentation
- Create visual bookends: opening and closing slides should have thematic visual connection
- Implement a consistent header/footer system with slide numbers and section indicators
- Use clear visual signals for transitions between major sections
- Create a table of contents slide that visually previews the presentation structure
- Include "bridge slides" that connect major sections with visual summaries of previous content
- Design section intro slides that establish visual vocabulary for upcoming content
</slide_structure>

<content_enhancement>
- Transform bullet points into visually engaging elements with icons or small illustrations
- Use metaphorical imagery that reinforces abstract concepts
- Create visual comparisons for contrasting ideas using consistent design elements
- Highlight key statistics with distinctive visual treatment (size, color, animation)
- Use visual storytelling techniques to create emotional connection with the material
- Incorporate meaningful transitions that visually connect related concepts
- Balance text and visuals with a 40/60 ratio (40% text, 60% visual elements)
- Use color psychology intentionally: warm colors for emphasis, cool colors for background
- Create visual mnemonics that help viewers remember key concepts
- Use the "rule of odds" (3, 5, 7) for grouping visual elements to create more appealing compositions
- Convert complex text explanations into visual diagrams, flowcharts, or infographics
- Use consistent visual metaphors throughout the presentation to reinforce key themes
- Create "aha moments" through strategic visual reveals that clarify complex concepts
- Implement visual storytelling techniques that create emotional engagement with the content
- Use "before and after" visual comparisons to demonstrate impact or transformation
- Create visual hierarchies that guide the viewer through complex information in logical sequence
</content_enhancement>

<visual_excellence>
- Create a signature visual style that's consistent yet distinctive for this presentation
- Use a visual rhythm with recurring elements that create cohesion across slides
- Implement the 60-30-10 rule for color distribution (60% primary, 30% secondary, 10% accent)
- Create depth through layering with subtle shadows (2-4px blur, 30-40% opacity)
- Use visual anchors that remain consistent across slide transitions
- Apply the golden ratio (1:1.618) for proportional relationships between elements
- Create focal points through strategic use of contrast, scale, and position
- Use negative space as an active design element, not just empty background
- Implement a consistent visual grid for alignment across all slides
- Create visual harmony through repetition of shapes, colors, and patterns
- Use consistent visual treatment for similar content types across all slides
- Implement a cohesive design system with reusable components and consistent styling
- Create visual emphasis through strategic use of color, size, and position
- Use visual contrast to direct attention to the most important elements on each slide
- Apply the "squint test" to ensure key elements remain visible even when details blur
- Create visual "breathing room" around important content to increase impact
</visual_excellence>

<data_visualization>
- Use consistent color coding across all charts and graphs
- Implement progressive reveals for complex data visualizations
- Limit data points to 5-7 per visualization for clarity
- Use appropriate chart types for different data relationships (bar, line, pie, scatter)
- Include clear, concise labels directly on visualizations
- Maintain consistent scale and units across related visualizations
- Use animation to show data changes or comparisons
- Highlight key insights with visual emphasis (color, size, annotations)
- Provide context for all data through titles and brief explanations
- Use consistent styling for all chart elements (axes, labels, legends)
- Create visual hierarchy within data visualizations to guide understanding
- Use data visualization to tell a clear story, not just display numbers
- Implement progressive disclosure for complex data (start simple, add complexity)
- Use annotations to highlight key insights directly on visualizations
- Create visual comparisons that make data relationships immediately apparent
</data_visualization>


<academic_math_support>
### LaTeX Formula Support:
- Enhanced styling: Add beautiful animations and hover effects to formulas
- Example with delightful styling:
```html
<script>
MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\(', '\)']],
    displayMath: [['$$', '$$'], ['\[', '\]']]
  }},
  options: {{
    processHtmlClass: 'mathjax-enabled'
  }}
}};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
<div class="code mathjax-enabled animate-reveal" style="white-space: pre-line; backdrop-filter: blur(10px); background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px;">
Algorithm with $f_θ$ and loss $L_t = \frac{{1}}{{t}} \delta_{{x_t,m}}$
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

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser with consistent navigation between ALL slides.

CRITICAL: Ensure ALL slides use the SAME navigation mechanism (opacity transitions recommended) and that arrow key navigation works throughout the entire presentation.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.

SLIDE NAVIGATION REQUIREMENTS:
1. All slides MUST use position: absolute within the same container
2. Navigation MUST use ONLY opacity transitions (.active class with opacity: 1)
3. DO NOT use transforms for slide positioning or transitions
4. Ensure keyboard arrow navigation works for ALL slides
5. Maintain consistent z-index strategy across all slides
6. Test all slide transitions to ensure smooth, predictable behavior
</output_requirements>'''
        try:
            logger.info("🔍 Analyzing PDF and generating slides in one step...")
            logger.info("📡 Using streaming for long-running operation...")
            
            # Use streaming for long operations
            stream = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50000,
                temperature=0.7,
                stream=True,
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
            
            # Collect the streamed response
            html_content = ""
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    html_content += chunk.delta.text
                    # Log progress every 1000 characters
                    if len(html_content) % 1000 == 0:
                        logger.info(f"📝 Generated {len(html_content)} characters...")
            
            logger.info(f"✅ Completed generation: {len(html_content)} characters")
            return self.clean_html_content(html_content), None

        except Exception as e:
            return None, f"Error generating slides directly: {str(e)}"
    

    def generate_presentation(self, pdf_source, presentation_focus="A comprehensive overview", theme="professional", slide_count=12, output_dir=str(Config.OUTPUT_DIR), extract_images=True):
        """
        One-step function to generate a presentation from a PDF source with organized file structure.
        
        Args:
            pdf_source: Either a URL to a PDF or a local file path
            presentation_focus: The main focus or theme of the presentation
            theme: Visual theme for the presentation ("professional", "academic", "modern", etc.)
            slide_count: Target number of slides
            output_dir: Output directory for organized files
            extract_images: Whether to extract and include images from the PDF
            
        Returns:
            Dict with result information or None if process failed
        """
        from opencanvas.utils.file_utils import generate_topic_slug, organize_pipeline_outputs
        
        logger.info(f"🚀 Starting PDF presentation generation...")
        logger.info(f"📄 Source: {pdf_source}")
        logger.info(f"🎯 Focus: {presentation_focus}")
        logger.info(f"🎨 Theme: {theme}")
        logger.info(f"📸 Extract images: {extract_images}")
        
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
        
        # Create organized output structure
        paths = create_organized_output_structure(output_path, topic_slug, timestamp)
        
        # Generate slides directly in one step with image extraction if enabled
        html_content, error = self.generate_slides_html(
            pdf_data, 
            presentation_focus,
            theme,
            extract_images=extract_images,
            output_dir=paths['base']
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
            'timestamp': timestamp,
            'extract_images': extract_images
        }
