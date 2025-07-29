"""
Topic-based image cache using DuckDB for efficient storage and retrieval.
Stores topic-ID pairs instead of full URLs for memory efficiency.
"""

import hashlib
import time
from typing import List, Optional, Tuple, Dict
from pathlib import Path
import duckdb
from datetime import datetime, timedelta


class TopicImageCache:
    """Efficient topic-to-image-ID cache using DuckDB."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the cache with DuckDB connection."""
        if db_path is None:
            db_path = str(Path(__file__).parent / "topic_images.duckdb")
        
        self.con = duckdb.connect(db_path)
        self.con.execute("SET memory_limit='256MB'")
        self._init_schema()
        
        # Common stopwords for topic normalization
        self.stopwords = {
            'the', 'a', 'an', 'in', 'on', 'at', 'for', 'with', 'by', 'of', 
            'to', 'from', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
    
    def _init_schema(self):
        """Initialize database schema."""
        # Main cache table
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS image_cache (
                topic_hash VARCHAR(32) NOT NULL,
                image_id VARCHAR(32) NOT NULL,
                source TINYINT DEFAULT 0,
                valid BOOLEAN NOT NULL,
                last_validated TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                confidence_score DECIMAL(3,2) DEFAULT 1.0,
                PRIMARY KEY (topic_hash, image_id)
            )
        """)
        
        # Topic mapping for debugging/analytics
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS topic_mappings (
                topic_hash VARCHAR(32) PRIMARY KEY,
                topic_text VARCHAR NOT NULL,
                normalized_text VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance tracking
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS cache_metrics (
                metric_date DATE PRIMARY KEY,
                total_lookups INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                claude_calls INTEGER DEFAULT 0,
                avg_response_time_ms INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_topic ON image_cache(topic_hash)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_valid ON image_cache(valid)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_usage ON image_cache(usage_count DESC)")
    
    def normalize_topic(self, text: str) -> str:
        """
        Normalize topic text for consistent caching.
        
        Args:
            text: Raw topic or slide content
            
        Returns:
            Normalized topic string
        """
        # Convert to lowercase and strip
        text = text.lower().strip()
        
        # Extract words, remove stopwords
        words = []
        for word in text.split():
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum())
            if word and word not in self.stopwords and len(word) > 2:
                words.append(word)
        
        # Sort for consistency and take top 5 keywords
        words = sorted(set(words))[:5]
        
        return ' '.join(words)
    
    def get_topic_hash(self, topic_text: str) -> str:
        """Generate consistent hash for a topic."""
        normalized = self.normalize_topic(topic_text)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_images_for_topic(
        self, 
        topic_text: str, 
        limit: int = 3,
        min_confidence: float = 0.7
    ) -> Optional[List[Tuple[str, int]]]:
        """
        Retrieve cached images for a topic.
        
        Args:
            topic_text: The topic to search for
            limit: Maximum number of images to return
            min_confidence: Minimum confidence score for results
            
        Returns:
            List of (image_id, source) tuples or None if not cached
        """
        topic_hash = self.get_topic_hash(topic_text)
        
        # Record lookup
        self._record_lookup()
        
        # Check cache
        results = self.con.execute("""
            SELECT image_id, source, confidence_score
            FROM image_cache
            WHERE topic_hash = ?
            AND valid = true
            AND confidence_score >= ?
            ORDER BY usage_count DESC, confidence_score DESC
            LIMIT ?
        """, [topic_hash, min_confidence, limit]).fetchall()
        
        if results:
            # Record cache hit
            self._record_cache_hit()
            
            # Increment usage count
            image_ids = [r[0] for r in results]
            self.con.execute("""
                UPDATE image_cache
                SET usage_count = usage_count + 1
                WHERE topic_hash = ? AND image_id = ANY(?)
            """, [topic_hash, image_ids])
            
            return [(r[0], r[1]) for r in results]
        
        return None
    
    def add_images_for_topic(
        self, 
        topic_text: str, 
        images: List[Tuple[str, int, bool, float]]
    ):
        """
        Add images to cache for a topic.
        
        Args:
            topic_text: The topic text
            images: List of (image_id, source, valid, confidence) tuples
        """
        topic_hash = self.get_topic_hash(topic_text)
        normalized = self.normalize_topic(topic_text)
        
        # Store topic mapping if new
        self.con.execute("""
            INSERT OR IGNORE INTO topic_mappings (topic_hash, topic_text, normalized_text)
            VALUES (?, ?, ?)
        """, [topic_hash, topic_text, normalized])
        
        # Insert images
        for image_id, source, valid, confidence in images:
            self.con.execute("""
                INSERT OR REPLACE INTO image_cache 
                (topic_hash, image_id, source, valid, last_validated, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [topic_hash, image_id, source, valid, datetime.now(), confidence])
    
    def find_similar_topics(
        self, 
        topic_text: str, 
        min_similarity: float = 0.6,
        limit: int = 5
    ) -> List[Tuple[str, float, List[str]]]:
        """
        Find similar cached topics using Jaccard similarity.
        
        Args:
            topic_text: Topic to find similarities for
            min_similarity: Minimum similarity threshold
            limit: Maximum results to return
            
        Returns:
            List of (topic_text, similarity_score, image_ids) tuples
        """
        normalized = self.normalize_topic(topic_text)
        query_words = set(normalized.split())
        
        if not query_words:
            return []
        
        # Get all cached topics with their best images
        results = self.con.execute("""
            WITH topic_words AS (
                SELECT 
                    tm.topic_hash,
                    tm.topic_text,
                    tm.normalized_text,
                    string_split(tm.normalized_text, ' ') as words
                FROM topic_mappings tm
            ),
            topic_scores AS (
                SELECT 
                    tw.topic_hash,
                    tw.topic_text,
                    tw.words,
                    -- Jaccard similarity calculation
                    CAST(len(list_intersect(tw.words, ?)) AS FLOAT) / 
                    len(list_distinct(list_concat(tw.words, ?))) as similarity
                FROM topic_words tw
                WHERE len(list_intersect(tw.words, ?)) > 0
            ),
            best_images AS (
                SELECT 
                    ic.topic_hash,
                    LIST(ic.image_id ORDER BY ic.usage_count DESC, ic.confidence_score DESC) as image_ids
                FROM image_cache ic
                WHERE ic.valid = true
                GROUP BY ic.topic_hash
            )
            SELECT 
                ts.topic_text,
                ts.similarity,
                bi.image_ids
            FROM topic_scores ts
            JOIN best_images bi ON ts.topic_hash = bi.topic_hash
            WHERE ts.similarity >= ?
            ORDER BY ts.similarity DESC
            LIMIT ?
        """, [list(query_words), list(query_words), list(query_words), min_similarity, limit]).fetchall()
        
        return [(r[0], r[1], r[2][:3]) for r in results]  # Limit to 3 images per topic
    
    def build_url(self, image_id: str, source: int = 0) -> str:
        """
        Reconstruct full URL from image ID and source.
        
        Args:
            image_id: The image identifier
            source: Image source (0=Unsplash, 1=Pexels, etc.)
            
        Returns:
            Full image URL
        """
        sources = {
            0: f"https://images.unsplash.com/photo-{image_id}",
            1: f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg",
            2: f"https://cdn.pixabay.com/photo/{image_id}"
        }
        return sources.get(source, "")
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        stats = self.con.execute("""
            SELECT 
                COUNT(DISTINCT topic_hash) as total_topics,
                COUNT(*) as total_images,
                SUM(CASE WHEN valid THEN 1 ELSE 0 END) as valid_images,
                AVG(usage_count) as avg_usage,
                MAX(usage_count) as max_usage
            FROM image_cache
        """).fetchone()
        
        metrics = self.con.execute("""
            SELECT 
                SUM(cache_hits) * 100.0 / NULLIF(SUM(total_lookups), 0) as hit_rate,
                SUM(claude_calls) as total_claude_calls
            FROM cache_metrics
            WHERE metric_date >= CURRENT_DATE - INTERVAL '7 days'
        """).fetchone()
        
        return {
            'total_topics': stats[0] or 0,
            'total_images': stats[1] or 0,
            'valid_images': stats[2] or 0,
            'avg_usage': float(stats[3] or 0),
            'max_usage': stats[4] or 0,
            'weekly_hit_rate': float(metrics[0] or 0) if metrics else 0,
            'weekly_claude_calls': metrics[1] or 0 if metrics else 0
        }
    
    def cleanup_expired(self, days: int = 30):
        """Remove entries not used in specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        deleted = self.con.execute("""
            DELETE FROM image_cache
            WHERE last_validated < ?
            AND usage_count < 5
        """, [cutoff]).fetchone()
        
        return deleted[0] if deleted else 0
    
    def _record_lookup(self):
        """Record a cache lookup."""
        self.con.execute("""
            INSERT INTO cache_metrics (metric_date, total_lookups)
            VALUES (CURRENT_DATE, 1)
            ON CONFLICT (metric_date) 
            DO UPDATE SET total_lookups = total_lookups + 1
        """)
    
    def _record_cache_hit(self):
        """Record a cache hit."""
        self.con.execute("""
            UPDATE cache_metrics
            SET cache_hits = cache_hits + 1
            WHERE metric_date = CURRENT_DATE
        """)
    
    def record_claude_call(self):
        """Record when Claude is called for image generation."""
        self.con.execute("""
            INSERT INTO cache_metrics (metric_date, claude_calls)
            VALUES (CURRENT_DATE, 1)
            ON CONFLICT (metric_date)
            DO UPDATE SET claude_calls = claude_calls + 1
        """)