#!/usr/bin/env python3
"""
Quick test script to verify image validation setup.
Run this first to check if all dependencies are available.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for proper imports
current_dir = Path(__file__).parent  # image_validation directory
opencanvas_dir = current_dir.parent   # opencanvas directory  
src_dir = opencanvas_dir.parent       # src directory
sys.path.insert(0, str(src_dir))

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'duckdb',
        'anthropic', 
        'aiohttp',
        'beautifulsoup4',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies available")
    return True

def check_environment():
    """Check environment configuration."""
    print("\n🔧 Checking environment...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"  ✅ ANTHROPIC_API_KEY set (length: {len(api_key)})")
    else:
        print("  ⚠️ ANTHROPIC_API_KEY not set (Claude features will be disabled)")
    
    # Check other settings
    settings = {
        'IMAGE_VALIDATION_TIMEOUT': '3.0',
        'MAX_CONCURRENT_VALIDATIONS': '10',
        'CACHE_TTL_DAYS': '7'
    }
    
    for key, default in settings.items():
        value = os.getenv(key, default)
        print(f"  • {key}: {value}")

def test_basic_imports():
    """Test basic module imports."""
    print("\n📦 Testing module imports...")
    
    try:
        from opencanvas.image_validation import (
            URLValidator,
            TopicImageCache,
            SlideImageParser,
            ImageReplacer,
            ImageValidationConfig
        )
        print("  ✅ opencanvas.image_validation imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_database_creation():
    """Test database creation."""
    print("\n💾 Testing database setup...")
    
    try:
        from opencanvas.image_validation import TopicImageCache
        cache = TopicImageCache()
        stats = cache.get_stats()
        print(f"  ✅ Database created successfully")
        print(f"  📊 Cache stats: {stats['total_topics']} topics, {stats['total_images']} images")
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_url_validation():
    """Test URL validation."""
    print("\n🌐 Testing URL validation...")
    
    try:
        from opencanvas.image_validation import URLValidator
        validator = URLValidator()
        
        # Test with a known good URL
        result = validator.validate_single("https://httpbin.org/status/200")
        print(f"  ✅ URL validation working")
        print(f"  📊 Test result: valid={result.get('valid', False)}")
        return True
    except Exception as e:
        print(f"  ❌ URL validation error: {e}")
        return False

def test_html_parsing():
    """Test HTML parsing."""
    print("\n📄 Testing HTML parsing...")
    
    try:
        from opencanvas.image_validation import SlideImageParser
        parser = SlideImageParser()
        
        # Test with sample HTML
        sample_html = '<div><h1>Test</h1><img src="test.jpg" alt="test"></div>'
        images = parser.extract_images_from_html(sample_html)
        context = parser.extract_slide_context(sample_html)
        
        print(f"  ✅ HTML parsing working")
        print(f"  📊 Found {len(images)} images, slide type: {context.get('slide_type', 'unknown')}")
        return True
    except Exception as e:
        print(f"  ❌ HTML parsing error: {e}")
        return False

def test_claude_integration():
    """Test Claude integration if API key is available."""
    print("\n🤖 Testing Claude integration...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("  ⚠️ Skipping Claude test - no API key")
        return True
    
    try:
        from opencanvas.image_validation import ClaudeImageRetriever, TopicImageCache
        
        cache = TopicImageCache()
        retriever = ClaudeImageRetriever(api_key, cache)
        
        print(f"  ✅ Claude integration initialized")
        print(f"  📊 Available strategies: {list(retriever.prompt_templates.keys())}")
        
        # Note: We don't actually call Claude in quick test to avoid API costs
        return True
    except Exception as e:
        print(f"  ❌ Claude integration error: {e}")
        return False

def main():
    """Run all quick tests."""
    print("🚀 Image Validation Quick Test")
    print("=" * 40)
    
    tests = [
        check_dependencies,
        check_environment,
        test_basic_imports,
        test_database_creation,
        test_url_validation,
        test_html_parsing,
        test_claude_integration
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ System ready! You can now run:")
        print("   python test_image_validation.py")
    else:
        print("❌ Fix the issues above before running full tests")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)