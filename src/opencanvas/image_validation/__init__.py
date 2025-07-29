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

from opencanvas.image_validation.image_validator import ImageValidationPipeline
from opencanvas.image_validation.topic_image_cache import TopicImageCache
from opencanvas.image_validation.url_validator import URLValidator
from opencanvas.image_validation.claude_image_retriever import ClaudeImageRetriever
from opencanvas.image_validation.html_parser import SlideImageParser
from opencanvas.image_validation.image_replacer import ImageReplacer
from opencanvas.image_validation.prompt_tester import PromptSuccessTracker
from opencanvas.image_validation.cache_utils import CacheMaintenanceUtils
from opencanvas.image_validation.config import ImageValidationConfig

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