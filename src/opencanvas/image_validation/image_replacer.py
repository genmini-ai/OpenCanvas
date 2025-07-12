"""
Image replacement system for swapping failed URLs with validated alternatives.
Maintains HTML structure while replacing invalid image sources.
"""

import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)


class ImageReplacer:
    """Replace failed image URLs in HTML content with validated alternatives."""
    
    def __init__(self):
        """Initialize the image replacer."""
        # Common image attributes to preserve
        self.preserve_attributes = [
            'alt', 'title', 'class', 'id', 'style', 'width', 'height',
            'loading', 'decoding', 'sizes', 'srcset', 'data-*'
        ]
        
        # Default fallback images for different contexts
        self.fallback_images = {
            'business': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
            'technology': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176',
            'nature': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
            'data': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71',
            'team': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c',
            'general': 'https://images.unsplash.com/photo-1557804506-669a67965ba0'
        }
    
    def replace_failed_images(
        self,
        html_content: str,
        replacements: List[Dict]
    ) -> Tuple[str, Dict]:
        """
        Replace failed images in HTML with new URLs.
        
        Args:
            html_content: Original HTML content
            replacements: List of replacement dictionaries with:
                - original_src: Original failed URL
                - new_src: New replacement URL
                - alt_text: Optional new alt text
                - preserve_attributes: Whether to keep original attributes
        
        Returns:
            Tuple of (updated_html, replacement_stats)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        stats = {
            'total_replacements': 0,
            'successful_replacements': 0,
            'failed_replacements': 0,
            'images_removed': 0,
            'replacements_detail': []
        }
        
        # Build replacement mapping
        replacement_map = {r['original_src']: r for r in replacements}
        
        # Find and replace images
        for img_tag in soup.find_all('img'):
            original_src = img_tag.get('src', '')
            
            if original_src in replacement_map:
                replacement = replacement_map[original_src]
                stats['total_replacements'] += 1
                
                try:
                    success = self._replace_single_image(img_tag, replacement)
                    
                    if success:
                        stats['successful_replacements'] += 1
                        stats['replacements_detail'].append({
                            'original': original_src,
                            'new': replacement.get('new_src', ''),
                            'method': 'replacement',
                            'success': True
                        })
                    else:
                        stats['failed_replacements'] += 1
                        stats['replacements_detail'].append({
                            'original': original_src,
                            'new': '',
                            'method': 'removal',
                            'success': False
                        })
                        
                except Exception as e:
                    logger.error(f"Error replacing image {original_src}: {e}")
                    stats['failed_replacements'] += 1
        
        return str(soup), stats
    
    def _replace_single_image(self, img_tag: Tag, replacement: Dict) -> bool:
        """
        Replace a single image tag.
        
        Args:
            img_tag: BeautifulSoup img tag
            replacement: Replacement configuration
            
        Returns:
            True if successful, False otherwise
        """
        new_src = replacement.get('new_src')
        
        if not new_src:
            # Remove the image if no replacement available
            img_tag.decompose()
            return False
        
        # Update src attribute
        img_tag['src'] = new_src
        
        # Update alt text if provided
        if 'alt_text' in replacement and replacement['alt_text']:
            img_tag['alt'] = replacement['alt_text']
        
        # Preserve or update other attributes
        if replacement.get('preserve_attributes', True):
            # Keep existing attributes, just update src
            pass
        else:
            # Clean attributes and add only essential ones
            essential_attrs = ['src', 'alt']
            attrs_to_remove = [attr for attr in img_tag.attrs if attr not in essential_attrs]
            for attr in attrs_to_remove:
                del img_tag[attr]
        
        # Add additional attributes if specified
        if 'additional_attributes' in replacement:
            for attr, value in replacement['additional_attributes'].items():
                img_tag[attr] = value
        
        return True
    
    def create_replacement_list(
        self,
        failed_images: List[Dict],
        new_images: Dict[str, List[Tuple[str, int]]]
    ) -> List[Dict]:
        """
        Create replacement list from failed images and new image mappings.
        
        Args:
            failed_images: List of failed image analysis from HTML parser
            new_images: Dict mapping topics to list of (image_id, source) tuples
            
        Returns:
            List of replacement dictionaries
        """
        replacements = []
        
        for failed_img in failed_images:
            original_src = failed_img['original_src']
            topic = failed_img['replacement_topic']
            
            # Try to get new image for this topic
            available_images = new_images.get(topic, [])
            
            if available_images:
                # Use first available image
                image_id, source = available_images[0]
                new_src = self._build_url_from_id(image_id, source)
                
                replacement = {
                    'original_src': original_src,
                    'new_src': new_src,
                    'alt_text': self._generate_alt_text(topic, failed_img),
                    'preserve_attributes': True,
                    'topic': topic,
                    'source': source,
                    'image_id': image_id
                }
                
                replacements.append(replacement)
                
                # Remove used image from available list
                available_images.pop(0)
            else:
                # Use fallback image
                fallback_src = self._get_fallback_image(failed_img)
                
                replacement = {
                    'original_src': original_src,
                    'new_src': fallback_src,
                    'alt_text': self._generate_alt_text(topic, failed_img),
                    'preserve_attributes': True,
                    'topic': topic,
                    'source': 'fallback'
                }
                
                replacements.append(replacement)
        
        return replacements
    
    def _build_url_from_id(self, image_id: str, source: int) -> str:
        """Build full URL from image ID and source."""
        source_templates = {
            0: f"https://images.unsplash.com/photo-{image_id}",
            1: f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg",
            2: f"https://cdn.pixabay.com/photo/{image_id}"
        }
        
        return source_templates.get(source, f"https://images.unsplash.com/photo-{image_id}")
    
    def _generate_alt_text(self, topic: str, failed_img: Dict) -> str:
        """Generate appropriate alt text for replacement image."""
        # Use existing alt text if meaningful
        existing_alt = failed_img.get('alt_text', '').strip()
        if existing_alt and len(existing_alt.split()) > 1:
            return existing_alt
        
        # Generate based on topic and context
        slide_type = failed_img.get('slide_type', 'general')
        
        # Create descriptive alt text
        if slide_type == 'data':
            return f"Data visualization related to {topic}"
        elif slide_type == 'title':
            return f"Professional image representing {topic}"
        elif slide_type == 'team':
            return f"Team collaboration in {topic}"
        else:
            return f"Image illustrating {topic}"
    
    def _get_fallback_image(self, failed_img: Dict) -> str:
        """Get fallback image URL based on context."""
        slide_type = failed_img.get('slide_type', 'general')
        topic = failed_img.get('replacement_topic', '').lower()
        
        # Try to match topic to fallback category
        if any(word in topic for word in ['business', 'professional', 'corporate']):
            return self.fallback_images['business']
        elif any(word in topic for word in ['technology', 'tech', 'computer', 'digital']):
            return self.fallback_images['technology']
        elif any(word in topic for word in ['nature', 'landscape', 'mountain', 'forest']):
            return self.fallback_images['nature']
        elif any(word in topic for word in ['data', 'chart', 'graph', 'analytics']):
            return self.fallback_images['data']
        elif any(word in topic for word in ['team', 'people', 'collaboration', 'meeting']):
            return self.fallback_images['team']
        else:
            return self.fallback_images['general']
    
    def validate_html_structure(self, html_content: str) -> Dict:
        """
        Validate that HTML structure is maintained after replacements.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            Validation results dictionary
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Count elements
            img_tags = soup.find_all('img')
            total_images = len(img_tags)
            
            # Check for valid src attributes
            valid_images = len([img for img in img_tags if img.get('src')])
            
            # Check for alt attributes
            images_with_alt = len([img for img in img_tags if img.get('alt')])
            
            # Check for malformed tags
            malformed = len([img for img in img_tags if not img.get('src') or len(img.get('src', '')) < 10])
            
            return {
                'valid_html': True,
                'total_images': total_images,
                'valid_images': valid_images,
                'images_with_alt': images_with_alt,
                'malformed_images': malformed,
                'alt_coverage': images_with_alt / total_images if total_images > 0 else 1.0,
                'validity_score': valid_images / total_images if total_images > 0 else 1.0
            }
            
        except Exception as e:
            return {
                'valid_html': False,
                'error': str(e),
                'total_images': 0,
                'valid_images': 0,
                'images_with_alt': 0,
                'malformed_images': 0,
                'alt_coverage': 0.0,
                'validity_score': 0.0
            }
    
    def batch_replace_images(
        self,
        slides_html: List[str],
        all_replacements: List[List[Dict]]
    ) -> List[Tuple[str, Dict]]:
        """
        Replace images in multiple slides efficiently.
        
        Args:
            slides_html: List of HTML content for each slide
            all_replacements: List of replacement lists for each slide
            
        Returns:
            List of (updated_html, stats) tuples
        """
        results = []
        
        for i, (html_content, replacements) in enumerate(zip(slides_html, all_replacements)):
            try:
                updated_html, stats = self.replace_failed_images(html_content, replacements)
                results.append((updated_html, stats))
            except Exception as e:
                logger.error(f"Error processing slide {i}: {e}")
                # Return original HTML with error stats
                error_stats = {
                    'total_replacements': len(replacements),
                    'successful_replacements': 0,
                    'failed_replacements': len(replacements),
                    'images_removed': 0,
                    'error': str(e)
                }
                results.append((html_content, error_stats))
        
        return results
    
    def generate_replacement_report(self, all_stats: List[Dict]) -> Dict:
        """
        Generate summary report for all image replacements.
        
        Args:
            all_stats: List of stats from each slide
            
        Returns:
            Summary report dictionary
        """
        total_replacements = sum(stats.get('total_replacements', 0) for stats in all_stats)
        successful_replacements = sum(stats.get('successful_replacements', 0) for stats in all_stats)
        failed_replacements = sum(stats.get('failed_replacements', 0) for stats in all_stats)
        images_removed = sum(stats.get('images_removed', 0) for stats in all_stats)
        
        success_rate = successful_replacements / total_replacements if total_replacements > 0 else 0
        
        return {
            'total_slides_processed': len(all_stats),
            'total_image_replacements': total_replacements,
            'successful_replacements': successful_replacements,
            'failed_replacements': failed_replacements,
            'images_removed': images_removed,
            'success_rate': success_rate,
            'slides_with_errors': len([s for s in all_stats if 'error' in s]),
            'replacement_methods': self._analyze_replacement_methods(all_stats)
        }
    
    def _analyze_replacement_methods(self, all_stats: List[Dict]) -> Dict:
        """Analyze which replacement methods were used."""
        methods = {'claude_generated': 0, 'cache_hit': 0, 'fallback': 0, 'similar_topic': 0}
        
        for stats in all_stats:
            details = stats.get('replacements_detail', [])
            for detail in details:
                if 'claude' in detail.get('method', ''):
                    methods['claude_generated'] += 1
                elif 'cache' in detail.get('method', ''):
                    methods['cache_hit'] += 1
                elif 'fallback' in detail.get('method', ''):
                    methods['fallback'] += 1
                elif 'similar' in detail.get('method', ''):
                    methods['similar_topic'] += 1
        
        return methods