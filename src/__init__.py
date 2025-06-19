"""Presentation Toolkit - Comprehensive presentation generation and evaluation"""

__version__ = "1.0.0"
__author__ = "Presentation Toolkit Team"
__description__ = "Generate, convert, and evaluate presentations from topics or PDFs"

from .config import Config
from .generators.router import GenerationRouter
from .conversion.html_to_pdf import PresentationConverter
from .evaluation.evaluator import PresentationEvaluator

__all__ = [
    'Config',
    'GenerationRouter', 
    'PresentationConverter',
    'PresentationEvaluator'
]