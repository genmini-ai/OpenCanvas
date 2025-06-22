"""
Main FastAPI application for the OpenCanvas API

This module creates and configures the FastAPI application with all
necessary middleware, error handlers, and route registration.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .routes import router
from .models import ErrorResponse
from ..utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenCanvas API",
    description="""
    OpenCanvas API - A comprehensive presentation generation and evaluation system.
    
    This API provides RESTful endpoints for:
    - **Generation**: Create presentations from topics or PDF documents
    - **Conversion**: Convert HTML presentations to PDF format
    - **Evaluation**: Assess presentation quality using AI
    - **Pipeline**: Complete end-to-end workflow
    
    ## Features
    
    🎨 **Dual Input Support**: Generate from text topics or PDF documents  
    🔄 **HTML to PDF Conversion**: High-quality PDF generation with browser automation  
    📊 **AI-Powered Evaluation**: Comprehensive quality assessment  
    🎯 **Smart Research**: Automatic web research for insufficient knowledge  
    🎨 **Multiple Themes**: Professional themes for different contexts  
    🔧 **Complete Pipeline**: End-to-end workflow from input to evaluation  
    
    ## Quick Start
    
    1. **Generate a presentation**:
       ```bash
       curl -X POST "http://localhost:8000/generate" \\
            -H "Content-Type: application/json" \\
            -d '{"input_source": "AI in healthcare", "purpose": "academic presentation"}'
       ```
    
    2. **Convert HTML to PDF**:
       ```bash
       curl -X POST "http://localhost:8000/convert" \\
            -H "Content-Type: application/json" \\
            -d '{"html_file": "output/slides.html", "zoom_factor": 1.2}'
       ```
    
    3. **Run complete pipeline**:
       ```bash
       curl -X POST "http://localhost:8000/pipeline" \\
            -H "Content-Type: application/json" \\
            -d '{"input_source": "quantum computing", "evaluate": true}'
       ```
    """,
    version="1.0.0",
    contact={
        "name": "OpenCanvas API Support",
        "url": "https://github.com/genmini-ai/OpenCanvas",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


def custom_openapi() -> Dict[str, Any]:
    """Custom OpenAPI schema with additional information"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "Generation",
            "description": "Endpoints for generating presentations from topics or PDFs"
        },
        {
            "name": "Conversion", 
            "description": "Endpoints for converting HTML presentations to PDF"
        },
        {
            "name": "Evaluation",
            "description": "Endpoints for evaluating presentation quality using AI"
        },
        {
            "name": "Pipeline",
            "description": "Endpoints for complete end-to-end workflows"
        },
        {
            "name": "Files",
            "description": "Endpoints for downloading generated files"
        },
        {
            "name": "Configuration",
            "description": "Endpoints for getting available options and settings"
        },
        {
            "name": "System",
            "description": "System health and status endpoints"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add trusted host middleware for production
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "your-domain.com"]
# )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error_response = ErrorResponse(
        error=f"HTTP {exc.status_code}",
        detail=exc.detail,
        timestamp=datetime.now().isoformat()
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        timestamp=datetime.now().isoformat()
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting OpenCanvas API server...")
    
    # Validate configuration
    try:
        from ..config import Config
        Config.validate()
        logger.info("Configuration validated successfully")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down OpenCanvas API server...")


# Include routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "OpenCanvas API",
        "version": "1.0.0",
        "description": "A comprehensive presentation generation and evaluation system",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 