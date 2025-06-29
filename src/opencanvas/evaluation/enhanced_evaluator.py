"""
Enhanced presentation evaluator that can handle source content for better evaluation
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Literal
from dataclasses import dataclass

from .evaluator import PresentationEvaluator, EvaluationResult

logger = logging.getLogger(__name__)

class EnhancedPresentationEvaluator(PresentationEvaluator):
    """
    Enhanced presentation evaluator that can handle source content for reference-required evaluation
    """
    
    def evaluate_presentation_with_sources(
        self,
        presentation_pdf_path: str,
        source_content_path: Optional[str] = None,
        source_pdf_path: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate a presentation with source content for reference-required evaluation
        
        Args:
            presentation_pdf_path: Path to the presentation PDF
            source_content_path: Path to source content text file (for topic-based presentations)
            source_pdf_path: Path to source PDF (for PDF-based presentations)
            
        Returns:
            EvaluationResult with comprehensive evaluation
        """
        logger.info("Starting enhanced presentation evaluation with source content...")
        
        # Extract presentation PDF
        presentation_pdf_data = self.extract_pdf_as_base64(presentation_pdf_path)
        if not presentation_pdf_data:
            logger.error("Failed to extract presentation PDF")
            return EvaluationResult()
        
        # Step 1: Visual evaluation (no source needed)
        visual_scores = self.evaluate_visual(presentation_pdf_data)
        
        # Step 2: Content-free evaluation (no source needed)
        content_free_scores = self.evaluate_content_free(presentation_pdf_data)
        
        # Step 3: Content-required evaluation (with source)
        content_required_scores = None
        
        if source_pdf_path:
            # Use PDF source for reference-required evaluation
            logger.info(f"Using PDF source for reference evaluation: {source_pdf_path}")
            source_pdf_data = self.extract_pdf_as_base64(source_pdf_path)
            if source_pdf_data:
                content_required_scores = self.evaluate_content_required(
                    presentation_pdf_data, 
                    source_pdf_data
                )
            else:
                logger.warning("Failed to extract source PDF data")
        
        elif source_content_path:
            # Use text content for reference-required evaluation
            logger.info(f"Using text source for reference evaluation: {source_content_path}")
            content_required_scores = self.evaluate_content_with_text_source(
                presentation_pdf_data,
                source_content_path
            )
        
        else:
            logger.warning("No source content provided for reference-required evaluation")
        
        # Combine results
        result = EvaluationResult(
            visual_scores=visual_scores,
            content_free_scores=content_free_scores,
            content_required_scores=content_required_scores
        )
        
        # Calculate overall scores
        result.overall_scores = self._calculate_overall_scores(result)
        
        return result
    
    def evaluate_content_with_text_source(
        self, 
        presentation_pdf_data: str, 
        source_content_path: str
    ) -> Dict[str, Any]:
        """
        Evaluate content dimensions using text source content
        
        Args:
            presentation_pdf_data: Base64 encoded presentation PDF
            source_content_path: Path to source text content
            
        Returns:
            Evaluation scores for content dimensions requiring reference
        """
        try:
            # Read source content
            with open(source_content_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            # Create enhanced prompt that includes the source content
            enhanced_prompt = f"""
{self.prompts.content_required}

SOURCE CONTENT FOR REFERENCE:
{source_content}

Please evaluate the presentation against this source content according to the criteria above.
Focus on how well the presentation captures, organizes, and presents the key information from the source content.
"""
            
            logger.info("Evaluating content with text source reference...")
            return self.call_api_with_pdfs(enhanced_prompt, presentation_pdf_data)
            
        except Exception as e:
            logger.error(f"Error evaluating with text source: {e}")
            return {"error": str(e)}
    
    def load_source_content_into_prompt(self, source_path: str) -> str:
        """
        Load source content and format it for evaluation prompts
        
        Args:
            source_path: Path to source content file
            
        Returns:
            Formatted source content for prompts
        """
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Truncate if too long (to avoid token limits)
            max_chars = 8000  # Adjust based on model limits
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n[Content truncated for evaluation...]"
            
            return f"""
SOURCE CONTENT FOR REFERENCE:
{'='*50}
{content}
{'='*50}

Please evaluate the presentation against this source content.
"""
        except Exception as e:
            logger.error(f"Error loading source content: {e}")
            return "Error loading source content for evaluation." 