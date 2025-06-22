"""
Pydantic models for API request/response schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from pathlib import Path


class PurposeEnum(str, Enum):
    """Valid presentation purposes"""
    ACADEMIC_PRESENTATION = "academic presentation"
    CONFERENCE_PRESENTATION = "conference presentation"
    CORPORATE_PRESENTATION = "corporate presentation"
    RESEARCH_SEMINAR = "research seminar"
    PITCH_DECK = "pitch deck"
    GENERAL_PRESENTATION = "general presentation"


class ThemeEnum(str, Enum):
    """Valid presentation themes"""
    PROFESSIONAL_BLUE = "professional blue"
    CLEAN_MINIMALIST = "clean minimalist"
    BOLD_HIGH_CONTRAST = "bold high contrast"
    COOL_PROFESSIONAL = "cool professional"
    NATURAL_EARTH = "natural earth"
    MUTED_MORANDI_TONES = "muted morandi tones"
    MODERN_CONTEMPORARY = "modern contemporary"
    WARM_EARTH_TONES = "warm earth tones"
    SOFT_PASTELS = "soft pastels"
    ACADEMIC = "academic"


class ConversionMethodEnum(str, Enum):
    """Valid conversion methods"""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"


class GenerateRequest(BaseModel):
    """Request model for presentation generation"""
    input_source: str = Field(..., description="Topic text or PDF file path/URL")
    purpose: PurposeEnum = Field(default=PurposeEnum.GENERAL_PRESENTATION, description="Purpose of presentation")
    theme: ThemeEnum = Field(default=ThemeEnum.PROFESSIONAL_BLUE, description="Visual theme")
    output_dir: Optional[str] = Field(default="output", description="Output directory")


class GenerateResponse(BaseModel):
    """Response model for presentation generation"""
    success: bool = Field(..., description="Whether generation was successful")
    html_file: Optional[str] = Field(None, description="Path to generated HTML file")
    research_performed: Optional[bool] = Field(None, description="Whether web research was performed")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class ConvertRequest(BaseModel):
    """Request model for HTML to PDF conversion"""
    html_file: str = Field(..., description="Path to HTML presentation file")
    output_filename: str = Field(default="presentation.pdf", description="Output PDF filename")
    method: ConversionMethodEnum = Field(default=ConversionMethodEnum.SELENIUM, description="Browser automation method")
    zoom_factor: float = Field(default=1.2, ge=0.1, le=3.0, description="Zoom factor for PDF")
    output_dir: str = Field(default="output", description="Output directory")
    cleanup: bool = Field(default=True, description="Whether to cleanup temporary files")


class ConvertResponse(BaseModel):
    """Response model for HTML to PDF conversion"""
    success: bool = Field(..., description="Whether conversion was successful")
    pdf_file: Optional[str] = Field(None, description="Path to generated PDF file")
    zoom_level: Optional[float] = Field(None, description="Applied zoom level")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class EvaluateRequest(BaseModel):
    """Request model for presentation evaluation"""
    eval_folder: str = Field(..., description="Folder containing presentation.pdf and optionally paper.pdf")
    output_filename: Optional[str] = Field(None, description="Output JSON filename")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model for evaluation")


class EvaluationScores(BaseModel):
    """Model for evaluation scores"""
    visual_scores: Optional[Dict[str, Any]] = None
    content_free_scores: Optional[Dict[str, Any]] = None
    content_required_scores: Optional[Dict[str, Any]] = None
    overall_scores: Optional[Dict[str, float]] = None


class EvaluateResponse(BaseModel):
    """Response model for presentation evaluation"""
    success: bool = Field(..., description="Whether evaluation was successful")
    evaluation_results: Optional[EvaluationScores] = Field(None, description="Evaluation scores")
    output_file: Optional[str] = Field(None, description="Path to saved evaluation results")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class PipelineRequest(BaseModel):
    """Request model for complete pipeline workflow"""
    input_source: str = Field(..., description="Topic text or PDF file path/URL")
    purpose: PurposeEnum = Field(default=PurposeEnum.GENERAL_PRESENTATION, description="Purpose of presentation")
    theme: ThemeEnum = Field(default=ThemeEnum.PROFESSIONAL_BLUE, description="Visual theme")
    source_pdf: Optional[str] = Field(None, description="Source PDF for evaluation (if input is topic)")
    evaluate: bool = Field(default=False, description="Run evaluation after generation")
    output_dir: str = Field(default="output", description="Output directory")
    zoom_factor: float = Field(default=1.2, ge=0.1, le=3.0, description="PDF zoom factor")
    method: ConversionMethodEnum = Field(default=ConversionMethodEnum.SELENIUM, description="Conversion method")


class PipelineResponse(BaseModel):
    """Response model for complete pipeline workflow"""
    success: bool = Field(..., description="Whether pipeline was successful")
    html_file: Optional[str] = Field(None, description="Path to generated HTML file")
    pdf_file: Optional[str] = Field(None, description="Path to generated PDF file")
    evaluation_results: Optional[EvaluationScores] = Field(None, description="Evaluation results if requested")
    research_performed: Optional[bool] = Field(None, description="Whether web research was performed")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp") 