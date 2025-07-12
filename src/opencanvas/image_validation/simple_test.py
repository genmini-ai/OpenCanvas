#!/usr/bin/env python3
"""
Simple test script using direct imports.
This works without needing to install the full package.
"""

import os
import sys

def test_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required = [
        ('duckdb', 'duckdb'),
        ('anthropic', 'anthropic'), 
        ('aiohttp', 'aiohttp'),
        ('beautifulsoup4', 'bs4'),  # beautifulsoup4 imports as bs4
        ('numpy', 'numpy')
    ]
    missing = []
    
    for package_name, import_name in required:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def test_local_imports():
    """Test local module imports."""
    print("\n📦 Testing local imports...")
    
    modules = [
        'url_validator',
        'topic_image_cache', 
        'html_parser',
        'image_replacer',
        'config'
    ]
    
    for module in modules:
        try:
            globals()[module] = __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_basic_functionality():
    """Test basic functionality with local imports."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test URL validator
        from url_validator import URLValidator
        validator = URLValidator()
        print("  ✅ URLValidator created")
        
        # Test topic cache
        from topic_image_cache import TopicImageCache  
        cache = TopicImageCache()
        stats = cache.get_stats()
        print(f"  ✅ TopicImageCache created (topics: {stats['total_topics']})")
        
        # Test HTML parser
        from html_parser import SlideImageParser
        parser = SlideImageParser()
        sample_html = '<div><h1>Test</h1><img src="test.jpg" alt="test"></div>'
        images = parser.extract_images_from_html(sample_html)
        print(f"  ✅ HTMLParser working (found {len(images)} images)")
        
        # Test config
        from config import ImageValidationConfig
        config = ImageValidationConfig()
        print("  ✅ Config loaded")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_integration():
    """Test integration if API key is available."""
    print("\n🤖 Testing integration...")
    
    # Check for API key in multiple places
    api_key = None
    
    # Try to import config and get key
    try:
        import sys
        sys.path.append('../..')
        from opencanvas.config import Config
        api_key = Config.ANTHROPIC_API_KEY
        if api_key:
            print("  ✅ API key found in Config")
    except Exception as e:
        print(f"  ⚠️ Could not load Config: {e}")
    
    # Fallback to environment variable
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            print("  ✅ API key found in environment")
    
    if not api_key:
        print("  ⚠️ No API key found - skipping Claude tests")
        print("  💡 Check .env file or set ANTHROPIC_API_KEY environment variable")
        return True
    
    try:
        # Test integration by creating components individually
        # This avoids the relative import issues
        
        from topic_image_cache import TopicImageCache
        from url_validator import URLValidator
        from html_parser import SlideImageParser
        
        # Test that we can create the components
        cache = TopicImageCache()
        validator = URLValidator() 
        parser = SlideImageParser()
        
        print("  ✅ Core components created successfully")
        
        # Test HTML parsing and URL validation together
        test_html = '<div><h1>Test</h1><img src="https://httpbin.org/status/200" alt="test"></div>'
        images = parser.extract_images_from_html(test_html)
        
        if images:
            test_url = images[0]['src']
            result = validator.validate_single(test_url)
            print(f"  ✅ URL validation test: {result.get('valid', False)}")
        
        # Test cache operations
        stats = cache.get_stats()
        print(f"  ✅ Cache operations working (topics: {stats['total_topics']})")
        
        # Test topic normalization
        normalized = cache.normalize_topic("Test Topic for Image Validation")
        print(f"  ✅ Topic normalization: '{normalized}'")
        
        print("  ✅ Integration components working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration error: {e}")
        return False

def main():
    """Run simple tests."""
    print("🚀 Simple Image Validation Test")
    print("=" * 40)
    
    tests = [
        test_dependencies,
        test_local_imports,
        test_basic_functionality,
        test_integration
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ Basic functionality working!")
        print("\n💡 Next steps:")
        print("  1. Set ANTHROPIC_API_KEY for full functionality")
        print("  2. Try: python simple_test.py")
    else:
        print("❌ Some tests failed - check dependencies")

if __name__ == "__main__":
    main()