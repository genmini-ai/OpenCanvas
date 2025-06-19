# OpenCanvas

OpenCanvas is a comprehensive presentation generation and evaluation system that creates HTML slide decks from topics or PDF documents, converts them to PDF format, and evaluates their quality using AI.

## Features

🎨 **Dual Input Support**: Generate presentations from either text topics or PDF documents  
🔄 **HTML to PDF Conversion**: Convert generated HTML slides to PDF format  
📊 **AI-Powered Evaluation**: Comprehensive presentation quality assessment  
🎯 **Smart Research**: Automatic web research for insufficient knowledge topics  
🎨 **Multiple Themes**: Professional themes for different presentation contexts  
🔧 **Complete Pipeline**: End-to-end workflow from input to evaluation  

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install browser drivers** (for HTML to PDF conversion)
```bash
# For Playwright
playwright install chromium

# For Selenium - download ChromeDriver manually or use:
# https://chromedriver.chromium.org/
```

4. **Setup environment variables**
```bash
cp env.example .env
# Edit .env with your API keys
```

Required API keys:
- `ANTHROPIC_API_KEY`: For Claude AI (required)
- `BRAVE_API_KEY`: For web search (optional, but recommended)

## Quick Start

### Generate from Topic
```bash
python -m src.main generate "AI in healthcare applications" --purpose "academic presentation" --theme "clean minimalist"
```

### Generate from PDF
```bash
python -m src.main generate "https://arxiv.org/pdf/2505.20286" --purpose "research seminar"
```

### Convert HTML to PDF
```bash
python -m src.main convert output/slides.html --output presentation.pdf --zoom 1.5
```

### Evaluate Presentation
```bash
python -m src.main evaluate evaluation_folder/
```

### Full Pipeline
```bash
python -m src.main pipeline "quantum computing" --purpose "conference talk" --evaluate --zoom 1.3
```

## Available Commands

### `generate`
Generate presentation from topic or PDF source.

**Arguments:**
- `input`: Topic text or PDF file path/URL
- `--purpose`: Purpose of presentation (default: "general presentation")
- `--theme`: Visual theme (default: "professional blue")
- `--output-dir`: Output directory (default: "output")

**Example:**
```bash
python -m src.main generate "sustainable energy solutions" --purpose "corporate presentation" --theme "natural earth"
```

### `convert`
Convert HTML presentation to PDF.

**Arguments:**
- `html_file`: HTML presentation file path
- `--output`: Output PDF filename (default: "presentation.pdf")
- `--method`: Browser method - "selenium" or "playwright" (default: "selenium")
- `--zoom`: Zoom factor 0.1-3.0 (default: 1.2)
- `--output-dir`: Output directory (default: "output")
- `--no-cleanup`: Keep temporary image files

**Example:**
```bash
python -m src.main convert slides.html --output final_presentation.pdf --zoom 1.8 --method playwright
```

### `evaluate`
Evaluate presentation quality using AI.

**Arguments:**
- `eval_folder`: Folder containing presentation.pdf and optionally paper.pdf
- `--output`: Output JSON file path (optional)
- `--model`: Claude model for evaluation (default: claude-3-5-sonnet-20241022)

**Example:**
```bash
python -m src.main evaluate my_presentation_folder/ --output results.json
```

### `pipeline`
Complete workflow: generate → convert → evaluate.

**Arguments:**
- `input`: Topic text or PDF file path/URL
- `--purpose`: Purpose of presentation
- `--theme`: Visual theme
- `--source-pdf`: Source PDF for evaluation (if input is topic)
- `--evaluate`: Run evaluation after generation
- `--output-dir`: Output directory
- `--zoom`: PDF zoom factor
- `--method`: Conversion method

**Example:**
```bash
python -m src.main pipeline "machine learning ethics" --purpose "academic seminar" --theme "modern contemporary" --evaluate --source-pdf ethics_paper.pdf
```

## Available Themes

- **professional blue**: Clean, professional theme with blue accents
- **clean minimalist**: Minimal design with subtle grays
- **bold high contrast**: High contrast theme for maximum impact
- **cool professional**: Cool tones for professional presentations
- **natural earth**: Earth tones for sustainability themes
- **muted morandi tones**: Soft, muted colors inspired by Morandi
- **modern contemporary**: Modern purple and gray combination
- **warm earth tones**: Warm oranges and browns for approachable feel
- **soft pastels**: Gentle pastels for personal or creative topics
- **academic**: Traditional academic presentation style

## File Structure

```
OpenCanvas/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── setup.py                      # Package setup configuration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── src/
│   ├── main.py                    # Main CLI interface
│   ├── config.py                  # Configuration management
│   ├── generators/
│   │   ├── router.py              # Generation routing
│   │   ├── topic_generator.py     # Topic-based generation
│   │   ├── pdf_generator.py       # PDF-based generation
│   │   └── base.py                # Base generator class
│   ├── conversion/
│   │   └── html_to_pdf.py         # HTML to PDF converter
│   ├── evaluation/
│   │   ├── evaluator.py           # Presentation evaluator
│   │   └── prompts.py             # Evaluation prompts
│   ├── shared/
│   │   ├── themes.py              # Theme definitions
│   │   └── html_utils.py          # HTML utilities
│   └── utils/
│       ├── logging.py             # Logging configuration
│       └── validation.py         # Input validation
├── tests/
│   ├── test_topics.py             # Topic generation tests
│   ├── test_pdfs.py               # PDF generation tests
│   └── test_conversion.py         # Conversion tests
└── examples/
    └── basic_usage.py             # Usage examples
```

## Features in Detail

### Topic-Based Generation
- **Knowledge Assessment**: Automatically determines if additional research is needed
- **Web Research**: Uses Brave Search API to gather authoritative sources
- **Source Credibility**: AI-powered ranking of search results
- **Content Synthesis**: Combines research with existing knowledge

### PDF-Based Generation
- **Academic Focus**: Optimized for research papers and academic content
- **LaTeX Support**: Mathematical formulas and equations
- **Mermaid Diagrams**: Process flows and system architecture
- **Citation Handling**: Proper attribution and references

### HTML to PDF Conversion
- **Multiple Methods**: Selenium and Playwright support
- **Zoom Control**: Adjustable PDF scaling (0.1x to 3.0x)
- **Slide Navigation**: Automatic slide detection and capture
- **Quality Optimization**: High-resolution output

### AI Evaluation
- **Visual Assessment**: Design, hierarchy, readability, balance
- **Content Analysis**: Structure, narrative, accuracy, coverage
- **Reference Comparison**: Accuracy against source materials
- **Comprehensive Scoring**: 1-5 scale with detailed reasoning

## Testing

Run the test suites:

```bash
# Topic generation tests
python tests/test_topics.py

# PDF generation tests  
python tests/test_pdfs.py

# Conversion tests
python tests/test_conversion.py

# All tests with pytest
pytest tests/
```

## Configuration

Environment variables in `.env`:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
BRAVE_API_KEY=your_brave_key
DEFAULT_THEME=professional blue
DEFAULT_PURPOSE=general presentation
OUTPUT_DIR=output
DEFAULT_ZOOM=1.2
DEFAULT_CONVERSION_METHOD=selenium
```

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Download ChromeDriver and add to PATH
   - Or use `playwright` method instead

2. **Brave Search API errors**
   - Check your API key and quota
   - Generation will work without it (no web research)

3. **PDF conversion fails**
   - Ensure HTML file has proper slide structure
   - Try different zoom factors
   - Check browser dependencies

4. **Evaluation requires both PDFs**
   - Place `presentation.pdf` and `paper.pdf` in eval folder
   - Reference-required evaluation needs source material

### Debug Mode

Enable verbose logging:
```bash
python -m src.main --verbose generate "your topic"
```

## Examples

See the `examples/` directory for:
- Basic usage patterns
- Advanced workflow examples
- Batch processing scripts
- Custom theme creation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request