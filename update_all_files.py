#!/usr/bin/env python3
"""
Update all files to use centralized prompts
"""

import re
from pathlib import Path

def update_core_agents():
    """Update core/agents.py to use centralized prompts"""
    file_path = Path("src/opencanvas/evolution/core/agents.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import
    if "from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts" not in content:
        content = content.replace(
            "from opencanvas.evolution.config.agent_prompts import AGENT_PROMPTS, AGENT_ACTIONS, AGENT_CONFIG",
            "from opencanvas.evolution.config.agent_prompts import AGENT_PROMPTS, AGENT_ACTIONS, AGENT_CONFIG\nfrom opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts"
        )
    
    # Replace all f-string prompts
    replacements = [
        (r'prompt = f"""Analyze the following presentation.*?Provide systematic analysis with specific metrics and actionable insights\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_ANALYZE_EVALUATIONS',
            evaluations_json=evaluations_json,
            topics_str=topics_str
        )"""),
        
        (r'prompt = f"""Design specific, systematic improvements.*?Focus on practical, implementable improvements with clear impact\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_DESIGN_IMPROVEMENTS',
            iteration_number=iteration_number,
            reflection_json=reflection_json,
            baseline_json=baseline_json
        )"""),
        
        (r'prompt = f"""Implement the following improvements.*?Focus on creating immediately deployable implementations\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_IMPLEMENT_IMPROVEMENTS',
            iteration_number=iteration_number,
            improvements_json=improvements_json,
            config_json=config_json
        )"""),
        
        (r'prompt = f"""As a reflection specialist.*?Provide your analysis and insights\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_REFLECTION',
            action=action,
            input_json=input_json
        )"""),
        
        (r'prompt = f"""As an improvement specialist.*?Design specific improvements based on the input\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_IMPROVEMENT',
            action=action,
            input_json=input_json
        )"""),
        
        (r'prompt = f"""As an implementation specialist.*?Create concrete implementations based on the requirements\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_IMPLEMENTATION',
            action=action,
            input_json=input_json
        )"""),
        
        (r'prompt = f"""As an orchestration specialist.*?Coordinate the evolution process based on the input\."""',
         """prompt = EvolutionPrompts.get_prompt(
            'CORE_GENERIC_ORCHESTRATION',
            action=action,
            input_json=input_json
        )"""),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated core/agents.py")

def update_evolved_generator():
    """Update evolved_generator.py to use centralized prompts"""
    file_path = Path("src/opencanvas/evolution/evolved_generator.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import
    if "from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts" not in content:
        content = content.replace(
            "from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager",
            "from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager\nfrom opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts"
        )
    
    # Replace fallback prompt
    content = re.sub(
        r'fallback_prompt = f"""Create a presentation about:.*?Generate a comprehensive HTML presentation with proper structure and styling\."""',
        """fallback_prompt = EvolutionPrompts.get_prompt(
            'FALLBACK_GENERATION',
            content=content,
            purpose=purpose,
            theme=theme
        )""",
        content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated evolved_generator.py")

def update_prompt_evolution_manager():
    """Update prompt_evolution_manager.py to use centralized prompts"""
    file_path = Path("src/opencanvas/evolution/prompt_evolution_manager.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import
    if "from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts" not in content:
        content = content.replace(
            "import json",
            "import json\nfrom opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts"
        )
    
    # Replace base prompts
    content = re.sub(
        r'base_prompt = """You are an expert presentation generator.*?THEME: {theme}"""',
        """base_prompt = EvolutionPrompts.get_prompt(
            'TOPIC_GENERATION_BASE',
            topic='{topic}',
            purpose='{purpose}',
            theme='{theme}'
        )""",
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'base_prompt = """You are an expert presentation generator.*?THEME: {theme}"""',
        """base_prompt = EvolutionPrompts.get_prompt(
            'PDF_GENERATION_BASE',
            pdf_content='{pdf_content}',
            purpose='{purpose}',
            theme='{theme}'
        )""",
        content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated prompt_evolution_manager.py")

def update_core_prompts():
    """Update core/prompts.py to use centralized prompts"""
    file_path = Path("src/opencanvas/evolution/core/prompts.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import
    if "from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts" not in content:
        content = content.replace(
            "import json",
            "import json\nfrom opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts"
        )
    
    # Replace base prompts
    content = re.sub(
        r'base_prompt = """You are an expert presentation generator.*?THEME: {theme}"""',
        """base_prompt = EvolutionPrompts.get_prompt(
            'TOPIC_GENERATION_BASE',
            topic='{topic}',
            purpose='{purpose}',
            theme='{theme}'
        )""",
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'base_prompt = """You are an expert presentation generator.*?THEME: {theme}"""',
        """base_prompt = EvolutionPrompts.get_prompt(
            'PDF_GENERATION_BASE',
            pdf_content='{pdf_content}',
            purpose='{purpose}',
            theme='{theme}'
        )""",
        content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated core/prompts.py")

def update_agent_prompts_config():
    """Update config/agent_prompts.py to use centralized prompts"""
    file_path = Path("src/opencanvas/evolution/config/agent_prompts.py")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the AGENT_PROMPTS dictionary to reference centralized prompts
    new_content = '''"""
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
        "test_implementation"
    ],
    "orchestrator": [
        "plan_evolution_cycle",
        "coordinate_agents",
        "track_progress",
        "evaluate_results"
    ]
}

AGENT_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.7,
    "max_tokens": 4000
}
'''
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Updated config/agent_prompts.py")

def main():
    print("🔧 Updating all files to use centralized prompts...")
    print("=" * 60)
    
    update_core_agents()
    update_evolved_generator()
    update_prompt_evolution_manager()
    update_core_prompts()
    update_agent_prompts_config()
    
    print("=" * 60)
    print("✅ All files updated to use centralized prompts!")
    print("\nNow all prompts are managed in:")
    print("src/opencanvas/evolution/prompts/evolution_prompts.py")

if __name__ == "__main__":
    main()