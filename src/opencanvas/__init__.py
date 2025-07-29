"""Presentation Toolkit - Comprehensive presentation generation and evaluation"""

__version__ = "1.0.0"
__author__ = "Presentation Toolkit Team"
__description__ = "Generate, convert, and evaluate presentations from topics or PDFs"

from opencanvas.config import Config
from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator
from opencanvas.editing.assist_mode import AssistModeStyleEditor

__all__ = [
    'Config',
    'GenerationRouter', 
    'PresentationConverter',
    'PresentationEvaluator',
    'AssistModeStyleEditor'
]