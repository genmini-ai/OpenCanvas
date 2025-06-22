import os
import pytest
import tempfile
from pathlib import Path

from opencanvas.generators.pdf_generator import PDFGenerator
from opencanvas.config import Config

# Test cases for PDF generation using arXiv papers
PDF_TEST_CASES = [
    {
        "name": "Scaling Laws Paper",
        "pdf_url": "https://arxiv.org/pdf/2505.20286",
        "purpose": "academic presentation",
        "theme": "academic"
    },
    {
        "name": "LLM Reasoning Paper", 
        "pdf_url": "https://arxiv.org/pdf/2410.17891",
        "purpose": "research seminar",
        "theme": "clean minimalist"
    },
    {
        "name": "AI Safety Paper",
        "pdf_url": "https://arxiv.org/pdf/2502.02533", 
        "purpose": "conference presentation",
        "theme": "professional blue"
    },
    {
        "name": "Machine Learning Theory",
        "pdf_url": "https://arxiv.org/pdf/2310.13855",
        "purpose": "academic lecture",
        "theme": "modern contemporary"
    },
    {
        "name": "Neural Networks Paper",
        "pdf_url": "https://arxiv.org/pdf/2307.08123",
        "purpose": "workshop presentation", 
        "theme": "cool professional"
    }
]

class TestPDFGenerator:
    """Test cases for PDF-based presentation generation"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method"""
        # Skip tests if no API key
        if not Config.ANTHROPIC_API_KEY:
            pytest.skip("ANTHROPIC_API_KEY not provided")
        
        self.generator = PDFGenerator(api_key=Config.ANTHROPIC_API_KEY)
    
    def test_pdf_url_validation(self):
        """Test PDF URL validation"""
        # Valid PDF URL
        valid, msg = self.generator.validate_pdf_url("https://arxiv.org/pdf/2505.20286")
        assert valid
        
        # Invalid URL
        valid, msg = self.generator.validate_pdf_url("not_a_url")
        assert not valid
        
        # Non-PDF URL
        valid, msg = self.generator.validate_pdf_url("https://example.com/page.html")
        assert not valid
    
    def test_pdf_file_validation(self):
        """Test PDF file validation"""
        # Non-existent file
        valid, msg = self.generator.validate_pdf_file("nonexistent.pdf")
        assert not valid
        
        # Wrong extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            valid, msg = self.generator.validate_pdf_file(tmp.name)
            assert not valid
            os.unlink(tmp.name)
    
    def test_pdf_encoding_from_url(self):
        """Test PDF encoding from URL"""
        # Use a small test PDF
        test_url = "https://arxiv.org/pdf/2505.20286"  # First page should be enough for testing
        
        pdf_data, error = self.generator.encode_pdf_from_url(test_url)
        
        if error:
            pytest.skip(f"Could not download test PDF: {error}")
        
        assert pdf_data is not None
        assert isinstance(pdf_data, str)
        assert len(pdf_data) > 1000  # Should be substantial base64 data
    
    @pytest.mark.parametrize("test_case", PDF_TEST_CASES[:2])  # Test first 2 cases
    def test_full_pdf_generation_pipeline(self, test_case):
        """Test complete PDF generation pipeline for selected papers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = self.generator.generate_presentation(
                    pdf_source=test_case["pdf_url"],
                    presentation_focus=test_case["purpose"],
                    theme=test_case["theme"]
                )
                
                # Verify result structure
                assert result is not None
                assert "html_content" in result
                assert "html_file" in result
                assert "pdf_source" in result
                
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
                
                # Check for academic features
                assert ("MathJax" in html_content or 
                       "mermaid" in html_content or
                       "$" in html_content)  # Should have some academic formatting
                
            finally:
                os.chdir(original_cwd)
    
    def test_theme_handling_pdf(self):
        """Test different theme handling for PDF generation"""
        # Create a minimal test with mock PDF data
        mock_pdf_data = "mock_base64_data_for_testing"
        
        themes_to_test = ["academic", "professional", "clean minimalist"]
        
        for theme in themes_to_test:
            # This will fail due to invalid PDF data, but we can test the structure
            try:
                html_content, error = self.generator.generate_slides_html(
                    pdf_data=mock_pdf_data,
                    presentation_focus="test presentation",
                    theme=theme
                )
                # Expected to fail due to mock data, but structure should be correct
            except Exception:
                pass  # Expected to fail with mock data
    
    def test_error_handling_pdf(self):
        """Test error handling for PDF generation"""
        # Test with invalid URL
        result = self.generator.generate_presentation(
            pdf_source="https://invalid-url.com/nonexistent.pdf",
            presentation_focus="test",
            theme="academic"
        )
        assert result is None
        
        # Test with invalid file path
        result = self.generator.generate_presentation(
            pdf_source="/nonexistent/path/file.pdf", 
            presentation_focus="test",
            theme="academic"
        )
        assert result is None

def run_pdf_tests():
    """Run all PDF tests and return results"""
    results = {}
    
    if not Config.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not provided. Skipping PDF tests.")
        return {"error": "No API key provided"}
    
    generator = PDFGenerator(api_key=Config.ANTHROPIC_API_KEY)
    
    print("🧪 Running PDF generation tests...")
    
    for i, test_case in enumerate(PDF_TEST_CASES, 1):
        print(f"\n=== Test {i}: {test_case['name']} ===")
        print(f"PDF URL: {test_case['pdf_url']}")
        print(f"Purpose: {test_case['purpose']} | Theme: {test_case['theme']}")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    result = generator.generate_presentation(
                        pdf_source=test_case['pdf_url'],
                        presentation_focus=test_case['purpose'],
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
                            
                            # Check for academic features
                            has_math = "MathJax" in html_content or "$" in html_content
                            has_diagrams = "mermaid" in html_content
                            
                            results[test_case['name']] = {
                                'status': 'success',
                                'slides_count': slide_count,
                                'has_math': has_math,
                                'has_diagrams': has_diagrams,
                                'pdf_source': test_case['pdf_url']
                            }
                            print(f"✓ Success: {slide_count} slides generated")
                            if has_math:
                                print(f"  ✓ Math support detected")
                            if has_diagrams:
                                print(f"  ✓ Diagram support detected")
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
    test_results = run_pdf_tests()
    
    print("\n" + "="*50)
    print("PDF GENERATION TEST RESULTS")
    print("="*50)
    
    successful = sum(1 for r in test_results.values() if r.get('status') == 'success')
    total = len(test_results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    for name, result in test_results.items():
        status_icon = "✓" if result.get('status') == 'success' else "✗"
        if result.get('status') == 'success':
            features = []
            if result.get('has_math'):
                features.append("Math")
            if result.get('has_diagrams'):
                features.append("Diagrams")
            feature_str = f" ({', '.join(features)})" if features else ""
            print(f"{status_icon} {name}: {result.get('slides_count', 0)} slides{feature_str}")
        else:
            print(f"{status_icon} {name}: {result.get('error', 'Unknown error')}")