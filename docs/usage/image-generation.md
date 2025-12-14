# Image Generation Guide

OpenCanvas's image generation mode creates beautiful PNG slides using Google's Gemini AI, with intelligent figure-to-slide matching for PDF inputs.

## Overview

Image mode generates presentation slides as individual PNG files, automatically compiled into a PDF. When generating from research papers, the system intelligently extracts figures and matches them to relevant slides.

## Quick Start

### Basic Usage

```bash
# From a topic
opencanvas generate "Introduction to Machine Learning" \
  --output-format image \
  --purpose "academic presentation"

# From a research paper (with automatic figure extraction)
opencanvas generate "https://arxiv.org/pdf/2412.06769" \
  --output-format image \
  --purpose "research seminar"

# From a local PDF
opencanvas generate "path/to/paper.pdf" \
  --output-format image \
  --theme "minimalist"
```

### Requirements

- **API Key**: `GEMINI_API_KEY` required (get from [Google AI Studio](https://aistudio.google.com/))
- **Generation Time**: ~3 minutes for 10-12 slides (includes rate limiting)
- **Model**: Uses `gemini-3-pro-image-preview` (Nano Banana Pro)

## 🎯 Intelligent Figure-to-Slide Matching

### How It Works

When generating from PDFs, OpenCanvas automatically:

1. **Extracts Figures** - Uses Docling library to extract high-quality figures from research papers
2. **Generates Captions** - Creates comprehensive captions for each figure using Claude
3. **Intelligent Matching** - Analyzes slide content and figure captions to assign the most relevant figures
4. **Multi-Figure Support** - Can assign multiple complementary figures to a single slide when appropriate

### Example Workflow

```bash
# Generate with automatic figure extraction (default)
opencanvas generate "https://arxiv.org/pdf/2412.06769" \
  --output-format image \
  --purpose "research seminar"
```

**What happens:**
1. PDF is downloaded and processed
2. Docling extracts all figures with bounding boxes
3. Claude generates descriptive captions for each figure
4. Blog content is generated from PDF text
5. Claude creates slide blueprints and assigns relevant figures to each slide
6. Gemini generates each slide with assigned figures integrated into the design
7. All slides are compiled into a PDF

### Output Structure

```
test_output/
└── paper_name_20241213_225914/
    ├── slides/
    │   ├── slide_001.png
    │   ├── slide_002.png
    │   ├── slide_003.png    # ← May contain extracted figures
    │   └── ...
    ├── extracted_images/
    │   ├── docling_page2_fig1.png
    │   ├── docling_page4_fig2.png
    │   ├── figure_captions.json    # Metadata for debugging
    │   └── ...
    ├── sources/
    │   ├── blog_content.txt
    │   └── slide_blueprints.json   # Shows figure assignments
    └── presentation.pdf
```

### Strategic Figure Selection

Claude uses intelligent heuristics to select figures:

- **Relevance**: Matches figure content to slide topic
- **Complementarity**: Chooses figures that add value, not redundancy
- **Diversity**: Avoids repetitive or similar figures
- **Multi-Figure**: Assigns multiple figures when they tell a cohesive story

**Example Blueprint Entry:**
```json
{
  "slide_number": 3,
  "title": "Chain of Continuous Thought",
  "figure_ids": [0, 1],
  "figure_usage": "primary",
  "content": "..."
}
```

### Controlling Figure Extraction

```bash
# Disable figure extraction
opencanvas generate "paper.pdf" \
  --output-format image \
  --no-use-extracted-images

# Enable figure extraction (default for PDFs)
opencanvas generate "paper.pdf" \
  --output-format image
```

## Advanced Options

### Themes

Available themes for image generation:
- `minimalist` - Clean, simple design
- `academic` - Professional academic style
- `modern` - Contemporary design
- `corporate` - Business presentation style

```bash
opencanvas generate "topic" \
  --output-format image \
  --theme "academic"
```

### Custom Output Directory

```bash
opencanvas generate "topic" \
  --output-format image \
  --output-dir "custom_output/"
```

## Troubleshooting

### No Figures Extracted

**Symptoms**: Log shows "No images extracted from PDF"

**Solutions**:
- Verify PDF contains actual figures (not just text)
- Check that figures are embedded, not scanned images
- Try with a different PDF

### Figure Extraction Errors

**Symptoms**: Error during Docling extraction

**Solutions**:
- Ensure sufficient memory (Docling requires ~2GB)
- Check PDF is not corrupted
- Verify PDF is not password-protected

### No Figures Assigned to Slides

**Symptoms**: `slide_blueprints.json` shows `"figure_ids": null` for all slides

**Solutions**:
- Check `figure_captions.json` to verify captions were generated
- Ensure figures are relevant to slide content
- Try with a different research paper

### API Rate Limits

**Symptoms**: Generation pauses between slides

**Expected**: System includes automatic rate limiting (15s between slides)

**To speed up**: Not recommended - may hit API limits

## Technical Details

### Figure Extraction Pipeline

1. **Docling Processing**
   - Converts PDF to structured document
   - Detects figure bounding boxes
   - Extracts high-resolution images

2. **Caption Generation**
   - Each figure sent to Claude with context
   - Generates comprehensive, descriptive captions
   - Captions used for intelligent matching

3. **Blueprint Planning**
   - Claude receives slide content + figure captions
   - Makes strategic assignments based on relevance
   - Supports multiple figures per slide

4. **Image Generation**
   - Gemini receives slide content + assigned figure images
   - Creates cohesive design integrating figures
   - Maintains consistent style across slides

### Data Flow

```
PDF Input
  ↓
Docling Extraction → Figures + Bounding Boxes
  ↓
Claude Caption Generation → Figure Captions
  ↓
Content Extraction → Blog Content
  ↓
Claude Blueprint Planning → Slide Blueprints + Figure Assignments
  ↓
Gemini Image Generation → PNG Slides (with figures)
  ↓
PDF Compilation → Final Presentation
```

## Best Practices

1. **Use Research Papers**: Figure extraction works best with academic papers
2. **Check Blueprints**: Review `slide_blueprints.json` to see figure assignments
3. **Verify Captions**: Check `figure_captions.json` for caption quality
4. **Theme Selection**: Use `academic` or `minimalist` themes for research presentations
5. **Output Review**: Always review generated slides before presenting

## Examples

### Example 1: Research Paper Presentation

```bash
opencanvas generate "https://arxiv.org/pdf/2412.06769" \
  --output-format image \
  --purpose "research seminar" \
  --theme "academic"
```

**Result**: 12 slides with 7 slides containing extracted figures

### Example 2: Topic-Based Presentation

```bash
opencanvas generate "Introduction to Neural Networks" \
  --output-format image \
  --purpose "lecture" \
  --theme "minimalist"
```

**Result**: 10 slides with AI-generated content (no figure extraction)

### Example 3: Local PDF with Custom Output

```bash
opencanvas generate "~/papers/research.pdf" \
  --output-format image \
  --purpose "conference talk" \
  --output-dir "conference_slides/"
```

**Result**: Slides saved to custom directory with extracted figures

## See Also

- [CLI Reference](cli.md) - Complete command reference
- [API Guide](../../API_README.md) - REST API documentation
- [Troubleshooting](../troubleshooting.md) - Common issues and solutions
