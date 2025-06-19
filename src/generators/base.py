from abc import ABC, abstractmethod
import webbrowser
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """Abstract base class for presentation generators"""
    
    def __init__(self, api_key):
        """Initialize generator with API key"""
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
    
    @abstractmethod
    def generate_slides_html(self, content, purpose, theme):
        """Generate HTML slides from content - must be implemented by subclasses"""
        pass
    
    def save_html_file(self, html_content, filename=None):
        """Save HTML content to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"slides_{timestamp}.html"
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML file saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving HTML file: {e}")
            return None

    def open_in_browser(self, filename):
        """Open HTML file in browser"""
        try:
            file_path = Path(filename).resolve()
            webbrowser.open(f"file://{file_path}")
            logger.info(f"Opened in browser: {filename}")
            return True
        except Exception as e:
            logger.error(f"Could not open browser: {e}")
            return False
    
    def clean_html_content(self, html_content):
        """Clean up HTML content if wrapped in code blocks"""
        if html_content.strip().startswith("```html"):
            html_content = html_content.strip()[7:-3].strip()
        elif html_content.strip().startswith("```"):
            html_content = html_content.strip()[3:-3].strip()
        
        return html_content