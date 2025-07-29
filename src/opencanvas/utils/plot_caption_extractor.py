#!/usr/bin/env python3
"""
AI-Powered Plot Caption Extractor for PDF Files

This module extracts plots, charts, and figures from PDF files using pdfplumber,
then generates intelligent captions using Claude's vision capabilities.
"""

import os
import base64
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import io
import os
from PIL import Image, ImageDraw

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic not available. Install with: pip install anthropic")

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available. Install with: pip install pdfplumber")

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available. Install with: pip install PyPDF2")

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available. Install with: pip install PyMuPDF")

try:
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams
    from io import StringIO

    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logging.warning(
        "pdfminer.six not available. Install with: pip install pdfminer.six"
    )

logger = logging.getLogger(__name__)


def extract_text_pymupdf(pdf_path: str) -> Dict[int, str]:
    """Extract text using PyMuPDF (fitz)"""
    try:
        doc = fitz.open(pdf_path)
        text_by_page = {}

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_by_page[page_num + 1] = text.strip()

        doc.close()
        return text_by_page
    except Exception as e:
        logger.error(f"PyMuPDF text extraction failed: {e}")
        return {}


def extract_text_pdfplumber(pdf_path: str) -> Dict[int, str]:
    """Extract text using pdfplumber"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_by_page = {}
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_by_page[page_num] = page_text.strip()
            return text_by_page
    except Exception as e:
        logger.error(f"pdfplumber text extraction failed: {e}")
        return {}


def extract_text_pdfminer(pdf_path: str) -> Dict[int, str]:
    """Extract text using pdfminer.six"""
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer

        text_by_page = {}
        for page_num, page_layout in enumerate(extract_pages(pdf_path), 1):
            page_text = []
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text.append(element.get_text())

            if page_text:
                text_by_page[page_num] = "\n".join(page_text).strip()

        return text_by_page
    except Exception as e:
        logger.error(f"pdfminer text extraction failed: {e}")
        return {}


def extract_text_pypdf2(pdf_path: str) -> Dict[int, str]:
    """Extract text using PyPDF2"""
    try:
        text_by_page = {}
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    text_by_page[page_num] = text.strip()
        return text_by_page
    except Exception as e:
        logger.error(f"PyPDF2 text extraction failed: {e}")
        return {}


@dataclass
class TableInfo:
    """Information about a table extracted from PDF"""

    table_id: str
    page_number: int
    table_data: List[List[str]]  # 2D array of table cells
    coordinates: Tuple[float, float, float, float]  # x0, y0, x1, y1
    caption: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PlotInfo:
    """Information about a plot extracted from PDF"""

    plot_id: str
    page_number: int
    image_data: bytes
    coordinates: Tuple[float, float, float, float]  # x0, y0, x1, y1
    image_name: Optional[str] = None
    caption: Optional[str] = None
    confidence: float = 0.0
    plot_type: str = "unknown"
    key_insights: List[str] = None
    suggested_title: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CaptionResult:
    """Result of caption extraction"""

    plot_id: str
    caption: str
    error: Optional[str] = None


class PDFPlotCaptionExtractor:
    """
    AI-powered caption extractor for plots, charts, and figures from PDF files
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "gpt"):
        """
        Initialize the caption extractor

        Args:
            api_key: API key (will use environment variable if not provided)
            provider: AI provider - "gpt" or "claude" (default: "gpt")
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError(
                "pdfplumber library not available. Install with: pip install pdfplumber"
            )

        self.provider = provider

        if provider == "gpt":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI library not available. Install with: pip install openai"
                )
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required for GPT caption extraction"
                )
            self.client = OpenAI(api_key=self.api_key)
        elif provider == "claude":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError(
                    "Anthropic library not available. Install with: pip install anthropic"
                )
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY is required for Claude caption extraction"
                )
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError("Provider must be 'gpt' or 'claude'")

        # Caption extraction prompt
        self.caption_prompt = """
You are an expert at extracting captions from PDF documents. Your task is to find and extract the exact caption text that appears in the PDF for this plot/figure.

IMPORTANT: Extract the caption VERBATIM from the PDF text content. Do not generate or interpret the caption - only extract what is actually written in the PDF.

Please provide your analysis in the following JSON format:

{
    "plot_id": "unique_identifier_for_this_plot",
    "caption": "The exact caption text as it appears in the PDF, verbatim"
}

Guidelines:
1. Look for caption text that appears near the plot/figure in the PDF
2. Extract the caption exactly as it appears - do not modify, interpret, or generate new text
3. If no caption is found in the PDF, use "No caption found" as the caption
4. The plot_id should be a unique identifier (e.g., "plot_page1_fig1", "plot_page2_chart1")
5. Focus on finding text that appears to be a caption for the visual element

Look for:
- Figure captions (e.g., "Figure 1: ...", "Fig. 2: ...")
- Chart captions (e.g., "Chart showing...", "Graph of...")
- Table captions (e.g., "Table 1: ...")
- Any descriptive text that appears to label or explain the visual element
"""

    def debug_image_extraction(self, pdf_path: str, output_dir: str = "debug_output"):
        """
        Debug method to visualize image extraction process

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save debug images
        """

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Debugging page {page_num}")

                    # Get page image
                    page_image = page.to_image(resolution=300)
                    page_width = page.width
                    page_height = page.height
                    img_width, img_height = page_image.original.size

                    # Create a debug image with bounding boxes
                    debug_img = page_image.original.copy()
                    draw = ImageDraw.Draw(debug_img)

                    # Process each image on the page
                    for img_idx, img_info in enumerate(page.images):
                        x0, y0, x1, y1 = (
                            img_info["x0"],
                            img_info["y0"],
                            img_info["x1"],
                            img_info["y1"],
                        )

                        # Convert coordinates
                        scale_x = img_width / page_width
                        scale_y = img_height / page_height

                        img_x0 = int(x0 * scale_x)
                        img_y0 = int((page_height - y1) * scale_y)
                        img_x1 = int(x1 * scale_x)
                        img_y1 = int((page_height - y0) * scale_y)

                        # Draw bounding box
                        draw.rectangle(
                            [img_x0, img_y0, img_x1, img_y1], outline="red", width=3
                        )

                        # Add label
                        draw.text((img_x0, img_y0 - 20), f"Image {img_idx}", fill="red")

                        # Save individual cropped images
                        if img_x1 > img_x0 and img_y1 > img_y0:
                            cropped = page_image.original.crop(
                                (img_x0, img_y0, img_x1, img_y1)
                            )
                            cropped.save(
                                output_path / f"page{page_num}_img{img_idx}_cropped.png"
                            )

                        # Log coordinate information
                        logger.info(f"Page {page_num}, Image {img_idx}:")
                        logger.info(
                            f"  PDF coords: ({x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f})"
                        )
                        logger.info(
                            f"  Image coords: ({img_x0}, {img_y0}, {img_x1}, {img_y1})"
                        )
                        logger.info(
                            f"  Page size: {page_width:.2f} x {page_height:.2f}"
                        )
                        logger.info(f"  Image size: {img_width} x {img_height}")

                    # Save debug image
                    debug_img.save(output_path / f"page{page_num}_debug.png")

        except Exception as e:
            logger.error(f"Error in debug_image_extraction: {e}")

    def extract_plots_from_pdf(self, pdf_path: str) -> List[PlotInfo]:
        """
        Extract all plots/images from a PDF file using pdfplumber

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of PlotInfo objects containing extracted plots
        """
        plots = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Processing PDF with {len(pdf.pages)} pages")

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}")

                    # Extract images from the page using pdfplumber
                    page_images = page.images

                    for img_idx, img in enumerate(page_images):
                        try:
                            # Get image coordinates
                            x0, y0, x1, y1 = (
                                img["x0"],
                                img["top"],
                                img["x1"],
                                img["bottom"],
                            )

                            # Extract image data using pdfplumber
                            image_data = self._extract_image_from_page(page, img)

                            if image_data:
                                plot_id = f"plot_page{page_num}_img{img_idx}"
                                plot_info = PlotInfo(
                                    plot_id=plot_id,
                                    page_number=page_num,
                                    image_data=image_data,
                                    coordinates=(x0, y0, x1, y1),
                                    image_name=img.get("name", f"image_{img_idx}"),
                                )
                                plots.append(plot_info)
                                logger.info(
                                    f"Extracted plot from page {page_num}, image {img_idx}"
                                )

                        except Exception as e:
                            logger.warning(
                                f"Failed to extract image {img_idx} from page {page_num}: {e}"
                            )
                            continue

                logger.info(f"Extracted {len(plots)} plots from PDF")
                return plots

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return []

    def _extract_image_from_page(self, page, img_info) -> Optional[bytes]:
        """
        Extract image data from a page using pdfplumber

        Args:
            page: pdfplumber page object
            img_info: Image information from page.images

        Returns:
            Image data as bytes, or None if extraction failed
        """
        try:
            # Method 1: Use page.to_image() with proper coordinate conversion
            page_image = page.to_image(resolution=300)

            # Get image coordinates from pdfplumber
            x0, y0, x1, y1 = (
                img_info["x0"],
                img_info["y0"],
                img_info["x1"],
                img_info["y1"],
            )

            # pdfplumber coordinates are in points, convert to image pixels
            # The page image has a different coordinate system
            page_width = page.width
            page_height = page.height

            # Get the actual image dimensions
            img_width, img_height = page_image.original.size

            # Convert PDF coordinates to image coordinates
            # Note: PDF coordinates start from bottom-left, image coordinates from top-left
            scale_x = img_width / page_width
            scale_y = img_height / page_height

            # Convert coordinates
            img_x0 = int(x0 * scale_x)
            img_y0 = int((page_height - y1) * scale_y)  # Flip Y coordinate
            img_x1 = int(x1 * scale_x)
            img_y1 = int((page_height - y0) * scale_y)  # Flip Y coordinate

            # Ensure coordinates are within bounds
            img_x0 = max(0, min(img_x0, img_width))
            img_y0 = max(0, min(img_y0, img_height))
            img_x1 = max(img_x0, min(img_x1, img_width))
            img_y1 = max(img_y0, min(img_y1, img_height))

            # Only crop if we have a valid region
            if img_x1 > img_x0 and img_y1 > img_y0:
                cropped_image = page_image.original.crop(
                    (img_x0, img_y0, img_x1, img_y1)
                )

                # Convert to PNG
                img_buffer = io.BytesIO()
                cropped_image.save(img_buffer, format="PNG")
                return img_buffer.getvalue()
            else:
                logger.warning(
                    f"Invalid crop region: ({img_x0}, {img_y0}, {img_x1}, {img_y1})"
                )
                return None

        except Exception as e:
            logger.warning(f"Failed to extract image using page.to_image(): {e}")
            return None

    def _extract_pdf_text(self, pdf_path: str, method: str = "auto") -> Dict[int, str]:
        """
        Extract text content from PDF using different methods (pdfplumber is used for image extraction)

        Args:
            pdf_path: Path to the PDF file
            method: Text extraction method - "auto", "pymupdf", "pdfplumber", "pdfminer", "pypdf2"
                   Note: pdfplumber is used for image extraction regardless of this setting

        Returns:
            Dictionary mapping page numbers to text content
        """
        if method == "auto":
            # Try methods in order of preference (excluding pdfplumber for text since it's used for images)
            methods = ["pymupdf", "pdfminer", "pypdf2"]
        else:
            methods = [method]

        for method_name in methods:
            try:
                if method_name == "pymupdf" and PYMUPDF_AVAILABLE:
                    return extract_text_pymupdf(pdf_path)
                elif method_name == "pdfplumber" and PDFPLUMBER_AVAILABLE:
                    # Use pdfplumber for text extraction if specifically requested
                    return extract_text_pdfplumber(pdf_path)
                elif method_name == "pdfminer" and PDFMINER_AVAILABLE:
                    return extract_text_pdfminer(pdf_path)
                elif method_name == "pypdf2" and PYPDF2_AVAILABLE:
                    return extract_text_pypdf2(pdf_path)
            except Exception as e:
                logger.warning(f"Failed to extract text with {method_name}: {e}")
                continue

        logger.error("No text extraction method available")
        return {}

    def extract_captions_from_pdf(
        self, pdf_path: str, text_method: str = "auto"
    ) -> List[PlotInfo]:
        """
        Extract plots from PDF and generate captions for each

        Args:
            pdf_path: Path to the PDF file
            text_method: Text extraction method to use

        Returns:
            List of PlotInfo objects with captions
        """
        # Step 1: Extract plots from PDF
        plots = self.extract_plots_from_pdf(pdf_path)

        if not plots:
            logger.warning(f"No plots found in PDF: {pdf_path}")
            return []

        # Step 2: Read PDF content for context (page-by-page)
        pdf_text_by_page = self._extract_pdf_text(pdf_path, text_method)

        # Step 3: Generate captions for each plot with page-specific context
        for plot in plots:
            logger.info(f"Generating caption for plot from page {plot.page_number}")

            # Get text from the specific page where the plot is located
            page_text = pdf_text_by_page.get(plot.page_number, "")
            if not page_text:
                logger.warning(f"No text found for page {plot.page_number}")
                page_text = ""

            caption_result = self._generate_caption_for_plot(
                plot.image_data, page_text, plot.page_number
            )

            # Update plot info with caption results
            plot.caption = caption_result.caption
            plot.error = caption_result.error

        return plots

    def _generate_caption_for_plot(
        self, image_data: bytes, page_text: str, page_number: int
    ) -> CaptionResult:
        """
        Generate caption for a plot using AI with page-specific context

        Args:
            image_data: Image data as bytes
            page_text: Text content from the specific page where plot was found
            page_number: Page number where plot was found

        Returns:
            CaptionResult with generated caption and metadata
        """
        try:
            # Validate image data
            if not image_data or len(image_data) == 0:
                logger.warning(f"Empty image data for page {page_number}")
                return CaptionResult(
                    plot_id=f"plot_page{page_number}",
                    caption="No image data available",
                    error="Empty image data",
                )

            # Convert image data to PNG format for API compatibility
            try:
                from PIL import Image
                import io

                # Open the image from bytes
                img = Image.open(io.BytesIO(image_data))

                # Convert to RGB if necessary (some PDF images might be in CMYK or other modes)
                if img.mode in ("CMYK", "LA", "P"):
                    img = img.convert("RGB")

                # Convert to PNG format
                png_buffer = io.BytesIO()
                img.save(png_buffer, format="PNG")
                png_image_data = png_buffer.getvalue()

                logger.info(
                    f"Converted image to PNG: {len(image_data)} -> {len(png_image_data)} bytes"
                )

            except Exception as e:
                logger.warning(
                    f"Failed to convert image to PNG for page {page_number}: {e}"
                )
                return CaptionResult(
                    plot_id=f"plot_page{page_number}",
                    caption="Image conversion failed",
                    error=f"Image conversion failed: {e}",
                )

            # Encode PNG image data
            image_base64 = base64.b64encode(png_image_data).decode("utf-8")

            # Create context-aware prompt with page-specific text
            context_prompt = f"""
This plot was extracted from page {page_number} of a PDF document. 

Page {page_number} Text Content:
{page_text[:1500] if page_text else "No text content available for this page"}

{self.caption_prompt}

Please analyze the plot in the context of the page text to find the exact caption that appears on this page.
"""

            if self.provider == "gpt":
                # Use GPT-4 Vision
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": context_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_base64}"
                                    },
                                },
                            ],
                        }
                    ],
                )
                response_text = response.choices[0].message.content
            else:
                # Use Claude
                message = self.client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_base64,
                                    },
                                },
                                {"type": "text", "text": context_prompt},
                            ],
                        }
                    ],
                )
                response_text = message.content[0].text

            # Parse JSON response
            import json

            try:
                # Find JSON in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1

                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)

                    return CaptionResult(
                        plot_id=result.get("plot_id", f"plot_page{page_number}"),
                        caption=result.get("caption", "No caption found"),
                    )
                else:
                    # Fallback: treat entire response as caption
                    return CaptionResult(
                        plot_id=f"plot_page{page_number}",
                        caption=response_text.strip(),
                        error="Could not parse JSON response",
                    )

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return CaptionResult(
                    plot_id=f"plot_page{page_number}",
                    caption=response_text.strip(),
                    error=f"JSON parsing failed: {e}",
                )

        except Exception as e:
            logger.error(f"Error in caption generation API call: {e}")
            return CaptionResult(
                plot_id=f"plot_page{page_number}", caption="", error=str(e)
            )

    def save_plots_to_directory(
        self, plots: List[PlotInfo], output_dir: str
    ) -> Dict[str, str]:
        """
        Save extracted plots to a directory

        Args:
            plots: List of PlotInfo objects
            output_dir: Directory to save plots

        Returns:
            Dictionary mapping plot names to file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        for i, plot in enumerate(plots):
            try:
                # Create filename
                filename = f"plot_page{plot.page_number}_{i+1}.png"
                file_path = output_path / filename

                # Save image
                with open(file_path, "wb") as f:
                    f.write(plot.image_data)

                saved_files[filename] = str(file_path)
                logger.info(f"Saved plot: {file_path}")

            except Exception as e:
                logger.error(f"Failed to save plot {i+1}: {e}")

        return saved_files

    def generate_json_output(self, plots: List[PlotInfo]) -> str:
        """
        Generate JSON output with plot_id and caption pairs

        Args:
            plots: List of PlotInfo objects

        Returns:
            JSON string with plot_id: caption pairs
        """
        import json

        result = {}
        for plot in plots:
            if plot.caption:
                result[plot.plot_id] = plot.caption
            else:
                result[plot.plot_id] = "No caption found"

        return json.dumps(result, indent=2, ensure_ascii=False)

    def generate_pdf_report(self, plots: List[PlotInfo], pdf_path: str) -> str:
        """
        Generate a comprehensive report of extracted plots and captions

        Args:
            plots: List of PlotInfo objects
            pdf_path: Path to the source PDF

        Returns:
            Formatted report string
        """
        if not plots:
            return f"No plots extracted from {pdf_path}"

        report_lines = [
            f"# PDF Plot Caption Extraction Report",
            f"",
            f"**Source PDF**: {pdf_path}",
            f"**Total plots extracted**: {len(plots)}",
            f"",
        ]

        # Summary statistics
        successful_captions = sum(
            1
            for p in plots
            if p.error is None and p.caption and p.caption != "No caption found"
        )
        pages_with_plots = set(p.page_number for p in plots)

        report_lines.extend(
            [
                f"## Summary",
                f"- Total plots extracted: {len(plots)}",
                f"- Successful captions: {successful_captions}",
                f"- Success rate: {successful_captions/len(plots)*100:.1f}%",
                f"- Pages with plots: {len(pages_with_plots)}",
                f"",
            ]
        )

        # Group plots by page
        plots_by_page = {}
        for plot in plots:
            page_num = plot.page_number
            if page_num not in plots_by_page:
                plots_by_page[page_num] = []
            plots_by_page[page_num].append(plot)

        # Detailed results by page
        report_lines.extend(["## Detailed Results by Page", ""])

        for page_num in sorted(plots_by_page.keys()):
            page_plots = plots_by_page[page_num]
            report_lines.extend([f"### Page {page_num}", f""])

            for i, plot in enumerate(page_plots, 1):
                report_lines.extend(
                    [
                        f"#### Plot {i}",
                        f"- **Plot ID**: {plot.plot_id}",
                        f"- **Caption**: {plot.caption}",
                        f"- **Coordinates**: ({plot.coordinates[0]:.1f}, {plot.coordinates[1]:.1f}, {plot.coordinates[2]:.1f}, {plot.coordinates[3]:.1f})",
                    ]
                )

                if plot.error:
                    report_lines.append(f"- **Error**: {plot.error}")

                report_lines.append("")

        return "\n".join(report_lines)

    def extract_tables_from_pdf(self, pdf_path: str) -> List[TableInfo]:
        """
        Extract all tables from a PDF file using pdfplumber

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of TableInfo objects containing extracted tables
        """
        tables = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Processing PDF with {len(pdf.pages)} pages for tables")

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num} for tables")

                    # Extract tables from the page using pdfplumber
                    page_tables = page.extract_tables()

                    for table_idx, table_data in enumerate(page_tables):
                        try:
                            if table_data and any(
                                any(cell.strip() for cell in row) for row in table_data
                            ):
                                # Get table bounding box (approximate)
                                table_bbox = self._get_table_bbox(page, table_data)

                                table_id = f"table_page{page_num}_tbl{table_idx}"
                                table_info = TableInfo(
                                    table_id=table_id,
                                    page_number=page_num,
                                    table_data=table_data,
                                    coordinates=table_bbox,
                                )
                                tables.append(table_info)
                                logger.info(
                                    f"Extracted table from page {page_num}, table {table_idx}"
                                )

                        except Exception as e:
                            logger.warning(
                                f"Failed to extract table {table_idx} from page {page_num}: {e}"
                            )
                            continue

                logger.info(f"Extracted {len(tables)} tables from PDF")
                return tables

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path} for tables: {e}")
            return []

    def _get_table_bbox(self, page, table_data) -> Tuple[float, float, float, float]:
        """
        Get approximate bounding box for a table

        Args:
            page: pdfplumber page object
            table_data: Table data as 2D array

        Returns:
            Tuple of (x0, y0, x1, y1) coordinates
        """
        try:
            # Try to find table boundaries using page.find_tables()
            tables = page.find_tables()
            if tables:
                # Use the first table found as reference
                table_bbox = tables[0].bbox
                return (table_bbox[0], table_bbox[1], table_bbox[2], table_bbox[3])
            else:
                # Fallback: use page dimensions
                return (0, 0, page.width, page.height)
        except Exception as e:
            logger.warning(f"Failed to get table bbox: {e}")
            # Fallback: use page dimensions
            return (0, 0, page.width, page.height)

    def extract_plots_and_tables_from_pdf(
        self, pdf_path: str
    ) -> Tuple[List[PlotInfo], List[TableInfo]]:
        """
        Extract both plots and tables from a PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (plots, tables) lists
        """
        plots = self.extract_plots_from_pdf(pdf_path)
        tables = self.extract_tables_from_pdf(pdf_path)

        logger.info(f"Extracted {len(plots)} plots and {len(tables)} tables from PDF")
        return plots, tables

    def generate_table_caption(
        self, table_data: List[List[str]], page_text: str, page_number: int
    ) -> CaptionResult:
        """
        Generate caption for a table using AI with page-specific context

        Args:
            table_data: Table data as 2D array
            page_text: Text content from the specific page where table was found
            page_number: Page number where table was found

        Returns:
            CaptionResult with generated caption and metadata
        """
        try:
            # Convert table data to string representation
            table_str = self._table_to_string(table_data)

            # Create context-aware prompt for table caption
            context_prompt = f"""
This table was extracted from page {page_number} of a PDF document. 

Page {page_number} Text Content:
{page_text[:1500] if page_text else "No text content available for this page"}

Table Data:
{table_str}

Please find the exact caption for this table in the page text. Look for:
- Table captions (e.g., "Table 1: ...", "Table 2: ...")
- Descriptive text that appears to label this table
- Any text that explains what the table shows

Please provide your analysis in the following JSON format:

{{
    "plot_id": "unique_identifier_for_this_table",
    "caption": "The exact caption text as it appears in the PDF, verbatim"
}}

If no caption is found, use "No caption found" as the caption.
"""

            if self.provider == "gpt":
                # Use GPT-4 for table caption extraction
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": context_prompt}],
                )
                response_text = response.choices[0].message.content
            else:
                # Use Claude for table caption extraction
                message = self.client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": context_prompt}],
                )
                response_text = message.content[0].text

            # Parse JSON response
            import json

            try:
                # Find JSON in response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1

                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)

                    return CaptionResult(
                        plot_id=result.get("plot_id", f"table_page{page_number}"),
                        caption=result.get("caption", "No caption found"),
                    )
                else:
                    # Fallback: treat entire response as caption
                    return CaptionResult(
                        plot_id=f"table_page{page_number}",
                        caption=response_text.strip(),
                        error="Could not parse JSON response",
                    )

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return CaptionResult(
                    plot_id=f"table_page{page_number}",
                    caption=response_text.strip(),
                    error=f"JSON parsing failed: {e}",
                )

        except Exception as e:
            logger.error(f"Error in table caption generation API call: {e}")
            return CaptionResult(
                plot_id=f"table_page{page_number}", caption="", error=str(e)
            )

    def _table_to_string(self, table_data: List[List[str]]) -> str:
        """
        Convert table data to string representation

        Args:
            table_data: Table data as 2D array

        Returns:
            String representation of the table
        """
        if not table_data:
            return "Empty table"

        # Find maximum column widths
        col_widths = []
        for col_idx in range(max(len(row) for row in table_data)):
            col_width = max(
                len(str(row[col_idx])) if col_idx < len(row) else 0
                for row in table_data
            )
            col_widths.append(col_width)

        # Build table string
        table_lines = []
        for row in table_data:
            row_str = "|"
            for col_idx, cell in enumerate(row):
                cell_str = str(cell) if cell else ""
                row_str += f" {cell_str:<{col_widths[col_idx]}} |"
            table_lines.append(row_str)

        return "\n".join(table_lines)

    def save_tables_to_files(
        self, tables: List[TableInfo], output_dir: str
    ) -> Dict[str, str]:
        """
        Save extracted tables to files

        Args:
            tables: List of TableInfo objects
            output_dir: Directory to save tables

        Returns:
            Dictionary mapping table names to file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        for i, table in enumerate(tables):
            try:
                # Create filename
                filename = f"table_page{table.page_number}_{i+1}.csv"
                file_path = output_path / filename

                # Save table as CSV
                import csv

                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(table.table_data)

                saved_files[filename] = str(file_path)
                logger.info(f"Saved table: {file_path}")

            except Exception as e:
                logger.error(f"Failed to save table {i+1}: {e}")

        return saved_files

    def generate_table_json_output(self, tables: List[TableInfo]) -> str:
        """
        Generate JSON output with table_id and caption pairs

        Args:
            tables: List of TableInfo objects

        Returns:
            JSON string with table_id: caption pairs
        """
        import json

        result = {}
        for table in tables:
            if table.caption:
                result[table.table_id] = table.caption
            else:
                result[table.table_id] = "No caption found"

        return json.dumps(result, indent=2, ensure_ascii=False)

    def extract_captions_for_plots_and_tables(
        self, pdf_path: str, text_method: str = "auto"
    ) -> Tuple[List[PlotInfo], List[TableInfo]]:
        """
        Extract plots and tables from PDF and generate captions for each

        Args:
            pdf_path: Path to the PDF file
            text_method: Text extraction method to use

        Returns:
            Tuple of (plots, tables) with captions
        """
        # Step 1: Extract plots and tables from PDF
        plots, tables = self.extract_plots_and_tables_from_pdf(pdf_path)

        if not plots and not tables:
            logger.warning(f"No plots or tables found in PDF: {pdf_path}")
            return [], []

        # Step 2: Read PDF content for context (page-by-page)
        pdf_text_by_page = self._extract_pdf_text(pdf_path, text_method)

        # Step 3: Generate captions for plots with page-specific context
        for plot in plots:
            logger.info(f"Generating caption for plot from page {plot.page_number}")

            # Get text from the specific page where the plot is located
            page_text = pdf_text_by_page.get(plot.page_number, "")
            if not page_text:
                logger.warning(f"No text found for page {plot.page_number}")
                page_text = ""

            caption_result = self._generate_caption_for_plot(
                plot.image_data, page_text, plot.page_number
            )

            # Update plot info with caption results
            plot.caption = caption_result.caption
            plot.error = caption_result.error

        # Step 4: Generate captions for tables with page-specific context
        for table in tables:
            logger.info(f"Generating caption for table from page {table.page_number}")

            # Get text from the specific page where the table is located
            page_text = pdf_text_by_page.get(table.page_number, "")
            if not page_text:
                logger.warning(f"No text found for page {table.page_number}")
                page_text = ""

            caption_result = self.generate_table_caption(
                table.table_data, page_text, table.page_number
            )

            # Update table info with caption results
            table.caption = caption_result.caption
            table.error = caption_result.error

        logger.info(
            f"Generated captions for {len(plots)} plots and {len(tables)} tables"
        )
        return plots, tables
