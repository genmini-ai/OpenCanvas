"""
Claude-based image URL generator with structured prompts and retry logic.
Uses multiple prompt strategies to maximize success rate.
"""

import json
import time
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import anthropic
from .url_validator import URLValidator
from .topic_image_cache import TopicImageCache


class ClaudeImageRetriever:
    """Generate image URLs using Claude with optimized prompts."""
    
    def __init__(self, anthropic_api_key: str, cache: Optional[TopicImageCache] = None):
        """
        Initialize the retriever.
        
        Args:
            anthropic_api_key: API key for Anthropic
            cache: Optional TopicImageCache instance
        """
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.validator = URLValidator()
        self.cache = cache or TopicImageCache()
        
        # Prompt templates with different strategies
        self.prompt_templates = {
            "v1_direct": {
                "system": "You are an expert at finding relevant Unsplash image IDs. You only suggest images you are certain exist on Unsplash.",
                "user": """Find 3 Unsplash images for this topic: "{topic}"

Return ONLY a JSON array of image IDs (not full URLs), like:
["1234567890", "0987654321", "1122334455"]

Requirements:
- Use only well-known Unsplash photo IDs you're certain exist
- IDs should be the alphanumeric string after 'photo-' in Unsplash URLs
- Choose images that directly relate to the topic
- Return ONLY the JSON array, no other text"""
            },
            
            "v2_context": {
                "system": "You are an expert at finding relevant stock images. You have deep knowledge of popular Unsplash photos and their IDs.",
                "user": """Context from presentation slide:
{slide_context}

Topic focus: {topic}

Suggest 3 relevant Unsplash photo IDs that would enhance this slide visually.

Return as JSON:
{{
  "images": [
    {{"id": "photo_id_here", "reason": "brief reason for selection"}},
    {{"id": "photo_id_here", "reason": "brief reason for selection"}},
    {{"id": "photo_id_here", "reason": "brief reason for selection"}}
  ]
}}

Use only verified Unsplash photo IDs you know exist."""
            },
            
            "v3_fallback": {
                "system": "You are helping find images for a presentation. Suggest realistic Unsplash photo IDs based on common photography subjects.",
                "user": """I need images related to: {topic}

Based on common Unsplash photography categories, suggest 3 photo IDs that likely exist.
Focus on:
- Generic subjects (nature, business, technology, people)
- Popular photography themes
- Well-documented photo collections

Format: ["id1", "id2", "id3"]

Important: Only suggest IDs using common Unsplash patterns you've seen before."""
            }
        }
        
        # Track performance
        self.prompt_stats = {k: {"attempts": 0, "successes": 0} for k in self.prompt_templates}
        self.current_strategy = "v1_direct"
    
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
    
    def extract_ids_from_response(self, response: str, strategy: str) -> List[str]:
        """
        Extract image IDs from Claude's response.
        
        Args:
            response: Claude's response text
            strategy: Which prompt strategy was used
            
        Returns:
            List of extracted image IDs
        """
        ids = []
        
        try:
            # Try to parse as JSON first
            if strategy == "v2_context":
                data = json.loads(response)
                if isinstance(data, dict) and "images" in data:
                    ids = [img["id"] for img in data["images"] if "id" in img]
            else:
                # For v1 and v3, expect a simple array
                data = json.loads(response)
                if isinstance(data, list):
                    ids = data
        except json.JSONDecodeError:
            # Fallback: extract using regex
            # Look for patterns like "1234567890" or photo-1234567890
            patterns = [
                r'"([a-zA-Z0-9_-]{10,})"',  # Quoted IDs
                r'photo-([a-zA-Z0-9_-]+)',   # photo- prefix
                r'\[.*?"([a-zA-Z0-9_-]{10,})".*?\]',  # In array
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response)
                if matches:
                    ids.extend(matches)
                    break
        
        # Clean and validate IDs
        clean_ids = []
        for id_str in ids:
            # Remove 'photo-' prefix if present
            clean_id = id_str.replace('photo-', '').strip()
            # Basic validation: should be alphanumeric with possible dashes/underscores
            if re.match(r'^[a-zA-Z0-9_-]+$', clean_id) and len(clean_id) >= 10:
                clean_ids.append(clean_id)
        
        return clean_ids[:3]  # Maximum 3 IDs
    
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
                start_time = time.time()
                message = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Fast model for simple tasks
                    max_tokens=500,
                    temperature=0.3,  # Lower temperature for more consistent IDs
                    system=template["system"],
                    messages=[{"role": "user", "content": user_prompt}]
                )
                response_time = (time.time() - start_time) * 1000
                
                # Extract IDs
                response_text = message.content[0].text
                image_ids = self.extract_ids_from_response(response_text, strategy)
                
                # Validate IDs
                if image_ids:
                    # Build URLs and validate
                    urls = [self.cache.build_url(img_id, 0) for img_id in image_ids]
                    validation_results = self.validator.validate_batch(urls)
                    
                    # Track valid images
                    for i, (img_id, result) in enumerate(zip(image_ids, validation_results)):
                        if result['valid']:
                            # Higher confidence for earlier suggestions
                            confidence = 0.9 - (i * 0.1) - (attempts - 1) * 0.2
                            confidence = max(confidence, 0.5)
                            valid_images.append((img_id, confidence))
                    
                    # Update strategy stats
                    self.prompt_stats[strategy]["attempts"] += 1
                    if valid_images:
                        self.prompt_stats[strategy]["successes"] += 1
                
            except Exception as e:
                print(f"Error generating images with {strategy}: {e}")
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
        cached = self.cache.get_images_for_topic(topic)
        if cached:
            return cached
        
        # Check for similar topics
        similar = self.cache.find_similar_topics(topic, min_similarity=0.7)
        if similar:
            # Use images from the most similar topic
            best_match = similar[0]
            print(f"Using images from similar topic: {best_match[0]} (similarity: {best_match[1]:.2f})")
            return [(img_id, 0) for img_id in best_match[2]]
        
        # Generate new images
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