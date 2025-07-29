import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for the presentation toolkit"""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Default settings
    DEFAULT_THEME = os.getenv('DEFAULT_THEME', 'professional blue')
    DEFAULT_PURPOSE = os.getenv('DEFAULT_PURPOSE', 'general presentation')
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'output'))
    
    # Models
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-7-sonnet-20250219')
    CLAUDE_ASSESSMENT_MODEL = os.getenv('CLAUDE_ASSESSMENT_MODEL', 'claude-sonnet-4-20250514')
    
    # Conversion settings
    DEFAULT_ZOOM = float(os.getenv('DEFAULT_ZOOM', '1.2'))
    DEFAULT_CONVERSION_METHOD = os.getenv('DEFAULT_CONVERSION_METHOD', 'playwright')
    
    # Evaluation settings with smart defaults
    EVALUATION_PROVIDER = os.getenv('EVALUATION_PROVIDER', 'gemini')
    _EVALUATION_MODEL = os.getenv('EVALUATION_MODEL', 'gemini-2.5-flash')
    
    @classmethod
    @property
    def EVALUATION_MODEL(cls):
        """Get evaluation model with provider validation"""
        provider = cls.EVALUATION_PROVIDER.lower()
        model = cls._EVALUATION_MODEL
        
        # Validate model matches provider
        if provider == 'claude':
            if model.startswith('gpt-') or model.startswith('o1-') or model.startswith('gemini-'):
                logger.warning(f"Claude provider specified but non-Claude model '{model}' configured. Using default Claude model.")
                return 'claude-3-5-sonnet-20241022'
            return model
        elif provider == 'gpt':
            if model.startswith('claude-') or model.startswith('gemini-'):
                logger.warning(f"GPT provider specified but non-GPT model '{model}' configured. Using default GPT model.")
                return 'gpt-4o-mini'
            return model
        elif provider == 'gemini':
            if model.startswith('claude-') or model.startswith('gpt-') or model.startswith('o1-'):
                logger.warning(f"Gemini provider specified but non-Gemini model '{model}' configured. Using default Gemini model.")
                return 'gemini-2.5-flash'
            return model
        else:
            logger.warning(f"Unknown provider '{provider}'. Defaulting to Gemini.")
            return 'gemini-2.5-flash'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # Only require ANTHROPIC_API_KEY if we're using Claude for evaluation
        if cls.EVALUATION_PROVIDER == 'claude' and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude evaluation")
        
        # Validate evaluation setup
        if cls.EVALUATION_PROVIDER == 'gpt' and not cls.OPENAI_API_KEY:
            logger.warning("GPT evaluation provider selected but OPENAI_API_KEY not provided. Evaluation will fail.")
        elif cls.EVALUATION_PROVIDER == 'gemini' and not cls.GEMINI_API_KEY:
            logger.warning("Gemini evaluation provider selected but GEMINI_API_KEY not provided. Evaluation will fail.")
        
        # Create output directory if it doesn't exist
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def get_evaluation_config(cls):
        """Get evaluation configuration with proper API key"""
        provider = cls.EVALUATION_PROVIDER.lower()
        
        if provider == 'claude':
            return {
                'provider': 'claude',
                'model': cls.EVALUATION_MODEL,
                'api_key': cls.ANTHROPIC_API_KEY
            }
        elif provider == 'gpt':
            return {
                'provider': 'gpt', 
                'model': cls.EVALUATION_MODEL,
                'api_key': cls.OPENAI_API_KEY
            }
        elif provider == 'gemini':
            return {
                'provider': 'gemini',
                'model': cls.EVALUATION_MODEL,
                'api_key': cls.GEMINI_API_KEY
            }
        else:
            raise ValueError(f"Unsupported evaluation provider: {provider}")