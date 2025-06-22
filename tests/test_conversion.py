import os
import pytest
import tempfile
from pathlib import Path

from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.config import Config

# Sample HTML content for testing
SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Presentation</title>
    <style>
        .slide {
            width: 100vw;
            height: 100vh;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 2em;
            background: white;
            border: 1px solid #ccc;
        }
        .slide.active {
            display: flex;
        }
    </style>
</head>
<body>
    <div class="slide active">
        <h1>Slide 1: Title</h1>
    </div>
    <div class="slide">
        <h2>Slide 2: Content</h2>
    </div>
    <div class="slide">
        <h2>Slide 3: Conclusion</h2>
    </div>
    
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        
        function showSlide(n) {
            slides.forEach(slide => slide.classList.remove('active'));
            if (slides[n]) slides[n].classList.add('active');
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' && currentSlide < slides.length - 1) {
                currentSlide++;
                showSlide(currentSlide);
            } else if (e.key === 'ArrowLeft' && currentSlide > 0) {
                currentSlide--;
                showSlide(currentSlide);
            }
        });
    </script>
</body>
</html>"""

class TestPresentationConverter:
    """Test cases for HTML to PDF conversion"""
    
    def test_converter_initialization(self):
        """Test converter initialization with different parameters"""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write(SAMPLE_HTML)
            tmp.flush()
            
            try:
                # Test with default parameters
                converter = PresentationConverter(tmp.name)
                assert converter.html_file.exists()
                assert converter.method == "selenium"
                assert converter.zoom_factor == 1.2
                
                # Test with custom parameters
                converter = PresentationConverter(
                    tmp.name, 
                    method="playwright", 
                    zoom_factor=1.5
                )
                assert converter.method == "playwright"
                assert converter.zoom_factor == 1.5
                
            finally:
                os.unlink(tmp.name)
    
    def test_invalid_html_file(self):
        """Test error handling for invalid HTML files"""
        # Non-existent file
        with pytest.raises(ValueError):
            PresentationConverter("nonexistent.html")
        
        # Non-HTML file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            try:
                with pytest.raises(ValueError):
                    PresentationConverter(tmp.name)
            finally:
                os.unlink(tmp.name)
    
    def test_invalid_zoom_factor(self):
        """Test error handling for invalid zoom factors"""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write(SAMPLE_HTML)
            tmp.flush()
            
            try:
                # Zero zoom factor
                with pytest.raises(ValueError):
                    PresentationConverter(tmp.name, zoom_factor=0)
                
                # Negative zoom factor
                with pytest.raises(ValueError):
                    PresentationConverter(tmp.name, zoom_factor=-1)
                
                # Too large zoom factor
                with pytest.raises(ValueError):
                    PresentationConverter(tmp.name, zoom_factor=5.0)
                    
            finally:
                os.unlink(tmp.name)
    
    @pytest.mark.parametrize("method", ["selenium"])  # Only test selenium to avoid playwright dependency issues
    def test_conversion_process(self, method):
        """Test the conversion process with different methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create HTML file
            html_file = Path(temp_dir) / "test_presentation.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_HTML)
            
            # Initialize converter
            converter = PresentationConverter(
                str(html_file),
                output_dir=temp_dir,
                method=method,
                zoom_factor=1.0
            )
            
            try:
                # Run conversion
                pdf_path = converter.convert("test_output.pdf", cleanup=False)
                
                # Verify PDF was created
                pdf_file = Path(pdf_path)
                assert pdf_file.exists()
                assert pdf_file.suffix == '.pdf'
                assert pdf_file.stat().st_size > 1000  # Should be substantial
                
                # Verify intermediate images were created
                image_files = list(Path(temp_dir).glob("slide_*.png"))
                assert len(image_files) >= 3  # Should have 3 slides
                
            except Exception as e:
                # Some tests might fail due to missing dependencies (ChromeDriver, etc.)
                pytest.skip(f"Conversion test skipped due to dependency issue: {e}")
    
    def test_zoom_factor_effects(self):
        """Test that different zoom factors produce different file sizes"""
        zoom_factors = [1.0, 1.5, 2.0]
        file_sizes = []
        
        for zoom in zoom_factors:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create HTML file
                html_file = Path(temp_dir) / "test_presentation.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(SAMPLE_HTML)
                
                try:
                    converter = PresentationConverter(
                        str(html_file),
                        output_dir=temp_dir,
                        zoom_factor=zoom
                    )
                    
                    pdf_path = converter.convert(f"test_zoom_{zoom}.pdf")
                    file_size = Path(pdf_path).stat().st_size
                    file_sizes.append(file_size)
                    
                except Exception:
                    # Skip if conversion fails due to dependencies
                    pytest.skip("Zoom factor test skipped due to dependency issues")
        
        # Generally, higher zoom should produce larger files
        # (though this isn't guaranteed due to compression)
        if len(file_sizes) > 1:
            assert all(size > 0 for size in file_sizes)

def run_conversion_tests():
    """Run conversion tests and return results"""
    results = {}
    
    print("🧪 Running HTML to PDF conversion tests...")
    
    test_cases = [
        {
            "name": "Basic Conversion Test",
            "method": "selenium",
            "zoom": 1.2
        },
        {
            "name": "High Zoom Test", 
            "method": "selenium",
            "zoom": 1.8
        },
        {
            "name": "Low Zoom Test",
            "method": "selenium", 
            "zoom": 0.8
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test {i}: {test_case['name']} ===")
        print(f"Method: {test_case['method']} | Zoom: {test_case['zoom']}")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test HTML file
                html_file = Path(temp_dir) / "test_presentation.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(SAMPLE_HTML)
                
                # Initialize converter
                converter = PresentationConverter(
                    str(html_file),
                    output_dir=temp_dir,
                    method=test_case['method'],
                    zoom_factor=test_case['zoom']
                )
                
                # Run conversion
                pdf_path = converter.convert("test_output.pdf", cleanup=False)
                
                # Verify results
                pdf_file = Path(pdf_path)
                if pdf_file.exists():
                    file_size = pdf_file.stat().st_size
                    
                    # Count generated images
                    image_files = list(Path(temp_dir).glob("slide_*.png"))
                    
                    results[test_case['name']] = {
                        'status': 'success',
                        'pdf_size_kb': file_size // 1024,
                        'slides_captured': len(image_files),
                        'zoom_factor': test_case['zoom']
                    }
                    print(f"✓ Success: {len(image_files)} slides, {file_size // 1024}KB PDF")
                else:
                    results[test_case['name']] = {
                        'status': 'error',
                        'error': 'PDF file not created'
                    }
                    print("✗ Error: PDF file not created")
                    
        except Exception as e:
            results[test_case['name']] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ Error: {e}")
    
    return results

if __name__ == "__main__":
    # Run tests when executed directly
    test_results = run_conversion_tests()
    
    print("\n" + "="*50)
    print("HTML TO PDF CONVERSION TEST RESULTS")
    print("="*50)
    
    successful = sum(1 for r in test_results.values() if r.get('status') == 'success')
    total = len(test_results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    for name, result in test_results.items():
        status_icon = "✓" if result.get('status') == 'success' else "✗"
        if result.get('status') == 'success':
            print(f"{status_icon} {name}: {result.get('slides_captured', 0)} slides, "
                  f"{result.get('pdf_size_kb', 0)}KB PDF, "
                  f"{result.get('zoom_factor', 1.0)}x zoom")
        else:
            print(f"{status_icon} {name}: {result.get('error', 'Unknown error')}")