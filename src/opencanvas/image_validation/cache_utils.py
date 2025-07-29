"""
Cache maintenance utilities for the image validation system.
Provides cleanup, export, and statistics functions.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

from opencanvas.image_validation.topic_image_cache import TopicImageCache
from opencanvas.image_validation.prompt_tester import PromptSuccessTracker

logger = logging.getLogger(__name__)


class CacheMaintenanceUtils:
    """Utilities for maintaining and analyzing cache data."""
    
    def __init__(self, cache_db_path: Optional[str] = None, test_db_path: Optional[str] = None):
        """
        Initialize maintenance utilities.
        
        Args:
            cache_db_path: Path to cache database
            test_db_path: Path to test database
        """
        self.cache = TopicImageCache(cache_db_path)
        self.tracker = PromptSuccessTracker(test_db_path)
    
    def cleanup_expired_data(self, days: int = 30) -> Dict:
        """
        Clean up expired data from both cache and test databases.
        
        Args:
            days: Number of days to keep data
            
        Returns:
            Cleanup summary
        """
        logger.info(f"🧹 Starting cleanup of data older than {days} days...")
        
        start_time = time.time()
        
        # Clean cache
        cache_removed = self.cache.cleanup_expired(days)
        
        # Clean test data
        test_removed = self.tracker.cleanup_old_tests(days)
        
        cleanup_time = time.time() - start_time
        
        summary = {
            'cache_entries_removed': cache_removed,
            'test_entries_removed': test_removed,
            'cleanup_time_seconds': cleanup_time,
            'cleanup_date': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Cleanup complete: {cache_removed} cache entries, {test_removed} test entries removed in {cleanup_time:.2f}s")
        
        return summary
    
    def export_cache_data(self, output_path: str, format: str = 'json') -> Dict:
        """
        Export cache data for backup or analysis.
        
        Args:
            output_path: Path to export file
            format: Export format ('json', 'csv')
            
        Returns:
            Export summary
        """
        logger.info(f"📤 Exporting cache data to {output_path}...")
        
        start_time = time.time()
        
        try:
            # Get all cache data
            cache_data = self.cache.con.execute("""
                SELECT 
                    tm.topic_text,
                    tm.normalized_text,
                    ic.image_id,
                    ic.source,
                    ic.valid,
                    ic.usage_count,
                    ic.confidence_score,
                    ic.last_validated
                FROM topic_mappings tm
                JOIN image_cache ic ON tm.topic_hash = ic.topic_hash
                ORDER BY tm.topic_text, ic.usage_count DESC
            """).fetchall()
            
            if format.lower() == 'json':
                # Export as JSON
                export_data = {
                    'export_date': datetime.now().isoformat(),
                    'total_entries': len(cache_data),
                    'cache_entries': [
                        {
                            'topic': row[0],
                            'normalized_topic': row[1],
                            'image_id': row[2],
                            'source': row[3],
                            'valid': bool(row[4]),
                            'usage_count': row[5],
                            'confidence_score': float(row[6]) if row[6] else 0.0,
                            'last_validated': row[7]
                        }
                        for row in cache_data
                    ]
                }
                
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
            elif format.lower() == 'csv':
                # Export as CSV
                import csv
                
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'topic', 'normalized_topic', 'image_id', 'source', 
                        'valid', 'usage_count', 'confidence_score', 'last_validated'
                    ])
                    writer.writerows(cache_data)
            
            export_time = time.time() - start_time
            
            summary = {
                'export_path': output_path,
                'format': format,
                'entries_exported': len(cache_data),
                'export_time_seconds': export_time,
                'file_size_bytes': Path(output_path).stat().st_size if Path(output_path).exists() else 0
            }
            
            logger.info(f"✅ Export complete: {len(cache_data)} entries exported in {export_time:.2f}s")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return {'error': str(e)}
    
    def analyze_cache_performance(self, days: int = 7) -> Dict:
        """
        Analyze cache performance over recent period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Performance analysis
        """
        logger.info(f"📊 Analyzing cache performance for last {days} days...")
        
        # Get cache metrics
        cache_stats = self.cache.get_stats()
        
        # Get recent metrics
        recent_metrics = self.cache.con.execute("""
            SELECT 
                metric_date,
                total_lookups,
                cache_hits,
                claude_calls,
                CASE 
                    WHEN total_lookups > 0 THEN cache_hits * 100.0 / total_lookups 
                    ELSE 0 
                END as hit_rate
            FROM cache_metrics
            WHERE metric_date >= CURRENT_DATE - INTERVAL ? days
            ORDER BY metric_date DESC
        """, [days]).fetchall()
        
        # Calculate totals
        total_lookups = sum(row[1] for row in recent_metrics)
        total_hits = sum(row[2] for row in recent_metrics)
        total_claude_calls = sum(row[3] for row in recent_metrics)
        
        # Get top topics
        top_topics = self.cache.con.execute("""
            SELECT 
                tm.topic_text,
                SUM(ic.usage_count) as total_usage,
                COUNT(DISTINCT ic.image_id) as unique_images,
                AVG(ic.confidence_score) as avg_confidence
            FROM topic_mappings tm
            JOIN image_cache ic ON tm.topic_hash = ic.topic_hash
            WHERE ic.valid = true
            GROUP BY tm.topic_hash, tm.topic_text
            ORDER BY total_usage DESC
            LIMIT 10
        """).fetchall()
        
        # Get domain statistics
        domain_stats = {}
        domain_data = self.cache.con.execute("""
            SELECT 
                CASE ic.source
                    WHEN 0 THEN 'unsplash'
                    WHEN 1 THEN 'pexels'
                    WHEN 2 THEN 'pixabay'
                    ELSE 'other'
                END as domain,
                COUNT(*) as total_images,
                SUM(CASE WHEN ic.valid THEN 1 ELSE 0 END) as valid_images,
                SUM(ic.usage_count) as total_usage
            FROM image_cache ic
            GROUP BY ic.source
        """).fetchall()
        
        for row in domain_data:
            domain_stats[row[0]] = {
                'total_images': row[1],
                'valid_images': row[2],
                'total_usage': row[3],
                'success_rate': row[2] / row[1] if row[1] > 0 else 0
            }
        
        analysis = {
            'analysis_period_days': days,
            'cache_overview': cache_stats,
            'recent_performance': {
                'total_lookups': total_lookups,
                'total_hits': total_hits,
                'total_claude_calls': total_claude_calls,
                'hit_rate': total_hits / total_lookups if total_lookups > 0 else 0,
                'claude_call_rate': total_claude_calls / total_lookups if total_lookups > 0 else 0
            },
            'daily_metrics': [
                {
                    'date': row[0],
                    'lookups': row[1],
                    'hits': row[2],
                    'claude_calls': row[3],
                    'hit_rate': row[4]
                }
                for row in recent_metrics
            ],
            'top_topics': [
                {
                    'topic': row[0],
                    'usage_count': row[1],
                    'unique_images': row[2],
                    'avg_confidence': float(row[3]) if row[3] else 0.0
                }
                for row in top_topics
            ],
            'domain_statistics': domain_stats
        }
        
        return analysis
    
    def optimize_cache(self) -> Dict:
        """
        Optimize cache by removing low-value entries and consolidating similar topics.
        
        Returns:
            Optimization summary
        """
        logger.info("⚡ Optimizing cache...")
        
        start_time = time.time()
        optimizations = []
        
        # Remove images with very low confidence and no usage
        low_confidence_removed = self.cache.con.execute("""
            DELETE FROM image_cache
            WHERE confidence_score < 0.3
            AND usage_count = 0
            AND last_validated < CURRENT_DATE - INTERVAL '7 days'
        """).fetchone()
        
        if low_confidence_removed and low_confidence_removed[0] > 0:
            optimizations.append(f"Removed {low_confidence_removed[0]} low-confidence unused images")
        
        # Remove orphaned topic mappings
        orphaned_removed = self.cache.con.execute("""
            DELETE FROM topic_mappings
            WHERE topic_hash NOT IN (SELECT DISTINCT topic_hash FROM image_cache)
        """).fetchone()
        
        if orphaned_removed and orphaned_removed[0] > 0:
            optimizations.append(f"Removed {orphaned_removed[0]} orphaned topic mappings")
        
        # Vacuum database
        self.cache.con.execute("VACUUM")
        optimizations.append("Database vacuumed")
        
        optimization_time = time.time() - start_time
        
        summary = {
            'optimizations_performed': optimizations,
            'optimization_time_seconds': optimization_time,
            'optimization_date': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Cache optimization complete in {optimization_time:.2f}s")
        for opt in optimizations:
            logger.info(f"  • {opt}")
        
        return summary
    
    def generate_maintenance_report(self) -> Dict:
        """
        Generate comprehensive maintenance report.
        
        Returns:
            Complete maintenance report
        """
        logger.info("📋 Generating maintenance report...")
        
        # Get basic stats
        cache_stats = self.cache.get_stats()
        
        # Get system health indicators
        performance = self.analyze_cache_performance(days=30)
        
        # Get test performance
        test_report = self.tracker.generate_report(days=30)
        
        # Calculate health score
        health_indicators = {
            'cache_hit_rate': performance['recent_performance']['hit_rate'],
            'image_success_rate': cache_stats['valid_images'] / cache_stats['total_images'] if cache_stats['total_images'] > 0 else 0,
            'prompt_success_rate': test_report['overall']['overall_success_rate'] if 'overall' in test_report else 0,
            'usage_distribution': min(1.0, cache_stats['avg_usage'] / 10.0) if cache_stats['avg_usage'] else 0
        }
        
        overall_health = sum(health_indicators.values()) / len(health_indicators)
        
        report = {
            'report_date': datetime.now().isoformat(),
            'system_health': {
                'overall_score': overall_health,
                'status': 'excellent' if overall_health > 0.8 else 'good' if overall_health > 0.6 else 'needs_attention',
                'indicators': health_indicators
            },
            'cache_statistics': cache_stats,
            'performance_analysis': performance,
            'test_performance': test_report,
            'recommendations': self._generate_recommendations(cache_stats, performance, test_report)
        }
        
        return report
    
    def _generate_recommendations(self, cache_stats: Dict, performance: Dict, test_report: Dict) -> List[str]:
        """Generate maintenance recommendations based on analysis."""
        recommendations = []
        
        # Cache recommendations
        hit_rate = performance['recent_performance']['hit_rate']
        if hit_rate < 0.5:
            recommendations.append("Low cache hit rate - consider expanding topic similarity matching")
        
        if cache_stats['total_topics'] < 50:
            recommendations.append("Small cache size - system will improve with more usage")
        
        # Performance recommendations
        claude_call_rate = performance['recent_performance']['claude_call_rate']
        if claude_call_rate > 0.3:
            recommendations.append("High Claude call rate - consider improving cache coverage")
        
        # Test recommendations
        if 'overall' in test_report and test_report['overall']['overall_success_rate'] < 0.7:
            recommendations.append("Low prompt success rate - consider optimizing prompt strategies")
        
        if len(recommendations) == 0:
            recommendations.append("System performing well - no immediate action needed")
        
        return recommendations