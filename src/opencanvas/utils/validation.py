import re
from pathlib import Path
from urllib.parse import urlparse
import mimetypes

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_pdf_url(url):
        """Validate if the URL points to a PDF file"""
        try:
            # Check URL format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"

            # Check if URL ends with .pdf
            if url.lower().endswith('.pdf'):
                return True, "Valid PDF URL"

            return False, "URL does not appear to point to a PDF file"

        except Exception as e:
            return False, f"Error validating URL: {str(e)}"

    @staticmethod
    def validate_pdf_file(file_path):
        """Validate if the file is a PDF"""
        try:
            file_path = Path(file_path)

            # Check if file exists
            if not file_path.exists():
                return False, "File does not exist"

            # Check file extension
            if file_path.suffix.lower() != '.pdf':
                return False, "File is not a PDF (wrong extension)"

            # Check MIME type
            # Use absolute path for URI conversion
            absolute_path = file_path.resolve()
            mime_type, _ = mimetypes.guess_type(absolute_path.as_uri())
            if mime_type != 'application/pdf':
                return False, "File MIME type is not 'application/pdf'"

            # Check file size (limit to 100MB for safety)
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, "PDF file is too large (>100MB)"

            return True, "Valid PDF file"

        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    @staticmethod
    def validate_html_file(file_path):
        """Validate if the file is an HTML file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, "File does not exist"
            
            if file_path.suffix.lower() not in ['.html', '.htm']:
                return False, "File is not an HTML file"
            
            return True, "Valid HTML file"
            
        except Exception as e:
            return False, f"Error validating HTML file: {str(e)}"
    
    @staticmethod
    def validate_theme(theme):
        """Validate theme name"""
        if not theme or not isinstance(theme, str):
            return False, "Theme must be a non-empty string"
        
        # Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', theme):
            return False, "Theme contains invalid characters"
        
        return True, "Valid theme"
    
    @staticmethod
    def validate_purpose(purpose):
        """Validate purpose text"""
        if not purpose or not isinstance(purpose, str):
            return False, "Purpose must be a non-empty string"
        
        if len(purpose.strip()) < 3:
            return False, "Purpose is too short"
        
        return True, "Valid purpose"
    
    @staticmethod
    def validate_zoom_factor(zoom):
        """Validate zoom factor for PDF conversion"""
        try:
            zoom_float = float(zoom)
            if zoom_float <= 0 or zoom_float > 3.0:
                return False, "Zoom factor must be between 0.1 and 3.0"
            return True, "Valid zoom factor"
        except (ValueError, TypeError):
            return False, "Zoom factor must be a number"