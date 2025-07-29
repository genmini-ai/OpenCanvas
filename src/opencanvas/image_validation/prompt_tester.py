"""
Test suite for tracking Claude prompt success rates and optimizing image retrieval.
Provides A/B testing framework and performance analytics.
"""

import json
import time
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import duckdb
import numpy as np

from opencanvas.image_validation.claude_image_retriever import ClaudeImageRetriever
from opencanvas.image_validation.url_validator import URLValidator
from opencanvas.image_validation.topic_image_cache import TopicImageCache
from opencanvas.config import Config


class PromptSuccessTracker:
    """Track and analyze prompt performance for image retrieval."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the tracker.
        
        Args:
            db_path: Path to DuckDB database for test results
        """
        if db_path is None:
            db_path = str(Path(__file__).parent / "prompt_tests.duckdb")
        
        self.con = duckdb.connect(db_path)
        self._init_schema()
        
        # Load test topics
        self.test_topics = self._load_test_topics()
    
    def _init_schema(self):
        """Initialize test database schema."""
        # Individual test results
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS prompt_tests (
                test_id VARCHAR PRIMARY KEY,
                prompt_version VARCHAR NOT NULL,
                topic VARCHAR NOT NULL,
                slide_context TEXT,
                generated_ids TEXT,  -- JSON array
                valid_ids TEXT,      -- JSON array after validation
                success_rate DECIMAL(3,2),
                response_time_ms INTEGER,
                tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Aggregated metrics per prompt version
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS prompt_metrics (
                prompt_version VARCHAR NOT NULL,
                test_date DATE NOT NULL,
                total_tests INTEGER DEFAULT 0,
                total_successes INTEGER DEFAULT 0,
                avg_success_rate DECIMAL(3,2),
                avg_valid_images DECIMAL(3,2),
                avg_response_time_ms INTEGER,
                min_success_rate DECIMAL(3,2),
                max_success_rate DECIMAL(3,2),
                PRIMARY KEY (prompt_version, test_date)
            )
        """)
        
        # A/B test configurations
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_name VARCHAR PRIMARY KEY,
                description TEXT,
                strategies TEXT,  -- JSON array of strategy names
                sample_size INTEGER,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status VARCHAR DEFAULT 'running',  -- running, completed, paused
                winner VARCHAR
            )
        """)
        
        # Create indexes
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_prompt_version ON prompt_tests(prompt_version)")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_tested_at ON prompt_tests(tested_at)")
    
    def _load_test_topics(self) -> List[Dict]:
        """Load diverse test topics for evaluation."""
        return [
            {
                "topic": "mountain landscape",
                "context": "Beautiful scenic mountain views with snow-capped peaks",
                "category": "nature"
            },
            {
                "topic": "data visualization",
                "context": "Charts and graphs showing business metrics and trends",
                "category": "business"
            },
            {
                "topic": "team collaboration",
                "context": "People working together in modern office environment",
                "category": "business"
            },
            {
                "topic": "artificial intelligence",
                "context": "Technology concepts related to AI and machine learning",
                "category": "technology"
            },
            {
                "topic": "sustainable energy",
                "context": "Solar panels, wind turbines, and renewable energy sources",
                "category": "environment"
            },
            {
                "topic": "urban architecture",
                "context": "Modern city buildings and architectural designs",
                "category": "architecture"
            },
            {
                "topic": "digital marketing",
                "context": "Online advertising, social media, and digital campaigns",
                "category": "marketing"
            },
            {
                "topic": "food photography",
                "context": "Delicious meals, ingredients, and culinary presentations",
                "category": "food"
            },
            {
                "topic": "fitness training",
                "context": "People exercising, gym equipment, and healthy lifestyle",
                "category": "health"
            },
            {
                "topic": "space exploration",
                "context": "Astronauts, rockets, planets, and cosmic imagery",
                "category": "science"
            },
            {
                "topic": "financial growth",
                "context": "Stock charts, money concepts, and investment graphics",
                "category": "finance"
            },
            {
                "topic": "ocean waves",
                "context": "Seascapes with powerful waves and marine environments",
                "category": "nature"
            },
            {
                "topic": "creative design",
                "context": "Artists working, design tools, and creative processes",
                "category": "creative"
            },
            {
                "topic": "remote work",
                "context": "Home office setups, video calls, and distributed teams",
                "category": "business"
            },
            {
                "topic": "medical technology",
                "context": "Healthcare innovations, medical devices, and research",
                "category": "healthcare"
            }
        ]
    
    def test_single_prompt(
        self, 
        retriever: ClaudeImageRetriever,
        strategy: str,
        topic_data: Dict
    ) -> Dict:
        """
        Test a single prompt strategy on one topic.
        
        Args:
            retriever: ClaudeImageRetriever instance
            strategy: Strategy name to test
            topic_data: Topic information
            
        Returns:
            Test result dictionary
        """
        test_id = f"{strategy}_{topic_data['topic']}_{int(time.time())}"
        topic = topic_data['topic']
        context = topic_data.get('context', f"A slide about {topic}")
        
        result = {
            'test_id': test_id,
            'prompt_version': strategy,
            'topic': topic,
            'slide_context': context,
            'generated_ids': [],
            'valid_ids': [],
            'success_rate': 0.0,
            'response_time_ms': 0,
            'error_message': None
        }
        
        try:
            # Temporarily set strategy
            original_strategy = retriever.current_strategy
            retriever.current_strategy = strategy
            
            # Test generation
            start_time = time.time()
            generated = retriever.generate_images(topic, context, max_retries=1)
            response_time = (time.time() - start_time) * 1000
            
            # Restore original strategy
            retriever.current_strategy = original_strategy
            
            # Process results
            if generated:
                result['generated_ids'] = [img_id for img_id, _ in generated]
                result['valid_ids'] = result['generated_ids']  # Already validated
                result['success_rate'] = len(result['valid_ids']) / len(result['generated_ids'])
            
            result['response_time_ms'] = int(response_time)
            
        except Exception as e:
            result['error_message'] = str(e)
        
        return result
    
    def run_ab_test(
        self,
        test_name: str,
        strategies: List[str],
        sample_size: int = 50,
        anthropic_api_key: Optional[str] = None
    ) -> Dict:
        """
        Run A/B test comparing multiple prompt strategies.
        
        Args:
            test_name: Name for this test
            strategies: List of strategy names to compare
            sample_size: Number of tests per strategy
            anthropic_api_key: Anthropic API key (from config/env if not provided)
            
        Returns:
            Test results summary
        """
        # Get API key if not provided
        if not anthropic_api_key:
            if Config and hasattr(Config, 'ANTHROPIC_API_KEY'):
                anthropic_api_key = Config.ANTHROPIC_API_KEY
            else:
                anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not anthropic_api_key:
            raise ValueError("No Anthropic API key found for A/B testing")
        
        # Initialize components
        cache = TopicImageCache()
        # Let ClaudeImageRetriever load API key from config/env  
        retriever = ClaudeImageRetriever(cache=cache)
        
        # Record test configuration
        self.con.execute("""
            INSERT OR REPLACE INTO ab_tests 
            (test_name, description, strategies, sample_size, start_date, status)
            VALUES (?, ?, ?, ?, ?, 'running')
        """, [
            test_name,
            f"A/B test comparing {', '.join(strategies)}",
            json.dumps(strategies),
            sample_size,
            datetime.now()
        ])
        
        # Run tests
        results = {strategy: [] for strategy in strategies}
        
        for strategy in strategies:
            print(f"Testing strategy: {strategy}")
            
            # Test each strategy on random sample of topics
            topic_sample = np.random.choice(
                len(self.test_topics), 
                min(sample_size, len(self.test_topics)), 
                replace=False
            )
            
            for i in topic_sample:
                topic_data = self.test_topics[i]
                result = self.test_single_prompt(retriever, strategy, topic_data)
                results[strategy].append(result)
                
                # Store individual result
                self._store_test_result(result)
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
        
        # Calculate summary statistics
        summary = self._calculate_test_summary(results)
        
        # Update A/B test record
        winner = max(summary.keys(), key=lambda k: summary[k]['avg_success_rate'])
        self.con.execute("""
            UPDATE ab_tests 
            SET end_date = ?, status = 'completed', winner = ?
            WHERE test_name = ?
        """, [datetime.now(), winner, test_name])
        
        return summary
    
    def _store_test_result(self, result: Dict):
        """Store individual test result in database."""
        self.con.execute("""
            INSERT INTO prompt_tests 
            (test_id, prompt_version, topic, slide_context, 
             generated_ids, valid_ids, success_rate, response_time_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            result['test_id'],
            result['prompt_version'],
            result['topic'],
            result['slide_context'],
            json.dumps(result['generated_ids']),
            json.dumps(result['valid_ids']),
            result['success_rate'],
            result['response_time_ms'],
            result['error_message']
        ])
    
    def _calculate_test_summary(self, results: Dict[str, List[Dict]]) -> Dict:
        """Calculate summary statistics for test results."""
        summary = {}
        
        for strategy, strategy_results in results.items():
            if not strategy_results:
                continue
            
            success_rates = [r['success_rate'] for r in strategy_results if r['success_rate'] is not None]
            response_times = [r['response_time_ms'] for r in strategy_results if r['response_time_ms'] is not None]
            valid_counts = [len(r['valid_ids']) for r in strategy_results]
            
            summary[strategy] = {
                'total_tests': len(strategy_results),
                'avg_success_rate': np.mean(success_rates) if success_rates else 0,
                'min_success_rate': np.min(success_rates) if success_rates else 0,
                'max_success_rate': np.max(success_rates) if success_rates else 0,
                'std_success_rate': np.std(success_rates) if success_rates else 0,
                'avg_response_time_ms': np.mean(response_times) if response_times else 0,
                'avg_valid_images': np.mean(valid_counts) if valid_counts else 0,
                'error_rate': len([r for r in strategy_results if r['error_message']]) / len(strategy_results)
            }
        
        return summary
    
    def get_best_strategy(self, min_tests: int = 10) -> Optional[str]:
        """
        Get the best performing strategy based on historical data.
        
        Args:
            min_tests: Minimum number of tests required
            
        Returns:
            Best strategy name or None
        """
        result = self.con.execute("""
            SELECT 
                prompt_version,
                COUNT(*) as test_count,
                AVG(success_rate) as avg_success_rate,
                AVG(response_time_ms) as avg_response_time
            FROM prompt_tests
            WHERE tested_at >= CURRENT_DATE - INTERVAL '30 days'
            AND error_message IS NULL
            GROUP BY prompt_version
            HAVING COUNT(*) >= ?
            ORDER BY avg_success_rate DESC, avg_response_time ASC
            LIMIT 1
        """, [min_tests]).fetchone()
        
        return result[0] if result else None
    
    def generate_report(self, days: int = 7) -> Dict:
        """
        Generate performance report for recent tests.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Performance report dictionary
        """
        # Overall statistics
        overall = self.con.execute("""
            SELECT 
                COUNT(*) as total_tests,
                COUNT(DISTINCT prompt_version) as strategies_tested,
                AVG(success_rate) as overall_success_rate,
                AVG(response_time_ms) as avg_response_time
            FROM prompt_tests
            WHERE tested_at >= CURRENT_DATE - INTERVAL ? days
        """, [days]).fetchone()
        
        # Per-strategy breakdown
        strategies = self.con.execute("""
            SELECT 
                prompt_version,
                COUNT(*) as test_count,
                AVG(success_rate) as avg_success_rate,
                STDDEV(success_rate) as std_success_rate,
                AVG(response_time_ms) as avg_response_time,
                MIN(success_rate) as min_success_rate,
                MAX(success_rate) as max_success_rate
            FROM prompt_tests
            WHERE tested_at >= CURRENT_DATE - INTERVAL ? days
            AND error_message IS NULL
            GROUP BY prompt_version
            ORDER BY avg_success_rate DESC
        """, [days]).fetchall()
        
        # Topic performance
        topics = self.con.execute("""
            SELECT 
                topic,
                COUNT(*) as test_count,
                AVG(success_rate) as avg_success_rate
            FROM prompt_tests
            WHERE tested_at >= CURRENT_DATE - INTERVAL ? days
            GROUP BY topic
            ORDER BY avg_success_rate ASC
            LIMIT 10
        """, [days]).fetchall()
        
        return {
            'period_days': days,
            'overall': {
                'total_tests': overall[0] if overall else 0,
                'strategies_tested': overall[1] if overall else 0,
                'overall_success_rate': float(overall[2] or 0),
                'avg_response_time_ms': float(overall[3] or 0)
            },
            'strategies': [
                {
                    'name': s[0],
                    'test_count': s[1],
                    'avg_success_rate': float(s[2] or 0),
                    'std_success_rate': float(s[3] or 0),
                    'avg_response_time_ms': float(s[4] or 0),
                    'min_success_rate': float(s[5] or 0),
                    'max_success_rate': float(s[6] or 0)
                }
                for s in strategies
            ],
            'worst_topics': [
                {
                    'topic': t[0],
                    'test_count': t[1],
                    'avg_success_rate': float(t[2] or 0)
                }
                for t in topics
            ]
        }
    
    def cleanup_old_tests(self, days: int = 90):
        """Remove test data older than specified days."""
        deleted = self.con.execute("""
            DELETE FROM prompt_tests
            WHERE tested_at < CURRENT_DATE - INTERVAL ? days
        """, [days]).fetchone()
        
        return deleted[0] if deleted else 0