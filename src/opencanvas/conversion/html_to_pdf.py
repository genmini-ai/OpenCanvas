#!/usr/bin/env python3
"""
HTML Presentation to PDF Converter

This script converts an HTML-based presentation with multiple slides to a PDF.
It uses Selenium to navigate through slides and Playwright for high-quality PDF generation.
Includes automatic whitespace removal and slide optimization.

Requirements:
- pip install selenium playwright reportlab pillow opencv-python
- playwright install chromium
- Download ChromeDriver for Selenium
"""

import os
import time
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import logging

# PDF and image processing
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
import asyncio
from playwright.async_api import async_playwright

from opencanvas.utils.validation import InputValidator

logger = logging.getLogger(__name__)

class PresentationConverter:
    """Enhanced PresentationConverter with native PDF generation capabilities and fixed 4:3 aspect ratio."""
    
    def __init__(self, html_file: str, output_dir: str = "output", 
                 method: str = "playwright", zoom_factor: float = 1.2):
        """
        Initialize the converter.
        
        Args:
            html_file: Path to HTML presentation file
            output_dir: Directory for output files  
            method: Conversion method - 'playwright' (default), 'chrome_headless', 
                   'selenium_cdp', or 'selenium' (original screenshot method)
            zoom_factor: Zoom level for PDF content (used in all methods)
        """
        self.html_file = Path(html_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.method = method
        self.zoom_factor = zoom_factor
        self.temp_images = []  # Kept for compatibility
        
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
        
        # Disable automation banner
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def convert_with_playwright(self, output_filename: str) -> str:
        """Convert using Playwright - produces selectable PDF with proper 4:3 format."""
        logger.info("Converting with Playwright...")
        
        pdf_path = self.output_dir / output_filename
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to file
            file_url = f"file://{self.html_file.absolute()}"
            page.goto(file_url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Set print media type for better PDF rendering
            page.emulate_media(media='print')
            
            # Hide navigation elements and setup slide breaks
            page.add_style_tag(content=f"""
                @media print {{
                    /* Hide navigation elements */
                    .controls, .slide-number, .progress-bar, .navigation,
                    [class*="control"], [class*="nav"], .presenter-notes {{
                        display: none !important;
                    }}
                    
                    /* Ensure full content width is captured */
                    body {{
                        zoom: {self.zoom_factor};
                        width: 100% !important;
                        max-width: none !important;
                        overflow: visible !important;
                    }}
                    
                    /* Ensure slides break properly and use full width */
                    .slide, section {{
                        page-break-after: always;
                        page-break-inside: avoid;
                        width: 100% !important;
                        max-width: none !important;
                        min-width: 100% !important;
                    }}
                    
                    /* Last slide shouldn't have page break */
                    .slide:last-child, section:last-child {{
                        page-break-after: auto;
                    }}
                }}
            """)
            
            # Use 16:9 aspect ratio to match 1920x1080 and capture full content
            page_width = 16.0 * self.zoom_factor  # 16:9 ratio for full width
            page_height = 9.0 * self.zoom_factor   # 16:9 ratio
            
            # Generate PDF with proper 4:3 aspect ratio
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
            
            browser.close()
        
        logger.info(f"PDF generated with Playwright (16:9 format): {pdf_path}")
        return str(pdf_path)

    def convert_with_chrome_headless(self, output_filename: str) -> str:
        """Convert using Chrome headless - produces selectable PDF with proper 4:3 format."""
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
        
        # Calculate 16:9 aspect ratio paper size in mm to match 1920x1080
        base_width_mm = 406   # 16.0 inches in mm (16:9 ratio)
        base_height_mm = 229  # 9.0 inches in mm (16:9 ratio)
        
        paper_width = base_width_mm * self.zoom_factor
        paper_height = base_height_mm * self.zoom_factor
        
        # Build command for headless Chrome (no automation banner)
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
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"Chrome command failed: {result.stderr}")
                raise RuntimeError(f"Chrome headless conversion failed: {result.stderr}")
            
            if not pdf_path.exists():
                raise RuntimeError("PDF was not created")
                
            logger.info(f"PDF generated with Chrome headless (16:9 format): {pdf_path}")
            return str(pdf_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Chrome headless conversion timed out")

    def convert_with_selenium_cdp(self, output_filename: str) -> str:
        """Convert using Selenium with Chrome DevTools Protocol - proper 4:3 format, no automation banner."""
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
            
            # Use 16:9 dimensions to match 1920x1080 viewport
            base_width, base_height = 16.0, 9.0  # 16:9 ratio (1920x1080 equivalent)
            
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