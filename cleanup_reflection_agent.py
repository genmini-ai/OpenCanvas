#!/usr/bin/env python3
"""
Clean up reflection_agent.py to properly use centralized prompts
"""

import re
from pathlib import Path

def cleanup_reflection_agent():
    """Remove all f-string prompts and their content from reflection_agent.py"""
    
    file_path = Path("src/opencanvas/evolution/multi_agent/reflection_agent.py")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    skip_until_triple_quote = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the start of an f-string prompt that needs fixing
        if 'prompt = EvolutionPrompts.get_prompt(' in line:
            # Keep this line and the following lines until the closing parenthesis
            cleaned_lines.append(line)
            i += 1
            paren_count = line.count('(') - line.count(')')
            while i < len(lines) and paren_count > 0:
                cleaned_lines.append(lines[i])
                paren_count += lines[i].count('(') - lines[i].count(')')
                i += 1
            # Now skip everything until we find the closing triple quotes
            while i < len(lines):
                if '"""' in lines[i]:
                    i += 1
                    break
                i += 1
        # Check for the second type of f-string prompt (Compare presentation quality)
        elif 'prompt = f"""Compare presentation quality' in line:
            # Replace with centralized prompt call
            cleaned_lines.append('        # Compare iterations - using reflection analysis prompt\n')
            cleaned_lines.append('        prompt = EvolutionPrompts.get_prompt(\n')
            cleaned_lines.append("            'REFLECTION_ANALYSIS',\n")
            cleaned_lines.append('            iteration_number=len(iterations),\n')
            cleaned_lines.append('            evaluation_json=json.dumps({"iterations": iterations}, indent=2),\n')
            cleaned_lines.append('            baseline_json=json.dumps({}, indent=2)\n')
            cleaned_lines.append('        )\n')
            # Skip until closing triple quotes
            i += 1
            while i < len(lines):
                if '"""' in lines[i]:
                    i += 1
                    break
                i += 1
        # Check for the third type of f-string prompt (root cause analysis)
        elif 'prompt = f"""Perform deep root cause' in line:
            # Replace with centralized prompt call
            cleaned_lines.append('        # Root cause analysis - using reflection analysis prompt\n')
            cleaned_lines.append('        prompt = EvolutionPrompts.get_prompt(\n')
            cleaned_lines.append("            'REFLECTION_ANALYSIS',\n")
            cleaned_lines.append('            iteration_number=1,\n')
            cleaned_lines.append('            evaluation_json=json.dumps(weakness_patterns, indent=2),\n')
            cleaned_lines.append('            baseline_json=json.dumps({}, indent=2)\n')
            cleaned_lines.append('        )\n')
            # Skip until closing triple quotes
            i += 1
            while i < len(lines):
                if '"""' in lines[i]:
                    i += 1
                    break
                i += 1
        # Skip lines that are part of leftover prompt content
        elif line.strip().startswith('EVALUATION DATA:') or \
             line.strip().startswith('TOPICS ANALYZED:') or \
             line.strip().startswith('## Analysis Required:') or \
             line.strip().startswith('### ') or \
             line.strip().startswith('ITERATIONS DATA:') or \
             line.strip().startswith('WEAKNESS PATTERNS:'):
            # Skip these lines and continue until we find actual code
            while i < len(lines):
                if 'result = self.call_claude(prompt)' in lines[i]:
                    cleaned_lines.append(lines[i])
                    break
                i += 1
            i += 1
        else:
            cleaned_lines.append(line)
            i += 1
    
    # Write back the cleaned content
    with open(file_path, 'w') as f:
        f.writelines(cleaned_lines)
    
    print(f"✅ Cleaned up reflection_agent.py")

if __name__ == "__main__":
    cleanup_reflection_agent()