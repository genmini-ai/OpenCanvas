# Multi-Agent Evolution System for OpenCanvas
# Implements systematic improvement of presentation generation through multi-agent analysis

# Lazy imports to avoid circular dependencies
__all__ = [
    'MultiAgentEvolutionManager',
    'PromptEvolutionManager', 
    'EvolvedGenerator',
    'EvolvedGenerationRouter'
]

def __getattr__(name):
    """Lazy import to avoid circular dependencies"""
    if name == 'MultiAgentEvolutionManager':
        from .multi_agent_evolution_manager import MultiAgentEvolutionManager
        return MultiAgentEvolutionManager
    elif name == 'PromptEvolutionManager':
        from .prompt_evolution_manager import PromptEvolutionManager
        return PromptEvolutionManager
    elif name == 'EvolvedGenerator':
        from .evolved_generator import EvolvedGenerator
        return EvolvedGenerator
    elif name == 'EvolvedGenerationRouter':
        from .evolved_generator import EvolvedGenerationRouter
        return EvolvedGenerationRouter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")