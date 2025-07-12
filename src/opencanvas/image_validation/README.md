# Image Validation System

A comprehensive image validation and replacement system for OpenCanvas presentation generation. This system validates image URLs, caches successful lookups, and uses Claude to generate replacement images for failed URLs.

## 🚀 Features

### Core Functionality
- **URL Validation**: Efficient batch validation with HEAD requests
- **Topic-Based Caching**: DuckDB storage with topic-to-image-ID mapping
- **Claude Integration**: AI-powered image retrieval with multiple prompt strategies
- **Smart Replacement**: Context-aware image replacement in HTML
- **Performance Tracking**: A/B testing framework for prompt optimization

### Key Benefits
- **Memory Efficient**: Stores only image IDs instead of full URLs (60% space reduction)
- **Compute Efficient**: DuckDB vectorized operations for fast batch processing
- **Self-Improving**: Topic similarity matching and usage-based ranking
- **Reliable**: Fallback mechanisms and graceful error handling

## 📁 Architecture

```
image_validation/
├── __init__.py                 # Package exports
├── config.py                   # Configuration settings
├── image_validator.py          # Main pipeline coordinator
├── topic_image_cache.py        # DuckDB topic-ID cache
├── url_validator.py            # URL validation with async support
├── claude_image_retriever.py   # Claude-based image generation
├── html_parser.py              # HTML parsing and context extraction
├── image_replacer.py           # Image replacement in HTML
├── prompt_tester.py            # A/B testing framework
├── cache_utils.py              # Maintenance utilities
├── test_image_validation.py    # Test suite
└── data/                       # Database storage
    ├── topic_images.duckdb     # Main cache database
    └── prompt_tests.duckdb     # Test results database
```

## 🔧 Quick Start

### 1. Basic Usage

```python
from opencanvas.image_validation import ImageValidationPipeline

# Initialize (requires ANTHROPIC_API_KEY environment variable)
pipeline = ImageValidationPipeline()

# Validate and fix images in slides
slides = [{'html': '<img src="https://invalid-url.jpg" alt="example">', 'id': 'slide1'}]
validated_slides, report = pipeline.validate_and_fix_slides(slides)

print(f"Replaced {report['successful_replacements']} images")
```

### 2. Integration with TopicGenerator

The system is automatically integrated with `TopicGenerator`:

```python
from opencanvas.generators.topic_generator import TopicGenerator

# Image validation is enabled by default
generator = TopicGenerator(api_key="your-key")

# Generate presentation with automatic image validation
results = generator.generate_from_topic("AI in healthcare", "educational")

# Check validation report
if 'image_validation_report' in results:
    print(f"Images validated: {results['image_validation_report']}")
```

### 3. Disable Image Validation

```python
# Disable during initialization
generator = TopicGenerator(api_key="your-key", enable_image_validation=False)

# Or via environment variable
import os
os.environ['ENABLE_IMAGE_VALIDATION'] = 'false'
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required for Claude functionality
export ANTHROPIC_API_KEY="your-anthropic-key"

# Core settings
export ENABLE_IMAGE_VALIDATION="true"
export IMAGE_VALIDATION_TIMEOUT="3.0"
export MAX_CONCURRENT_VALIDATIONS="10"

# Cache settings
export CACHE_TTL_DAYS="7"
export MAX_IMAGES_PER_TOPIC="3"
export MIN_CONFIDENCE_SCORE="0.7"

# Performance settings
export SLIDE_PROCESSING_TIMEOUT="30.0"
export MIN_TOPIC_SIMILARITY="0.6"
```

### Configuration Class

```python
from opencanvas.image_validation import ImageValidationConfig

# Print current configuration
ImageValidationConfig.print_config_summary()

# Validate environment
status = ImageValidationConfig.validate_environment()
if not status['valid']:
    print("Configuration errors:", status['errors'])
```

## 🧪 Testing

### Run Test Suite

```bash
# Navigate to the image validation directory
cd src/opencanvas/image_validation

# Quick setup verification
python quick_test.py

# Full test suite
python test_image_validation.py
```

### Individual Component Tests

```python
# Test URL validation
from opencanvas.image_validation import URLValidator
validator = URLValidator()
results = validator.validate_batch(["https://images.unsplash.com/photo-123"])

# Test topic cache
from opencanvas.image_validation import TopicImageCache
cache = TopicImageCache()
images = cache.get_images_for_topic("mountain landscape")

# Test Claude retrieval (requires API key)
from opencanvas.image_validation import ClaudeImageRetriever
retriever = ClaudeImageRetriever("your-api-key")
images = retriever.get_images_with_fallback("technology trends")
```

## 📊 Performance Analytics

### A/B Testing Framework

```python
from opencanvas.image_validation import PromptSuccessTracker

tracker = PromptSuccessTracker()

# Run A/B test comparing prompt strategies
results = tracker.run_ab_test(
    test_name="prompt_comparison_v1",
    strategies=["v1_direct", "v2_context", "v3_fallback"],
    sample_size=20,
    anthropic_api_key="your-key"
)

# Generate performance report
report = tracker.generate_report(days=7)
print(f"Overall success rate: {report['overall']['overall_success_rate']:.1%}")
```

### Cache Analytics

```python
from opencanvas.image_validation import CacheMaintenanceUtils

utils = CacheMaintenanceUtils()

# Analyze performance
analysis = utils.analyze_cache_performance(days=7)
print(f"Cache hit rate: {analysis['recent_performance']['hit_rate']:.1%}")

# Generate maintenance report
report = utils.generate_maintenance_report()
print(f"System health: {report['system_health']['status']}")
```

## 🔍 How It Works

### 1. URL Validation Flow

```
HTML Content → Extract Images → Batch Validate URLs → Identify Failed Images
```

- Uses async HTTP HEAD requests for efficiency
- Validates content-type headers
- Caches validation results in-memory

### 2. Topic-Based Replacement

```
Failed Image → Extract Context → Normalize Topic → Check Cache → Generate with Claude
```

- Analyzes slide content for context
- Normalizes topics for consistent matching
- Uses Jaccard similarity for topic matching
- Stores only image IDs for efficiency

### 3. Cache Architecture

```sql
-- Topic mappings for debugging
topic_mappings: topic_hash → topic_text, normalized_text

-- Image cache with usage tracking
image_cache: (topic_hash, image_id) → source, valid, usage_count, confidence

-- Performance metrics
cache_metrics: date → lookups, hits, claude_calls
```

### 4. Prompt Strategies

The system uses optimized prompt strategies for Claude image generation:

- **v2_improved** ⭐: Context-aware with anti-duplicate instructions - **DEFAULT STRATEGY**
- **v1_direct**: Simple, direct URL requests - previous default
- **v3_quality**: Professional photographer perspective, quality over quantity

Performance is tracked and the best-performing strategy is automatically selected.

#### Strategy Performance Benchmarks (10-topic average)

| Strategy | Success Rate | Response Time | Cost per Request | Notes |
|----------|-------------|---------------|------------------|-------|
| **CURRENT_PRODUCTION** | **100.0%** | **39ms** | Cache/Free | Uses cache + fallbacks |
| **v2_improved** ⭐ | **93.3%** | **1725ms** | **$0.000215** | **NEW DEFAULT - Best individual** |
| **v1_direct** | 90.0% | 2199ms | $0.000211 | Previous default |
| **v3_quality** | 60.0% | 1719ms | $0.000245 | Conservative quality-focused |

*Benchmark shows production pipeline (with caching) significantly outperforms individual strategies due to cache hits and topic similarity matching.*

## 🛠️ Maintenance

### Regular Maintenance

```python
from opencanvas.image_validation import CacheMaintenanceUtils

utils = CacheMaintenanceUtils()

# Clean up old data (run weekly)
cleanup_result = utils.cleanup_expired_data(days=30)

# Optimize cache (run monthly)
optimization_result = utils.optimize_cache()

# Export cache for backup
export_result = utils.export_cache_data("backup.json", format="json")
```

### Health Monitoring

```python
# Check system health
pipeline = ImageValidationPipeline()
stats = pipeline.get_system_stats()

print(f"Cache hit rate: {stats['cache']['weekly_hit_rate']:.1f}%")
print(f"Prompt success rate: {stats['system_health']['avg_prompt_success']:.1f}%")
```

## 🐛 Troubleshooting

### Common Issues

**1. "No Anthropic API key provided"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**2. "Image validation disabled due to error"**
- Check database permissions in `data/` directory
- Verify DuckDB installation: `pip install duckdb`

**3. "Low cache hit rate"**
- Increase `MIN_TOPIC_SIMILARITY` for broader matching
- Check topic normalization with similar phrases

**4. "High Claude call rate"**
- Improve cache coverage by running more diverse topics
- Lower `MIN_CONFIDENCE_SCORE` to accept more cached images

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
os.environ['IMAGE_VALIDATION_LOG_LEVEL'] = 'DEBUG'
```

### Performance Profiling

```python
# Profile URL validation
import time
start = time.time()
results = validator.validate_batch(urls)
print(f"Validated {len(urls)} URLs in {time.time() - start:.2f}s")

# Profile cache operations
start = time.time()
images = cache.get_images_for_topic("business")
print(f"Cache lookup in {(time.time() - start) * 1000:.1f}ms")
```

## 🧪 Testing

### Strategy Performance Testing

Test different prompt strategies and measure performance:

```bash
cd src/opencanvas/image_validation
python test_claude_retriever.py
```

**Test Options:**
- **Option 1**: Test all topics (comprehensive)
- **Option 2**: Test prompt strategies (single topic or "multi" for 10-topic average)
- **Option 3**: Test single topic
- **Option 4**: Quick test (3 topics)

**Example Multi-Topic Benchmark:**
```bash
# Choose option 2, enter "multi"
python test_claude_retriever.py
Enter choice (1-4): 2
Enter topic (or 'multi' for 10-topic average): multi
```

**Sample Output:**
```
🔹 v1_direct:
   Average Success Rate: 86.7%
   Test Success Rate: 90.0% (9/10 topics)
   Average Response Time: 3430ms
   Total Images: 23/25 distinct valid (from 30 generated)
   Average Tokens: 360 (235 in, 125 out)
   Average Cost: $0.000215 per request
```

**Key Metrics:**
- **Success Rate**: % of distinct URLs that are valid
- **Distinct vs Generated**: Shows duplicate detection (e.g., 25 distinct from 30 total)
- **Token Usage**: Input/output tokens for cost analysis
- **Cost per Request**: Based on Haiku pricing ($0.25/1M input, $1.25/1M output)

## 🤝 Contributing

### Adding New Image Sources

```python
# In config.py, add new source
IMAGE_SOURCES = {
    # ... existing sources
    3: {
        'name': 'new_source',
        'url_template': 'https://example.com/image/{id}',
        'enabled': True
    }
}

# Update url_validator.py patterns
self.cdn_patterns['new_source'] = re.compile(r'example\.com/image/([a-zA-Z0-9_-]+)')
```

### Adding New Prompt Strategies

```python
# In claude_image_retriever.py
self.prompt_templates["v4_new"] = {
    "system": "Your system prompt...",
    "user": "Your user prompt template with {topic} and {slide_context}..."
}
```

### Performance Optimization

1. **Database Optimization**: Add indexes for frequent queries
2. **Caching Strategy**: Implement Redis for distributed caching
3. **Prompt Efficiency**: Reduce token usage while maintaining quality
4. **Parallel Processing**: Increase concurrent validations based on hardware

## 📋 API Reference

### Main Classes

- **ImageValidationPipeline**: Main entry point for validation
- **TopicImageCache**: DuckDB-based topic-to-image cache
- **URLValidator**: Async URL validation with batch support
- **ClaudeImageRetriever**: AI-powered image generation
- **SlideImageParser**: HTML parsing and context extraction
- **ImageReplacer**: HTML modification for image replacement
- **PromptSuccessTracker**: A/B testing and performance tracking
- **CacheMaintenanceUtils**: System maintenance utilities
- **ImageValidationConfig**: Configuration management

### Key Methods

```python
# Validate slides
validated_slides, report = pipeline.validate_and_fix_slides(slides)

# Manual validation
is_valid = validator.validate_single("https://example.com/image.jpg")

# Cache operations
images = cache.get_images_for_topic("landscape photography")
cache.add_images_for_topic("nature", [("image_id", 0, True, 0.9)])

# Generate images
images = retriever.get_images_with_fallback("business meeting")

# System maintenance
utils.cleanup_expired_data(days=30)
report = utils.generate_maintenance_report()
```

## 📜 License

This module is part of the OpenCanvas project. See the main project license for details.

## 🙋 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the test suite for usage examples
3. Check system health with `utils.generate_maintenance_report()`
4. Enable debug logging for detailed error information