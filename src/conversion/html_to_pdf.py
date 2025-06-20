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

from ..utils.validation import InputValidator

logger = logging.getLogger(__name__)

class PresentationConverter:
    def __init__(self, html_file: str, output_dir: str = "output", method: str = "selenium", zoom_factor: float = 1.2):
        self.html_file = Path(html_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.method = method
        self.zoom_factor = zoom_factor
        self.temp_images = []
        
        # Validate inputs
        is_valid, msg = InputValidator.validate_html_file(str(self.html_file))
        if not is_valid:
            raise ValueError(f"Invalid HTML file: {msg}")
        
        is_valid, msg = InputValidator.validate_zoom_factor(zoom_factor)
        if not is_valid:
            raise ValueError(f"Invalid zoom factor: {msg}")
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with optimal settings for PDF generation."""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def capture_slides_selenium(self) -> List[str]:
        """Capture all slides using Selenium."""
        logger.info("Starting slide capture with Selenium...")
        driver = self.setup_selenium_driver()
        image_paths = []
        
        try:
            # Open HTML file
            file_url = f"file://{self.html_file.absolute()}"
            driver.get(file_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "slide"))
            )
            
            # Wait a bit more for animations/rendering
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
            
            # Get total number of slides
            slides = driver.find_elements(By.CLASS_NAME, "slide")
            total_slides = len(slides)
            logger.info(f"Found {total_slides} slides")
            
            # Capture each slide
            for slide_num in range(1, total_slides + 1):
                logger.info(f"Capturing slide {slide_num}/{total_slides}")
                
                # Take screenshot - use raw PNG without cropping
                screenshot_path = self.output_dir / f"slide_{slide_num:02d}.png"
                driver.save_screenshot(str(screenshot_path))
                
                # Use the original screenshot directly
                image_paths.append(str(screenshot_path))
                
                # Navigate to next slide (except for last slide)
                if slide_num < total_slides:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
                    time.sleep(2)  # Wait for transition
            
        except Exception as e:
            logger.error(f"Error during slide capture: {e}")
            raise
        finally:
            driver.quit()
        
        return image_paths
    
    async def capture_slides_playwright(self) -> List[str]:
        """Capture all slides using Playwright (higher quality)."""
        logger.info("Starting slide capture with Playwright...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Open HTML file
            file_url = f"file://{self.html_file.absolute()}"
            await page.goto(file_url)
            
            # Wait for page to load
            await page.wait_for_selector('.slide')
            await page.wait_for_timeout(3000)  # Wait for animations
            
            # Hide UI elements to clean up the capture
            await page.add_style_tag(content="""
                .controls, .slide-number, .progress-bar {
                    display: none !important;
                }
            """)
            
            # Get total number of slides
            slides = await page.query_selector_all('.slide')
            total_slides = len(slides)
            logger.info(f"Found {total_slides} slides")
            
            image_paths = []
            
            # Capture each slide
            for slide_num in range(1, total_slides + 1):
                logger.info(f"Capturing slide {slide_num}/{total_slides}")
                
                # Take screenshot - use the raw PNG without cropping
                screenshot_path = self.output_dir / f"slide_{slide_num:02d}.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                
                # Use the original screenshot directly
                image_paths.append(str(screenshot_path))
                
                # Navigate to next slide (except for last slide)
                if slide_num < total_slides:
                    await page.keyboard.press('ArrowRight')
                    await page.wait_for_timeout(2000)  # Wait for transition
            
            await browser.close()
            return image_paths
    
    def create_pdf_from_images(self, image_paths: List[str], output_filename: str = "presentation.pdf"):
        """Create PDF from captured slide images using original PNG dimensions."""
        logger.info(f"Creating PDF from {len(image_paths)} images with {self.zoom_factor*100:.0f}% zoom...")
        
        pdf_path = self.output_dir / output_filename
        
        # We'll create the canvas with the first image size, then adjust per page
        first_image = Image.open(image_paths[0])
        if first_image.mode != 'RGB':
            first_image = first_image.convert('RGB')
        
        # Apply zoom factor to the image dimensions
        img_width, img_height = first_image.size
        page_width = img_width * self.zoom_factor
        page_height = img_height * self.zoom_factor
        
        c = canvas.Canvas(str(pdf_path), pagesize=(page_width, page_height))
        first_image.close()
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"Adding slide {i+1} to PDF...")
            
            # Open image
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image dimensions and apply zoom
                img_width, img_height = img.size
                page_width = img_width * self.zoom_factor
                page_height = img_height * self.zoom_factor
                
                # For pages after the first, we need to set the page size
                if i > 0:
                    c.setPageSize((page_width, page_height))
                
                # Draw image to fill the entire page (no margins, no centering)
                c.drawImage(ImageReader(img), 0, 0, page_width, page_height)
                
                # Add page break (except for last page)
                if i < len(image_paths) - 1:
                    c.showPage()
        
        c.save()
        logger.info(f"PDF saved: {pdf_path}")
        return str(pdf_path)
    
    def cleanup_temp_files(self):
        """Remove temporary image files."""
        logger.info("Cleaning up temporary files...")
        # Since we're not creating temp files anymore, this is optional
        # Only clean up if user specifically wants to remove the PNGs
        pass
    
    def convert(self, output_filename: str = "presentation.pdf", cleanup: bool = True) -> str:
        """Main conversion method."""
        try:
            # Capture slides
            if self.method == "playwright":
                image_paths = asyncio.run(self.capture_slides_playwright())
            else:
                image_paths = self.capture_slides_selenium()
            
            # Create PDF
            pdf_path = self.create_pdf_from_images(image_paths, output_filename)
            
            # Cleanup
            if cleanup:
                self.cleanup_temp_files()
            
            logger.info(f"Conversion completed successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")