"""
Main image validation pipeline that integrates all components.
Post-processes slides from topic_generator to validate and replace failed images.
"""

import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from .topic_image_cache import TopicImageCache
from .url_validator import URLValidator
from .claude_image_retriever import ClaudeImageRetriever
from .html_parser import SlideImageParser
from .image_replacer import ImageReplacer

logger = logging.getLogger(__name__)


class ImageValidationPipeline:
    """Main pipeline for validating and replacing images in presentation slides."""
    
    def __init__(
        self, 
        anthropic_api_key: Optional[str] = None,
        cache_db_path: Optional[str] = None,
        enable_validation: bool = True
    ):
        """
        Initialize the validation pipeline.
        
        Args:
            anthropic_api_key: API key for Claude (from env if not provided)
            cache_db_path: Path to cache database
            enable_validation: Whether to enable validation (for testing)
        """
        self.enable_validation = enable_validation
        
        if not self.enable_validation:
            return
        
        # Get API key from environment if not provided
        if not anthropic_api_key:
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                logger.warning("No Anthropic API key provided. Image validation disabled.")
                self.enable_validation = False
                return
        
        # Initialize components
        try:
            self.cache = TopicImageCache(cache_db_path)
            self.validator = URLValidator()
            self.retriever = ClaudeImageRetriever(anthropic_api_key, self.cache)
            self.parser = SlideImageParser()
            self.replacer = ImageReplacer()
            
            logger.info("Image validation pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize image validation pipeline: {e}")
            self.enable_validation = False
    
    def validate_and_fix_slides(
        self, 
        slides: List[Dict],
        timeout_per_slide: float = 30.0
    ) -> Tuple[List[Dict], Dict]:
        """
        Validate and fix images in presentation slides.
        
        Args:
            slides: List of slide dictionaries with 'html' content
            timeout_per_slide: Maximum time to spend per slide
            
        Returns:
            Tuple of (updated_slides, validation_report)
        """
        if not self.enable_validation:
            logger.info("Image validation disabled, returning original slides")
            return slides, {'status': 'disabled', 'message': 'Validation disabled'}
        
        start_time = time.time()
        report = {
            'total_slides': len(slides),
            'processed_slides': 0,
            'total_images_checked': 0,
            'failed_images_found': 0,
            'successful_replacements': 0,
            'claude_calls_made': 0,
            'cache_hits': 0,
            'processing_time_seconds': 0,
            'slides_with_changes': 0,
            'errors': []
        }
        
        updated_slides = []
        
        for i, slide in enumerate(slides):
            slide_start = time.time()
            
            try:
                # Process single slide with timeout
                updated_slide, slide_stats = self._process_single_slide(
                    slide, 
                    timeout_per_slide
                )
                
                updated_slides.append(updated_slide)
                
                # Update report
                report['processed_slides'] += 1
                report['total_images_checked'] += slide_stats.get('images_checked', 0)
                report['failed_images_found'] += slide_stats.get('failed_images', 0)
                report['successful_replacements'] += slide_stats.get('replacements_made', 0)
                report['claude_calls_made'] += slide_stats.get('claude_calls', 0)
                report['cache_hits'] += slide_stats.get('cache_hits', 0)
                
                if slide_stats.get('changes_made', False):
                    report['slides_with_changes'] += 1
                
                # Log progress
                processing_time = time.time() - slide_start
                logger.info(f"Processed slide {i+1}/{len(slides)} in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error processing slide {i+1}: {e}")
                report['errors'].append(f"Slide {i+1}: {str(e)}")
                # Add original slide if processing fails
                updated_slides.append(slide)
        
        report['processing_time_seconds'] = time.time() - start_time
        
        logger.info(f"Image validation completed: {report['successful_replacements']} images replaced in {report['processing_time_seconds']:.2f}s")
        
        return updated_slides, report
    
    def _process_single_slide(
        self, 
        slide: Dict, 
        timeout: float
    ) -> Tuple[Dict, Dict]:
        """
        Process a single slide for image validation and replacement.
        
        Args:
            slide: Slide dictionary with 'html' content
            timeout: Processing timeout
            
        Returns:
            Tuple of (updated_slide, processing_stats)
        """
        slide_start = time.time()
        html_content = slide.get('html', '')
        
        stats = {
            'images_checked': 0,
            'failed_images': 0,
            'replacements_made': 0,
            'claude_calls': 0,
            'cache_hits': 0,
            'changes_made': False
        }
        
        if not html_content.strip():
            return slide, stats
        
        # Step 1: Extract images from HTML
        images = self.parser.extract_images_from_html(html_content)
        stats['images_checked'] = len(images)
        
        if not images:
            return slide, stats
        
        # Step 2: Validate image URLs
        image_urls = [img['src'] for img in images if img['src']]
        
        if not image_urls:
            return slide, stats
        
        # Check timeout
        if time.time() - slide_start > timeout:
            logger.warning(f"Slide processing timeout reached during URL extraction")
            return slide, stats
        
        validation_results = self.validator.validate_batch(image_urls)
        
        # Step 3: Identify failed images
        failed_urls = [
            result['url'] for result in validation_results 
            if not result['valid']
        ]
        
        stats['failed_images'] = len(failed_urls)
        
        if not failed_urls:
            # All images are valid
            return slide, stats
        
        # Check timeout
        if time.time() - slide_start > timeout:
            logger.warning(f"Slide processing timeout reached during validation")
            return slide, stats
        
        # Step 4: Analyze failed images for context
        failed_image_analysis = self.parser.analyze_failed_images(html_content, failed_urls)
        
        # Step 5: Get replacement images
        replacement_images = {}  # topic -> [(image_id, source), ...]
        
        for failed_img in failed_image_analysis:
            topic = failed_img['replacement_topic']
            
            if topic not in replacement_images:
                # Check cache first
                cached_images = self.cache.get_images_for_topic(topic, limit=3)
                
                if cached_images:
                    replacement_images[topic] = cached_images
                    stats['cache_hits'] += 1
                else:
                    # Use Claude to generate new images
                    try:
                        slide_context = failed_img.get('slide_context', '')
                        new_images = self.retriever.get_images_with_fallback(topic, slide_context)
                        
                        if new_images:
                            replacement_images[topic] = new_images
                            stats['claude_calls'] += 1
                        else:
                            # No images found, will use fallback
                            replacement_images[topic] = []
                            
                    except Exception as e:
                        logger.error(f"Error generating images for topic '{topic}': {e}")
                        replacement_images[topic] = []
            
            # Check timeout
            if time.time() - slide_start > timeout:
                logger.warning(f"Slide processing timeout reached during image generation")
                break
        
        # Step 6: Create replacement list
        replacements = self.replacer.create_replacement_list(
            failed_image_analysis,
            replacement_images
        )
        
        # Step 7: Replace images in HTML
        if replacements:
            updated_html, replacement_stats = self.replacer.replace_failed_images(
                html_content,
                replacements
            )
            
            stats['replacements_made'] = replacement_stats['successful_replacements']
            stats['changes_made'] = replacement_stats['successful_replacements'] > 0
            
            # Update slide with new HTML
            updated_slide = slide.copy()
            updated_slide['html'] = updated_html
            
            return updated_slide, stats
        
        return slide, stats
    
    def validate_single_presentation(
        self, 
        slides: List[Dict],
        presentation_title: str = "Unknown"
    ) -> Dict:
        """
        Quick validation of a presentation without making changes.
        
        Args:
            slides: List of slide dictionaries
            presentation_title: Title for logging
            
        Returns:
            Validation report
        """
        if not self.enable_validation:
            return {'status': 'disabled'}
        
        report = {
            'presentation_title': presentation_title,
            'total_slides': len(slides),
            'total_images': 0,
            'valid_images': 0,
            'invalid_images': 0,
            'validation_details': [],
            'images_by_domain': {},
            'recommendations': []
        }
        
        all_urls = []
        
        # Extract all image URLs
        for i, slide in enumerate(slides):
            html_content = slide.get('html', '')
            images = self.parser.extract_images_from_html(html_content)
            
            slide_urls = [img['src'] for img in images if img['src']]
            all_urls.extend(slide_urls)
            
            report['validation_details'].append({
                'slide_index': i,
                'slide_id': slide.get('id', f'slide_{i}'),
                'image_count': len(slide_urls),
                'image_urls': slide_urls
            })
        
        report['total_images'] = len(all_urls)
        
        if all_urls:
            # Validate all URLs
            validation_results = self.validator.validate_batch(all_urls)
            
            valid_count = sum(1 for r in validation_results if r['valid'])
            report['valid_images'] = valid_count
            report['invalid_images'] = len(all_urls) - valid_count
            
            # Group by domain
            for result in validation_results:
                if result['url']:
                    domain = result['url'].split('/')[2] if '://' in result['url'] else 'unknown'
                    if domain not in report['images_by_domain']:
                        report['images_by_domain'][domain] = {'total': 0, 'valid': 0}
                    
                    report['images_by_domain'][domain]['total'] += 1
                    if result['valid']:
                        report['images_by_domain'][domain]['valid'] += 1
            
            # Generate recommendations
            if report['invalid_images'] > 0:
                report['recommendations'].append(
                    f"Found {report['invalid_images']} invalid images that should be replaced"
                )
            
            cache_stats = self.cache.get_stats()
            if cache_stats['total_topics'] > 0:
                report['recommendations'].append(
                    f"Cache contains {cache_stats['total_topics']} topics with {cache_stats['valid_images']} validated images"
                )
        
        return report
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics."""
        if not self.enable_validation:
            return {'status': 'disabled'}
        
        try:
            cache_stats = self.cache.get_stats()
            validator_stats = self.validator.get_validation_stats()
            prompt_stats = self.retriever.get_prompt_stats()
            
            return {
                'cache': cache_stats,
                'validator': validator_stats,
                'prompts': prompt_stats,
                'system_health': {
                    'cache_hit_rate': cache_stats.get('weekly_hit_rate', 0),
                    'avg_prompt_success': sum(
                        p.get('success_rate', 0) for p in prompt_stats.values()
                    ) / len(prompt_stats) if prompt_stats else 0,
                    'total_validations_cached': cache_stats.get('total_images', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def cleanup_system(self, days: int = 30) -> Dict:
        """Clean up old cache entries and test data."""
        if not self.enable_validation:
            return {'status': 'disabled'}
        
        try:
            cache_cleaned = self.cache.cleanup_expired(days)
            validator_cleaned = self.validator.clear_cache()
            
            return {
                'cache_entries_removed': cache_cleaned,
                'validator_cache_cleared': True,
                'cleanup_date': time.time()
            }
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {'error': str(e)}