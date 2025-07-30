# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
pip install -e .                    # Recommended: CLI + core functionality
pip install -r requirements-all.txt # Complete installation (CLI + API)
pip install -r requirements.txt     # Core functionality only
pip install -r requirements-api.txt # API dependencies only

# Install browser drivers for PDF conversion
playwright install chromium

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# CLI Usage
opencanvas generate "AI in healthcare" --purpose "academic presentation" --theme "clean minimalist"
opencanvas convert output/slides.html --output presentation.pdf --zoom 1.5
opencanvas evaluate evaluation_folder/
opencanvas pipeline "quantum computing" --purpose "conference talk" --evaluate

# Start API server
opencanvas api --host 0.0.0.0 --port 8000 --reload

# Run tests
python run_tests.py                 # Full E2E test suite
python run_tests.py light           # Light mode (faster)
python run_tests.py topic           # Topic tests only
python run_tests.py pdf             # PDF tests only
python run_tests.py force           # Force regenerate all files

# Adversarial evaluation testing
python run_adversarial_eval_test.py
python run_adversarial_eval_test.py --regenerate

# Validate configuration
python -c "from opencanvas.config import Config; Config.validate(); print('✅ Configuration valid')"
```

## Project Architecture

This is a Python-based presentation generation and evaluation system with both CLI and REST API interfaces:

**Core Components:**
- **CLI Interface** (`src/opencanvas/main.py`): Primary command-line interface with `generate`, `convert`, `evaluate`, `pipeline`, and `api` commands
- **Generation Router** (`src/opencanvas/generators/router.py`): Routes between topic-based and PDF-based generation
- **Topic Generator** (`src/opencanvas/generators/topic_generator.py`): Creates presentations from text topics with optional web research
- **PDF Generator** (`src/opencanvas/generators/pdf_generator.py`): Extracts and converts PDF content to presentations
- **HTML-to-PDF Converter** (`src/opencanvas/conversion/html_to_pdf.py`): Converts generated HTML slides to PDF using Selenium/Playwright
- **AI Evaluator** (`src/opencanvas/evaluation/evaluator.py`): Evaluates presentation quality using Claude, GPT, or Gemini models

**API Layer:**
- **FastAPI Application** (`src/api/app.py`): REST API with auto-generated documentation
- **API Routes** (`src/api/routes.py`): Endpoints for generation, conversion, evaluation, and pipeline operations
- **Pydantic Models** (`src/api/models.py`): Request/response schemas

### Key Features

**Dual Input Support**: Generate from either text topics or PDF documents  
**Smart Research**: Automatic web research using Brave Search API when knowledge is insufficient  
**Multi-Provider Evaluation**: Support for Claude, GPT, and Gemini evaluation models  
**Organized Output Structure**: Creates timestamped folders with slides/, evaluation/, and sources/ subdirectories  
**Multiple Themes**: Professional themes defined in `src/opencanvas/shared/themes.py`  
**Comprehensive Testing**: E2E test suite with adversarial evaluation testing

### Configuration Management

**Environment Variables** (`.env`):
- `ANTHROPIC_API_KEY`: Required for Claude models
- `OPENAI_API_KEY`: Required for GPT evaluation
- `GEMINI_API_KEY`: Required for Gemini evaluation (default provider)
- `BRAVE_API_KEY`: Optional for web research
- `EVALUATION_PROVIDER`: claude/gpt/gemini (default: gemini)
- `EVALUATION_MODEL`: Model name matching provider
- `DEFAULT_THEME`: Presentation theme (default: professional blue)
- `DEFAULT_ZOOM`: PDF zoom factor (default: 1.2)

**Smart Model Validation**: Config class automatically validates model/provider combinations and provides sensible defaults.

### Pipeline Workflow

1. **Generation**: Creates HTML slides from topic or PDF input
2. **Research** (if needed): Fetches additional information via Brave Search
3. **Conversion**: Renders HTML to PDF using browser automation
4. **Evaluation**: AI-powered quality assessment with scoring
5. **Organization**: Saves all outputs in structured directories

### Testing Architecture

**E2E Test Suite** (`tests/test_e2e_pipeline.py`): Comprehensive testing of the full pipeline  
**Adversarial Testing** (`run_adversarial_eval_test.py`): Tests evaluation robustness with 5 attack methods  
**Individual Component Tests**: Separate test files for topics, PDFs, and conversion  
**API Testing** (`test_api.py`): REST API endpoint testing

The testing system supports light mode for faster validation and force regeneration for comprehensive testing.

## Important File Locations

- **Main CLI**: `src/opencanvas/main.py` - Entry point with all command handling
- **Configuration**: `src/opencanvas/config.py` - Environment variable management and validation
- **Themes**: `src/opencanvas/shared/themes.py` - Visual theme definitions
- **Evaluation Prompts**: `src/opencanvas/evaluation/prompts.py` - AI evaluation prompt templates
- **Test Runner**: `run_tests.py` - Convenient wrapper for running E2E tests
- **API Documentation**: Available at `/docs` when API server is running

## Required API Keys

At minimum, one evaluation provider key is required:
- **ANTHROPIC_API_KEY**: For generation (always required) and Claude evaluation
- **GEMINI_API_KEY**: For Gemini evaluation (default provider)
- **OPENAI_API_KEY**: For GPT evaluation
- **BRAVE_API_KEY**: Optional for web research enhancement