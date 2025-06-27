"""
Service layer for the OpenCanvas API

This module provides async service classes that wrap the existing
generation, conversion, and evaluation functionality.
"""

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from opencanvas.config import Config
from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator
from .models import (
    GenerateResponse, ConvertResponse, EvaluateResponse, PipelineResponse,
    EvaluationScores
)

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for presentation generation"""
    
    def __init__(self):
        """Initialize the generation service"""
        self.router = GenerationRouter(
            api_key=Config.ANTHROPIC_API_KEY,
            brave_api_key=Config.BRAVE_API_KEY
        )
    
    async def generate_presentation(
        self, 
        input_source: str, 
        purpose: str, 
        theme: str, 
        output_dir: str = "output"
    ) -> GenerateResponse:
        """Generate presentation from topic or PDF"""
        try:
            logger.info(f"Starting generation: {input_source}")
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.router.generate,
                input_source,
                purpose,
                theme,
                output_dir
            )
            
            if result:
                return GenerateResponse(
                    success=True,
                    html_file=result.get('html_file'),
                    research_performed=result.get('research_performed'),
                    message="Presentation generated successfully"
                )
            else:
                return GenerateResponse(
                    success=False,
                    message="Generation failed",
                    error="No result returned from generator"
                )
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return GenerateResponse(
                success=False,
                message="Generation failed",
                error=str(e)
            )


class ConversionService:
    """Service for HTML to PDF conversion"""
    
    async def convert_html_to_pdf(
        self,
        html_file: str,
        output_filename: str = "presentation.pdf",
        method: str = "selenium",
        zoom_factor: float = 1.2,
        output_dir: str = "output",
        cleanup: bool = True
    ) -> ConvertResponse:
        """Convert HTML presentation to PDF"""
        try:
            logger.info(f"Starting conversion: {html_file}")
            
            # Validate input file
            html_path = Path(html_file)
            if not html_path.exists():
                return ConvertResponse(
                    success=False,
                    message="HTML file not found",
                    error=f"File not found: {html_file}"
                )
            
            # Validate zoom factor
            if zoom_factor <= 0 or zoom_factor > 3.0:
                return ConvertResponse(
                    success=False,
                    message="Invalid zoom factor",
                    error="Zoom factor must be between 0.1 and 3.0"
                )
            
            # Run conversion in thread pool
            loop = asyncio.get_event_loop()
            converter = PresentationConverter(
                html_file=html_file,
                output_dir=output_dir,
                method=method,
                zoom_factor=zoom_factor
            )
            
            pdf_path = await loop.run_in_executor(
                None,
                converter.convert,
                output_filename,
                cleanup
            )
            
            return ConvertResponse(
                success=True,
                pdf_file=str(pdf_path),
                zoom_level=zoom_factor,
                message="PDF conversion completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConvertResponse(
                success=False,
                message="Conversion failed",
                error=str(e)
            )


class EvaluationService:
    """Service for presentation evaluation"""
    
    def __init__(self):
        """Initialize the evaluation service"""
        self.evaluator = PresentationEvaluator(
            api_key=Config.ANTHROPIC_API_KEY,
            model=Config.EVALUATION_MODEL
        )
    
    async def evaluate_presentation(
        self,
        eval_folder: str,
        output_filename: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> EvaluateResponse:
        """Evaluate presentation quality"""
        try:
            logger.info(f"Starting evaluation: {eval_folder}")
            
            # Update model if different from default
            if model != Config.EVALUATION_MODEL:
                self.evaluator.model = model
            
            # Run evaluation in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.evaluator.evaluate_presentation,
                eval_folder
            )
            
            # Determine output filename
            if not output_filename:
                folder_name = Path(eval_folder).name
                output_filename = f"{folder_name}_evaluation_results.json"
            
            output_path = Path(eval_folder) / output_filename
            
            # Save results
            await loop.run_in_executor(
                None,
                self.evaluator.save_results,
                result,
                str(output_path)
            )
            
            # Convert to API model
            evaluation_scores = EvaluationScores(
                visual_scores=result.visual_scores,
                content_free_scores=result.content_free_scores,
                content_required_scores=result.content_required_scores,
                overall_scores=result.overall_scores
            )
            
            return EvaluateResponse(
                success=True,
                evaluation_results=evaluation_scores,
                output_file=str(output_path),
                message="Evaluation completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return EvaluateResponse(
                success=False,
                message="Evaluation failed",
                error=str(e)
            )


class PipelineService:
    """Service for complete pipeline workflow"""
    
    def __init__(self):
        """Initialize pipeline service with all sub-services"""
        self.generation_service = GenerationService()
        self.conversion_service = ConversionService()
        self.evaluation_service = EvaluationService()
    
    async def run_pipeline(
        self,
        input_source: str,
        purpose: str,
        theme: str,
        source_pdf: Optional[str] = None,
        evaluate: bool = False,
        output_dir: str = "output",
        zoom_factor: float = 1.2,
        method: str = "selenium"
    ) -> PipelineResponse:
        """Run complete pipeline: generate → convert → evaluate"""
        try:
            logger.info(f"Starting pipeline: {input_source}")
            
            # Step 1: Generate
            logger.info("Step 1: Generating presentation...")
            gen_response = await self.generation_service.generate_presentation(
                input_source=input_source,
                purpose=purpose,
                theme=theme,
                output_dir=output_dir
            )
            
            if not gen_response.success:
                return PipelineResponse(
                    success=False,
                    message="Pipeline failed at generation step",
                    error=gen_response.error
                )
            
            html_file = gen_response.html_file
            if not html_file:
                return PipelineResponse(
                    success=False,
                    message="No HTML file generated",
                    error="Generation succeeded but no HTML file path returned"
                )
            
            # Step 2: Convert to PDF
            logger.info("Step 2: Converting to PDF...")
            conv_response = await self.conversion_service.convert_html_to_pdf(
                html_file=html_file,
                output_filename="presentation.pdf",
                method=method,
                zoom_factor=zoom_factor,
                output_dir=output_dir,
                cleanup=True
            )
            
            if not conv_response.success:
                return PipelineResponse(
                    success=False,
                    html_file=html_file,
                    message="Pipeline failed at conversion step",
                    error=conv_response.error
                )
            
            pdf_file = conv_response.pdf_file
            
            # Step 3: Evaluate (if requested)
            evaluation_results = None
            if evaluate:
                logger.info("Step 3: Evaluating presentation...")
                
                # Copy source PDF if provided
                if source_pdf:
                    source_path = Path(source_pdf)
                    if source_path.exists():
                        target_path = Path(output_dir) / "paper.pdf"
                        shutil.copy2(source_path, target_path)
                        logger.info(f"Copied source PDF: {source_pdf}")
                
                eval_response = await self.evaluation_service.evaluate_presentation(
                    eval_folder=output_dir,
                    output_filename="evaluation_results.json"
                )
                
                if eval_response.success:
                    evaluation_results = eval_response.evaluation_results
                else:
                    logger.warning(f"Evaluation failed: {eval_response.error}")
            
            return PipelineResponse(
                success=True,
                html_file=html_file,
                pdf_file=pdf_file,
                evaluation_results=evaluation_results,
                research_performed=gen_response.research_performed,
                message="Pipeline completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return PipelineResponse(
                success=False,
                message="Pipeline failed",
                error=str(e)
            ) 