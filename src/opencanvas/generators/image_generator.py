"""
Image-based slide generator using Gemini multimodal model
"""
import os
import json
from pathlib import Path
from anthropic import Anthropic
from google import genai
from datetime import datetime
import logging
import io
from PIL import Image

logger = logging.getLogger(__name__)

class ImageSlideGenerator:
    """MVP: Generate slides as images using Gemini"""
    
    def __init__(self, anthropic_key, gemini_key):
        """Initialize with both API keys"""
        self.claude = Anthropic(api_key=anthropic_key)
        
        # Initialize Google GenAI client (new API)
        self.genai_client = genai.Client(api_key=gemini_key)
        # Use Gemini 3 Pro Image Preview for image generation
        self.model_name = 'gemini-3-pro-image-preview'
    
    def generate_slides_images(self, blog_content, purpose, theme, output_dir=None, topic_slug=None, timestamp=None, extracted_figures=None, use_extracted_images=True):
        """
        Generate presentation slides as images with varied layouts.
        
        Args:
            blog_content: Content to present
            purpose: Presentation purpose
            theme: Visual theme/style (minimalist, passionate, cartoon, etc.)
            output_dir: Output directory
            topic_slug: Topic identifier
            timestamp: Timestamp for folder naming
            extracted_figures: List of extracted figures from PDF (optional)
            use_extracted_images: Whether to use extracted figures in slides (default: True)
        """
        import time
        from datetime import datetime
        
        logger.info("🎨 Starting image-based slide generation...")
        
        output_dir = output_dir or str(Config.OUTPUT_DIR)
        
        # Create output structure
        from datetime import datetime
        from opencanvas.utils.file_utils import generate_topic_slug
        
        topic_slug = topic_slug or generate_topic_slug(blog_content[:50])
        timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        base_dir = Path(output_dir) / f"{topic_slug}_{timestamp}"
        slides_dir = base_dir / "slides"
        sources_dir = base_dir / "sources"
        
        slides_dir.mkdir(parents=True, exist_ok=True)
        sources_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Output directory: {slides_dir}")
        
        # Step 1: Generate style settings for the chosen theme
        style_settings = self._generate_style_settings(theme)
        logger.info(f"🎨 Style: {theme}")
        
        # Step 2: Plan slide blueprints with layout variations
        blueprints = self._plan_blueprints(
            blog_content, 
            purpose,
            extracted_figures=extracted_figures,
            use_extracted_images=use_extracted_images
        )
        logger.info(f"📋 Planned {len(blueprints)} slides")
        
        # Save intermediate results
        with open(sources_dir / "blog_content.txt", "w") as f:
            f.write(blog_content)
        logger.info("💾 Saved blog content: blog_content.txt")
        
        with open(sources_dir / "slide_blueprints.json", "w") as f:
            json.dump(blueprints, f, indent=2)
        logger.info("💾 Saved blueprints: slide_blueprints.json")
        
        with open(sources_dir / "style_settings.txt", "w") as f:
            f.write(style_settings)
        logger.info("💾 Saved style settings: style_settings.txt")
        
        # Step 3: Generate images for each slide
        slide_paths = []
        style_reference = None  # Will be set to slide 2
        
        for i, blueprint in enumerate(blueprints, 1):
            logger.info(f"🖼️  Generating slide {i}/{len(blueprints)}...")
            
            # Generate slide image with style settings
            slide_image = self._generate_slide_image(
                blueprint, 
                style_settings=style_settings,
                style_ref=style_reference,
                extracted_figures=extracted_figures
            )
            
            # Save immediately (incremental saving)
            slide_filename = f"slide_{blueprint['slide_number']:03d}.png"
            slide_path = slides_dir / slide_filename
            
            with open(slide_path, 'wb') as f:
                f.write(slide_image)
            
            slide_paths.append(slide_path)
            logger.info(f"💾 Saved: {slide_filename}")
            
            # Capture slide 2 as style reference for consistency
            if i == 2:
                style_reference = slide_image
                logger.info("✨ Captured Slide 2 as style anchor")
            
            # Progressive rate limiting
            if i < len(blueprints):
                if i % 5 == 0:
                    logger.info("⏸️  Extra wait after 5 slides: 30s...")
                    time.sleep(30)
                else:
                    logger.info("⏸️  Waiting 15s to respect rate limits...")
                    time.sleep(15)
        
        logger.info(f"✅ All {len(slide_paths)} slides generated and saved!")
        
        return {
            'base_dir': base_dir,
            'slides_dir': slides_dir,
            'slide_paths': slide_paths
        }
    
    def _generate_style_settings(self, theme):
        """Generate style settings based on the chosen theme"""
        
        style_templates = {
            "minimalist": """- Tone: Academic elegance - clean, sophisticated, scholarly
- Color Palette:
  * Base: #F5F0E8 (warm beige/cream) or #FAF7F2 (lighter cream)
  * Text: #1B3A52 (deep navy blue) for headings, #2C3E50 (dark slate) for body
  * Accent: #D4AF37 (muted gold) or #C9A961 (warm gold) for highlights and diagrams
  * Secondary: #8B9DC3 (soft blue-gray) for supporting elements
  * Diagram Lines: Mix of #D4AF37 (gold), #8B9DC3 (blue-gray), and #C4C4C4 (light gray)
- Typography:
  * Headings: Clean sans-serif (Helvetica, Arial, SF Pro). Bold (700), large and commanding
  * Subheadings: Same font family, Medium (500-600), slightly smaller
  * Body: Sans-serif, Regular (400), comfortable reading size
  * Authors/Credits: Smaller, lighter weight (300-400)
- Layout Principles:
  * Whitespace: Generous margins (80-100px), breathing room around all elements
  * Alignment: Center-aligned for title slides, left-aligned for content
  * Grid: Invisible grid for precise alignment
  * Two-column layouts: 50:50 split with vertical divider or clear separation
  * Diagrams: Integrated seamlessly, not as afterthoughts
- Visual Elements:
  * Network Diagrams: Nodes as circles, connecting lines in gold/blue-gray
  * Icons: Simple, outlined, minimal detail
  * Illustrations: Line-based, elegant, not cartoonish
  * Dividers: Thin horizontal lines or subtle spacing
  * Emphasis: Underlines, bold text, or gold highlights - never garish
- Special Notes:
  * Maintain academic credibility - professional, not playful
  * Diagrams should feel integral to the design, not pasted on
  * Use the warm beige background to create a sophisticated, approachable feel
  * Navy + gold color combination conveys authority and elegance""",
            
            "corporate": """- Tone: Professional, trustworthy, polished business aesthetic
- Color Palette:
  * Base: #FFFFFF (white) or #F8F9FA (light gray)
  * Text: #212529 (dark gray)
  * Accent: #0056B3 (corporate blue) or #28A745 (success green)
  * Special: Subtle gradients for depth and sophistication
- Typography:
  * Headings: Professional sans-serif (Arial, Calibri). Clean and authoritative
  * Body: Sans-serif. Clear, readable, business-appropriate
- Layout: Balanced grids, professional spacing, structured hierarchy""",
            
            "academic": """- Tone: Scholarly, precise, authoritative research aesthetic
- Color Palette:
  * Base: #FFFFFF (white) or #F5F5F5 (off-white)
  * Text: #000000 (black) or #2C2C2C (dark gray)
  * Accent: #003366 (navy blue) or #8B0000 (dark red)
  * Special: Subtle backgrounds for data emphasis
- Typography:
  * Headings: Serif (Georgia, Times New Roman). Traditional and scholarly
  * Body: Serif or clean sans-serif. Academic readability standards
- Layout: Traditional grids, formal spacing, clear hierarchical structure""",
            
            "creative": """- Tone: Bold, artistic, visually striking and innovative
- Color Palette:
  * Base: #FFFFFF (white) or gradient backgrounds
  * Text: #1A1A1A (near black)
  * Accent: #FF6B6B (coral), #4ECDC4 (turquoise), #FFE66D (yellow), #9B59B6 (purple)
  * Special: Vibrant color blocks, artistic gradients
- Typography:
  * Headings: Display fonts (Playfair Display, Bebas Neue). Large and dramatic
  * Body: Modern sans-serif. Clean with personality
- Layout: Asymmetrical compositions, dynamic spacing, artistic freedom""",
            
            "tech": """- Tone: Modern, innovative, cutting-edge technology aesthetic
- Color Palette:
  * Base: #0A0E27 (dark blue) or #FFFFFF (white)
  * Text: #E0E0E0 (light gray) on dark, #1A1A1A on light
  * Accent: #00D9FF (cyan), #7B2FFF (electric purple), #00FF88 (neon green)
  * Special: Dark mode with neon accents, futuristic glows
- Typography:
  * Headings: Geometric sans-serif (Rajdhani, Orbitron). Futuristic and precise
  * Body: Monospace or clean sans-serif. Technical clarity
- Layout: Grid-based with tech elements, wireframes, data visualization focus""",
            
            "cartoon": """- Tone: Playful, friendly, approachable and fun
- Color Palette:
  * Base: #FFF9E6 (warm cream) or #E8F4F8 (light sky blue)
  * Text: #2C3E50 (soft dark blue-gray) for readability
  * Accent: #FF6B6B (coral pink), #4ECDC4 (turquoise), #FFE66D (sunny yellow), #95E1D3 (mint green)
  * Special: Bright, cheerful color blocks and playful gradients
- Typography:
  * Headings: Rounded sans-serif (Nunito, Quicksand, Comic Neue). Friendly and bold
  * Body: Rounded sans-serif. Comfortable, casual reading
  * Numbers/Data: Playful, rounded figures
- Layout Principles:
  * Whitespace: Generous but playful, not rigid
  * Shapes: Rounded corners everywhere - circles, rounded rectangles
  * Alignment: Casual but organized, not perfectly rigid
  * Balance: Friendly asymmetry with visual interest
- Visual Elements:
  * Icons: Rounded, filled style with soft shadows
  * Illustrations: Simple, cute, hand-drawn feel
  * Characters: Friendly mascots or simple character illustrations
  * Shapes: Organic, rounded, soft edges
  * Diagrams: Colorful, simplified, easy to understand
  * Emphasis: Bright color highlights, speech bubbles, fun callouts
- Special Notes:
  * Keep it light and approachable - not childish, but friendly
  * Use bright colors generously but harmoniously
  * Illustrations should feel hand-drawn or playful, not corporate
  * Perfect for educational content, presentations for general audiences
  * Conveys warmth, accessibility, and enthusiasm"""
        }
        
        # Return the style settings for the chosen theme, default to minimalist
        return style_templates.get(theme.lower(), style_templates["minimalist"])
    
    def _format_figures_for_prompt(self, extracted_figures):
        """Format extracted figures for Claude prompt"""
        if not extracted_figures or len(extracted_figures) == 0:
            return "No figures available from PDF."
        
        formatted = []
        for i, fig in enumerate(extracted_figures):
            # PlotInfo is a dataclass, use attribute access
            caption = fig.caption if fig.caption else 'No caption available'
            # Truncate long captions
            if len(caption) > 200:
                caption = caption[:197] + "..."
            formatted.append(f"Figure {i}: {caption}")
        
        return "\n".join(formatted)
    
    def convert_slides_to_pdf(self, slide_paths, output_dir, filename="presentation.pdf"):
        """
        Convert generated PNG slides to a single PDF file.
        
        Args:
            slide_paths: List of Path objects to PNG files
            output_dir: Directory to save the PDF
            filename: Name of the output PDF file
            
        Returns:
            Path to the generated PDF file
        """
        from PIL import Image
        
        logger.info(f"📄 Converting {len(slide_paths)} slides to PDF...")
        
        # Load all images
        images = []
        for slide_path in slide_paths:
            img = Image.open(slide_path)
            # Convert to RGB if necessary (PDF doesn't support RGBA)
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                images.append(rgb_img)
            else:
                images.append(img.convert('RGB'))
        
        # Save as PDF
        pdf_path = Path(output_dir) / filename
        if images:
            images[0].save(
                pdf_path,
                save_all=True,
                append_images=images[1:],
                resolution=100.0,
                quality=95
            )
            logger.info(f"✅ PDF created: {pdf_path}")
            return pdf_path
        else:
            raise Exception("No images to convert to PDF")
    
    def _plan_blueprints(self, blog_content, purpose, extracted_figures=None, use_extracted_images=True):
        """Use Claude to plan slide structure with sophisticated layout variations
        
        Args:
            blog_content: Content to present
            purpose: Presentation purpose
            extracted_figures: List of extracted figures from PDF (optional)
            use_extracted_images: Whether to assign figures to slides (default: True)
        """
        
        planning_prompt = f"""Analyze this blog content and create a slide-by-slide blueprint for a presentation.

Blog Content:
{blog_content}

Purpose: {purpose}

GLOBAL DESIGN SETTINGS:
- Tone: Professional, architectural, sharp-edged minimalism
- Color Palette:
  * Base: #E9E9E9 (light gray) or #FFFFFF (white)
  * Text: #000000 (jet black) or #333333 (dark gray)
  * Accent: #000000 (black) - bold lines and emphasized text
  * Special: Dark mode (black background) for emphasis slides
- Typography:
  * Headings: Sans-serif (Helvetica, Inter). Bold and decoratively positioned
  * Body: Gothic typeface. Small size with generous letter spacing
- Navigation: Small section number (e.g., '01. INTRODUCTION') in top-left/right
- Grid: Strict grid system for alignment
- Whitespace: Large empty areas for luxury feel

LAYOUT VARIATIONS (Choose appropriate layout for each slide):
1. Title Typography: Scattered layout, award badges/keywords like stamps, small bold title
2. Text + Data Emphasis: Asymmetrical split, text left, oversized numbers right, thin dividers
3. Card Grid: Tightly spaced grid of images with text overlay
4. Full-Screen Graphic: Photography occupying full/half screen, small caption bottom-left
5. Photo + List Split: 50:50, left photo, right data list (bold headings + light descriptions)
6. Minimal Map: Silhouette-style map with thin callout lines
7. Vertical Timeline: Thin vertical line with text branching left/right
8. Bubble Chart/Venn: Wireframe style, thin lines, semi-transparent circles
9. Dialogue (Chat): Minimal conversational format, simple text blocks with bold names
10. Chronological List: Large years left, descriptions right, strong font contrast
11. Network Diagram: Thin lines, constellation/network appearance with connected nodes
12. 3-Step Columns: Typography-driven, large numbers (01,02,03) as pillars
13. Logo Grid: Monochrome grid, logos in strict alignment
14. Two Columns (Problem vs Solution): Thick vertical divider, block text
15. Centered Layout: Small visual centered, emotional tagline
16. Formula/Flow: Mathematical style, 'A × B = C' in large serif, minimal arrows
17. Arrow Steps: Linear process, text inside large arrows, high contrast
18. Chart: Precision data, thin lines with small dots, scientific appearance


Create a JSON array with 10-12 slides. For EACH slide specify:
- slide_number: int
- slide_type: "opening", "content", or "ending"
- layout_type: string (choose from variations above, e.g., "Title Typography", "Text + Data Emphasis")
- title: string (concise, 5-7 words max)
- content: string (substantive, detailed content - provide depth and specific information, not superficial bullet points)
- visual_notes: string (describe specific visual elements: diagrams, charts, icons, illustrations, data visualizations)
- figure_ids: array of ints or null (indices of figures from PDF to use, 0-based, e.g., [0, 2] or null if no figures)
- figure_usage: string or null ("primary" for main visuals, "reference" for supporting, or null)

IMPORTANT: 
- Vary the layouts across slides - don't use the same layout repeatedly
- Match layout to content type (data → charts, timeline → vertical timeline, etc.)
- Use dark mode layouts sparingly for emphasis
- Ensure visual rhythm and variety throughout presentation
- Content should be substantive with depth - avoid shallow, generic statements
- Include specific visual elements (diagrams, charts, icons) to complement text
- Balance text with visual elements - not text-only slides
- Maintain a clear storyline and logical flow that connects slides into a coherent narrative

Output ONLY valid JSON array, no markdown formatting.

Example:
[
  {{
    "slide_number": 1,
    "slide_type": "opening",
    "layout_type": "Title Typography",
    "title": "AI in Healthcare",
    "content": "Transforming Patient Care Through Technology",
    "visual_notes": "Medical cross icon, scattered tech badges, minimalist stamps",
    "figure_ids": null,
    "figure_usage": null
  }},
  {{
    "slide_number": 2,
    "slide_type": "content",
    "layout_type": "Text + Data Emphasis",
    "title": "Market Growth",
    "content": "Healthcare AI market experiencing unprecedented expansion\\n• 45% compound annual growth rate (2023-2028)\\n• $20B total addressable market\\n• 500+ active startups globally\\n• Major investments from tech giants",
    "visual_notes": "Oversized '45%' in black on right side, thin vertical divider line, growth arrow graphic",
    "figure_id": 0,
    "figure_usage": "primary"
  }},
  ...
]
"""
        
        # Add figures section if available
        if use_extracted_images and extracted_figures:
            figures_info = self._format_figures_for_prompt(extracted_figures)
            planning_prompt += f"""

AVAILABLE FIGURES FROM PDF:
{figures_info}

FIGURE SELECTION STRATEGY:
You can assign figures to slides, but be STRATEGIC and SELECTIVE:

Selection Criteria:
- ONLY assign figures that directly support or enhance the slide's core message
- Each figure should add unique value - avoid repetitive or similar figures
- If multiple figures are assigned to ONE slide, they must be COMPLEMENTARY (showing different aspects)
- Quality over quantity - it's better to use 2-3 perfect matches than force many mediocre ones

Assignment Rules:
- Set figure_ids to an array of indices (0-based) of relevant figures, e.g., [0, 2] or null if no figures needed
- You can assign MULTIPLE figures to one slide if they show complementary aspects (e.g., [7, 8] for related charts)
- Set figure_usage to "primary" if figures are the main visual elements (e.g., key diagrams, critical data)
- Set figure_usage to "reference" if figures provide supporting context (e.g., supplementary charts)
- Match figures to slides based on caption content relevance to slide topic
- NOT every slide needs figures - only use when they genuinely enhance understanding

Quality Checks:
- Do these figures directly illustrate the slide's main point?
- Are these figures different enough from already-assigned figures?
- If assigning multiple figures to one slide, do they show complementary aspects (not redundant)?
- Would the slide be significantly better WITH these figures than without?
- If you're unsure, leave figure_ids as null
"""
        

        response = self.claude.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            temperature=0.3,
            messages=[{"role": "user", "content": planning_prompt}]
        )
        
        # Parse JSON response
        json_text = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if "```" in json_text:
            # Extract content between code blocks
            parts = json_text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    json_text = part[4:].strip()
                    break
                elif part.startswith("["):
                    json_text = part
                    break
        
        # Try to parse JSON
        try:
            blueprints = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Problematic JSON text (first 1000 chars): {json_text[:1000]}")
            
            # Try to fix common issues
            # Remove trailing commas before closing brackets
            import re
            json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
            
            # Try to find and extract just the JSON array
            match = re.search(r'\[\s*\{.*\}\s*\]', json_text, re.DOTALL)
            if match:
                json_text = match.group(0)
                try:
                    blueprints = json.loads(json_text)
                    logger.info("✅ Successfully parsed JSON after cleanup")
                except:
                    raise e
            else:
                raise e
        
        # Validate figure assignments if figures were provided
        if extracted_figures and len(extracted_figures) > 0:
            slides_with_figures = [bp for bp in blueprints if bp.get('figure_ids') and len(bp.get('figure_ids', [])) > 0]
            if len(slides_with_figures) == 0:
                logger.error(f"❌ VALIDATION FAILED: {len(extracted_figures)} figures were extracted but NONE were assigned to slides!")
                logger.error(f"This indicates the figure selection prompt is not working correctly.")
                raise ValueError(f"No figures assigned in blueprint despite {len(extracted_figures)} figures available")
            else:
                logger.info(f"✅ Figure assignment validation passed: {len(slides_with_figures)} slides assigned figures")
        

        return blueprints
    
    def _generate_slide_image(self, blueprint, style_settings="", style_ref=None, extracted_figures=None):
        """Generate single slide image with Gemini
        
        Args:
            blueprint: Slide blueprint with content and layout
            style_settings: Theme style settings
            style_ref: Reference image for style consistency
            extracted_figures: List of extracted figures from PDF (optional)
        """
        
        # Build text prompt with style settings
        prompt = self._build_prompt(blueprint, style_settings, has_reference=bool(style_ref))
        
        # Prepare content for Gemini
        content_parts = [prompt]
        
        # Add reference image if available (for style consistency)
        if style_ref:
            # Convert bytes to PIL Image for Google GenAI
            ref_image = Image.open(io.BytesIO(style_ref))
            content_parts.append(ref_image)
        
        # Add figures if assigned in blueprint
        if extracted_figures and blueprint.get('figure_ids') is not None:
            figure_ids = blueprint['figure_ids']
            if isinstance(figure_ids, list) and len(figure_ids) > 0:
                usage = blueprint.get('figure_usage', 'primary')
                loaded_figures = []
                
                for fig_id in figure_ids:
                    if 0 <= fig_id < len(extracted_figures):
                        try:
                            # Load figure image from PlotInfo (has image_data as bytes)
                            fig_data = extracted_figures[fig_id].image_data
                            if fig_data:
                                figure_image = Image.open(io.BytesIO(fig_data))
                                content_parts.append(figure_image)
                                loaded_figures.append(fig_id)
                            else:
                                logger.warning(f"  ⚠️  Figure {fig_id} has no image data, skipping")
                        except Exception as e:
                            logger.warning(f"  ⚠️  Error loading Figure {fig_id}: {e}")
                    else:
                        logger.warning(f"  ⚠️  Figure {fig_id} out of range (0-{len(extracted_figures)-1})")
                
                # Update prompt if any figures were loaded
                if loaded_figures:
                    if usage == 'primary':
                        if len(loaded_figures) == 1:
                            prompt += "\n\nINCLUDE THE PROVIDED FIGURE as the main visual element. Integrate it seamlessly into the slide design while maintaining the overall theme and style."
                        else:
                            prompt += f"\n\nINCLUDE THE {len(loaded_figures)} PROVIDED FIGURES as the main visual elements. Integrate them seamlessly into the slide design while maintaining the overall theme and style. Arrange them in a complementary layout."
                    elif usage == 'reference':
                        if len(loaded_figures) == 1:
                            prompt += "\n\nREFERENCE THE PROVIDED FIGURE in your design as supporting visual content alongside other elements."
                        else:
                            prompt += f"\n\nREFERENCE THE {len(loaded_figures)} PROVIDED FIGURES in your design as supporting visual content alongside other elements."
                    
                    # Update content_parts with modified prompt
                    content_parts[0] = prompt
                    
                    logger.info(f"  📊 Using Figures {loaded_figures} ({usage})")
        
        # Generate image using Google GenAI client
        response = self.genai_client.models.generate_content(
            model=self.model_name,
            contents=content_parts
        )
        
        # Extract image from response - correct API structure
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Get image bytes directly from inline_data
                    image_bytes = part.inline_data.data
                    # Convert to PIL Image and back to PNG bytes
                    image = Image.open(io.BytesIO(image_bytes))
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue()
        
        raise Exception(f"Failed to generate image - no image in response. Response: {response}")
    
    def _build_prompt(self, blueprint, style_settings, has_reference=False):
        """Build prompt to implement the layout chosen during planning"""
        
        # Get layout details from blueprint (already chosen by Claude)
        layout_type = blueprint.get('layout_type', 'Text + Data Emphasis')
        
        consistency_note = ""
        if has_reference:
            consistency_note = """
CRITICAL: Match the reference image's visual style exactly:
- Same color palette and design system
- Same aesthetic
"""
        
        prompt = f"""Generate a presentation slide image.

SPECIFICATIONS:
- Size: 1920x1080 pixels (16:9)
- Navigation: '{blueprint['slide_number']:02d}. {blueprint['title'].upper()}' in bottom-right corner

STYLE SETTINGS:
{style_settings}

LAYOUT: {layout_type}

CONTENT:
Slide {blueprint['slide_number']}
Title: {blueprint['title']}
Content: {blueprint['content']}
Visual Elements: {blueprint.get('visual_notes', '')}

{consistency_note}

Implement the layout precisely with the specified content and style settings.
"""
        
        return prompt
    
    def _get_layout_instructions(self, layout_type):
        """Get specific instructions for each layout type"""
        
        layout_instructions = {
            "Title Typography": """
- Scattered layout with keywords/badges placed like stamps
- Central title should be small, bold, and restrained
- Use generous whitespace
- Minimal, decorative text placement
""",
            "Text + Data Emphasis": """
- Asymmetrical split: narrative text on left, oversized numbers (black) on right
- Include thin divider lines
- Strong contrast between text and data
- Numbers should be very large and bold
""",
            "Card Grid": """
- Tightly spaced grid of cards/images
- Text appears on hover effect (suggest with subtle overlay)
- Web-like interaction feel
- Uniform spacing and alignment
""",
            "Full-Screen Graphic": """
- Photography or graphic occupying full screen or more than half
- Reduce saturation for cool tone
- Very small caption in bottom-left corner
- Minimal text overlay
""",
            "Photo + List Split": """
- 50:50 split layout
- Left: architectural or abstract photography
- Right: data list with bold English headings + light-weight descriptions
- Generous spacing, avoid overcrowding
""",
            "Minimal Map": """
- Silhouette-style map
- Light gray background with white map
- Ultra-thin callout lines to indicate locations
- Clean, minimal aesthetic
""",
            "Vertical Timeline": """
- Single thin vertical line as axis
- Text branches left and right
- Clean chronological order
- Strong visual rhythm
""",
            "Bubble Chart/Venn": """
- Wireframe style
- Black background with thin white line art
- Semi-transparent overlapping circles
- Network or constellation appearance
""",
            "Dialogue (Chat)": """
- Minimal conversational format
- NOT comic speech bubbles
- Simple text blocks with bold speaker names
- Clean, modern messaging aesthetic
""",
            "Chronological List": """
- Rhythmic list format
- Large years (e.g., 2024) on the left
- Descriptions on the right
- Strong contrast in font sizes
""",
            "Dark Mode Diagram": """
- Intellectual tech aesthetic
- Black background with thin white lines
- Nodes connected by fine lines
- Constellation or network-like appearance
- Geometric patterns expressing tech + creativity fusion
""",
            "3-Step Columns": """
- Typography-driven columns
- Large numbers (01, 02, 03) act as visual pillars
- NO icons - rely on typographic contrast
- Strong vertical rhythm
""",
            "Logo Grid": """
- Monochrome grid
- All logos converted to black or gray
- Strict grid alignment
- Uniform spacing
""",
            "Two Columns (Problem vs Solution)": """
- Sharp contrast
- Thick black vertical line separates 'Problem' and 'Solution'
- Text aligned in block form
- Clear visual division
""",
            "Centered Layout (Dark)": """
- Cinematic feel
- Small visual/video thumbnail centered on black background
- Emotional English tagline
- Dramatic, focused composition
""",
            "Formula/Flow": """
- Mathematical style
- Expressions like 'A × B = C' in large serif type
- Minimal arrows
- Scientific, precise aesthetic
""",
            "Arrow Steps": """
- Linear process flow
- Text placed inside large arrows
- High contrast (black arrows with white text)
- Clear directional flow
""",
            "Chart": """
- Precision data visualization
- Thin lines ending in small black dots
- Scientific instrument-like appearance
- Clean, minimal chart design
"""
        }
        
        return layout_instructions.get(layout_type, """
- Use structured layout with clear hierarchy
- Follow minimalist design principles
- Generous whitespace
- Sharp, architectural aesthetic
""")
    
    def _get_context(self, blueprints):
        """Get full presentation context for reference"""
        context = "Full Presentation:\n"
        for bp in blueprints:
            context += f"Slide {bp['slide_number']}: {bp['title']}\n"
        return context
    
    def save_slides(self, slide_images, output_dir, topic_slug, timestamp):
        """Save slide images to organized directory"""
        
        # Create output structure
        base_dir = Path(output_dir) / f"{topic_slug}_{timestamp}"
        slides_dir = base_dir / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)
        
        # Save each slide
        slide_paths = []
        for i, image_bytes in enumerate(slide_images, 1):
            slide_path = slides_dir / f"slide_{i:03d}.png"
            with open(slide_path, 'wb') as f:
                f.write(image_bytes)
            slide_paths.append(slide_path)
            logger.info(f"💾 Saved: {slide_path}")
        
        logger.info(f"✅ All slides saved to: {slides_dir}")
        return {
            'base_dir': base_dir,
            'slides_dir': slides_dir,
            'slide_paths': slide_paths
        }
