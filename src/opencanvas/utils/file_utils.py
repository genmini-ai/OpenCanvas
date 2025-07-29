"""
File utilities for OpenCanvas - handles file naming, organization, and source storage
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_topic_slug(text: str, max_words: int = 5) -> str:
    """
    Generate a clean slug from topic text for file naming
    
    Args:
        text: Input text to convert to slug
        max_words: Maximum number of words to include
        
    Returns:
        Clean slug suitable for file names
    """
    # Remove special characters and convert to lowercase
    clean_text = re.sub(r'[^\w\s-]', '', text.lower())
    
    # Split into words and take first max_words
    words = clean_text.split()[:max_words]
    
    # Join with underscores and remove extra spaces
    slug = '_'.join(words)
    
    # Remove any double underscores
    slug = re.sub(r'_+', '_', slug)
    
    # Ensure it's not empty
    if not slug:
        slug = "presentation"
    
    return slug

def create_organized_output_structure(output_dir: Path, topic_slug: str, timestamp: str) -> Dict[str, Path]:
    """
    Create organized directory structure for outputs
    Structure: output_dir/timestamp/slides/, output_dir/timestamp/evaluation/, etc.
    
    Args:
        output_dir: Base output directory (already contains topic name)
        topic_slug: Clean topic identifier (not used in new structure)
        timestamp: Timestamp string
        
    Returns:
        Dictionary with paths for different file types
    """
    # Create timestamp folder within the topic directory
    presentation_folder = output_dir / timestamp
    presentation_folder.mkdir(parents=True, exist_ok=True)
    
    # Create subfolders
    slides_folder = presentation_folder / "slides"
    slides_folder.mkdir(exist_ok=True)
    
    evaluation_folder = presentation_folder / "evaluation"
    evaluation_folder.mkdir(exist_ok=True)
    
    sources_folder = presentation_folder / "sources"
    sources_folder.mkdir(exist_ok=True)
    
    return {
        'base': presentation_folder,
        'slides': slides_folder,
        'evaluation': evaluation_folder,
        'sources': sources_folder
    }

def save_source_content(sources_folder: Path, content: str, filename: str) -> Optional[Path]:
    """
    Save source content (blog text, etc.) to sources folder
    
    Args:
        sources_folder: Path to sources directory
        content: Content to save
        filename: Name of the file
        
    Returns:
        Path to saved file or None if failed
    """
    try:
        source_path = sources_folder / filename
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"📄 Saved source content: {source_path}")
        return source_path
    except Exception as e:
        logger.error(f"Failed to save source content: {e}")
        return None

def copy_source_pdf(sources_folder: Path, pdf_source: str) -> Optional[Path]:
    """
    Copy source PDF to sources folder
    
    Args:
        sources_folder: Path to sources directory
        pdf_source: Path to source PDF
        
    Returns:
        Path to copied PDF or None if failed
    """
    try:
        source_path = Path(pdf_source)
        if source_path.exists():
            dest_path = sources_folder / "source.pdf"
            shutil.copy2(source_path, dest_path)
            logger.info(f"📄 Copied source PDF: {dest_path}")
            return dest_path
        else:
            logger.warning(f"Source PDF not found: {pdf_source}")
            return None
    except Exception as e:
        logger.error(f"Failed to copy source PDF: {e}")
        return None

def organize_pipeline_outputs(
    output_dir: Path,
    topic_slug: str,
    timestamp: str,
    html_content: str,
    pdf_path: Optional[str] = None,
    evaluation_result: Optional[Dict[str, Any]] = None,
    source_content: Optional[str] = None,
    source_pdf: Optional[str] = None
) -> Dict[str, Path]:
    """
    Organize all pipeline outputs into a structured directory
    
    Args:
        output_dir: Base output directory
        topic_slug: Clean topic identifier
        timestamp: Timestamp string
        html_content: HTML presentation content
        pdf_path: Path to generated PDF
        evaluation_result: Evaluation results
        source_content: Source blog/content text
        source_pdf: Path to source PDF
        
    Returns:
        Dictionary with paths to all organized files
    """
    # Create directory structure
    paths = create_organized_output_structure(output_dir, topic_slug, timestamp)
    
    organized_files = {}
    
    # Save HTML file with simple name
    try:
        html_path = paths['slides'] / "presentation.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        organized_files['html'] = html_path
        logger.info(f"📄 Saved HTML: {html_path}")
    except Exception as e:
        logger.error(f"Failed to save HTML: {e}")
    
    # Copy/move PDF file with simple name
    if pdf_path and Path(pdf_path).exists():
        try:
            pdf_dest = paths['slides'] / "presentation.pdf"
            shutil.copy2(pdf_path, pdf_dest)
            organized_files['pdf'] = pdf_dest
            logger.info(f"📄 Saved PDF: {pdf_dest}")
        except Exception as e:
            logger.error(f"Failed to copy PDF: {e}")
    
    # Save evaluation results with simple name
    if evaluation_result:
        try:
            import json
            eval_path = paths['evaluation'] / "evaluation_results.json"
            with open(eval_path, 'w', encoding='utf-8') as f:
                json.dump(evaluation_result, f, indent=2, ensure_ascii=False)
            organized_files['evaluation'] = eval_path
            logger.info(f"📄 Saved evaluation: {eval_path}")
        except Exception as e:
            logger.error(f"Failed to save evaluation: {e}")
    
    # Save source content with simple name
    if source_content:
        source_path = save_source_content(
            paths['sources'], 
            source_content, 
            "source_content.txt"
        )
        if source_path:
            organized_files['source_content'] = source_path
    
    # Copy source PDF
    if source_pdf:
        source_pdf_path = copy_source_pdf(paths['sources'], source_pdf)
        if source_pdf_path:
            organized_files['source_pdf'] = source_pdf_path
    
    organized_files['base_folder'] = paths['base']
    
    return organized_files

def get_file_summary(organized_files: Dict[str, Path]) -> str:
    """
    Generate a summary of organized files
    
    Args:
        organized_files: Dictionary of file paths
        
    Returns:
        Formatted summary string
    """
    summary = []
    summary.append(f"📁 Base folder: {organized_files.get('base_folder', 'N/A')}")
    
    if 'html' in organized_files:
        summary.append(f"🌐 HTML slides: {organized_files['html'].name}")
    
    if 'pdf' in organized_files:
        summary.append(f"📄 PDF presentation: {organized_files['pdf'].name}")
    
    if 'evaluation' in organized_files:
        summary.append(f"📊 Evaluation results: {organized_files['evaluation'].name}")
    
    if 'source_content' in organized_files:
        summary.append(f"📝 Source content: {organized_files['source_content'].name}")
    
    if 'source_pdf' in organized_files:
        summary.append(f"📄 Source PDF: {organized_files['source_pdf'].name}")
    
    return "\n".join(summary) 