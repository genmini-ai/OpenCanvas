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

# Evolution System - Autonomous presentation improvement
python test_evolution_unified_final.py  # Run complete autonomous evolution system

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

**Evolution System** (Autonomous Improvement):
- **Evolution System** (`src/opencanvas/evolution/core/evolution.py`): Main orchestrator for autonomous presentation quality improvement
- **Multi-Agent System** (`src/opencanvas/evolution/core/agents.py`): Reflection, improvement, and implementation agents
- **Auto Tool Implementation** (`src/opencanvas/evolution/core/tool_implementation.py`): Fully autonomous tool creation and deployment system
- **Evolved Router** (`src/opencanvas/evolution/core/evolved_router.py`): Enhanced generation router with evolved prompts and auto-generated tools
- **Prompt Evolution** (`src/opencanvas/evolution/core/prompts.py`): Dynamic prompt improvement based on evaluation results
- **Tools Manager** (`src/opencanvas/evolution/core/tools.py`): Tool discovery, specification, and lifecycle management

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

**Autonomous Evolution System**: ML-style self-improvement system that automatically:
- **Evaluates Current Performance**: Uses AI evaluation to identify quality weaknesses and improvement opportunities
- **Proposes Tools & Prompts**: Multi-agent system designs specific improvements (tools, prompt enhancements) based on evaluation gaps
- **Implements Tools Automatically**: 9-step pipeline generates, tests, and deploys Python tools without human intervention
- **Evolves Prompts**: Dynamically improves generation prompts based on evaluation feedback and performance data
- **Tracks Performance**: Measures tool effectiveness and maintains learning patterns for future iterations
- **Checkpoint System**: ML-style checkpoints with full experiment reproducibility and continuation capability
- **Resource-Constrained**: Only uses available APIs (Claude, GPT, Gemini, Brave Search) without requiring external service setup

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

**Standard Pipeline:**
1. **Generation**: Creates HTML slides from topic or PDF input
2. **Research** (if needed): Fetches additional information via Brave Search
3. **Conversion**: Renders HTML to PDF using browser automation
4. **Evaluation**: AI-powered quality assessment with scoring
5. **Organization**: Saves all outputs in structured directories

**Evolution Pipeline** (Autonomous Improvement):
1. **Generate**: Create test presentations using current best prompts and tools
2. **Evaluate**: AI evaluation with reference-required scoring for accuracy gaps
3. **Reflect**: Multi-agent analysis identifies specific weaknesses and improvement opportunities
4. **Improve**: Design targeted solutions (new tools, prompt enhancements) using reflection results
5. **Implement**: Automatically generate, test, and deploy improvements with 9-step validation pipeline
6. **Apply**: Integrate evolved prompts and auto-generated tools into production pipeline
7. **Track**: Measure performance improvements and learn from successful/failed patterns
8. **Checkpoint**: Save complete iteration state for reproducibility and continuation

### Testing Architecture

**E2E Test Suite** (`tests/test_e2e_pipeline.py`): Comprehensive testing of the full pipeline  
**Adversarial Testing** (`run_adversarial_eval_test.py`): Tests evaluation robustness with 5 attack methods  
**Individual Component Tests**: Separate test files for topics, PDFs, and conversion  
**API Testing** (`test_api.py`): REST API endpoint testing  
**Evolution Testing** (`test_evolution_unified_final.py`): Autonomous evolution system with ML-style unified logging

The testing system supports light mode for faster validation and force regeneration for comprehensive testing.

### Evolution System Details

**Architecture**: ML-inspired autonomous improvement system with multi-agent coordination  
**Goal**: Systematically improve presentation quality through iterative tool creation and prompt evolution  
**Approach**: "Offline RL" style learning with complete observability and checkpoint-based training  

**Key Components**:
- **Multi-Agent System**: Reflection, improvement, and implementation agents working in coordination
- **Automatic Tool Implementation**: 9-step pipeline (spec → code → test → performance → deploy)  
- **Evolved Generation Router**: Production router enhanced with evolved prompts and auto-generated tools
- **Performance Tracking**: Before/after measurement with learning from successful patterns
- **Checkpoint Management**: ML-style experiment tracking with full reproducibility

**Tool Creation Guidelines**:
- **Resource Constraints**: Auto-generated tools can ONLY use Claude/GPT/Gemini APIs, Brave Search, Python stdlib, and configured services
- **YAML Prompts**: All LLM prompts for tool generation use YAML format (NOT JSON) to avoid f-string nesting issues
- **Centralized Prompts**: Tool generation prompts stored in `src/opencanvas/evolution/prompts/tool_generation.yaml`
- **F-String Safety**: Generated tools are instructed to avoid nested f-strings and use .format() for complex string building
- **Template-Based Approach**: Tools that generate LLM prompts use template-based string formatting to prevent syntax errors
- **Autonomous Pipeline**: Tools are generated, tested, and deployed automatically without human intervention (unless explicitly configured)
- **Learning System**: Failed and successful tool patterns are tracked to improve future tool creation

**Output Structure**: 
```
evolution_runs/experiment_name/
├── config.json                    # Experiment configuration
├── training.log                   # Complete evolution log (288+ entries)
├── iteration_001/                 # Checkpoint with reusable state
├── summary.json                   # Final results and metrics
└── auto_generated_tools/          # Deployed tools integrated into pipeline
```

## Important File Locations

**Core System**:
- **Main CLI**: `src/opencanvas/main.py` - Entry point with all command handling
- **Configuration**: `src/opencanvas/config.py` - Environment variable management and validation
- **Themes**: `src/opencanvas/shared/themes.py` - Visual theme definitions
- **Evaluation Prompts**: `src/opencanvas/evaluation/prompts.py` - AI evaluation prompt templates
- **Test Runner**: `run_tests.py` - Convenient wrapper for running E2E tests
- **API Documentation**: Available at `/docs` when API server is running

**Evolution System**:
- **Evolution Orchestrator**: `src/opencanvas/evolution/core/evolution.py` - Main evolution system coordination
- **Multi-Agent System**: `src/opencanvas/evolution/core/agents.py` - Reflection and improvement agents
- **Tool Implementation**: `src/opencanvas/evolution/core/tool_implementation.py` - Autonomous tool creation pipeline
- **Evolved Router**: `src/opencanvas/evolution/core/evolved_router.py` - Enhanced generation with evolved components
- **Prompt Evolution**: `src/opencanvas/evolution/core/prompts.py` - Dynamic prompt improvement system
- **Tools Manager**: `src/opencanvas/evolution/core/tools.py` - Tool lifecycle management
- **Tool Generation Prompts**: `src/opencanvas/evolution/prompts/tool_generation.yaml` - Centralized YAML prompts for tool creation
- **Evolution Test**: `test_evolution_unified_final.py` - Complete autonomous evolution demonstration

## Required API Keys

At minimum, one evaluation provider key is required:
- **ANTHROPIC_API_KEY**: For generation (always required) and Claude evaluation
- **GEMINI_API_KEY**: For Gemini evaluation (default provider)
- **OPENAI_API_KEY**: For GPT evaluation
- **BRAVE_API_KEY**: Optional for web research enhancement