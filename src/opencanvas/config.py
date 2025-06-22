import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the presentation toolkit"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Default settings
    DEFAULT_THEME = os.getenv('DEFAULT_THEME', 'professional blue')
    DEFAULT_PURPOSE = os.getenv('DEFAULT_PURPOSE', 'general presentation')
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'output'))
    
    # Models
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-7-sonnet-20250219')
    CLAUDE_ASSESSMENT_MODEL = os.getenv('CLAUDE_ASSESSMENT_MODEL', 'claude-sonnet-4-20250514')
    
    # Conversion settings
    DEFAULT_ZOOM = float(os.getenv('DEFAULT_ZOOM', '1.2'))
    DEFAULT_CONVERSION_METHOD = os.getenv('DEFAULT_CONVERSION_METHOD', 'selenium')
    
    # Evaluation settings
    EVALUATION_MODEL = os.getenv('EVALUATION_MODEL', 'claude-3-5-sonnet-20241022')
    EVALUATION_PROVIDER = os.getenv('EVALUATION_PROVIDER', 'claude')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        # Create output directory if it doesn't exist
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        
        return True