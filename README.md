# OpenCanvas

OpenCanvas is a comprehensive presentation generation and evaluation system that creates HTML slide decks from topics or PDF documents, converts them to PDF format, and evaluates their quality using AI.

## TODO
- [ ] add source saving while generating, to streamline eval {pdf: paper.pdf, topic: blog.txt}
    - [ ] fix full pipeline run
    - [ ] try self evolution
- [ ] add GPT model for eval
- [ ] improve visual layout and component (image, diagram, etc.)
- [ ] improve template design taste

## Features

🎨 **Dual Input Support**: Generate presentations from either text topics or PDF documents  
🔄 **HTML to PDF Conversion**: Convert generated HTML slides to PDF format  
📊 **AI-Powered Evaluation**: Comprehensive presentation quality assessment  
🎯 **Smart Research**: Automatic web research for insufficient knowledge topics  
🎨 **Multiple Themes**: Professional themes for different presentation contexts  
🔧 **Complete Pipeline**: End-to-end workflow from input to evaluation  
🚀 **REST API**: Full RESTful API for programmatic access  
📚 **Interactive Docs**: Auto-generated API documentation  

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
```

2. **Install dependencies**

Choose one of the following installation options:

**Option A (recommended): directly install this package (CLI)**
```
pip install -e .
```

**Option B: Complete installation (CLI + API)**
```bash
pip install -r requirements-all.txt
```

**Option C: Core functionality only (CLI)**
```bash
pip install -r requirements.txt
```

**Option D: API only (for microservices)**
```bash
pip install -r requirements-api.txt
```

**Option E: Install separately**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install API dependencies (if needed)
pip install -r requirements-api.txt
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
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- `ANTHROPIC_API_KEY`: For Claude AI (required)
- `BRAVE_API_KEY`: For web search (optional, but recommended)
- `OPENAI_API_KEY`: For GPT evaluation (optional)

## Quick Start

### CLI Usage

#### Generate from Topic
```bash
opencanvas generate "AI in healthcare applications" --purpose "academic presentation" --theme "clean minimalist"
```

#### Generate from PDF
```bash
opencanvas generate "https://arxiv.org/pdf/2505.20286" --purpose "research seminar"
```

#### Convert HTML to PDF
```bash
opencanvas convert output/slides.html --output presentation.pdf --zoom 1.5
```

#### Evaluate Presentation
```bash
opencanvas evaluate evaluation_folder/
```

#### Full Pipeline
```bash
# Complete workflow with organized outputs
opencanvas pipeline "quantum computing" --purpose "conference talk" --evaluate --zoom 1.3

# Pipeline with source PDF for evaluation
opencanvas pipeline "quantum computing" --source-pdf paper.pdf --evaluate
```

## Organized Output Structure

OpenCanvas now creates organized directory structures for all outputs:

```
output/
└── quantum_computing_20241128_120000/
    ├── slides/
    │   ├── quantum_computing_slides.html
    │   └── quantum_computing_presentation.pdf
    ├── evaluation/
    │   └── quantum_computing_evaluation.json
    └── sources/
        ├── quantum_computing_source_blog.txt    # For topic-based generation
        └── quantum_computing_source.pdf         # For PDF-based generation
```

### Benefits of Organized Structure

- **Topic-based naming**: Files use meaningful names derived from your topic (max 5 words)
- **Source storage**: Original content is saved for reference-required evaluation
- **Complete pipeline**: All outputs (.html, .pdf, .json) in one organized folder
- **Easy evaluation**: Source content is automatically available for comprehensive evaluation

### API Usage

#### Start the API Server
```bash
# Using the standalone server script
python server.py

# Or using the main CLI
opencanvas api

# Or with custom settings
python server.py --host 0.0.0.0 --port 8080 --reload
```

#### Access API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

#### Example API Calls

**Generate a presentation:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "input_source": "Machine learning in healthcare",
       "purpose": "academic presentation",
       "theme": "professional blue"
     }'
```

**Convert to PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/convert" \
     -H "Content-Type: application/json" \
     -d '{
       "html_file": "output/presentation.html",
       "zoom_factor": 1.2
     }'
```

**Run complete pipeline:**
```bash
curl -X POST "http://localhost:8000/api/v1/pipeline" \
     -H "Content-Type: application/json" \
     -d '{
       "input_source": "Quantum computing applications",
       "evaluate": true
     }'
```

For complete API documentation, see [API_README.md](API_README.md).

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | - | Claude API key for generation |
| `BRAVE_API_KEY` | ❌ | - | Brave Search API for web research |
| `OPENAI_API_KEY` | ❌ | - | OpenAI API key for GPT evaluation |
| `EVALUATION_PROVIDER` | ❌ | `claude` | Evaluation provider: `claude` or `gpt` |
| `EVALUATION_MODEL` | ❌ | `claude-3-5-sonnet-20241022` | Model for evaluation |
| `DEFAULT_THEME` | ❌ | `professional blue` | Default presentation theme |
| `DEFAULT_ZOOM` | ❌ | `1.2` | PDF zoom factor |
| `DEFAULT_CONVERSION_METHOD` | ❌ | `playwright` | PDF conversion method |

### Available Themes

- `professional blue` - Clean, corporate-friendly design
- `clean minimalist` - Simple, elegant layout
- `natural earth` - Warm, earth-tone colors
- `modern contemporary` - Trendy, cutting-edge design
- `warm earth tones` - Cozy, approachable feel
- `bold high contrast` - High-impact, attention-grabbing

### Available Models

**Claude Models:**
- `claude-3-5-sonnet-20241022` (recommended for evaluation)
- `claude-3-7-sonnet-20250219` (good for generation)
- `claude-sonnet-4-20250514` (latest, premium)

**GPT Models:**
- `gpt-4o` (best quality, higher cost)
- `gpt-4o-mini` (good balance, recommended)
- `gpt-4-turbo` (fast, good quality)

## Troubleshooting

### Common Issues

**1. "opencanvas command not found"**
```bash
# Make sure you installed with -e flag
pip install -e .

# Check if it's in your PATH
which opencanvas
```

**2. "ANTHROPIC_API_KEY is required"**
```bash
# Check your .env file exists and has the key
cat .env | grep ANTHROPIC_API_KEY

# Make sure .env is in the same directory where you run opencanvas
```

**3. "Model 'gpt-4.1' not found" with Claude provider**
```bash
# This happens when EVALUATION_MODEL doesn't match EVALUATION_PROVIDER
# Fix in .env:
EVALUATION_PROVIDER=claude
EVALUATION_MODEL=claude-3-5-sonnet-20241022

# Or use GPT:
EVALUATION_PROVIDER=gpt  
EVALUATION_MODEL=gpt-4o-mini
```

**4. "Playwright not available"**
```bash
# Install Playwright browser
playwright install chromium

# Or use selenium method
opencanvas convert slides.html --method selenium
```

**5. Web research not working**
```bash
# Add BRAVE_API_KEY to .env for web research
# Without it, generation uses only Claude's knowledge
BRAVE_API_KEY=your-brave-key-here
```

### Validation Commands

```bash
# Test your configuration
python -c "from opencanvas.config import Config; Config.validate(); print('✅ Configuration valid')"

# Test API keys
opencanvas generate "test topic" --output-dir test_output

# Check available models
python -c "
from opencanvas.config import Config
print('Claude Model:', Config.CLAUDE_MODEL)
print('Evaluation Model:', Config.EVALUATION_MODEL)
print('Evaluation Provider:', Config.EVALUATION_PROVIDER)
"
```

## Available Commands

### CLI Commands

#### `generate`
Generate presentation from topic or PDF source.

**Arguments:**
- `input`: Topic text or PDF file path/URL
- `--purpose`: Purpose of presentation (default: "general presentation")
- `--theme`: Visual theme (default: "professional blue")
- `--output-dir`: Output directory (default: "output")

**Example:**
```bash
opencanvas generate "sustainable energy solutions" --purpose "corporate presentation" --theme "natural earth"
```

#### `convert`
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
opencanvas convert slides.html --output final_presentation.pdf --zoom 1.8 --method playwright
```

#### `evaluate`
Evaluate presentation quality using AI.

**Arguments:**
- `eval_folder`: Folder containing presentation.pdf and optionally paper.pdf
- `--output`: Output JSON file path (optional)
- `--model`: Claude model for evaluation (default: claude-3-5-sonnet-20241022)

**Example:**
```bash
opencanvas evaluate my_presentation_folder/ --output results.json
```

#### `pipeline`
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
opencanvas pipeline "machine learning ethics" --purpose "academic seminar" --theme "modern contemporary" --evaluate --source-pdf ethics_paper.pdf
```

#### `api`
Start the REST API server.

**Arguments:**
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development
- `--log-level`: Log level (default: info)
- `--workers`: Number of worker processes (default: 1)

**Example:**
```bash
opencanvas api --host 0.0.0.0 --port 8080 --reload
```

### API Endpoints

#### Core Endpoints
- `POST /api/v1/generate` - Generate presentation from topic or PDF
- `POST /api/v1/convert` - Convert HTML to PDF
- `POST /api/v1/evaluate` - Evaluate presentation quality
- `POST /api/v1/pipeline` - Run complete pipeline workflow

#### Configuration Endpoints
- `GET /api/v1/themes` - Get available themes
- `GET /api/v1/purposes` - Get available purposes
- `GET /api/v1/conversion-methods` - Get conversion methods

#### System Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/files/{file_path}` - Download generated files

For detailed API documentation, see [API_README.md](API_README.md).

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
├── API_README.md                  # API documentation
├── requirements.txt               # Core dependencies only
├── requirements-api.txt           # API dependencies only
├── requirements-all.txt           # All dependencies
├── setup.py                      # Package setup configuration
├── server.py                     # Standalone API server
├── test_api.py                   # API test script
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── src/
│   ├── main.py                    # Main CLI interface
│   ├── config.py                  # Configuration management
│   ├── api/                       # API package
│   │   ├── __init__.py            # API package init
│   │   ├── app.py                 # FastAPI application
│   │   ├── models.py              # Pydantic models
│   │   ├── routes.py              # API route handlers
│   │   └── services.py            # Service layer
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

### REST API
- **Full CRUD Operations**: All functionality available via HTTP
- **Async Processing**: Non-blocking operations for better performance
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger docs
- **Error Handling**: Consistent error responses and status codes
- **File Management**: Download generated files via API

## Testing

### CLI Testing
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

### API Testing
Test the API functionality:

```bash
# Start the API server
python server.py

# In another terminal, run the test suite
python test_api.py
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
EVALUATION_MODEL=claude-3-5-sonnet-20241022
```

## Production Deployment

### API Server Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-all.txt .
RUN pip install -r requirements-all.txt
COPY . .
EXPOSE 8000
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using Docker Compose
```yaml
version: '3.8'
services:
  opencanvas-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    volumes:
      - ./output:/app/output
```

### Microservices Deployment

For microservices architecture, you can deploy the API separately:

```dockerfile
# API-only Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt
COPY src/api/ ./src/api/
COPY src/config.py ./src/config.py
COPY src/utils/ ./src/utils/
EXPOSE 8000
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
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

5. **API not starting**
   - Check if FastAPI dependencies are installed: `pip install -r requirements-api.txt`
   - Verify environment variables are set
   - Check if port is already in use

6. **Missing dependencies**
   - For CLI only: `pip install -r requirements.txt`
   - For API only: `pip install -r requirements-api.txt`
   - For everything: `pip install -r requirements-all.txt`

### Debug Mode

Enable verbose logging:
```bash
# CLI
opencanvas --verbose generate "your topic"

# API
python server.py --log-level debug --reload
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
