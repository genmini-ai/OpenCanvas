"""
Claude-based image URL generator with structured prompts and retry logic.
Uses multiple prompt strategies to maximize success rate.
"""

import json
import time
import re
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import anthropic

from opencanvas.image_validation.url_validator import URLValidator
from opencanvas.image_validation.topic_image_cache import TopicImageCache
from opencanvas.config import Config


class ClaudeImageRetriever:
    """Generate image URLs using Claude with optimized prompts."""
    
    def __init__(self, anthropic_api_key: Optional[str] = None, cache: Optional[TopicImageCache] = None):
        """
        Initialize the retriever.
        
        Args:
            anthropic_api_key: API key for Anthropic (from config/env if not provided)
            cache: Optional TopicImageCache instance
        """
        # Get API key from multiple sources
        if not anthropic_api_key:
            # Try main config first (loads from .env)
            if Config and hasattr(Config, 'ANTHROPIC_API_KEY'):
                anthropic_api_key = Config.ANTHROPIC_API_KEY
            
            # Fallback to direct environment variable
            if not anthropic_api_key:
                anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not anthropic_api_key:
            raise ValueError("No Anthropic API key found. Check Config.ANTHROPIC_API_KEY or ANTHROPIC_API_KEY env var.")
        
        print(f"  🔑 API key loaded successfully (length: {len(anthropic_api_key)})")
        
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.validator = URLValidator()
        self.cache = cache or TopicImageCache()
        
        # Prompt templates with different strategies
        self.prompt_templates = {
            "v1_direct": {
                "system": "You are an expert at finding relevant Unsplash images. You provide complete Unsplash URLs for images you know exist.",
                "user": """Find 3 Unsplash images for this topic: "{topic}"

Return ONLY a JSON array of complete Unsplash URLs, like:
["https://images.unsplash.com/photo-1234567890?ixlib=rb-4.0.3", "https://images.unsplash.com/photo-0987654321?ixlib=rb-4.0.3", "https://images.unsplash.com/photo-1122334455?ixlib=rb-4.0.3"]

Requirements:
- Use only complete Unsplash URLs for images you are confident exist
- URLs should be in format: https://images.unsplash.com/photo-[ID]?ixlib=rb-4.0.3
- Choose images that directly relate to the topic
- Return ONLY the JSON array, no other text"""
            },
            
            "v2_improved": {
                "system": "You are an expert at finding relevant Unsplash images. You provide complete Unsplash URLs for images you know exist.",
                "user": """Find Unsplash images for this topic: "{topic}"

Context: {slide_context}

Return ONLY a JSON array of complete Unsplash URLs, like:
["https://images.unsplash.com/photo-1234567890?ixlib=rb-4.0.3", "https://images.unsplash.com/photo-0987654321?ixlib=rb-4.0.3"]

CRITICAL Requirements:
- Use only complete Unsplash URLs for images you are confident exist
- URLs must be in format: https://images.unsplash.com/photo-[ID]?ixlib=rb-4.0.3
- NEVER repeat the same URL - each must be unique
- Choose images that directly relate to the topic and context
- Provide UP TO 3 images maximum - if you only know 1-2 good ones, stop there
- Return ONLY the JSON array, no other text"""
            },
            
            "v3_quality": {
                "system": "You are a professional photographer and designer with deep knowledge of Unsplash's high-quality image collection. You only recommend images you are absolutely certain exist and are of professional quality.",
                "user": """Topic: "{topic}"
Context: {slide_context}

Think like a professional: What would be the PERFECT image for this presentation slide?

Step 1: Consider the visual needs (but don't write this out)
Step 2: Identify 1-2 Unsplash images you are 100% confident exist and are visually excellent
Step 3: Return ONLY those high-confidence URLs

Return ONLY a JSON array of complete Unsplash URLs:
["https://images.unsplash.com/photo-ID?ixlib=rb-4.0.3"]

QUALITY REQUIREMENTS:
- Only provide URLs you are absolutely certain exist on Unsplash
- Each image must be visually striking and professionally composed
- Quality over quantity - prefer 1 perfect image over 3 mediocre ones
- URLs must use exact format: https://images.unsplash.com/photo-[ID]?ixlib=rb-4.0.3
- NO duplicates, NO made-up IDs, NO guessing
- If unsure, provide fewer images or skip entirely"""
            }
        }
        
        # Track performance
        self.prompt_stats = {k: {"attempts": 0, "successes": 0} for k in self.prompt_templates}
        self.current_strategy = "v2_improved"
    
    def get_best_strategy(self) -> str:
        """Select the best performing prompt strategy."""
        # Calculate success rates
        rates = {}
        for strategy, stats in self.prompt_stats.items():
            if stats["attempts"] > 0:
                rates[strategy] = stats["successes"] / stats["attempts"]
            else:
                rates[strategy] = 0.5  # Default rate for untested
        
        # If current strategy has > 70% success, keep it
        if rates.get(self.current_strategy, 0) > 0.7:
            return self.current_strategy
        
        # Otherwise pick the best performer with at least 5 attempts
        tested_strategies = {k: v for k, v in rates.items() 
                           if self.prompt_stats[k]["attempts"] >= 5}
        
        if tested_strategies:
            return max(tested_strategies, key=tested_strategies.get)
        
        # Rotate through strategies for testing
        strategies = list(self.prompt_templates.keys())
        current_idx = strategies.index(self.current_strategy)
        return strategies[(current_idx + 1) % len(strategies)]
    
    def extract_urls_from_response(self, response: str, strategy: str) -> List[str]:
        """
        Extract image URLs from Claude's response.
        
        Args:
            response: Claude's response text
            strategy: Which prompt strategy was used
            
        Returns:
            List of extracted image URLs
        """
        urls = []
        
        try:
            # All strategies now expect a simple JSON array of URLs
            data = json.loads(response)
            if isinstance(data, list):
                urls = data
        except json.JSONDecodeError:
            # Fallback: extract using regex
            # Look for Unsplash URL patterns
            patterns = [
                r'https://images\.unsplash\.com/photo-[a-zA-Z0-9_-]+[^"\s]*',  # Complete URLs
                r'"(https://[^"]*unsplash[^"]*)"',  # Quoted URLs
                r'https://[^\s]*unsplash[^\s]*',  # Any unsplash URLs
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response)
                if matches:
                    urls.extend(matches)
                    break
        
        # Clean and validate URLs
        clean_urls = []
        for url_str in urls:
            url_str = url_str.strip()
            # Basic validation: should be a valid Unsplash URL
            if ('unsplash.com' in url_str and 
                url_str.startswith('http') and 
                'photo-' in url_str):
                clean_urls.append(url_str)
        
        return clean_urls[:3]  # Maximum 3 URLs
    
    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract the image ID from an Unsplash URL.
        
        Args:
            url: Complete Unsplash URL
            
        Returns:
            Image ID or None if not found
        """
        # Pattern to match photo ID in Unsplash URLs
        # e.g., https://images.unsplash.com/photo-1234567890?params -> 1234567890
        match = re.search(r'photo-([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else None
    
    def generate_images(
        self, 
        topic: str, 
        slide_context: Optional[str] = None,
        max_retries: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Generate image IDs for a topic using Claude.
        
        Args:
            topic: The topic to find images for
            slide_context: Optional context from the slide
            max_retries: Maximum retry attempts
            
        Returns:
            List of (image_id, confidence_score) tuples
        """
        valid_images = []
        attempts = 0
        strategies_tried = set()
        
        # Record Claude call in cache metrics
        self.cache.record_claude_call()
        
        while attempts < max_retries and len(valid_images) < 3:
            attempts += 1
            
            # Select strategy
            if attempts == 1:
                strategy = self.get_best_strategy()
            else:
                # Try a different strategy on retry
                remaining = set(self.prompt_templates.keys()) - strategies_tried
                if remaining:
                    strategy = list(remaining)[0]
                else:
                    break
            
            strategies_tried.add(strategy)
            
            # Prepare prompt
            template = self.prompt_templates[strategy]
            user_prompt = template["user"].format(
                topic=topic,
                slide_context=slide_context or f"A slide about {topic}"
            )
            
            try:
                # Call Claude
                print(f"    📝 Prompt preview: {user_prompt[:100]}...")
                start_time = time.time()
                message = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Fast model for simple tasks
                    max_tokens=500,
                    temperature=0.3,  # Lower temperature for more consistent IDs
                    system=template["system"],
                    messages=[{"role": "user", "content": user_prompt}]
                )
                response_time = (time.time() - start_time) * 1000
                
                # Extract URLs
                response_text = message.content[0].text
                print(f"    🤖 Claude response: {response_text}")
                image_urls = self.extract_urls_from_response(response_text, strategy)
                print(f"    📷 Extracted URLs: {image_urls}")
                
                # Validate URLs
                if image_urls:
                    validation_results = self.validator.validate_batch(image_urls)
                    
                    # Track valid images and extract IDs for storage
                    for i, (url, result) in enumerate(zip(image_urls, validation_results)):
                        if result['valid']:
                            # Extract ID from URL for cache storage
                            img_id = self._extract_id_from_url(url)
                            if img_id:
                                # Higher confidence for earlier suggestions
                                confidence = 0.9 - (i * 0.1) - (attempts - 1) * 0.2
                                confidence = max(confidence, 0.5)
                                valid_images.append((img_id, confidence))
                    
                    # Update strategy stats
                    self.prompt_stats[strategy]["attempts"] += 1
                    if valid_images:
                        self.prompt_stats[strategy]["successes"] += 1
                
            except Exception as e:
                print(f"    ❌ Error generating images with {strategy}: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # If we have at least one valid image, we can stop
            if len(valid_images) >= 1:
                break
        
        return valid_images[:3]
    
    def get_images_with_fallback(
        self, 
        topic: str, 
        slide_context: Optional[str] = None
    ) -> List[Tuple[str, int]]:
        """
        Get images with fallback to similar topics.
        
        Args:
            topic: The topic to find images for
            slide_context: Optional context from the slide
            
        Returns:
            List of (image_id, source) tuples
        """
        # First check cache for exact match
        print(f"    🔍 Checking cache for topic: '{topic}'")
        cached = self.cache.get_images_for_topic(topic)
        if cached:
            print(f"    ✅ Found {len(cached)} cached images")
            return cached
        
        # Check for similar topics
        print(f"    🔍 Checking for similar topics...")
        similar = self.cache.find_similar_topics(topic, min_similarity=0.7)
        if similar:
            # Use images from the most similar topic
            best_match = similar[0]
            print(f"    🔗 Using images from similar topic: {best_match[0]} (similarity: {best_match[1]:.2f})")
            return [(img_id, 0) for img_id in best_match[2]]
        
        # Generate new images
        print(f"    🆕 Generating new images with Claude...")
        generated = self.generate_images(topic, slide_context)
        
        if generated:
            # Add to cache
            cache_entries = [(img_id, 0, True, conf) for img_id, conf in generated]
            self.cache.add_images_for_topic(topic, cache_entries)
            
            return [(img_id, 0) for img_id, _ in generated]
        
        # Last resort: try very similar topics with lower threshold
        similar_loose = self.cache.find_similar_topics(topic, min_similarity=0.5, limit=10)
        if similar_loose:
            print(f"Using images from loosely similar topic: {similar_loose[0][0]}")
            return [(img_id, 0) for img_id in similar_loose[0][2]]
        
        return []
    
    def get_prompt_stats(self) -> Dict:
        """Get statistics about prompt performance."""
        stats = {}
        for strategy, data in self.prompt_stats.items():
            if data["attempts"] > 0:
                stats[strategy] = {
                    "attempts": data["attempts"],
                    "successes": data["successes"],
                    "success_rate": data["successes"] / data["attempts"],
                    "is_current": strategy == self.current_strategy
                }
        return stats