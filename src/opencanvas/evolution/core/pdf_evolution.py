"""
PDF-Based Evolution System - Autonomous improvement for PDF presentation generation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from opencanvas.config import Config

# Import evolution components first to avoid circular dependencies
from .evolution import EvolutionSystem
from .agents import EvolutionAgent
from .tools import ToolsManager, ToolDiscovery
from .prompts import PromptManager
from .improvement_tracker import get_improvement_tracker, ImprovementType
from .agent_wrapper import AgentExecutor, PartialProgressTracker

logger = logging.getLogger(__name__)

# PresentationConverter will be imported conditionally when needed
PresentationConverter = None

class PDFEvolutionSystem(EvolutionSystem):
    """
    PDF-specific evolution system that autonomously improves PDF presentation generation
    through iterative prompt evolution and tool development
    """
    
    def __init__(self, 
                 test_pdf: str,
                 output_dir: str = None,
                 max_iterations: int = 5,
                 improvement_threshold: float = 0.2,
                 diagnostic_mode: bool = False,
                 prompt_only: bool = False,
                 prompts_registry: str = "PROMPTS_REGISTRY.md",
                 theme: str = "academic blue",
                 purpose: str = "academic conference presentation",
                 initial_prompt_path: Optional[str] = None,
                 use_memory: bool = True):
        """Initialize PDF evolution system"""
        
        # Create PDF-specific output directory if not provided
        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"evolution_runs/pdf_tracked_evolution_{timestamp}/evolution"
        
        # Initialize parent with PDF-specific settings
        super().__init__(
            output_dir=output_dir,
            test_topics=[],  # Will be overridden for PDF
            max_iterations=max_iterations,
            improvement_threshold=improvement_threshold,
            diagnostic_mode=diagnostic_mode,
            prompt_only=prompt_only,
            prompts_registry=prompts_registry,
            theme=theme,
            purpose=purpose,
            initial_prompt_path=initial_prompt_path,
            use_memory=use_memory
        )
        
        # PDF-specific configuration
        self.test_pdf = test_pdf
        self.pdf_mode = True
        
        logger.info(f"🔧 Initializing PDFEvolutionSystem with test_pdf={test_pdf}")
        logger.info(f"📁 PDF evolution output: {output_dir}")
        logger.info(f"🎯 Theme: {theme}, Purpose: {purpose}")
        
        # Extract and save initial PDF prompt if this is the first iteration
        if not initial_prompt_path:
            self._extract_and_save_initial_pdf_prompt()
        
        # Initialize PDF cache directory
        self.pdf_cache_dir = self.output_dir / "pdf_cache"
    
    def _extract_and_save_initial_pdf_prompt(self):
        """Extract the hardcoded prompt from PDFGenerator and save as v0"""
        
        logger.info("🔍 Extracting initial PDF prompt from PDFGenerator...")
        
        try:
            # Read the PDFGenerator source file
            from opencanvas.generators.pdf_generator import PDFGenerator
            import inspect
            
            # Get the source code of the generate_slides_html method
            source_code = inspect.getsource(PDFGenerator.generate_slides_html)
            
            # Find the academic_gen_prompt definition
            start_marker = "academic_gen_prompt = f'''"
            end_marker = "'''"
            
            start_idx = source_code.find(start_marker)
            if start_idx == -1:
                raise ValueError("Could not find academic_gen_prompt in PDFGenerator source")
            
            # Find the actual prompt content start
            prompt_start = start_idx + len(start_marker)
            
            # Find the end of the prompt (look for ''' that's not escaped)
            search_pos = prompt_start
            while True:
                end_idx = source_code.find(end_marker, search_pos)
                if end_idx == -1:
                    raise ValueError("Could not find end of academic_gen_prompt")
                
                # Check if this ''' is escaped or part of the prompt content
                # Look for the context to ensure it's the actual end
                if "{image_context}" in source_code[prompt_start:end_idx]:
                    # This looks like the complete prompt
                    break
                search_pos = end_idx + 3
            
            # Extract the prompt content
            initial_prompt = source_code[prompt_start:end_idx].strip()
            
            # Clean up the prompt (remove extra indentation)
            lines = initial_prompt.split('\n')
            if lines and not lines[0].strip():
                lines = lines[1:]  # Remove first empty line
            if lines and not lines[-1].strip():
                lines = lines[:-1]  # Remove last empty line
            
            # Remove common indentation
            if lines:
                min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
                cleaned_lines = []
                for line in lines:
                    if line.strip():
                        cleaned_lines.append(line[min_indent:])
                    else:
                        cleaned_lines.append("")
                initial_prompt = '\n'.join(cleaned_lines)
            
            # Save as v0 prompt (ensure it includes static examples)
            evolved_dir = self.output_dir / "evolved_prompts"
            evolved_dir.mkdir(parents=True, exist_ok=True)
            
            # For PDF mode, ensure initial prompt has static examples
            from .pdf_static_examples import add_static_examples, remove_static_sections
            
            # Remove any existing static sections and add them back to ensure consistency
            clean_prompt = remove_static_sections(initial_prompt)
            complete_initial_prompt = add_static_examples(clean_prompt)
            
            v0_file = evolved_dir / "pdf_generation_prompt_v0.txt"
            v0_file.write_text(complete_initial_prompt)
            
            # Set as initial prompt for evolution
            self.initial_prompt = complete_initial_prompt
            
            logger.info(f"✅ Extracted and saved initial PDF prompt: {v0_file.relative_to(self.output_dir)}")
            logger.info(f"📝 Prompt length: {len(initial_prompt)} characters")
            
        except Exception as e:
            logger.error(f"❌ Failed to extract initial PDF prompt: {e}")
            # Fallback to a basic prompt
            fallback_prompt = """<presentation_task>
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

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser and immediately impresses with its sophisticated visual design and smooth interactions.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
</output_requirements>
{image_context}
"""
            
            # Add static examples to fallback prompt
            from .pdf_static_examples import add_static_examples
            complete_fallback_prompt = add_static_examples(fallback_prompt)
            
            evolved_dir = self.output_dir / "evolved_prompts"
            evolved_dir.mkdir(parents=True, exist_ok=True)
            v0_file = evolved_dir / "pdf_generation_prompt_v0.txt"
            v0_file.write_text(complete_fallback_prompt)
            self.initial_prompt = complete_fallback_prompt
            
            logger.warning(f"⚠️ Using fallback prompt: {v0_file.relative_to(self.output_dir)}")
    
    def _generate_test_presentations(self, iteration_dir: Path, iteration_number: int) -> Dict[str, Any]:
        """Generate test presentations using cached PDF data"""
        
        logger.info(f"🚀 Generating PDF-based test presentation (iteration {iteration_number})")
        
        presentations_dir = iteration_dir / "presentations"
        presentations_dir.mkdir(exist_ok=True)
        
        # Get or cache PDF data once
        pdf_data, image_metadata = self._get_or_cache_pdf_data()
        if not pdf_data:
            error_msg = "Failed to load or cache PDF data"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "presentations": [],
                "errors": [error_msg]
            }
        
        # Determine router type based on iteration
        use_evolved_router = False
        
        if iteration_number == 1:
            # ALWAYS use baseline for iteration 1 to establish baseline
            use_evolved_router = False
            logger.info(f"📦 Iteration 1: using baseline router to establish baseline")
            
        elif iteration_number > 1:
            # For iterations > 1, use evolved router with evolved prompt
            evolved_dir = self.output_dir / "evolved_prompts"
            prev_prompt_file = evolved_dir / f"pdf_generation_prompt_v{iteration_number-1}.txt"
            
            if not prev_prompt_file.exists():
                error_msg = f"PDF Evolution cannot continue: Required prompt file not found: {prev_prompt_file.relative_to(self.output_dir)}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "presentations": [],
                    "errors": [error_msg]
                }
            
            logger.info(f"📝 Found evolved PDF prompt from iteration {iteration_number-1}: {prev_prompt_file.relative_to(self.output_dir)}")
            use_evolved_router = True
        
        if use_evolved_router:
            logger.info(f"📝 Using EVOLVED router for PDF (iteration {iteration_number})")
            from .evolved_router import EvolvedGenerationRouter
            router = EvolvedGenerationRouter(
                api_key=Config.ANTHROPIC_API_KEY,
                brave_api_key=Config.BRAVE_API_KEY,
                evolution_iteration=iteration_number,
                prompt_only=self.prompt_only,
                evolution_output_dir=str(self.output_dir),
                initial_prompt=None,  # Evolved iterations load prompt from file
                pdf_mode=True  # Enable PDF mode
            )
        else:
            logger.info(f"📦 Using BASELINE router for PDF")
            from opencanvas.generators.router import GenerationRouter
            router = GenerationRouter(
                api_key=Config.ANTHROPIC_API_KEY,
                brave_api_key=Config.BRAVE_API_KEY
            )
        
        presentations = []
        errors = []
        
        try:
            # Generate presentation using cached PDF data
            pdf_slug = "test_pdf_presentation"
            pdf_dir = presentations_dir / pdf_slug
            pdf_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy cached images to presentation directory for this iteration
            if image_metadata and "extracted_images_dir" in image_metadata:
                cached_images_dir = Path(image_metadata["extracted_images_dir"])
                iteration_images_dir = pdf_dir / "extracted_images"
                
                if cached_images_dir.exists():
                    logger.info(f"📸 Copying cached images to iteration directory...")
                    iteration_images_dir.mkdir(exist_ok=True)
                    
                    # Copy each cached image
                    for image_file in cached_images_dir.glob("*.png"):
                        dest_file = iteration_images_dir / image_file.name
                        import shutil
                        shutil.copy2(image_file, dest_file)
                    
                    logger.info(f"📸 Copied {len(list(iteration_images_dir.glob('*.png')))} cached images")
            
            # For evolved router (iteration 2+) with cached data, we need to call the PDF generator directly
            # since the router's generate() method would re-download and re-extract
            if use_evolved_router and hasattr(router, 'pdf_generator'):
                # Use the evolved PDF generator directly with cached data
                pdf_generator = router.pdf_generator
                
                # Build image context from cached metadata - integrated format
                image_context = ""
                if image_metadata and image_metadata.get("image_captions"):
                    image_captions_dict = image_metadata["image_captions"]
                    logger.info(f"🖼️ Building image context with {len(image_captions_dict)} images")
                    image_context = "\n**Visual Assets:** The following images have been extracted from the PDF with their captions and dimensions:\n"
                    for image_id, info in image_captions_dict.items():
                        dimensions = info.get('dimensions', 'unknown')
                        # Update path to point to iteration-specific images
                        relative_path = f"../extracted_images/{image_id}.png"
                        image_context += f"- {image_id}: {info['caption']} (file: {relative_path}, size: {dimensions})\n"
                    image_context += "\n**Integration Instructions:**\n"
                    image_context += "- Incorporate these images strategically throughout the presentation\n"
                    image_context += "- Use format: `<img src='../extracted_images/image_id.png' alt='caption'>`\n"
                    image_context += "- Consider image dimensions for proper layout and positioning\n"
                    image_context += "- Place images where they enhance understanding and visual impact\n"
                    logger.info(f"📝 Image context: {len(image_context)} characters")
                else:
                    image_context = "\n**Visual Assets:** No images were found in the source PDF."
                    logger.info("📝 No images in metadata - using 'no images' context")
                
                # Override the evolved prompt to include image context
                if hasattr(pdf_generator, 'evolved_prompt') and pdf_generator.evolved_prompt:
                    try:
                        formatted_prompt = pdf_generator.evolved_prompt.format(
                            presentation_focus=self.purpose,
                            theme=self.theme,
                            image_context=image_context
                        )
                        # Temporarily store the formatted prompt
                        original_prompt = pdf_generator.evolved_prompt
                        pdf_generator.evolved_prompt = formatted_prompt
                        
                        html_content, error = pdf_generator.generate_slides_html(
                            pdf_data=pdf_data,
                            presentation_focus=self.purpose,
                            theme=self.theme,
                            extract_images=False,  # Images already cached and copied
                            output_dir=pdf_dir
                        )
                        
                        # Restore original prompt
                        pdf_generator.evolved_prompt = original_prompt
                    except Exception as e:
                        logger.error(f"❌ Failed to format evolved prompt with cached image context: {e}")
                        html_content, error = pdf_generator.generate_slides_html(
                            pdf_data=pdf_data,
                            presentation_focus=self.purpose,
                            theme=self.theme,
                            extract_images=False,  # Images already cached and copied
                            output_dir=pdf_dir
                        )
                else:
                    html_content, error = pdf_generator.generate_slides_html(
                        pdf_data=pdf_data,
                        presentation_focus=self.purpose,
                        theme=self.theme,
                        extract_images=False,  # Images already cached and copied
                        output_dir=pdf_dir
                    )
                
                if error:
                    errors.append(f"PDF generation failed: {error}")
                    html_content = None
                
                # Create result structure similar to router.generate()
                if html_content:
                    html_file = pdf_dir / "slides" / "slides.html"
                    html_file.parent.mkdir(parents=True, exist_ok=True)
                    html_file.write_text(html_content)
                    
                    result = {
                        'html_file': str(html_file),
                        'html_content': html_content,
                        'pdf_source': self.test_pdf,
                        'presentation_focus': self.purpose,
                        'theme': self.theme,
                        'extract_images': True,
                        'cached_data_used': True
                    }
                else:
                    result = None
                    
            else:
                # For baseline router, fall back to standard generation
                # (will re-download but that's expected for baseline comparison)
                result = router.generate(
                    input_source=self.test_pdf,
                    purpose=self.purpose,
                    theme=self.theme, 
                    output_dir=str(pdf_dir),
                    extract_images=True  # Enable image extraction for PDFs
                )
            
            if result and result.get('html_file'):
                # Convert to PDF if available
                pdf_path = None
                try:
                    from opencanvas.conversion.html_to_pdf import PresentationConverter
                    converter = PresentationConverter(
                        html_file=result['html_file'],
                        output_dir=str(pdf_dir),
                        method="playwright",
                        zoom_factor=1.0,
                        compress_images=True
                    )
                    pdf_path = converter.convert(output_filename="presentation.pdf")
                except ImportError:
                    logger.warning("    ⚠️ PDF conversion skipped - converter not available")
                    pdf_path = None
                
                # Save PDF source for reference-required evaluation (use cached if available)
                source_pdf_path = None
                try:
                    cached_pdf_file = self.pdf_cache_dir / "pdf_data.b64"
                    if cached_pdf_file.exists():
                        # Use cached PDF data
                        import base64
                        pdf_content = base64.b64decode(cached_pdf_file.read_text())
                        source_pdf_path = pdf_dir / "sources" / "source.pdf"
                        source_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(source_pdf_path, 'wb') as f:
                            f.write(pdf_content)
                        logger.info(f"    📄 Saved source PDF from cache: {source_pdf_path.name}")
                    else:
                        # Fallback to download if cache missing
                        import requests
                        response = requests.get(self.test_pdf, timeout=30)
                        if response.status_code == 200:
                            source_pdf_path = pdf_dir / "sources" / "source.pdf"
                            source_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(source_pdf_path, 'wb') as f:
                                f.write(response.content)
                            logger.info(f"    📄 Downloaded and saved source PDF: {source_pdf_path.name}")
                        else:
                            logger.warning(f"    ⚠️ Failed to download source PDF: HTTP {response.status_code}")
                except Exception as e:
                    logger.warning(f"    ⚠️ Failed to save source PDF: {e}")
                
                presentations.append({
                    "topic": f"PDF: {self.test_pdf}",
                    "html_path": result['html_file'],
                    "pdf_path": pdf_path,
                    "source_pdf_path": str(source_pdf_path) if source_pdf_path else None,
                    "output_dir": str(pdf_dir),
                    "result": result,  # Keep full result for reference
                    "cached_data_used": result.get('cached_data_used', False)
                })
            else:
                errors.append(f"PDF generation failed for: {self.test_pdf}")
                
        except Exception as e:
            errors.append(f"Error with PDF {self.test_pdf}: {e}")
            logger.error(f"❌ PDF generation error: {e}")
        
        success = len(presentations) > 0
        logger.info(f"✅ Generated {len(presentations)} PDF presentations ({len(errors)} errors)")
        
        return {
            "success": success,
            "presentations": presentations,
            "errors": errors
        }
    
    def run_evolution_cycle(self, start_iteration: int = 1) -> Dict[str, Any]:
        """Run complete PDF evolution cycle"""
        
        logger.info("="*70)
        logger.info(f"🔄 Starting PDF evolution cycle from iteration {start_iteration}")
        logger.info(f"📄 Test PDF: {self.test_pdf}")
        logger.info(f"🔢 Max iterations: {self.max_iterations}")
        logger.info(f"📊 Improvement threshold: {self.improvement_threshold}")
        logger.info(f"🎨 Theme: {self.theme}")
        logger.info(f"🎯 Purpose: {self.purpose}")
        logger.info("="*70)
        
        # Call parent's run_evolution_cycle
        return super().run_evolution_cycle(start_iteration)
    
    def _get_or_cache_pdf_data(self):
        """Get PDF data and image metadata, using cache if available"""
        
        # Check if cache exists
        cache_file = self.pdf_cache_dir / "pdf_data.b64"
        metadata_file = self.pdf_cache_dir / "image_metadata.json"
        
        if cache_file.exists() and metadata_file.exists():
            logger.info("📦 Loading cached PDF data and images")
            return self._load_cached_pdf_data()
        else:
            logger.info("🔄 First iteration - downloading and caching PDF data")
            return self._cache_pdf_data()
    
    def _cache_pdf_data(self):
        """Download PDF, extract images, and cache everything"""
        
        # Import PDF processing here to avoid dependency issues
        try:
            from opencanvas.generators.pdf_generator import PDFGenerator
        except ImportError:
            logger.error("❌ PDFGenerator not available")
            return None, {}
        
        try:
            # Create temporary PDF generator for download and extraction
            temp_generator = PDFGenerator(Config.ANTHROPIC_API_KEY)
            
            # Download and encode PDF
            logger.info(f"📥 Downloading PDF: {self.test_pdf}")
            if self.test_pdf.startswith(('http://', 'https://')):
                pdf_data, error = temp_generator.encode_pdf_from_url(self.test_pdf)
            else:
                pdf_data, error = temp_generator.encode_pdf_from_file(self.test_pdf)
            
            if error:
                logger.error(f"❌ Failed to encode PDF: {error}")
                return None, {}
            
            # Create cache directory
            self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract images to cache directory
            logger.info("🔍 Extracting images and captions from PDF...")
            extracted_images_dir = self.pdf_cache_dir / "extracted_images"
            extracted_images_dir.mkdir(exist_ok=True)
            
            image_captions, _, plots = temp_generator._extract_images_and_captions(
                pdf_data, 
                self.pdf_cache_dir
            )
            
            # Prepare image metadata for caching
            image_metadata = {
                "image_captions": image_captions,
                "extracted_images_dir": str(extracted_images_dir),
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            # Save PDF data to cache
            cache_file = self.pdf_cache_dir / "pdf_data.b64"
            cache_file.write_text(pdf_data)
            logger.info(f"💾 Cached PDF data: {cache_file}")
            
            # Save image metadata to cache
            metadata_file = self.pdf_cache_dir / "image_metadata.json"
            import json
            try:
                metadata_file.write_text(json.dumps(image_metadata, indent=2))
                logger.info(f"💾 Cached image metadata: {metadata_file}")
            except Exception as json_error:
                logger.error(f"❌ Failed to save image metadata: {json_error}")
                logger.info("🔄 Continuing without metadata cache (will re-extract next time)")
                # Don't fail the entire process - we still have the images and PDF data
            
            if image_captions:
                logger.info(f"📸 Cached {len(image_captions)} images with captions")
                # Debug: Show sample of what was extracted
                sample_images = list(image_captions.keys())[:3]
                for img_id in sample_images:
                    info = image_captions[img_id]
                    logger.info(f"  📷 {img_id}: '{info.get('caption', 'No caption')}' ({info.get('dimensions', 'unknown')})")
            else:
                logger.info("📸 No images found in PDF")
            
            return pdf_data, image_metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to cache PDF data: {e}")
            return None, {}
    
    def _load_cached_pdf_data(self):
        """Load PDF data and image metadata from cache"""
        
        try:
            import json
            
            # Load PDF data
            cache_file = self.pdf_cache_dir / "pdf_data.b64"
            pdf_data = cache_file.read_text()
            
            # Load image metadata
            metadata_file = self.pdf_cache_dir / "image_metadata.json"
            image_metadata = json.loads(metadata_file.read_text())
            
            # Log cache info
            extraction_time = image_metadata.get("extraction_timestamp", "unknown")
            image_count = len(image_metadata.get("image_captions", {}))
            logger.info(f"📦 Loaded cached PDF data (extracted: {extraction_time})")
            logger.info(f"📸 Loaded {image_count} cached images")
            
            return pdf_data, image_metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to load cached PDF data: {e}")
            return None, {}