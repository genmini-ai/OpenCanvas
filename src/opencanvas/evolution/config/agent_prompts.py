"""
Agent System Prompts - References to centralized prompts
"""

from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts

# Get agent system prompts from centralized location
AGENT_PROMPTS = {
    "reflection": EvolutionPrompts.AGENT_SYSTEM_REFLECTION,
    "improvement": EvolutionPrompts.AGENT_SYSTEM_IMPROVEMENT,
    "implementation": EvolutionPrompts.AGENT_SYSTEM_IMPLEMENTATION,
    "orchestrator": EvolutionPrompts.AGENT_SYSTEM_ORCHESTRATOR
}

AGENT_ACTIONS = {
    "reflection": [
        "analyze_evaluations",
        "identify_weaknesses", 
        "compare_iterations",
        "root_cause_analysis"
    ],
    "improvement": [
        "design_improvements",
        "prioritize_improvements",
        "estimate_impact",
        "create_implementation_plan"
    ],
    "implementation": [
        "implement_improvements",
        "generate_prompts",
        "create_validation",
        "test_implementation",
        "propose_tools",
        "create_tools"
    ],
    "orchestrator": [
        "plan_evolution_cycle",
        "coordinate_agents",
        "track_progress",
        "evaluate_results"
    ]
}

AGENT_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.7,
    "max_tokens": 4000
}
