"""
Wrapper for image-based slide generation - uses composition, doesn't modify existing generators
"""
import os
import logging
from pathlib import Path
from opencanvas.generators.topic_generator import TopicGenerator
from opencanvas.generators.pdf_generator import PDFGenerator
from opencanvas.generators.image_generator import ImageSlideGenerator
from opencanvas.config import Config

logger = logging.getLogger(__name__)

class ImagePresentationGenerator:
    """
    Wrapper class for generating presentations as images.
    Uses composition pattern - doesn't modify existing generators.
    """
    
    def __init__(self, anthropic_key=None, gemini_key=None, brave_api_key=None):
        """Initialize with API keys"""
        self.anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        self.gemini_key = gemini_key or os.getenv('GEMINI_API_KEY')
        self.brave_api_key = brave_api_key or os.getenv('BRAVE_API_KEY')
        
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY is required for image generation")
        
        # Initialize generators
        self.topic_generator = TopicGenerator(
            api_key=self.anthropic_key,
            brave_api_key=self.brave_api_key
        )
        self.image_generator = ImageSlideGenerator(
            anthropic_key=self.anthropic_key,
            gemini_key=self.gemini_key
        )
        
        logger.info("✅ Image presentation generator initialized")
    
    def generate_from_topic(self, topic, purpose, theme="academic", output_dir=None):
        """
        Generate image-based presentation from a topic.
        
        Uses existing TopicGenerator for content creation,
        then ImageSlideGenerator for rendering.
        """
        logger.info(f"🎨 Generating image presentation from topic: {topic}")
        
        output_dir = output_dir or str(Config.OUTPUT_DIR)
        
        # Step 1: Use existing TopicGenerator to create blog content
        # We'll extract just the blog generation part
        logger.info("📝 Generating blog content...")
        
        # Knowledge assessment
        knowledge_assessment = self.topic_generator.assess_knowledge_depth(topic)
        logger.info(f"📊 Knowledge assessment: {knowledge_assessment}")
        
        additional_context = None
        if knowledge_assessment == "INSUFFICIENT":
            logger.info("🔍 Performing web research...")
            search_query = self.topic_generator.generate_search_query(topic)
            search_results = self.topic_generator.web_search(search_query, self.brave_api_key)
            
            if search_results:
                best_sources = self.topic_generator.assess_source_credibility(search_results)
                if best_sources:
                    additional_context_parts = []
                    for i, source in enumerate(best_sources[:2]):
                        scraped_content = self.topic_generator.scrape_web_content(source.get('link'))
                        if scraped_content:
                            additional_context_parts.append(
                                f"Source {i+1} - {source.get('title', 'Unknown')}:\n{scraped_content}"
                            )
                    if additional_context_parts:
                        additional_context = "\n\n" + "="*50 + "\n\n".join(additional_context_parts)
        
        # Generate blog
        blog_content = self.topic_generator.generate_blog(topic, additional_context)
        if not blog_content:
            logger.error("❌ Failed to generate blog content")
            return None
        
        logger.info("✅ Blog content generated")
        
        # Step 2: Generate slides as images (saves incrementally)
        logger.info("🖼️  Generating slide images...")
        
        from opencanvas.utils.file_utils import generate_topic_slug
        from datetime import datetime
        
        topic_slug = generate_topic_slug(topic)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        result = self.image_generator.generate_slides_images(
            blog_content, 
            purpose, 
            theme,
            output_dir=output_dir,
            topic_slug=topic_slug,
            timestamp=timestamp
        )
        
        # Convert slides to PDF
        logger.info("📄 Converting slides to PDF...")
        pdf_path = self.image_generator.convert_slides_to_pdf(
            result['slide_paths'],
            result['base_dir'],
            filename="presentation.pdf"
        )
        result['pdf_path'] = pdf_path
        
        logger.info(f"✅ Image presentation complete!")
        logger.info(f"📁 Output: {result['slides_dir']}")
        logger.info(f"📄 PDF: {pdf_path}")
        
        return result
    
    def generate_from_pdf(self, pdf_source, purpose, theme="academic", output_dir=None, extract_images=True, use_extracted_images=True):
        """
        Generate image-based presentation from a PDF document.
        
        Extracts content and images from PDF, then generates slides as images.
        
        Args:
            pdf_source: PDF URL or file path
            purpose: Presentation purpose
            theme: Visual theme
            output_dir: Output directory
            extract_images: Whether to extract images from PDF
            use_extracted_images: Whether to use extracted images in slides (default: True)
        """
        from opencanvas.generators.pdf_generator import PDFGenerator
        from opencanvas.utils.file_utils import generate_topic_slug
        from datetime import datetime
        import base64
        import os
        

        logger.info(f"🎨 Generating image presentation from PDF: {pdf_source}")
        
        output_dir = output_dir or str(Config.OUTPUT_DIR)
        
        # Initialize PDF generator for extraction
        pdf_gen = PDFGenerator(self.anthropic_key)
        
        # Step 1: Download/load and encode PDF
        logger.info("📥 Loading PDF...")
        if pdf_source.startswith(('http://', 'https://')):
            pdf_data, error = pdf_gen.encode_pdf_from_url(pdf_source)
        else:
            pdf_data, error = pdf_gen.encode_pdf_from_file(pdf_source)
        
        if error:
            logger.error(f"❌ Failed to load PDF: {error}")
            return None
        
        # Step 2: Extract text content for blog generation
        logger.info("📝 Extracting content from PDF...")
        # Use Claude to extract and summarize PDF content
        pdf_bytes = base64.b64decode(pdf_data)
        
        # Create a temporary file for content extraction
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
        
        try:
            # Extract text using pdfplumber
            import pdfplumber
            pdf_text = ""
            with pdfplumber.open(temp_pdf_path) as pdf:
                for page in pdf.pages:
                    pdf_text += page.extract_text() or ""
            
            # Generate blog content from PDF text
            logger.info("📝 Generating blog content from PDF...")
            blog_content = self.topic_generator.generate_blog(
                f"Create a presentation about this research paper:\n\n{pdf_text[:10000]}",  # Limit to first 10k chars
                additional_context=None
            )
            
            if not blog_content:
                logger.error("❌ Failed to generate blog content from PDF")
                return None
            
            logger.info("✅ Blog content generated")
            
            # Create timestamp and topic slug early for consistent directory structure
            topic_slug = generate_topic_slug(pdf_source.split('/')[-1].replace('.pdf', ''))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_output_dir = os.path.join(output_dir, f"{topic_slug}_{timestamp}")
            
            # Step 3: Extract images if enabled
            extracted_images_info = None
            if extract_images:
                logger.info("🖼️  Extracting images from PDF...")
                image_captions, extracted_images_dir, plots = pdf_gen._extract_images_and_captions(
                    pdf_data, 
                    timestamped_output_dir  # Use timestamped directory
                )
                
                # Debug logging
                logger.info(f"🔍 Debug: image_captions={type(image_captions)}, plots={type(plots)}, len(plots)={len(plots)}")
                
                if plots:
                    logger.info(f"✅ Extracted {len(plots)} images")
                    extracted_images_info = {
                        'image_captions': image_captions,
                        'extracted_images_dir': extracted_images_dir,
                        'plots': plots
                    }
                else:
                    logger.info("ℹ️  No images extracted from PDF")
            
            # Step 4: Generate slides as images
            logger.info("🖼️  Generating slide images...")
            
            # Prepare extracted figures in the format expected by image_generator
            extracted_figures = None
            if extract_images and extracted_images_info and extracted_images_info.get('plots'):
                extracted_figures = extracted_images_info['plots']  # Already in correct format with 'path' and 'caption'
                logger.info(f"📊 Passing {len(extracted_figures)} figures to slide generator")
            
            result = self.image_generator.generate_slides_images(
                blog_content,
                purpose,
                theme,
                output_dir=output_dir,
                topic_slug=topic_slug,
                timestamp=timestamp,
                extracted_figures=extracted_figures,
                use_extracted_images=use_extracted_images
            )
            
            # Add extracted images info to result
            if extracted_images_info:
                result['extracted_images'] = extracted_images_info
            
            # Convert slides to PDF
            logger.info("📄 Converting slides to PDF...")
            pdf_path = self.image_generator.convert_slides_to_pdf(
                result['slide_paths'],
                result['base_dir'],
                filename="presentation.pdf"
            )
            result['pdf_path'] = pdf_path
            
            logger.info(f"✅ Image presentation complete!")
            logger.info(f"📁 Output: {result['slides_dir']}")
            logger.info(f"📄 PDF: {pdf_path}")
            if extracted_images_info:
                logger.info(f"🖼️  Extracted images: {extracted_images_dir}")
            
            return result
            
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)

def generate_image_presentation(topic, purpose="academic presentation", theme="academic", output_dir=None):
    """
    Convenience function to generate image-based presentation.
    
    Example:
        result = generate_image_presentation(
            "AI in Healthcare",
            purpose="academic presentation"
        )
    """
    generator = ImagePresentationGenerator()
    return generator.generate_from_topic(topic, purpose, theme, output_dir)
