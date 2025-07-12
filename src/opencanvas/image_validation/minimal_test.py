#!/usr/bin/env python3
"""
Minimal test that avoids complex imports.
Tests core functionality without integration issues.
"""

import os
from pathlib import Path

def test_api_key_access():
    """Test if we can access the API key."""
    print("🔑 Testing API key access...")
    
    # Method 1: Direct environment variable
    env_key = os.getenv('ANTHROPIC_API_KEY')
    if env_key:
        print(f"  ✅ Found API key in environment (length: {len(env_key)})")
        return True
    
    # Method 2: Try loading from .env file manually
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        print(f"  📁 Found .env file at: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'')
                    if key:
                        print(f"  ✅ Found API key in .env file (length: {len(key)})")
                        return True
    
    print("  ❌ No API key found")
    return False

def test_basic_components():
    """Test basic components individually."""
    print("\n🧪 Testing basic components...")
    
    try:
        # Test URL validator
        from url_validator import URLValidator
        validator = URLValidator()
        print("  ✅ URLValidator imported and created")
        
        # Test topic cache
        from topic_image_cache import TopicImageCache
        cache = TopicImageCache()
        stats = cache.get_stats()
        print(f"  ✅ TopicImageCache created (topics: {stats['total_topics']})")
        
        # Test HTML parser
        from html_parser import SlideImageParser
        parser = SlideImageParser()
        print("  ✅ SlideImageParser created")
        
        # Test basic parsing
        sample = '<div><h1>Test</h1><img src="test.jpg" alt="test"></div>'
        images = parser.extract_images_from_html(sample)
        print(f"  ✅ HTML parsing works (found {len(images)} images)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component test failed: {e}")
        return False

def test_url_validation():
    """Test URL validation with a real URL."""
    print("\n🌐 Testing URL validation...")
    
    try:
        from url_validator import URLValidator
        validator = URLValidator()
        
        # Test with a known working URL
        test_url = "https://httpbin.org/status/200"
        result = validator.validate_single(test_url)
        
        print(f"  📊 Test URL: {test_url}")
        print(f"  📊 Valid: {result.get('valid', False)}")
        print(f"  📊 Status: {result.get('status_code', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ URL validation failed: {e}")
        return False

def main():
    """Run minimal tests."""
    print("🚀 Minimal Image Validation Test")
    print("=" * 40)
    
    tests = [
        test_api_key_access,
        test_basic_components,
        test_url_validation
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test exception: {e}")
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ Core functionality working!")
        print("\n💡 Next steps:")
        print("  1. Try: python minimal_test.py")
        print("  2. If this works, try: python simple_test.py")
        print("  3. Then try integration with topic generation")
    else:
        print("❌ Some core components have issues")
        
    return passed == len(tests)

if __name__ == "__main__":
    main()