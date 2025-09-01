"""
FastAPI route handlers for the OpenCanvas API

This module defines all the REST API endpoints for presentation
generation, conversion, evaluation, and pipeline workflows.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from .models import (
    GenerateRequest, GenerateResponse,
    ConvertRequest, ConvertResponse,
    EvaluateRequest, EvaluateResponse,
    PipelineRequest, PipelineResponse,
    HealthResponse, ErrorResponse
)
from .services import (
    GenerationService, ConversionService, 
    EvaluationService, PipelineService
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Service instances
generation_service = GenerationService()
conversion_service = ConversionService()
evaluation_service = EvaluationService()
pipeline_service = PipelineService()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.post("/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate_presentation(request: GenerateRequest):
    """
    Generate a presentation from a topic or PDF source
    
    This endpoint creates an HTML presentation from either:
    - A text topic (with optional web research)
    - A PDF document (academic paper, etc.)
    
    The generated presentation will be saved as an HTML file in the specified output directory.
    """
    try:
        logger.info(f"Generate request: {request.input_source[:50]}...")
        
        response = await generation_service.generate_presentation(
            input_source=request.input_source,
            purpose=request.purpose.value,
            theme=request.theme.value,
            output_dir=request.output_dir,
            extract_images=request.extract_images
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert", response_model=ConvertResponse, tags=["Conversion"])
async def convert_html_to_pdf(request: ConvertRequest):
    """
    Convert an HTML presentation to PDF format
    
    This endpoint takes an HTML presentation file and converts it to a PDF
    using browser automation (Selenium or Playwright). The conversion process
    captures each slide as an image and combines them into a single PDF.
    """
    try:
        logger.info(f"Convert request: {request.html_file}")
        
        response = await conversion_service.convert_html_to_pdf(
            html_file=request.html_file,
            output_filename=request.output_filename,
            method=request.method.value,
            zoom_factor=request.zoom_factor,
            output_dir=request.output_dir,
            cleanup=request.cleanup
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Convert endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_presentation(request: EvaluateRequest):
    """
    Evaluate the quality of a presentation
    
    This endpoint performs a comprehensive evaluation of a presentation using AI.
    The evaluation includes:
    - Visual assessment (design, layout, readability)
    - Content analysis (structure, narrative, coverage)
    - Reference comparison (if source material is provided)
    
    The evaluation results are saved as a JSON file and also returned in the response.
    """
    try:
        logger.info(f"Evaluate request: {request.eval_folder}")
        
        response = await evaluation_service.evaluate_presentation(
            eval_folder=request.eval_folder,
            output_filename=request.output_filename,
            model=request.model
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluate endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline", response_model=PipelineResponse, tags=["Pipeline"])
async def run_pipeline(request: PipelineRequest):
    """
    Run the complete presentation pipeline
    
    This endpoint executes the full workflow:
    1. Generate presentation from topic or PDF
    2. Convert HTML to PDF
    3. Optionally evaluate the presentation quality
    
    This is the most comprehensive endpoint that combines all functionality
    into a single request.
    """
    try:
        logger.info(f"Pipeline request: {request.input_source[:50]}...")
        
        response = await pipeline_service.run_pipeline(
            input_source=request.input_source,
            purpose=request.purpose.value,
            theme=request.theme.value,
            source_pdf=request.source_pdf,
            evaluate=request.evaluate,
            output_dir=request.output_dir,
            zoom_factor=request.zoom_factor,
            method=request.method.value,
            extract_images=request.extract_images
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_path:path}", tags=["Files"])
async def download_file(file_path: str):
    """
    Download a generated file
    
    This endpoint allows downloading of generated files (HTML, PDF, evaluation results)
    from the output directories. The file_path should be relative to the output directory.
    """
    try:
        from pathlib import Path
        
        # Security: prevent directory traversal
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Construct full path
        full_path = Path("output") / file_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Not a file")
        
        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/themes", tags=["Configuration"])
async def get_available_themes():
    """Get list of available presentation themes"""
    from .models import ThemeEnum
    
    return {
        "themes": [theme.value for theme in ThemeEnum],
        "default": "professional blue"
    }


@router.get("/purposes", tags=["Configuration"])
async def get_available_purposes():
    """Get list of available presentation purposes"""
    from .models import PurposeEnum
    
    return {
        "purposes": [purpose.value for purpose in PurposeEnum],
        "default": "general presentation"
    }


@router.get("/conversion-methods", tags=["Configuration"])
async def get_conversion_methods():
    """Get list of available conversion methods"""
    from .models import ConversionMethodEnum
    
    return {
        "methods": [method.value for method in ConversionMethodEnum],
        "default": "selenium"
    }


@router.get("/features", tags=["Configuration"])
async def get_available_features():
    """Get available features and their status"""
    from .services import check_optional_dependencies
    
    features = check_optional_dependencies()
    
    return {
        "image_extraction": {
            "docling": features.get('docling', False),
            "pdfplumber": features.get('pdfplumber', False),
            "description": "Advanced image extraction from PDFs"
        },
        "supported": {
            "pdf_generation": True,
            "topic_generation": True,
            "html_to_pdf": True,
            "evaluation": True
        }
    } 