"""
Configuration settings for the image validation system.
Centralizes all configurable parameters.
"""

import os
from pathlib import Path
from typing import Dict, Any


class ImageValidationConfig:
    """Configuration class for image validation system."""
    
    # Database paths
    DEFAULT_CACHE_DB_PATH = str(Path(__file__).parent / "data" / "topic_images.duckdb")
    DEFAULT_TEST_DB_PATH = str(Path(__file__).parent / "data" / "prompt_tests.duckdb")
    
    # URL validation settings
    URL_VALIDATION_TIMEOUT = float(os.getenv('IMAGE_VALIDATION_TIMEOUT', '3.0'))
    MAX_CONCURRENT_VALIDATIONS = int(os.getenv('MAX_CONCURRENT_VALIDATIONS', '10'))
    
    # Cache settings
    CACHE_TTL_DAYS = int(os.getenv('CACHE_TTL_DAYS', '7'))
    MAX_IMAGES_PER_TOPIC = int(os.getenv('MAX_IMAGES_PER_TOPIC', '3'))
    MIN_CONFIDENCE_SCORE = float(os.getenv('MIN_CONFIDENCE_SCORE', '0.7'))
    
    # Claude settings
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
    CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', '500'))
    CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', '0.3'))
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    
    # Performance settings
    ENABLE_IMAGE_VALIDATION = os.getenv('ENABLE_IMAGE_VALIDATION', 'true').lower() == 'true'
    SLIDE_PROCESSING_TIMEOUT = float(os.getenv('SLIDE_PROCESSING_TIMEOUT', '30.0'))
    
    # Similarity matching
    MIN_TOPIC_SIMILARITY = float(os.getenv('MIN_TOPIC_SIMILARITY', '0.6'))
    MAX_TOPIC_KEYWORDS = int(os.getenv('MAX_TOPIC_KEYWORDS', '5'))
    
    # Image sources configuration
    IMAGE_SOURCES = {
        0: {
            'name': 'unsplash',
            'url_template': 'https://images.unsplash.com/photo-{id}',
            'enabled': True
        },
        1: {
            'name': 'pexels',
            'url_template': 'https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg',
            'enabled': True
        },
        2: {
            'name': 'pixabay',
            'url_template': 'https://cdn.pixabay.com/photo/{id}',
            'enabled': False  # Disabled by default
        }
    }
    
    # Fallback images for different contexts
    FALLBACK_IMAGES = {
        'business': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
        'technology': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176',
        'nature': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
        'data': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
        'team': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c',
        'general': 'https://images.unsplash.com/photo-1557804506-669a67965ba0'
    }
    
    # Maintenance settings
    MAINTENANCE_CLEANUP_DAYS = int(os.getenv('MAINTENANCE_CLEANUP_DAYS', '30'))
    AUTO_CLEANUP_ENABLED = os.getenv('AUTO_CLEANUP_ENABLED', 'false').lower() == 'true'
    MAINTENANCE_LOG_LEVEL = os.getenv('MAINTENANCE_LOG_LEVEL', 'INFO')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('IMAGE_VALIDATION_LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_db_paths(cls) -> Dict[str, str]:
        """Get database paths, creating directories if needed."""
        cache_path = Path(cls.DEFAULT_CACHE_DB_PATH)
        test_path = Path(cls.DEFAULT_TEST_DB_PATH)
        
        # Create data directory if it doesn't exist
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        return {
            'cache_db': str(cache_path),
            'test_db': str(test_path)
        }
    
    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Get URL validation configuration."""
        return {
            'timeout': cls.URL_VALIDATION_TIMEOUT,
            'max_concurrent': cls.MAX_CONCURRENT_VALIDATIONS,
            'enabled_sources': [
                source_id for source_id, config in cls.IMAGE_SOURCES.items()
                if config['enabled']
            ]
        }
    
    @classmethod
    def get_claude_config(cls) -> Dict[str, Any]:
        """Get Claude configuration."""
        return {
            'model': cls.CLAUDE_MODEL,
            'max_tokens': cls.CLAUDE_MAX_TOKENS,
            'temperature': cls.CLAUDE_TEMPERATURE,
            'max_retries': cls.MAX_RETRY_ATTEMPTS
        }
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            'ttl_days': cls.CACHE_TTL_DAYS,
            'max_images_per_topic': cls.MAX_IMAGES_PER_TOPIC,
            'min_confidence': cls.MIN_CONFIDENCE_SCORE,
            'min_similarity': cls.MIN_TOPIC_SIMILARITY,
            'max_keywords': cls.MAX_TOPIC_KEYWORDS
        }
    
    @classmethod
    def validate_environment(cls) -> Dict[str, Any]:
        """Validate environment and return status."""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config_summary': {}
        }
        
        # Check API key
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            status['warnings'].append('ANTHROPIC_API_KEY not set - Claude functionality will be disabled')
        
        # Check database paths
        try:
            db_paths = cls.get_db_paths()
            status['config_summary']['database_paths'] = db_paths
        except Exception as e:
            status['errors'].append(f'Database path configuration error: {e}')
            status['valid'] = False
        
        # Validate numeric settings
        try:
            timeout = cls.URL_VALIDATION_TIMEOUT
            if timeout <= 0 or timeout > 60:
                status['warnings'].append(f'URL validation timeout {timeout}s may be too extreme')
        except (ValueError, TypeError):
            status['errors'].append('Invalid URL_VALIDATION_TIMEOUT value')
            status['valid'] = False
        
        # Check if image validation is enabled
        status['config_summary']['image_validation_enabled'] = cls.ENABLE_IMAGE_VALIDATION
        status['config_summary']['cache_ttl_days'] = cls.CACHE_TTL_DAYS
        status['config_summary']['max_concurrent_validations'] = cls.MAX_CONCURRENT_VALIDATIONS
        
        return status
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary."""
        print("🔧 Image Validation Configuration")
        print("=" * 40)
        
        validation_status = cls.validate_environment()
        
        if validation_status['valid']:
            print("✅ Configuration valid")
        else:
            print("❌ Configuration has errors:")
            for error in validation_status['errors']:
                print(f"  • {error}")
        
        if validation_status['warnings']:
            print("⚠️ Warnings:")
            for warning in validation_status['warnings']:
                print(f"  • {warning}")
        
        print(f"\n📋 Settings:")
        print(f"  • Image validation: {'Enabled' if cls.ENABLE_IMAGE_VALIDATION else 'Disabled'}")
        print(f"  • URL timeout: {cls.URL_VALIDATION_TIMEOUT}s")
        print(f"  • Cache TTL: {cls.CACHE_TTL_DAYS} days")
        print(f"  • Max concurrent: {cls.MAX_CONCURRENT_VALIDATIONS}")
        print(f"  • Claude model: {cls.CLAUDE_MODEL}")
        
        enabled_sources = [s['name'] for s in cls.IMAGE_SOURCES.values() if s['enabled']]
        print(f"  • Image sources: {', '.join(enabled_sources)}")
        
        print(f"\n📁 Database paths:")
        db_paths = cls.get_db_paths()
        print(f"  • Cache: {db_paths['cache_db']}")
        print(f"  • Tests: {db_paths['test_db']}")


# Environment variable documentation
ENV_VARS_HELP = """
Image Validation Environment Variables:

Core Settings:
  ANTHROPIC_API_KEY          - Required for Claude functionality
  ENABLE_IMAGE_VALIDATION    - Enable/disable validation (default: true)
  IMAGE_VALIDATION_TIMEOUT   - URL validation timeout in seconds (default: 3.0)
  MAX_CONCURRENT_VALIDATIONS - Max concurrent validations (default: 10)

Cache Settings:
  CACHE_TTL_DAYS            - Cache entry lifetime in days (default: 7)
  MAX_IMAGES_PER_TOPIC      - Max images cached per topic (default: 3)
  MIN_CONFIDENCE_SCORE      - Minimum confidence for cached images (default: 0.7)

Claude Settings:
  CLAUDE_MODEL              - Claude model to use (default: claude-3-haiku-20240307)
  CLAUDE_MAX_TOKENS         - Max tokens for Claude responses (default: 500)
  CLAUDE_TEMPERATURE        - Claude temperature (default: 0.3)
  MAX_RETRY_ATTEMPTS        - Max retry attempts for Claude calls (default: 3)

Performance Settings:
  SLIDE_PROCESSING_TIMEOUT  - Max time per slide in seconds (default: 30.0)
  MIN_TOPIC_SIMILARITY      - Min similarity for topic matching (default: 0.6)
  MAX_TOPIC_KEYWORDS        - Max keywords per topic (default: 5)

Maintenance Settings:
  MAINTENANCE_CLEANUP_DAYS  - Days to keep old data (default: 30)
  AUTO_CLEANUP_ENABLED      - Enable automatic cleanup (default: false)
  IMAGE_VALIDATION_LOG_LEVEL - Logging level (default: INFO)

Example usage:
  export ANTHROPIC_API_KEY="your-key-here"
  export ENABLE_IMAGE_VALIDATION="true"
  export IMAGE_VALIDATION_TIMEOUT="5.0"
"""

if __name__ == "__main__":
    ImageValidationConfig.print_config_summary()
    print("\n" + ENV_VARS_HELP)