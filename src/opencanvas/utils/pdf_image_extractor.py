"""
PDF Image Extractor utility module.
"""

import os
from typing import List
import pdfplumber
from PIL import Image


class PDFImageExtractor:
    """
    A class for extracting images from PDF files by cropping them from rendered pages.
    """
    
    def __init__(self, resolution: int = 300):
        """
        Initialize the PDFImageExtractor.
        
        Args:
            resolution (int): Resolution in DPI for rendering PDF pages. Default is 300.
        """
        self.resolution = resolution
        self.scale_factor = resolution / 72  # Convert PDF points to pixels
    
    def extract_images_from_pdf(self, pdf_path: str, output_dir: str) -> List[str]:
        """
        Extracts all images from a PDF file by cropping them from the page using their coordinates and saves them to the specified output directory.

        Args:
            pdf_path (str): Path to the PDF file.
            output_dir (str): Directory where extracted images will be saved.

        Returns:
            List[str]: List of file paths to the extracted images.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        image_paths = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                if page.images:
                    # Render the page as a PIL image
                    page_image = page.to_image(resolution=self.resolution)
                    pil_page = page_image.original
                    
                    for img_index, img in enumerate(page.images):
                        # Get coordinates in PDF points and scale to pixels
                        x0 = int(img['x0'] * self.scale_factor)
                        top = int(img['top'] * self.scale_factor)
                        x1 = int(img['x1'] * self.scale_factor)
                        bottom = int(img['bottom'] * self.scale_factor)
                        
                        # Crop the image from the page
                        cropped = pil_page.crop((x0, top, x1, bottom))
                        image_filename = f"page{page_number+1}_img{img_index+1}.png"
                        image_path = os.path.join(output_dir, image_filename)
                        cropped.save(image_path)
                        image_paths.append(image_path)
        return image_paths


# Convenience function for backward compatibility
def extract_images_from_pdf(pdf_path: str, output_dir: str, resolution: int = 300) -> List[str]:
    """
    Convenience function to extract images from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory where extracted images will be saved.
        resolution (int): Resolution in DPI for rendering PDF pages. Default is 300.
        
    Returns:
        List[str]: List of file paths to the extracted images.
    """
    extractor = PDFImageExtractor(resolution=resolution)
    return extractor.extract_images_from_pdf(pdf_path, output_dir) 