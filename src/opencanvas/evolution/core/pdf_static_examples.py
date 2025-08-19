"""
Static code examples for PDF evolution system.

These examples are kept separate from the evolvable prompt content to avoid
brace escaping issues with Python's .format() method. The LLM evolves the
instructions and guidelines, while these working code examples remain stable.
"""

PDF_STATIC_EXAMPLES = """
<academic_math_support>
### LaTeX Formula Support:
- Enhanced styling: Add beautiful animations and hover effects to formulas
- Example with delightful styling:
```html
<script>
MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']]
  }},
  options: {{
    processHtmlClass: 'mathjax-enabled'
  }}
}};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
<div class="code mathjax-enabled animate-reveal" style="white-space: pre-line; backdrop-filter: blur(10px); background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px;">
Algorithm with $f_θ$ and loss $L_t = \\frac{{1}}{{t}} \\delta_{{x_t,m}}$
Next line preserved
</div>
```
- Animated reveals: Use CSS animations to reveal formulas progressively
- Interactive math: Add hover effects and smooth transitions to mathematical expressions
- When to use: Any mathematical expressions, equations, statistical notation, scientific formulas, research calculations
</academic_math_support>

<diagram_support>
### Mermaid Diagram Support:
- Always include: `<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>`
- CRITICAL: Use horizontal, landscape-optimized layouts for fixed width: 1280px; min-height: 720px;
- Enhanced structure with modern styling:
```html
<div class="mermaid diagram-container" style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border-radius: 16px; padding: 24px; backdrop-filter: blur(10px); width: 1200px; margin: 0 auto;">
    graph LR
        A[Start] --> B[Process 1] --> C[Process 2] --> D[End]
        E[Input] --> B
        F[Config] --> C
        style A fill:#667eea,stroke:#fff,stroke-width:3px,color:#fff,rx:12,ry:12
        style B fill:#764ba2,stroke:#fff,stroke-width:2px,color:#fff,rx:12,ry:12
        style C fill:#f39c12,stroke:#fff,stroke-width:2px,color:#fff,rx:12,ry:12
        style D fill:#27ae60,stroke:#fff,stroke-width:3px,color:#fff,rx:12,ry:12
</div>
```
- Diagram orientation priority: Always use `graph LR` (left-to-right) or `graph RL` (right-to-left) instead of `graph TD` (top-down)
- Flowchart layouts: Use horizontal flows: `flowchart LR` for process flows, timelines, and sequential steps
- Network diagrams: Spread nodes horizontally with compact vertical spacing
- Modern colors with gradients: Primary: #667eea to #764ba2, Success: #27ae60 to #2ecc71, Process: #f39c12 to #e67e22, Warning: #f5576c to #e74c3c
- Container sizing: Use `width: 1200px; margin: 0 auto;` for diagram containers to center within 1280px slide width
- Animated diagrams: Add CSS animations to make diagram elements appear with staggered timing
</diagram_support>
"""


def get_static_examples():
    """Get the static code examples for PDF evolution."""
    return PDF_STATIC_EXAMPLES


def remove_static_sections(prompt_content: str) -> str:
    """
    Remove static code example sections from prompt content before evolution.
    
    Args:
        prompt_content: The full prompt content
        
    Returns:
        Prompt content with static sections removed
    """
    import re
    
    # Remove <academic_math_support> section
    prompt_content = re.sub(
        r'<academic_math_support>.*?</academic_math_support>\s*\n?',
        '',
        prompt_content,
        flags=re.DOTALL
    )
    
    # Remove <diagram_support> section
    prompt_content = re.sub(
        r'<diagram_support>.*?</diagram_support>\s*\n?',
        '',
        prompt_content,
        flags=re.DOTALL
    )
    
    return prompt_content


def add_static_examples(evolved_prompt: str) -> str:
    """
    Add static code examples to an evolved prompt.
    
    Args:
        evolved_prompt: The evolved prompt content without static examples
        
    Returns:
        Complete prompt with static examples appended
    """
    # Find the insertion point - before output_requirements if it exists
    if '<output_requirements>' in evolved_prompt:
        # Insert before output_requirements
        parts = evolved_prompt.split('<output_requirements>')
        return parts[0] + PDF_STATIC_EXAMPLES + '\n\n<output_requirements>' + parts[1]
    else:
        # Append at the end
        return evolved_prompt + '\n' + PDF_STATIC_EXAMPLES