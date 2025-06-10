academic_gen_prompt = '''Create a beautiful HTML presentation based on this content:

```{blog_content}```

**Purpose of presentation:** ```{purpose}```
**Visual theme:** ```{theme}```

Instructions:
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library)
3. Include elegant transitions between slides
4. Use a color scheme appropriate for the "{theme}" theme
5. Optimize typography for readability
6. Target ~100 words per slide maximum - avoid dense text blocks
7. Use the navigation button to switch pages

## Academic Math & Diagrams Integration:

### LaTeX Formula Support:
- **Example:**
```html
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']]
  },
  options: {
    processHtmlClass: 'mathjax-enabled'
  }
};
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>

<div class="code mathjax-enabled" style="white-space: pre-line;">
Algorithm with $f_θ$ and loss $L_t = \frac{1}{t} \delta_{x_t,m}$
Next line preserved
</div>
```
- **Inline formulas:** Use `$E = mc^2$` within text
- **Display equations:** Use `$$\frac{d}{dx}f(x) = f'(x)$$` for centered equations
- **Multi-line equations:** Use `\begin{align}` for step-by-step mathematical derivations
- **Code with math:** ALWAYS Use `class="mathjax-enabled"` AND `white-space: pre-line` for pseudocode
- **When to use:** Any mathematical expressions, equations, statistical notation, scientific formulas, research calculations


### Mermaid Diagram Support:
- **Always include:** `<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>`
- **Structure format:**
```html
<div class="mermaid">
    graph TD
        A[Start] --> B[Process] --> C[End]
        style A fill:#667eea,stroke:#fff,stroke-width:3px,color:#fff
</div>
```
- **When to use:** Process flows, system architecture, research methodology, decision trees, conceptual frameworks
- **Standard colors:** Primary: #667eea, Success: #27ae60, Process: #f39c12, Warning: #f5576c


### Academic Enhancement Guidelines:
- **Show the problem clearly:** Use concrete examples and visual comparisons to demonstrate what's broken with current approaches
- **Explain the solution simply:** Present the main idea with clear diagrams and math, then explain in plain language what it means
- **Break down complex algorithms:** Provide step-by-step walkthroughs with code examples and explain each step's purpose
- **Prove it works visually:** Use charts and graphs to show dramatic before/after improvements that anyone can understand at a glance
- **Explain the magic:** Help readers understand why the approach succeeds where others fail, using intuitive analogies
- **Be honest about limits:** Clearly state what doesn't work yet and what exciting possibilities this opens up


SLIDE STRUCTURE TEMPLATE:
- Title slide with clear value proposition
- 8-15 content slides (each with one key message)
- Conclusion slide summarizing key takeaways

IMPORTANT: The HTML must be a complete, self-contained file that can be opened directly in a browser.
Do not include any explanations, just output the complete HTML code.
        
IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.'''

analytics_gen_prompt = '''Create a beautiful HTML presentation based on this content:

```{blog_content}```

Purpose of presentation: ```{purpose}```
Visual theme: ```{theme}```

Instructions:
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library)
3. Include elegant transitions between slides
4. Use a color scheme appropriate for the "{theme}" theme
5. Optimize typography for readability
6. Use the navigation button to switch pages

MCKINSEY-INSPIRED SLIDE STRUCTURE:
7. **Titles as Conclusions**: Make slide titles ~14 words that explain WHY the information matters, not just what it is (use active voice)
8. **One Message Per Slide**: Each slide should convey a single, clear message (62% McKinsey standard)
9. **Word Economy**: Target ~100 words per slide maximum - avoid dense text blocks
10. **Strategic Layout Selection**: Use these four proven layouts (70% of effective slides):
    - Single chart (most impactful)
    - Chart with bullet points
    - Two-column comparison
    - Clean tables
11. **Visual Hierarchy**: Structure information top-down from title → subtitles → content
12. **Minimal Color Strategy**: Use color sparingly and purposefully - only to highlight key information or communicate specific messages
13. **Consistent Design Elements**: Maintain design consistency throughout, especially with icons and visual elements

CHART AND DATA VISUALIZATION REQUIREMENTS:
14. **Chart Priority**: Include charts on 71% of content slides to enhance understanding and credibility
15. **Bar Chart Preference**: Prioritize bar charts (40% of all charts) for data comparison
16. **Single Chart Focus**: Use only one chart per slide (42.9% standard) to maintain clarity
17. **Strategic Callouts**: Add callouts to 72% of charts to highlight key insights
18. **Interactive Elements**: For data analysis content, embed Chart.js or D3.js visualizations

SLIDE STRUCTURE TEMPLATE:
- Title slide with clear value proposition
- 8-15 content slides (each with one key message)
- Conclusion slide summarizing key takeaways

IMPORTANT: The HTML must be a complete, self-contained file that can be opened directly in a browser.
Do not include any explanations, just output the complete HTML code.
        
IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.'''
