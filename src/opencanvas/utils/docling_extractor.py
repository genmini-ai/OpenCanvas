#!/usr/bin/env python3
"""
Docling Image Extractor for Production PDF Generation
Replaces fragmented pdfplumber extraction with complete figure detection
"""

import os
import json
import logging
import tempfile
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from opencanvas.utils.plot_caption_extractor import PlotInfo

logger = logging.getLogger(__name__)

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import PictureItem, TableItem
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling not available. Install with: pip install docling docling-core")


@dataclass
class DoclingFigure:
    """Information about a figure extracted by Docling"""
    
    figure_id: str
    page_number: int
    image_data: bytes
    caption: str
    bounding_box: Dict[str, float]
    width: int
    height: int
    dimensions: str


class DoclingImageExtractor:
    """
    Extract complete figures from PDFs using Docling
    
    This replaces the fragmented pdfplumber approach with proper figure detection
    that maintains semantic integrity of complex diagrams and charts.
    """
    
    def __init__(self, dpi_scale: float = 2.0):
        """
        Initialize Docling extractor
        
        Args:
            dpi_scale: Scale factor for image resolution (2.0 = 144 DPI)
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "Docling libraries not available. Install with: pip install docling docling-core"
            )
        
        self.dpi_scale = dpi_scale
        
        # Configure pipeline for high-quality image extraction
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.images_scale = dpi_scale
        self.pipeline_options.generate_page_images = True
        self.pipeline_options.generate_picture_images = True
        
        # Create converter with options
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)
            }
        )
        
        logger.info(f"Initialized Docling extractor with DPI scale: {dpi_scale}")
    
    def extract_from_pdf_data(self, pdf_data: str, output_dir: Path) -> Tuple[Dict, Optional[Path], List[PlotInfo]]:
        """
        Extract images from base64 PDF data (compatible with existing interface)
        
        Args:
            pdf_data: Base64 encoded PDF data
            output_dir: Directory to save extracted images
            
        Returns:
            Tuple of (image_captions_dict, extracted_images_dir, plots_list)
            This matches the interface expected by pdf_generator.py
        """
        try:
            # Decode base64 PDF data and save to temporary file
            pdf_bytes = base64.b64decode(pdf_data)
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf.write(pdf_bytes)
                temp_pdf_path = temp_pdf.name
            
            try:
                # Extract using Docling
                docling_figures = self.extract_figures_from_pdf(temp_pdf_path)
                
                if not docling_figures:
                    logger.info("No figures found by Docling")
                    return {}, None, []
                
                # Create extracted_images directory
                extracted_images_dir = output_dir / "extracted_images"
                extracted_images_dir.mkdir(exist_ok=True)
                
                # Convert to format expected by pdf_generator.py
                image_captions = {}
                plots_list = []
                
                for figure in docling_figures:
                    # Save image with consistent naming
                    image_filename = f"{figure.figure_id}.png"
                    image_path = extracted_images_dir / image_filename
                    
                    with open(image_path, "wb") as f:
                        f.write(figure.image_data)
                    
                    # Create relative path for HTML (go up one level from slides/ to parent directory)
                    relative_path = f"../extracted_images/{image_filename}"
                    
                    # Build image_captions dict (expected by pdf_generator.py)
                    image_captions[figure.figure_id] = {
                        'caption': figure.caption,
                        'path': relative_path,
                        'dimensions': figure.dimensions,
                        'width': figure.width,
                        'height': figure.height,
                        'error': None
                    }
                    
                    # Build PlotInfo for compatibility
                    plot_info = PlotInfo(
                        plot_id=figure.figure_id,
                        page_number=figure.page_number,
                        image_data=figure.image_data,
                        coordinates=(
                            figure.bounding_box['left'],
                            figure.bounding_box['top'],
                            figure.bounding_box['right'],
                            figure.bounding_box['bottom']
                        ),
                        caption=figure.caption,
                        width=figure.width,
                        height=figure.height,
                        dimensions=figure.dimensions
                    )
                    plots_list.append(plot_info)
                    
                    logger.info(f"Extracted figure: {figure.figure_id} -> {image_path} ({figure.dimensions})")
                
                logger.info(f"Docling extracted {len(image_captions)} complete figures")
                return image_captions, extracted_images_dir, plots_list
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
                    
        except Exception as e:
            logger.error(f"Error in Docling extraction: {e}")
            return {}, None, []
    
    def extract_figures_from_pdf(self, pdf_path: str) -> List[DoclingFigure]:
        """
        Extract complete figures from PDF using Docling
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of DoclingFigure objects
        """
        figures = []
        
        try:
            logger.info(f"Processing PDF with Docling: {pdf_path}")
            result = self.converter.convert(pdf_path)
            
            # Get document name for figure naming
            doc_name = Path(pdf_path).stem
            
            # Process each picture element
            picture_count = 0
            for element, level in result.document.iterate_items():
                if isinstance(element, PictureItem):
                    picture_count += 1
                    
                    # Get page number and bounding box
                    page_no = element.prov[0].page_no
                    bbox = element.prov[0].bbox
                    
                    logger.info(f"Processing figure {picture_count} on page {page_no}")
                    
                    # Get the page image
                    page = result.document.pages.get(page_no)
                    if page and page.image:
                        # Extract the figure image
                        image_data = self._extract_figure_image(page, bbox)
                        
                        if image_data:
                            # Get caption text
                            caption_text = self._extract_caption(element, result.document)
                            
                            # Get image dimensions
                            width, height = self._get_image_dimensions(image_data)
                            
                            # Create figure object
                            figure = DoclingFigure(
                                figure_id=f"docling_page{page_no}_fig{picture_count}",
                                page_number=page_no,
                                image_data=image_data,
                                caption=caption_text,
                                bounding_box={
                                    'left': float(bbox.l),
                                    'top': float(bbox.t),
                                    'right': float(bbox.r),
                                    'bottom': float(bbox.b)
                                },
                                width=width,
                                height=height,
                                dimensions=f"{width}x{height}px"
                            )
                            figures.append(figure)
                            
                            logger.info(f"Extracted: {figure.figure_id} ({figure.dimensions})")
                            if caption_text:
                                logger.info(f"Caption: {caption_text[:100]}...")
                        else:
                            logger.warning(f"Could not extract image data for figure {picture_count}")
                    else:
                        logger.warning(f"Could not get page image for page {page_no}")
            
            logger.info(f"Docling extraction completed: {len(figures)} figures")
            
        except Exception as e:
            logger.error(f"Error in Docling figure extraction: {e}")
        
        return figures
    
    def _extract_figure_image(self, page, bbox) -> Optional[bytes]:
        """
        Extract figure image from page using bounding box
        
        Args:
            page: Docling page object
            bbox: Bounding box coordinates
            
        Returns:
            Image data as bytes or None
        """
        try:
            # Get PIL image of the page
            page_image = page.image.pil_image
            
            # Calculate page height for coordinate conversion
            pdf_page_height = page_image.height / self.dpi_scale
            
            # Convert bbox coordinates from PDF to PIL coordinates
            left = bbox.l * self.dpi_scale
            right = bbox.r * self.dpi_scale
            top = (pdf_page_height - bbox.t) * self.dpi_scale
            bottom = (pdf_page_height - bbox.b) * self.dpi_scale
            
            # Ensure coordinates are in correct order
            if top > bottom:
                top, bottom = bottom, top
            
            # Crop the image
            crop_box = (int(left), int(top), int(right), int(bottom))
            cropped_image = page_image.crop(crop_box)
            
            # Convert to PNG bytes
            from io import BytesIO
            img_buffer = BytesIO()
            cropped_image.save(img_buffer, format="PNG")
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error extracting figure image: {e}")
            return None
    
    def _extract_caption(self, picture_element, document) -> str:
        """
        Extract caption for a picture element
        
        Args:
            picture_element: PictureItem element
            document: Docling document object
            
        Returns:
            Caption text or empty string
        """
        try:
            # Try built-in caption extraction first
            if hasattr(picture_element, 'caption_text'):
                caption = picture_element.caption_text(doc=document)
                if caption:
                    return caption.strip()
            
            # Fallback: get following text element
            caption = self._extract_following_text(document, picture_element)
            return caption.strip() if caption else ""
            
        except Exception as e:
            logger.warning(f"Error extracting caption: {e}")
            return ""
    
    def _extract_following_text(self, document, picture_element, max_chars: int = 500) -> str:
        """
        Extract text that follows a picture element (likely its caption)
        
        Args:
            document: Docling document object
            picture_element: The PictureItem to find caption for
            max_chars: Maximum characters to extract for caption
            
        Returns:
            String containing the following text/caption
        """
        found_picture = False
        caption_text = ""
        
        try:
            for element, level in document.iterate_items():
                # First find our picture element
                if element == picture_element:
                    found_picture = True
                    continue
                
                # Once found, get the next text element
                if found_picture:
                    # Check if it's a text element (not another picture or table)
                    if hasattr(element, 'text') and not isinstance(element, (PictureItem, TableItem)):
                        caption_text = element.text if hasattr(element, 'text') else str(element)
                        # Limit caption length
                        if len(caption_text) > max_chars:
                            caption_text = caption_text[:max_chars] + "..."
                        break
        except Exception as e:
            logger.warning(f"Error in following text extraction: {e}")
        
        return caption_text
    
    def _get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """
        Get dimensions of image from bytes
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Tuple of (width, height)
        """
        try:
            from PIL import Image
            from io import BytesIO
            
            img = Image.open(BytesIO(image_data))
            return img.size
        except Exception as e:
            logger.warning(f"Error getting image dimensions: {e}")
            return (0, 0)
    
    def save_extraction_metadata(self, figures: List[DoclingFigure], output_dir: Path, source_info: str):
        """
        Save extraction metadata for debugging and analysis
        
        Args:
            figures: List of extracted figures
            output_dir: Output directory
            source_info: Information about the source
        """
        try:
            metadata = {
                "source": source_info,
                "total_figures": len(figures),
                "dpi_scale": self.dpi_scale,
                "figures": [
                    {
                        "figure_id": fig.figure_id,
                        "page_number": fig.page_number,
                        "caption": fig.caption,
                        "dimensions": fig.dimensions,
                        "bounding_box": fig.bounding_box
                    }
                    for fig in figures
                ]
            }
            
            metadata_path = output_dir / "docling_extraction_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved extraction metadata to: {metadata_path}")
            
        except Exception as e:
            logger.warning(f"Error saving extraction metadata: {e}")