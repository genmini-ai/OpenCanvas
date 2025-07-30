# Multi-Agent Evolution System for OpenCanvas
# Implements systematic improvement of presentation generation through multi-agent analysis

from .multi_agent_evolution_manager import MultiAgentEvolutionManager
from .prompt_evolution_manager import PromptEvolutionManager
from .evolved_generator import EvolvedGenerator, EvolvedGenerationRouter

__all__ = [
    'MultiAgentEvolutionManager',
    'PromptEvolutionManager', 
    'EvolvedGenerator',
    'EvolvedGenerationRouter'
]