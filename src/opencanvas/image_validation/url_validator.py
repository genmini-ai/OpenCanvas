"""
URL validation utility for checking image availability.
Uses HEAD requests for efficiency and supports batch validation.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
import re
from concurrent.futures import ThreadPoolExecutor
import threading


class URLValidator:
    """Efficient URL validation with caching and batch support."""
    
    def __init__(self, timeout: float = 3.0, max_concurrent: int = 10):
        """
        Initialize URL validator.
        
        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent validations
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        
        # In-memory cache for session (not persistent)
        self._session_cache = {}
        self._cache_lock = threading.Lock()
        
        # Valid image content types
        self.valid_content_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'image/webp', 'image/svg+xml', 'image/bmp', 'image/tiff'
        }
        
        # Known CDN patterns for quick validation
        self.cdn_patterns = {
            'unsplash': re.compile(r'images\.unsplash\.com/photo-([a-zA-Z0-9_-]+)'),
            'pexels': re.compile(r'images\.pexels\.com/photos/(\d+)/'),
            'pixabay': re.compile(r'cdn\.pixabay\.com/photo/'),
        }
    
    def extract_image_id(self, url: str) -> Optional[Tuple[str, int]]:
        """
        Extract image ID and source from URL.
        
        Args:
            url: Full image URL
            
        Returns:
            Tuple of (image_id, source) or None
        """
        for source_name, pattern in self.cdn_patterns.items():
            match = pattern.search(url)
            if match:
                source_map = {'unsplash': 0, 'pexels': 1, 'pixabay': 2}
                if source_name == 'unsplash':
                    return (match.group(1), source_map[source_name])
                elif source_name == 'pexels':
                    return (match.group(1), source_map[source_name])
                elif source_name == 'pixabay':
                    # Extract ID from path
                    path = urlparse(url).path
                    id_match = re.search(r'/(\d+)[_-]', path)
                    if id_match:
                        return (id_match.group(1), source_map[source_name])
        
        return None
    
    async def validate_url_async(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """
        Validate a single URL asynchronously.
        
        Args:
            session: aiohttp session
            url: URL to validate
            
        Returns:
            Dictionary with validation results
        """
        # Check session cache first
        with self._cache_lock:
            if url in self._session_cache:
                return self._session_cache[url]
        
        result = {
            'url': url,
            'valid': False,
            'status_code': None,
            'content_type': None,
            'content_length': None,
            'error': None,
            'image_id': None,
            'source': None
        }
        
        # Extract image ID if possible
        id_info = self.extract_image_id(url)
        if id_info:
            result['image_id'], result['source'] = id_info
        
        try:
            # Use HEAD request for efficiency
            async with session.head(
                url, 
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=True
            ) as response:
                result['status_code'] = response.status
                result['content_type'] = response.headers.get('Content-Type', '').lower()
                
                # Check if it's a valid image
                if response.status == 200:
                    content_type = result['content_type'].split(';')[0].strip()
                    if any(content_type.startswith(valid) for valid in self.valid_content_types):
                        result['valid'] = True
                        result['content_length'] = int(response.headers.get('Content-Length', 0))
                    else:
                        result['error'] = f"Invalid content type: {content_type}"
                else:
                    result['error'] = f"HTTP {response.status}"
                    
        except asyncio.TimeoutError:
            result['error'] = "Timeout"
        except aiohttp.ClientError as e:
            result['error'] = f"Client error: {str(e)}"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        # Cache the result for this session
        with self._cache_lock:
            self._session_cache[url] = result
        
        return result
    
    async def validate_batch_async(self, urls: List[str]) -> List[Dict]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of validation results
        """
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url and url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_with_semaphore(session, url):
            async with semaphore:
                return await self.validate_url_async(session, url)
        
        # Validate all URLs
        async with aiohttp.ClientSession() as session:
            tasks = [validate_with_semaphore(session, url) for url in unique_urls]
            results = await asyncio.gather(*tasks)
        
        # Map results back to original order (including duplicates)
        result_map = {r['url']: r for r in results}
        return [result_map.get(url, {'url': url, 'valid': False, 'error': 'Not processed'}) 
                for url in urls]
    
    def validate_batch(self, urls: List[str]) -> List[Dict]:
        """
        Synchronous wrapper for batch validation.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of validation results
        """
        # Try to get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async validation
        if loop.is_running():
            # If loop is already running (e.g., in Jupyter), use thread pool
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.validate_batch_async(urls))
                return future.result()
        else:
            return loop.run_until_complete(self.validate_batch_async(urls))
    
    def validate_single(self, url: str) -> Dict:
        """
        Validate a single URL synchronously.
        
        Args:
            url: URL to validate
            
        Returns:
            Validation result dictionary
        """
        return self.validate_batch([url])[0]
    
    def quick_validate_format(self, url: str) -> bool:
        """
        Quick validation based on URL format without making requests.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL format looks valid
        """
        try:
            parsed = urlparse(url)
            
            # Check basic URL structure
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it's a known CDN pattern
            for pattern in self.cdn_patterns.values():
                if pattern.search(url):
                    return True
            
            # Check file extension
            path = parsed.path.lower()
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
            return any(path.endswith(ext) for ext in image_extensions)
            
        except Exception:
            return False
    
    def get_validation_stats(self) -> Dict:
        """Get statistics about validations in this session."""
        with self._cache_lock:
            total = len(self._session_cache)
            valid = sum(1 for r in self._session_cache.values() if r['valid'])
            
            # Group by domain
            domains = {}
            for url, result in self._session_cache.items():
                domain = urlparse(url).netloc
                if domain not in domains:
                    domains[domain] = {'total': 0, 'valid': 0}
                domains[domain]['total'] += 1
                if result['valid']:
                    domains[domain]['valid'] += 1
            
            return {
                'total_validated': total,
                'total_valid': valid,
                'success_rate': valid / total if total > 0 else 0,
                'domains': domains
            }
    
    def clear_cache(self):
        """Clear session cache."""
        with self._cache_lock:
            self._session_cache.clear()