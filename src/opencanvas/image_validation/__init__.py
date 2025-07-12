"""
Image validation package for OpenCanvas presentation generation.

This package provides comprehensive image validation and replacement capabilities
for generated presentations, including:

- URL validation with efficient caching
- Claude-based image retrieval with multiple prompt strategies
- Topic-based image caching using DuckDB
- HTML parsing and context analysis
- Intelligent image replacement
- Performance tracking and analytics

Main entry point: ImageValidationPipeline
"""

from .image_validator import ImageValidationPipeline
from .topic_image_cache import TopicImageCache
from .url_validator import URLValidator
from .claude_image_retriever import ClaudeImageRetriever
from .html_parser import SlideImageParser
from .image_replacer import ImageReplacer
from .prompt_tester import PromptSuccessTracker
from .cache_utils import CacheMaintenanceUtils
from .config import ImageValidationConfig

__all__ = [
    'ImageValidationPipeline',
    'TopicImageCache',
    'URLValidator', 
    'ClaudeImageRetriever',
    'SlideImageParser',
    'ImageReplacer',
    'PromptSuccessTracker',
    'CacheMaintenanceUtils',
    'ImageValidationConfig'
]

__version__ = '1.0.0'