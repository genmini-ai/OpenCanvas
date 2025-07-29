"""
HTML parser for extracting images and slide context from presentation HTML.
Analyzes slide content to determine appropriate image topics.
"""

import re
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse, urljoin


class SlideImageParser:
    """Extract images and context from slide HTML."""
    
    def __init__(self):
        """Initialize the parser."""
        # Priority weights for different HTML elements
        self.element_weights = {
            'h1': 3.0,
            'h2': 2.5,
            'h3': 2.0,
            'h4': 1.5,
            'h5': 1.2,
            'h6': 1.0,
            'strong': 1.5,
            'b': 1.5,
            'em': 1.2,
            'i': 1.2,
            'p': 1.0,
            'li': 0.8,
            'span': 0.5,
            'div': 0.3
        }
        
        # Stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once'
        }
    
    def extract_images_from_html(self, html_content: str) -> List[Dict]:
        """
        Extract all image elements from HTML.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of image dictionaries with metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []
        
        for img_tag in soup.find_all('img'):
            img_data = {
                'tag': str(img_tag),
                'src': img_tag.get('src', ''),
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
                'class': img_tag.get('class', []),
                'style': img_tag.get('style', ''),
                'width': img_tag.get('width'),
                'height': img_tag.get('height'),
                'parent_context': self._get_parent_context(img_tag),
                'surrounding_text': self._get_surrounding_text(img_tag),
                'position_index': len(images)
            }
            
            # Extract image ID if from known CDN
            img_data['image_id'] = self._extract_image_id(img_data['src'])
            
            images.append(img_data)
        
        return images
    
    def extract_slide_context(self, html_content: str) -> Dict:
        """
        Extract contextual information from slide content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dictionary with slide context information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content with weights
        weighted_text = self._extract_weighted_text(soup)
        
        # Get key phrases and topics
        key_phrases = self._extract_key_phrases(weighted_text)
        
        # Detect slide type
        slide_type = self._detect_slide_type(soup, weighted_text)
        
        # Extract lists and structured content
        lists = self._extract_lists(soup)
        
        # Get title/heading hierarchy
        headings = self._extract_headings(soup)
        
        return {
            'weighted_text': weighted_text,
            'key_phrases': key_phrases,
            'slide_type': slide_type,
            'headings': headings,
            'lists': lists,
            'word_count': len(weighted_text.split()),
            'main_topic': self._determine_main_topic(key_phrases, headings),
            'text_density': self._calculate_text_density(soup),
            'has_data_elements': self._has_data_elements(soup)
        }
    
    def _get_parent_context(self, img_tag: Tag) -> Dict:
        """Get context from parent elements."""
        context = {
            'parent_tag': img_tag.parent.name if img_tag.parent else None,
            'parent_class': img_tag.parent.get('class', []) if img_tag.parent else [],
            'section_heading': None,
            'container_type': None
        }
        
        # Find nearest heading
        current = img_tag
        while current and current.parent:
            current = current.parent
            if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                context['section_heading'] = current.get_text().strip()
                break
            elif current.name in ['section', 'article', 'div'] and current.get('class'):
                context['container_type'] = ' '.join(current.get('class'))
        
        return context
    
    def _get_surrounding_text(self, img_tag: Tag, radius: int = 100) -> str:
        """Get text content around the image."""
        # Get all text from parent container
        parent = img_tag.parent
        if not parent:
            return ""
        
        # Get text before and after the image
        all_text = parent.get_text()
        img_text = img_tag.get('alt', '') + ' ' + img_tag.get('title', '')
        
        # Find approximate position of image in text
        if img_text.strip():
            img_pos = all_text.find(img_text.strip())
            if img_pos != -1:
                start = max(0, img_pos - radius)
                end = min(len(all_text), img_pos + len(img_text) + radius)
                return all_text[start:end].strip()
        
        # Fallback: return parent text (truncated)
        return all_text[:radius * 2].strip()
    
    def _extract_image_id(self, src: str) -> Optional[str]:
        """Extract image ID from URL if possible."""
        if not src:
            return None
        
        # Unsplash pattern
        unsplash_match = re.search(r'images\.unsplash\.com/photo-([a-zA-Z0-9_-]+)', src)
        if unsplash_match:
            return unsplash_match.group(1)
        
        # Pexels pattern
        pexels_match = re.search(r'images\.pexels\.com/photos/(\d+)/', src)
        if pexels_match:
            return pexels_match.group(1)
        
        return None
    
    def _extract_weighted_text(self, soup: BeautifulSoup) -> str:
        """Extract text with importance weighting."""
        weighted_content = []
        
        for element in soup.find_all(text=True):
            if element.parent and element.parent.name:
                weight = self.element_weights.get(element.parent.name, 0.1)
                text = element.strip()
                
                if text and element.parent.name not in ['script', 'style', 'meta']:
                    # Repeat important text based on weight
                    repeat_count = max(1, int(weight))
                    weighted_content.extend([text] * repeat_count)
        
        return ' '.join(weighted_content)
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words
        filtered_words = [w for w in words if w not in self.stop_words]
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top phrases (words appearing multiple times)
        key_phrases = [word for word, freq in word_freq.items() if freq > 1]
        
        # Sort by frequency and take top 10
        key_phrases.sort(key=lambda w: word_freq[w], reverse=True)
        
        return key_phrases[:10]
    
    def _detect_slide_type(self, soup: BeautifulSoup, text: str) -> str:
        """Detect the type/purpose of the slide."""
        # Check for data visualization indicators
        if any(keyword in text.lower() for keyword in 
               ['chart', 'graph', 'data', 'statistics', 'metrics', 'analysis']):
            return 'data'
        
        # Check for title slide indicators
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 1 and len(soup.get_text().split()) < 20:
            return 'title'
        
        # Check for list/bullet slides
        if soup.find_all(['ul', 'ol']) and len(soup.find_all('li')) > 3:
            return 'list'
        
        # Check for content slides
        if len(soup.find_all('p')) > 2:
            return 'content'
        
        # Check for conclusion slides
        if any(keyword in text.lower() for keyword in 
               ['conclusion', 'summary', 'takeaway', 'recap', 'in summary']):
            return 'conclusion'
        
        return 'general'
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract list content."""
        lists = []
        
        for list_tag in soup.find_all(['ul', 'ol']):
            list_items = [li.get_text().strip() for li in list_tag.find_all('li')]
            lists.append({
                'type': list_tag.name,
                'items': list_items,
                'count': len(list_items)
            })
        
        return lists
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract heading hierarchy."""
        headings = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.get_text().strip(),
                'tag': heading.name
            })
        
        return headings
    
    def _determine_main_topic(self, key_phrases: List[str], headings: List[Dict]) -> str:
        """Determine the main topic of the slide."""
        # Prioritize heading text
        if headings:
            main_heading = headings[0]['text']  # First heading is usually most important
            return main_heading
        
        # Fallback to key phrases
        if key_phrases:
            return ' '.join(key_phrases[:3])  # Top 3 key phrases
        
        return "general topic"
    
    def _calculate_text_density(self, soup: BeautifulSoup) -> float:
        """Calculate text density (words per element)."""
        all_text = soup.get_text()
        word_count = len(all_text.split())
        element_count = len(soup.find_all())
        
        return word_count / max(element_count, 1)
    
    def _has_data_elements(self, soup: BeautifulSoup) -> bool:
        """Check if slide has data visualization elements."""
        # Look for table elements
        if soup.find_all('table'):
            return True
        
        # Look for common chart/graph classes
        chart_classes = ['chart', 'graph', 'visualization', 'plot', 'diagram']
        for element in soup.find_all(class_=True):
            element_classes = ' '.join(element.get('class', [])).lower()
            if any(chart_class in element_classes for chart_class in chart_classes):
                return True
        
        return False
    
    def analyze_failed_images(self, html_content: str, failed_urls: List[str]) -> List[Dict]:
        """
        Analyze failed images and extract context for replacement.
        
        Args:
            html_content: HTML content
            failed_urls: List of URLs that failed validation
            
        Returns:
            List of image analysis for replacement
        """
        images = self.extract_images_from_html(html_content)
        slide_context = self.extract_slide_context(html_content)
        
        failed_images = []
        
        for img in images:
            if img['src'] in failed_urls:
                # Determine replacement topic
                replacement_topic = self._determine_replacement_topic(img, slide_context)
                
                failed_images.append({
                    'original_src': img['src'],
                    'alt_text': img['alt'],
                    'surrounding_text': img['surrounding_text'],
                    'replacement_topic': replacement_topic,
                    'slide_context': slide_context['main_topic'],
                    'slide_type': slide_context['slide_type'],
                    'position': img['position_index'],
                    'img_tag': img['tag']
                })
        
        return failed_images
    
    def _determine_replacement_topic(self, img: Dict, slide_context: Dict) -> str:
        """Determine appropriate topic for image replacement."""
        # Priority order for topic determination:
        
        # 1. Alt text (if meaningful)
        alt_text = img['alt'].strip()
        if alt_text and len(alt_text.split()) > 1:
            return alt_text
        
        # 2. Surrounding text context
        surrounding = img['surrounding_text']
        if surrounding and len(surrounding.split()) > 3:
            # Extract first meaningful phrase
            words = surrounding.split()[:10]  # First 10 words
            meaningful_words = [w for w in words if w.lower() not in self.stop_words]
            if meaningful_words:
                return ' '.join(meaningful_words[:5])
        
        # 3. Section heading
        if img['parent_context']['section_heading']:
            return img['parent_context']['section_heading']
        
        # 4. Slide main topic
        if slide_context['main_topic']:
            return slide_context['main_topic']
        
        # 5. Slide type-based fallback
        slide_type = slide_context['slide_type']
        fallback_topics = {
            'data': 'business data visualization',
            'title': 'professional presentation',
            'list': 'business concepts',
            'content': 'general business',
            'conclusion': 'success achievement',
            'general': 'business professional'
        }
        
        return fallback_topics.get(slide_type, 'business professional')