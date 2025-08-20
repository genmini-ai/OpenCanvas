#!/usr/bin/env python3
"""
HTML Presentation to PDF Converter - Enhanced Version

This script converts an HTML-based presentation with multiple slides to a PDF
with SELECTABLE TEXT and EDITABLE content (not rasterized screenshots).

Drop-in replacement for the original PresentationConverter class.
Maintains the same API while adding native PDF generation methods.

Requirements:
- pip install selenium playwright 
- playwright install chromium
- Download ChromeDriver for Selenium (for fallback compatibility)
"""

import os
import time
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import asyncio
import base64

# PDF and image processing (kept for fallback compatibility)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageOps

# Browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Playwright for high-quality PDF generation
try:
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright && playwright install chromium")

# Import validation if available
try:
    from opencanvas.utils.validation import InputValidator
except ImportError:
    # Fallback validation
    class InputValidator:
        @staticmethod
        def validate_html_file(file_path: str) -> Tuple[bool, str]:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            if not file_path.endswith(('.html', '.htm')):
                return False, "File must be HTML"
            return True, "Valid"
        
        @staticmethod
        def validate_zoom_factor(zoom: float) -> Tuple[bool, str]:
            if not 0.1 <= zoom <= 5.0:
                return False, "Zoom must be between 0.1 and 5.0"
            return True, "Valid"

logger = logging.getLogger(__name__)

class PresentationConverter:
    """Enhanced PresentationConverter with native PDF generation capabilities and fixed 4:3 aspect ratio."""
    
    def __init__(self, html_file: str, output_dir: str = "output", 
                 method: str = "playwright", zoom_factor: float = 1.2, 
                 compress_images: bool = False):
        """
        Initialize the converter.
        
        Args:
            html_file: Path to HTML presentation file
            output_dir: Directory for output files  
            method: Conversion method - 'playwright' (default), 'chrome_headless', 
                   'selenium_cdp', or 'selenium' (original screenshot method)
            zoom_factor: Zoom level for PDF content (used in all methods)
            compress_images: Whether to compress Unsplash images for smaller PDFs (default: False)
        """
        self.html_file = Path(html_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.method = method
        self.zoom_factor = zoom_factor
        self.compress_images = compress_images
        self.temp_images = []  # Kept for compatibility
        self.temp_html_file = None  # For compressed HTML cleanup
        
        # Validate inputs
        is_valid, msg = InputValidator.validate_html_file(str(self.html_file))
        if not is_valid:
            raise ValueError(f"Invalid HTML file: {msg}")
        
        is_valid, msg = InputValidator.validate_zoom_factor(zoom_factor)
        if not is_valid:
            raise ValueError(f"Invalid zoom factor: {msg}")
        
        # Check method availability
        if method == "playwright" and not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, falling back to chrome_headless")
            self.method = "chrome_headless"

    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with optimal settings for PDF generation and no automation banner."""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")  # Full HD for complete content capture
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--allow-file-access-from-files")  # Allow access to local image files
        
        # Disable automation banner
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def _compress_images_in_html(self) -> Path:
        """Create a temporary HTML file with compressed Unsplash images"""
        import re
        import time
        
        # Read original HTML
        with open(self.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Apply aggressive compression: w=1350→w=400, q=80→q=40
        compressed_content = re.sub(r'w=1350', 'w=400', html_content)
        compressed_content = re.sub(r'q=80', 'q=40', compressed_content)
        
        # Create temp file IN THE SAME DIRECTORY as original (not /tmp!)
        # This preserves relative paths to ../extracted_images/
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        temp_path = self.html_file.parent / f"compressed_{timestamp}.html"
        self.temp_html_file = temp_path
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(compressed_content)
        
        logger.info(f"Created compressed HTML: {self.temp_html_file}")
        return self.temp_html_file

    def _cleanup_temp_html(self):
        """Clean up temporary compressed HTML file"""
        if self.temp_html_file and self.temp_html_file.exists():
            try:
                self.temp_html_file.unlink()
                logger.info(f"Cleaned up temporary HTML: {self.temp_html_file}")
                self.temp_html_file = None
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary HTML: {e}")


    def convert_with_playwright(self, output_filename: str) -> str:
        """Convert using Playwright - produces selectable PDF with proper multi-slide support."""
        logger.info("Converting with Playwright...")
        
        pdf_path = self.output_dir / output_filename
        
        # Use compressed HTML if image compression is enabled
        html_file_to_use = self.html_file
        if self.compress_images:
            html_file_to_use = self._compress_images_in_html()
            logger.info("Using compressed images for PDF generation")
        
        with sync_playwright() as p:
            # Launch browser with flags to allow local file access (needed for extracted images)
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--allow-file-access-from-files',
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ]
            )
            # Create context with bypass CSP to allow local file access
            context = browser.new_context(
                bypass_csp=True,
                ignore_https_errors=True
            )
            page = context.new_page()
            
            # Navigate to file (using original HTML)
            file_url = f"file://{html_file_to_use.absolute()}"
            logger.info(f"Loading HTML from: {file_url}")
            page.goto(file_url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Set print media type for better PDF rendering
            page.emulate_media(media='print')
            
            # Hide navigation elements
            page.add_style_tag(content="""
                @media print {
                    /* Hide navigation elements */
                    .controls, .slide-number, .progress-bar, .navigation,
                    [class*="control"], [class*="nav"], .presenter-notes {
                        display: none !important;
                    }
                    
                    /* Ensure full content width is captured */
                    body {
                        width: 100% !important;
                        max-width: none !important;
                        overflow: visible !important;
                    }
                    
                    /* Ensure slides break properly and use full width */
                    .slide, section {
                        page-break-after: always;
                        page-break-inside: avoid;
                        width: 100% !important;
                        max-width: none !important;
                        min-width: 100% !important;
                    }
                    
                    /* Last slide shouldn't have page break */
                    .slide:last-child, section:last-child {
                        page-break-after: auto;
                    }
                }
            """)
            
            # Check if this is a multi-slide presentation
            slides = page.query_selector_all('.slide')
            total_slides = len(slides)
            
            if total_slides <= 1:
                # Single slide or no slide structure detected - use single page PDF
                logger.info("Single slide detected, using single-page PDF generation")
                
                # Use 16:9 aspect ratio to match 1920x1080 and capture full content
                page_width = 16.0 * self.zoom_factor  # 16:9 ratio for full width
                page_height = 9.0 * self.zoom_factor   # 16:9 ratio
                
                # Generate PDF with proper 16:9 aspect ratio
                page.pdf(
                    path=str(pdf_path),
                    width=f"{page_width}in",
                    height=f"{page_height}in",
                    print_background=True,
                    margin={
                        'top': '0.2in',
                        'right': '0.2in', 
                        'bottom': '0.2in',
                        'left': '0.2in'
                    },
                    prefer_css_page_size=False,
                    display_header_footer=False,
                    landscape=False
                )
            else:
                # Multi-slide presentation - capture each slide individually
                logger.info(f"Multi-slide presentation detected ({total_slides} slides)")
                
                # Capture each slide as a separate PDF page
                temp_pdfs = []
                
                for slide_num in range(1, total_slides + 1):
                    logger.info(f"Capturing slide {slide_num}/{total_slides}")
                    
                    # Navigate to specific slide (most presentations use arrow keys)
                    if slide_num > 1:
                        page.keyboard.press('ArrowRight')
                        page.wait_for_timeout(1000)
                    
                    # Generate PDF for this slide
                    temp_pdf_path = self.output_dir / f"temp_slide_{slide_num:02d}.pdf"
                    
                    page_width = 16.0 * self.zoom_factor  # 16:9 ratio
                    page_height = 9.0 * self.zoom_factor
                    
                    page.pdf(
                        path=str(temp_pdf_path),
                        width=f"{page_width}in",
                        height=f"{page_height}in",
                        print_background=True,
                        margin={
                            'top': '0.2in',
                            'right': '0.2in', 
                            'bottom': '0.2in',
                            'left': '0.2in'
                        },
                        prefer_css_page_size=False,
                        display_header_footer=False,
                        landscape=False
                    )
                    
                    temp_pdfs.append(str(temp_pdf_path))
                
                # Combine all PDFs into one
                self._combine_pdfs(temp_pdfs, str(pdf_path))
                
                # Clean up temporary PDFs
                for temp_pdf in temp_pdfs:
                    try:
                        os.remove(temp_pdf)
                    except:
                        pass
            
            browser.close()
            
            # Clean up temporary files
            if self.compress_images:
                self._cleanup_temp_html()
            
            logger.info(f"PDF generated with Playwright (16:9 format): {pdf_path}")
            return str(pdf_path)

    def _combine_pdfs(self, pdf_paths: List[str], output_path: str):
        """Combine multiple PDFs into one using PyPDF2 or fallback to system tools."""
        try:
            # Try using PyPDF2 first
            try:
                from PyPDF2 import PdfMerger
                merger = PdfMerger()
                
                for pdf_path in pdf_paths:
                    merger.append(pdf_path)
                
                merger.write(output_path)
                merger.close()
                logger.info(f"Combined {len(pdf_paths)} PDFs using PyPDF2")
                return
                
            except ImportError:
                logger.info("PyPDF2 not available, trying system tools...")
                
            # Fallback to system tools
            if shutil.which('pdftk'):
                # Use pdftk if available
                cmd = ['pdftk'] + pdf_paths + ['cat', 'output', output_path]
                subprocess.run(cmd, check=True)
                logger.info(f"Combined {len(pdf_paths)} PDFs using pdftk")
                return
                
            elif shutil.which('gs'):
                # Use Ghostscript if available
                cmd = ['gs', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', 
                       f'-sOutputFile={output_path}'] + pdf_paths
                subprocess.run(cmd, check=True)
                logger.info(f"Combined {len(pdf_paths)} PDFs using Ghostscript")
                return
                
            else:
                # Last resort: just use the first PDF
                logger.warning("No PDF merging tools available, using first slide only")
                shutil.copy(pdf_paths[0], output_path)
                
        except Exception as e:
            logger.error(f"Error combining PDFs: {e}")
            # Fallback: copy first PDF
            if pdf_paths:
                shutil.copy(pdf_paths[0], output_path)

    def convert_with_chrome_headless(self, output_filename: str) -> str:
        """Convert using Chrome headless - produces selectable PDF with proper multi-slide support."""
        logger.info("Converting with Chrome headless...")
        
        pdf_path = self.output_dir / output_filename
        
        file_url = f"file://{self.html_file.absolute()}"
        
        # Find Chrome executable
        chrome_executables = [
            'google-chrome',
            'chromium-browser', 
            'chromium',
            'chrome',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Windows
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        ]
        
        chrome_path = None
        for executable in chrome_executables:
            if shutil.which(executable) or os.path.exists(executable):
                chrome_path = executable
                break
        
        if not chrome_path:
            raise RuntimeError("Chrome/Chromium not found. Please install Chrome or Chromium browser.")
        
        # For multi-slide presentations, we need to use Selenium to navigate
        # Chrome headless alone can't navigate between slides
        try:
            # Check if this is a multi-slide presentation using Selenium
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox") 
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            # Add flags to allow local file access for extracted images
            options.add_argument("--allow-file-access-from-files")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            
            try:
                driver.get(file_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)
                
                # Check for slides
                slides = driver.find_elements(By.CLASS_NAME, "slide")
                total_slides = len(slides)
                
                if total_slides <= 1:
                    # Single slide - use direct Chrome headless
                    logger.info("Single slide detected, using direct Chrome headless")
                    driver.quit()
                    
                    # Calculate 16:9 aspect ratio paper size in mm
                    base_width_mm = 406   # 16.0 inches in mm (16:9 ratio)
                    base_height_mm = 229  # 9.0 inches in mm (16:9 ratio)
                    
                    paper_width = base_width_mm * self.zoom_factor
                    paper_height = base_height_mm * self.zoom_factor
                    
                    # Build command for headless Chrome
                    cmd = [
                        chrome_path,
                        '--headless',
                        '--disable-gpu', 
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--run-all-compositor-stages-before-draw',
                        '--virtual-time-budget=5000',
                        '--disable-infobars',
                        '--disable-extensions',
                        f'--force-device-scale-factor={self.zoom_factor}',
                        f'--print-to-pdf-paper-width={paper_width}',
                        f'--print-to-pdf-paper-height={paper_height}',
                        '--print-to-pdf=' + str(pdf_path),
                        '--no-pdf-header-footer',
                        file_url
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        logger.error(f"Chrome command failed: {result.stderr}")
                        raise RuntimeError(f"Chrome headless conversion failed: {result.stderr}")
                    
                    if not pdf_path.exists():
                        raise RuntimeError("PDF was not created")
                        
                    logger.info(f"PDF generated with Chrome headless (16:9 format): {pdf_path}")
                    return str(pdf_path)
                
                else:
                    # Multi-slide presentation - capture each slide using Selenium CDP
                    logger.info(f"Multi-slide presentation detected ({total_slides} slides), using Selenium CDP")
                    
                    # Hide navigation elements
                    driver.execute_script("""
                        const style = document.createElement('style');
                        style.textContent = `
                            .controls, .slide-number, .progress-bar, .navigation,
                            [class*="control"], [class*="nav"], .presenter-notes {
                                display: none !important;
                            }
                            .slide, section {
                                width: 100% !important;
                                max-width: none !important;
                                min-width: 100% !important;
                            }
                        `;
                        document.head.appendChild(style);
                    """)
                    
                    # Apply zoom
                    driver.execute_script(f"""
                        document.body.style.zoom = '{self.zoom_factor}';
                        document.body.style.width = '100%';
                        document.body.style.maxWidth = 'none';
                        document.body.style.overflow = 'visible';
                    """)
                    
                    # Capture each slide using CDP
                    temp_pdfs = []
                    
                    for slide_num in range(1, total_slides + 1):
                        logger.info(f"Capturing slide {slide_num}/{total_slides}")
                        
                        # Navigate to specific slide
                        if slide_num > 1:
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
                            time.sleep(1)
                        
                        # Use CDP to generate PDF for this slide
                        base_width, base_height = 16.0, 9.0  # 16:9 ratio
                        
                        pdf_options = {
                            'landscape': False,
                            'displayHeaderFooter': False,
                            'printBackground': True,
                            'preferCSSPageSize': False,
                            'marginTop': 0.2,
                            'marginBottom': 0.2, 
                            'marginLeft': 0.2,
                            'marginRight': 0.2,
                            'paperWidth': base_width * self.zoom_factor,
                            'paperHeight': base_height * self.zoom_factor,
                            'scale': 1.0
                        }
                        
                        result = driver.execute_cdp_cmd('Page.printToPDF', pdf_options)
                        pdf_data = result['data']
                        
                        # Save temporary PDF
                        temp_pdf_path = self.output_dir / f"temp_slide_{slide_num:02d}.pdf"
                        with open(temp_pdf_path, 'wb') as f:
                            f.write(base64.b64decode(pdf_data))
                        
                        temp_pdfs.append(str(temp_pdf_path))
                    
                    # Combine all PDFs
                    self._combine_pdfs(temp_pdfs, str(pdf_path))
                    
                    # Clean up temporary PDFs
                    for temp_pdf in temp_pdfs:
                        try:
                            os.remove(temp_pdf)
                        except:
                            pass
                    
                    logger.info(f"PDF generated with Chrome headless multi-slide (16:9 format): {pdf_path}")
                    return str(pdf_path)
                    
            finally:
                driver.quit()
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Chrome headless conversion timed out")
        except Exception as e:
            logger.error(f"Chrome headless conversion failed: {e}")
            raise RuntimeError(f"Chrome headless conversion failed: {str(e)}")

    def convert_with_selenium_cdp(self, output_filename: str) -> str:
        """Convert using Selenium with Chrome DevTools Protocol - proper multi-slide support."""
        logger.info("Converting with Selenium + Chrome DevTools Protocol...")
        
        pdf_path = self.output_dir / output_filename
        
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        
        # Disable automation banner
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # Remove automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to file
            file_url = f"file://{self.html_file.absolute()}"
            driver.get(file_url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # Check for slides
            slides = driver.find_elements(By.CLASS_NAME, "slide")
            total_slides = len(slides)
            
            if total_slides <= 1:
                # Single slide - generate single PDF
                logger.info("Single slide detected, generating single PDF")
                
                # Apply zoom and ensure full width capture
                driver.execute_script(f"""
                    document.body.style.zoom = '{self.zoom_factor}';
                    document.body.style.width = '100%';
                    document.body.style.maxWidth = 'none';
                    document.body.style.overflow = 'visible';
                    
                    // Hide navigation elements
                    const style = document.createElement('style');
                    style.textContent = `
                        .controls, .slide-number, .progress-bar, .navigation,
                        [class*="control"], [class*="nav"], .presenter-notes {{
                            display: none !important;
                        }}
                        .slide, section {{
                            width: 100% !important;
                            max-width: none !important;
                            min-width: 100% !important;
                        }}
                    `;
                    document.head.appendChild(style);
                """)
                
                # Use 16:9 dimensions
                base_width, base_height = 16.0, 9.0  # 16:9 ratio
                
                pdf_options = {
                    'landscape': False,
                    'displayHeaderFooter': False,
                    'printBackground': True,
                    'preferCSSPageSize': False,
                    'marginTop': 0.2,
                    'marginBottom': 0.2, 
                    'marginLeft': 0.2,
                    'marginRight': 0.2,
                    'paperWidth': base_width * self.zoom_factor,
                    'paperHeight': base_height * self.zoom_factor,
                    'scale': 1.0
                }
                
                # Execute CDP command
                result = driver.execute_cdp_cmd('Page.printToPDF', pdf_options)
                pdf_data = result['data']
                
                # Decode and save PDF
                with open(pdf_path, 'wb') as f:
                    f.write(base64.b64decode(pdf_data))
                
                logger.info(f"PDF generated with Selenium CDP (16:9 format): {pdf_path}")
                return str(pdf_path)
                
            else:
                # Multi-slide presentation - capture each slide
                logger.info(f"Multi-slide presentation detected ({total_slides} slides)")
                
                # Apply zoom and hide navigation elements
                driver.execute_script(f"""
                    document.body.style.zoom = '{self.zoom_factor}';
                    document.body.style.width = '100%';
                    document.body.style.maxWidth = 'none';
                    document.body.style.overflow = 'visible';
                    
                    // Hide navigation elements
                    const style = document.createElement('style');
                    style.textContent = `
                        .controls, .slide-number, .progress-bar, .navigation,
                        [class*="control"], [class*="nav"], .presenter-notes {{
                            display: none !important;
                        }}
                        .slide, section {{
                            width: 100% !important;
                            max-width: none !important;
                            min-width: 100% !important;
                        }}
                    `;
                    document.head.appendChild(style);
                """)
                
                # Capture each slide
                temp_pdfs = []
                
                for slide_num in range(1, total_slides + 1):
                    logger.info(f"Capturing slide {slide_num}/{total_slides}")
                    
                    # Navigate to specific slide
                    if slide_num > 1:
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
                        time.sleep(1)
                    
                    # Use 16:9 dimensions
                    base_width, base_height = 16.0, 9.0  # 16:9 ratio
                    
                    pdf_options = {
                        'landscape': False,
                        'displayHeaderFooter': False,
                        'printBackground': True,
                        'preferCSSPageSize': False,
                        'marginTop': 0.2,
                        'marginBottom': 0.2, 
                        'marginLeft': 0.2,
                        'marginRight': 0.2,
                        'paperWidth': base_width * self.zoom_factor,
                        'paperHeight': base_height * self.zoom_factor,
                        'scale': 1.0
                    }
                    
                    # Execute CDP command
                    result = driver.execute_cdp_cmd('Page.printToPDF', pdf_options)
                    pdf_data = result['data']
                    
                    # Save temporary PDF
                    temp_pdf_path = self.output_dir / f"temp_slide_{slide_num:02d}.pdf"
                    with open(temp_pdf_path, 'wb') as f:
                        f.write(base64.b64decode(pdf_data))
                    
                    temp_pdfs.append(str(temp_pdf_path))
                
                # Combine all PDFs
                self._combine_pdfs(temp_pdfs, str(pdf_path))
                
                # Clean up temporary PDFs
                for temp_pdf in temp_pdfs:
                    try:
                        os.remove(temp_pdf)
                    except:
                        pass
                
                logger.info(f"PDF generated with Selenium CDP multi-slide (16:9 format): {pdf_path}")
                return str(pdf_path)
            
        finally:
            driver.quit()

    # Original methods kept for backward compatibility
    def capture_slides_selenium(self) -> List[str]:
        """Capture all slides using Selenium (original screenshot method)."""
        logger.info("Starting slide capture with Selenium (screenshot method)...")
        driver = self.setup_selenium_driver()
        image_paths = []
        
        try:
            file_url = f"file://{self.html_file.absolute()}"
            driver.get(file_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "slide"))
            )
            time.sleep(3)
            
            # Hide UI elements
            driver.execute_script("""
                const style = document.createElement('style');
                style.textContent = `
                    .controls, .slide-number, .progress-bar {
                        display: none !important;
                    }
                `;
                document.head.appendChild(style);
            """)
            
            slides = driver.find_elements(By.CLASS_NAME, "slide")
            total_slides = len(slides)
            logger.info(f"Found {total_slides} slides")
            
            for slide_num in range(1, total_slides + 1):
                logger.info(f"Capturing slide {slide_num}/{total_slides}")
                
                screenshot_path = self.output_dir / f"slide_{slide_num:02d}.png"
                driver.save_screenshot(str(screenshot_path))
                image_paths.append(str(screenshot_path))
                
                if slide_num < total_slides:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
                    time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error during slide capture: {e}")
            raise
        finally:
            driver.quit()
        
        return image_paths

    async def capture_slides_playwright(self) -> List[str]:
        """Capture all slides using Playwright (original screenshot method)."""
        logger.info("Starting slide capture with Playwright (screenshot method)...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})  # Full HD viewport
            
            file_url = f"file://{self.html_file.absolute()}"
            await page.goto(file_url)
            await page.wait_for_selector('.slide')
            await page.wait_for_timeout(3000)
            
            await page.add_style_tag(content="""
                .controls, .slide-number, .progress-bar {
                    display: none !important;
                }
            """)
            
            slides = await page.query_selector_all('.slide')
            total_slides = len(slides)
            logger.info(f"Found {total_slides} slides")
            
            image_paths = []
            
            for slide_num in range(1, total_slides + 1):
                logger.info(f"Capturing slide {slide_num}/{total_slides}")
                
                screenshot_path = self.output_dir / f"slide_{slide_num:02d}.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                image_paths.append(str(screenshot_path))
                
                if slide_num < total_slides:
                    await page.keyboard.press('ArrowRight')
                    await page.wait_for_timeout(2000)
            
            await browser.close()
            return image_paths

    def create_pdf_from_images(self, image_paths: List[str], output_filename: str = "presentation.pdf"):
        """Create PDF from captured slide images with proper 4:3 aspect ratio."""
        logger.info(f"Creating PDF from {len(image_paths)} images with {self.zoom_factor*100:.0f}% zoom...")
        
        pdf_path = self.output_dir / output_filename
        
        first_image = Image.open(image_paths[0])
        if first_image.mode != 'RGB':
            first_image = first_image.convert('RGB')
        
        img_width, img_height = first_image.size
        
        # Calculate 16:9 aspect ratio dimensions to match content
        aspect_ratio = 16/9
        if img_width / img_height > aspect_ratio:
            # Image is wider than 16:9, fit to width  
            page_width = img_width * self.zoom_factor
            page_height = page_width / aspect_ratio
        else:
            # Image is taller than 16:9, fit to height
            page_height = img_height * self.zoom_factor
            page_width = page_height * aspect_ratio
        
        c = canvas.Canvas(str(pdf_path), pagesize=(page_width, page_height))
        first_image.close()
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"Adding slide {i+1} to PDF...")
            
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                if i > 0:
                    c.setPageSize((page_width, page_height))
                
                # Center the image within the 16:9 page
                x_offset = max(0, (page_width - img.width * self.zoom_factor) / 2)
                y_offset = max(0, (page_height - img.height * self.zoom_factor) / 2)
                
                c.drawImage(ImageReader(img), x_offset, y_offset, 
                          img.width * self.zoom_factor, img.height * self.zoom_factor)
                
                if i < len(image_paths) - 1:
                    c.showPage()
        
        c.save()
        logger.info(f"PDF saved with 16:9 aspect ratio (1920x1080): {pdf_path}")
        return str(pdf_path)

    def cleanup_temp_files(self):
        """Remove temporary image files."""
        logger.info("Cleaning up temporary files...")
        for image_path in self.temp_images:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                logger.warning(f"Could not remove {image_path}: {e}")
        self.temp_images.clear()

    def convert(self, output_filename: str = "presentation.pdf", cleanup: bool = True) -> str:
        """
        Main conversion method - maintains original API with fixed 4:3 format.
        
        Args:
            output_filename: Output PDF filename  
            cleanup: Whether to cleanup temp files (kept for compatibility)
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Use enhanced PDF generation methods by default
            if self.method == "playwright":
                pdf_path = self.convert_with_playwright(output_filename)
            elif self.method == "chrome_headless":
                pdf_path = self.convert_with_chrome_headless(output_filename)
            elif self.method == "selenium_cdp":
                pdf_path = self.convert_with_selenium_cdp(output_filename)
            elif self.method == "selenium":
                # Original screenshot method for backward compatibility
                image_paths = self.capture_slides_selenium()
                self.temp_images = image_paths
                pdf_path = self.create_pdf_from_images(image_paths, output_filename)
            else:
                # Default fallback to playwright
                logger.warning(f"Unknown method '{self.method}', using playwright")
                pdf_path = self.convert_with_playwright(output_filename)
            
            if cleanup:
                self.cleanup_temp_files()
            
            logger.info(f"Conversion completed successfully with 16:9 format (1920x1080): {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
