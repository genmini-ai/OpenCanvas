import os
import pytest
import tempfile
from pathlib import Path

from opencanvas.generators.topic_generator import TopicGenerator
from opencanvas.config import Config

# Test cases for topic generation
TOPIC_TEST_CASES = [
    {
        "name": "Startup Pitch Deck",
        "user_text": "AI-powered fitness app that creates personalized workout plans using computer vision to analyze form and provide real-time feedback",
        "purpose": "pitch deck",
        "theme": "bold high contrast"
    },
    {
        "name": "Academic Research Presentation",
        "user_text": "Climate change impacts on coral reef ecosystems: a longitudinal study of bleaching events in the Great Barrier Reef from 2010-2024",
        "purpose": "academic presentation",
        "theme": "clean minimalist"
    },
    {
        "name": "Product Marketing Launch",
        "user_text": "New sustainable packaging initiative that reduces plastic waste by 70% while maintaining product freshness and brand appeal",
        "purpose": "marketing presentation",
        "theme": "natural earth"
    },
    {
        "name": "Industry Keynote",
        "user_text": "The future of artificial intelligence in healthcare: from diagnostic imaging to personalized medicine and ethical considerations",
        "purpose": "general presentation",
        "theme": "modern contemporary"
    },
    {
        "name": "Personal Finance Workshop",
        "user_text": "Building wealth through smart investing: understanding compound interest, diversification strategies, and retirement planning for millennials",
        "purpose": "educational presentation",
        "theme": "warm earth tones"
    }
]

class TestTopicGenerator:
    """Test cases for topic-based presentation generation"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method"""
        # Skip tests if no API key
        if not Config.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not provided")
        
        self.generator = TopicGenerator(
            api_key=Config.ANTHROPIC_API_KEY,
            brave_api_key=Config.BRAVE_API_KEY
        )
    
    def test_knowledge_assessment(self):
        """Test knowledge depth assessment"""
        # Test with a well-known topic
        result = self.generator.assess_knowledge_depth("Python programming basics")
        assert result in ["SUFFICIENT", "INSUFFICIENT"]
        
        # Test with a very specific/recent topic
        result = self.generator.assess_knowledge_depth("Latest AI developments in Q1 2025")
        assert result in ["SUFFICIENT", "INSUFFICIENT"]
    
    def test_search_query_generation(self):
        """Test search query generation"""
        query = self.generator.generate_search_query("machine learning applications")
        assert isinstance(query, str)
        assert len(query.split()) <= 8
        assert len(query) > 0
    
    def test_blog_generation(self):
        """Test blog content generation"""
        blog = self.generator.generate_blog("Renewable energy benefits")
        assert isinstance(blog, str)
        assert len(blog) > 500  # Should be substantial content
        assert "renewable" in blog.lower() or "energy" in blog.lower()
    
    @pytest.mark.parametrize("test_case", TOPIC_TEST_CASES[:2])  # Test first 2 cases
    def test_full_generation_pipeline(self, test_case):
        """Test complete generation pipeline for selected topics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory for outputs
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = self.generator.generate_from_topic(
                    user_text=test_case["user_text"],
                    purpose=test_case["purpose"],
                    theme=test_case["theme"]
                )
                
                # Verify result structure
                assert result is not None
                assert "html_content" in result
                assert "html_file" in result
                assert "knowledge_assessment" in result
                
                # Verify HTML file was created
                html_file = Path(result["html_file"])
                assert html_file.exists()
                
                # Verify HTML content
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                assert "<!DOCTYPE html>" in html_content
                assert "<html" in html_content
                assert "</html>" in html_content
                assert len(html_content) > 1000  # Should be substantial
                
            finally:
                os.chdir(original_cwd)
    
    def test_theme_handling(self):
        """Test different theme handling"""
        themes_to_test = ["professional blue", "clean minimalist", "academic"]
        
        for theme in themes_to_test:
            result = self.generator.generate_slides_html(
                blog_content="Sample blog content for testing themes.",
                purpose="test presentation",
                theme=theme
            )
            
            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 100
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with empty input
        result = self.generator.generate_blog("")
        # Should handle gracefully, might return None or empty content
        
        # Test with very long input
        very_long_text = "test " * 10000
        result = self.generator.assess_knowledge_depth(very_long_text)
        assert result in ["SUFFICIENT", "INSUFFICIENT"]

def run_topic_tests():
    """Run all topic tests and return results"""
    results = {}
    
    if not Config.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not provided. Skipping topic tests.")
        return {"error": "No API key provided"}
    
    generator = TopicGenerator(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    print("🧪 Running topic generation tests...")
    
    for i, test_case in enumerate(TOPIC_TEST_CASES, 1):
        print(f"\n=== Test {i}: {test_case['name']} ===")
        print(f"Topic: {test_case['user_text'][:80]}...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    result = generator.generate_from_topic(
                        user_text=test_case['user_text'],
                        purpose=test_case['purpose'],
                        theme=test_case['theme']
                    )
                    
                    if result and result.get('html_file'):
                        # Count slides
                        html_file = Path(result['html_file'])
                        if html_file.exists():
                            with open(html_file, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            slide_count = html_content.count('<div class="slide"')
                            if slide_count == 0:
                                slide_count = html_content.count('<section class="slide"')
                            
                            results[test_case['name']] = {
                                'status': 'success',
                                'slides_count': slide_count,
                                'knowledge_assessment': result.get('knowledge_assessment'),
                                'research_performed': result.get('research_performed', False)
                            }
                            print(f"✓ Success: {slide_count} slides generated")
                        else:
                            results[test_case['name']] = {
                                'status': 'error',
                                'error': 'HTML file not found'
                            }
                            print("✗ Error: HTML file not found")
                    else:
                        results[test_case['name']] = {
                            'status': 'error',
                            'error': 'Generation failed'
                        }
                        print("✗ Error: Generation failed")
                        
                finally:
                    os.chdir(original_cwd)
                    
        except Exception as e:
            results[test_case['name']] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ Error: {e}")
    
    return results

if __name__ == "__main__":
    # Run tests when executed directly
    test_results = run_topic_tests()
    
    print("\n" + "="*50)
    print("TOPIC GENERATION TEST RESULTS")
    print("="*50)
    
    successful = sum(1 for r in test_results.values() if r.get('status') == 'success')
    total = len(test_results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    for name, result in test_results.items():
        status_icon = "✓" if result.get('status') == 'success' else "✗"
        if result.get('status') == 'success':
            print(f"{status_icon} {name}: {result.get('slides_count', 0)} slides")
        else:
            print(f"{status_icon} {name}: {result.get('error', 'Unknown error')}")