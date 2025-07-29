"""Presentation evaluation module"""

from opencanvas.evaluation.evaluator import PresentationEvaluator, EvaluationResult
from opencanvas.evaluation.prompts import EvaluationPrompts
from opencanvas.evaluation.adversarial_attacks import PresentationAdversarialAttacks, apply_adversarial_attack

__all__ = ['PresentationEvaluator', 'EvaluationResult', 'EvaluationPrompts', 'PresentationAdversarialAttacks', 'apply_adversarial_attack']