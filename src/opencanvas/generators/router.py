from pathlib import Path
from urllib.parse import urlparse
import logging

from opencanvas.generators.topic_generator import TopicGenerator
from opencanvas.generators.pdf_generator import PDFGenerator
from opencanvas.utils.validation import InputValidator

logger = logging.getLogger(__name__)

class GenerationRouter:
    """Router to determine appropriate generator based on input type"""
    
    def __init__(self, api_key=None, brave_api_key=None):
        """Initialize router with both generators"""
        self.topic_generator = TopicGenerator(api_key, brave_api_key)
        self.pdf_generator = PDFGenerator(api_key)
    
    def detect_input_type(self, input_source: str) -> str:
        """Detect if input is PDF URL, PDF file, or topic text"""
        logger.debug(f"Detecting input type for: {input_source}")
        
        # Check if it's a URL ending in .pdf
        if input_source.startswith(('http://', 'https://')):
            if 'pdf' in input_source.lower():
                is_valid, msg = InputValidator.validate_pdf_url(input_source)
                if is_valid:
                    logger.info(f"Detected PDF URL: {input_source}")
                    return 'pdf_url'
                else:
                    logger.warning(f"Invalid PDF URL: {msg}")
        
        # Check if it's a local PDF file
        path = Path(input_source)
        if path.exists() and path.suffix.lower() == '.pdf':
            is_valid, msg = InputValidator.validate_pdf_file(input_source)
            if is_valid:
                logger.info(f"Detected PDF file: {input_source}")
                return 'pdf_file'
            else:
                logger.warning(f"Invalid PDF file: {msg}")
        
        # Otherwise assume it's a topic
        logger.info(f"Detected topic text: {input_source[:50]}...")
        return 'topic'
    
    def generate(self, input_source: str, purpose: str, theme: str, output_dir: str = 'output'):
        """Route to appropriate generator based on input type"""
        logger.info(f"Starting generation with router")
        logger.info(f"Input: {input_source}")
        logger.info(f"Purpose: {purpose}")
        logger.info(f"Theme: {theme}")
        
        # Validate inputs
        is_valid, msg = InputValidator.validate_purpose(purpose)
        if not is_valid:
            raise ValueError(f"Invalid purpose: {msg}")
        
        is_valid, msg = InputValidator.validate_theme(theme)
        if not is_valid:
            raise ValueError(f"Invalid theme: {msg}")
        
        # Detect input type and route appropriately
        input_type = self.detect_input_type(input_source)
        
        try:
            if input_type in ['pdf_url', 'pdf_file']:
                logger.info("Routing to PDF generator")
                return self.pdf_generator.generate_presentation(
                    pdf_source=input_source,
                    presentation_focus=purpose,
                    theme=theme,
                    output_dir=output_dir
                )
            else:
                logger.info("Routing to topic generator")
                return self.topic_generator.generate_from_topic(
                    user_text=input_source,
                    purpose=purpose,
                    theme=theme,
                    output_dir=output_dir
                )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise