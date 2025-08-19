# PDF Prompts Registry

This registry tracks the evolution of PDF presentation generation prompts, documenting lessons learned and improvements made through autonomous evolution.

## Current Status

**Active Version**: v0 (baseline production prompt)  
**Last Updated**: 2025-01-18  
**Total Experiments**: 0  
**Best Performing Version**: v0 (baseline)

## Prompt Versions

### v0 - Production Baseline (2025-01-18)
- **Location**: `evolution_runs/evolved_prompts/pdf_generation_prompt_v0.txt`
- **Source**: Extracted from `src/opencanvas/generators/pdf_generator.py` (lines 168-297)
- **Performance**: Baseline (no metrics yet)
- **Description**: Original hardcoded prompt from production PDFGenerator
- **Key Features**:
  - Visual focus on "wow factor" over conventional academic design
  - Comprehensive LaTeX/MathJax support for mathematical expressions
  - Mermaid diagram support with horizontal layouts
  - Glassmorphism and modern web design trends
  - Fixed dimensions: 1280px width × 720px height
  - Academic content presentation guidelines

## Lessons Learned

### Design Philosophy
- **Visual Impact**: PDF presentations benefit from emotional impact over purely academic aesthetics
- **Layout Constraints**: Fixed 1280px × 720px dimensions work well for PDF-sourced content
- **Mathematical Content**: LaTeX/MathJax support is crucial for academic PDFs

### Technical Requirements
- **Self-contained HTML**: All CSS and JavaScript must be embedded
- **Animation Balance**: Subtle movements enhance without distracting from content
- **Horizontal Layouts**: Better suited for fixed-width presentations than vertical flows

## Evolution Experiments

_No experiments recorded yet. This section will track autonomous evolution runs._

## Guidelines for PDF Prompt Evolution

### What Works Well
1. **Academic Math Support**: Comprehensive LaTeX formatting with animations
2. **Modern Visual Design**: Glassmorphism, gradients, and micro-interactions
3. **Horizontal Diagram Layouts**: Better fit for landscape presentation format
4. **Progressive Content Disclosure**: Animated reveals for complex information

### Areas for Improvement
1. **Content Extraction**: Better handling of PDF structure and flow
2. **Image Integration**: Seamless incorporation of extracted PDF figures
3. **Academic Style Balance**: Finding sweet spot between "wow factor" and scholarly presentation
4. **Content Density**: Optimal text amount per slide for PDF-sourced material

### Known Issues
- None documented yet for v0

## Evolution Rules

### Prompt Filename Convention
- PDF prompts use: `pdf_generation_prompt_v{N}.txt`
- Topic prompts use: `generation_prompt_v{N}.txt`
- This separation ensures PDF and topic evolution don't interfere

### Testing Guidelines
1. **Test PDF**: Use https://arxiv.org/pdf/2505.20286 as standard test document
2. **Evaluation Metrics**: Focus on PDF-specific quality:
   - Accuracy to source material
   - Mathematical notation rendering
   - Academic content presentation
   - Visual appeal vs scholarly appropriateness
3. **Iteration Limits**: Start with 2-5 iterations to avoid overfitting

### Memory Integration
- PDF prompts registry should be referenced for:
  - Previous successful patterns
  - Known failure modes
  - Academic content presentation best practices
  - PDF-specific technical requirements

## Usage Examples

### Starting Evolution from Baseline
```bash
python test_pdf_evolution.py --max-iterations 5 --prompt-only
```

### Starting from Specific Version
```bash
python test_pdf_evolution.py \
  --max-iterations 10 \
  --initial-prompt "evolution_runs/evolved_prompts/pdf_generation_prompt_v2.txt" \
  --memory \
  --prompt-only
```

### Quick Single Iteration Test
```bash
python test_pdf_evolution.py --max-iterations 1 --diagnostic
```

## Integration Notes

### PDF vs Topic Evolution
- **Separate Pipelines**: PDF and topic evolution run independently
- **Shared Infrastructure**: Both use same EvolutionSystem base class
- **Different Metrics**: PDF evolution focuses on academic accuracy, topic evolution on general quality
- **Isolated Outputs**: PDF runs create `pdf_tracked_evolution_*` folders

### Technical Architecture
- **PDFEvolutionSystem**: Specialized evolution class for PDF documents
- **EvolvedPDFGenerator**: PDF generator that injects evolved prompts
- **pdf_mode Flag**: Routes system to use PDF-specific evolved prompts

---

*This registry is maintained automatically by the PDF evolution system and manually curated for insights and guidelines.*