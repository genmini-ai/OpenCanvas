# OpenCanvas Test Suite

This directory contains comprehensive tests for the OpenCanvas presentation generation system, including end-to-end pipeline tests and adversarial evaluation testing.

## Quick Start

```bash
# From root directory (recommended)
python run_tests.py light              # Quick validation
python run_tests.py topic              # Topic tests only
python run_tests.py pdf                # PDF tests only
python run_adversarial_eval_test.py    # Adversarial robustness testing

# From tests directory
cd tests
python run_e2e_tests.py light          # Quick validation
```

## Test Structure

### 📁 Test Files

- **`test_e2e_pipeline.py`** - Complete end-to-end pipeline tests
- **`test_adversarial_evaluation.py`** - Adversarial robustness evaluation tests
- **`test_topics.py`** - Topic-based generation tests
- **`test_pdfs.py`** - PDF-based generation tests  
- **`test_conversion.py`** - HTML to PDF conversion tests

### 🎯 E2E Test Suite

The main test suite (`test_e2e_pipeline.py`) includes:

#### **Topic-Based Tests (5 test cases)**
1. **Sustainable Energy Solutions** - Corporate presentation with natural earth theme
2. **AI in Healthcare** - Academic presentation with professional blue theme
3. **Quantum Computing Fundamentals** - Educational presentation with modern contemporary theme
4. **Climate Change Mitigation** - Conference talk with clean minimalist theme
5. **Blockchain Technology** - Pitch deck with bold high contrast theme

#### **PDF-Based Tests (5 arXiv papers)**
1. **Scaling Laws for Neural Language Models** - `arxiv:2505.20286`
2. **Chain-of-Thought Reasoning** - `arxiv:2410.17891`
3. **AI Safety and Alignment** - `arxiv:2502.02533`
4. **Transformer Architecture Analysis** - `arxiv:2310.13855`
5. **Large Language Model Training** - `arxiv:2307.08123`

### 🛡️ Adversarial Evaluation Tests

Tests the robustness of the presentation evaluation system by applying adversarial attacks to presentations and comparing evaluation scores.

#### **5 Adversarial Attacks**
1. **Beautiful Nonsense** - Replace scientific content with surrealist art references
2. **Fact Flip** - Invert factual claims and numerical values
3. **Logical Chaos** - Randomly shuffle slide order
4. **Swiss Cheese** - Randomly delete critical content  
5. **Gradual Decay** - Progressive quality degradation

#### **Test Structure**
- **Original**: 5 topic-based presentations with clean evaluations
- **Attacked**: 5 topics × 5 attacks = 25 attacked presentations  
- **Comparison**: Score differences to measure attack effectiveness

## Running Tests

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required API keys**:
   - `ANTHROPIC_API_KEY` - Required for generation
   - `GEMINI_API_KEY` - Default for evaluation (recommended)
   - `OPENAI_API_KEY` - Optional for GPT evaluation
   - `BRAVE_API_KEY` - Optional for enhanced research

### Quick Tests

#### Test Gemini Integration
```bash
python test_gemini_integration.py
```

#### Test Individual Components
```bash
# Topic generation tests
python -m pytest tests/test_topics.py -v

# PDF generation tests  
python -m pytest tests/test_pdfs.py -v

# Conversion tests
python -m pytest tests/test_conversion.py -v
```

### Full E2E Test Suite

#### Run Complete Suite
```bash
python run_e2e_tests.py
```

#### Run Specific Test Types
```bash
# Topic-based tests only
python run_e2e_tests.py topic

# PDF-based tests only
python run_e2e_tests.py pdf

# Full suite (default)
python run_e2e_tests.py full
```

#### Light Testing Mode (Fast)
For quick validation, use light mode which runs only 1 test per type:

```bash
# Light mode - full suite (2 tests total, ~5 minutes)
python run_e2e_tests.py light

# Light mode - topic tests only (1 test, ~2 minutes)
python run_e2e_tests.py topic light

# Light mode - PDF tests only (1 test, ~3 minutes)
python run_e2e_tests.py pdf light

# You can also combine arguments in any order
python run_e2e_tests.py light topic
```

#### Resume/Caching (Skip Existing)
The test suite automatically detects existing slides and skips generation for faster iteration:

```bash
# Normal run - will skip generation if slides exist
python run_e2e_tests.py light

# Force regeneration - ignores existing slides
python run_e2e_tests.py light force

# Force regeneration for specific test type
python run_e2e_tests.py topic force
python run_e2e_tests.py pdf force

# Combine all options
python run_e2e_tests.py topic light force
```

**How Caching Works:**
- Tests check for existing `presentation.html` and `presentation.pdf` in organized output directories
- If both files exist, generation and conversion stages are skipped
- Evaluation still runs (unless results already exist)
- Use `force` flag to regenerate everything from scratch

#### Using pytest
```bash
# Run all E2E tests
python -m pytest tests/test_e2e_pipeline.py -v

# Run specific test types
python -m pytest tests/test_e2e_pipeline.py::TestE2EPipeline::test_topic_based_e2e_individual -v
python -m pytest tests/test_e2e_pipeline.py::TestE2EPipeline::test_pdf_based_e2e_individual -v
```

### Adversarial Evaluation Testing

Tests the robustness of the presentation evaluation system by applying adversarial attacks.

#### Prerequisites
1. **Run topic-based tests first** to generate original presentations:
   ```bash
   python run_e2e_tests.py topic
   ```

2. **Evaluation API key configured** (Gemini by default):
   - Set `GEMINI_API_KEY` environment variable
   - Or configure in `src/opencanvas/config.py`

#### Run Adversarial Tests
```bash
# Use existing presentations (recommended)
cd ..  # Go back to root directory
python run_adversarial_eval_test.py

# Generate fresh presentations first
python run_adversarial_eval_test.py --regenerate

# Run only analysis (skip testing)
python run_adversarial_eval_test.py --analysis-only

# Custom directories
python run_adversarial_eval_test.py --output-dir custom_analysis

# Verbose logging
python run_adversarial_eval_test.py --verbose
```

#### Expected Results
- **🟢 HIGH robustness** (mean drop < 0.1): Evaluation is robust
- **🟡 MODERATE robustness** (mean drop 0.1-0.5): Some vulnerability  
- **🔴 LOW robustness** (mean drop > 0.5): Evaluation is vulnerable

#### Output Structure
```
test_output/adversarial_analysis/
├── adversarial_evaluation_results.json    # Complete test results
├── analysis_report.json                   # Statistical analysis
├── attacked_presentations/                # HTML files with attacks
└── attacked_evaluations/                  # Individual evaluation JSONs
```

## Test Pipeline Stages

Each E2E test runs through these stages:

### Topic-Based Pipeline
1. **📝 Generation** - Generate presentation from topic using TopicGenerator
2. **📄 Conversion** - Convert HTML to PDF using PresentationConverter
3. **📁 Organization** - Organize files using organized output structure
4. **🔍 Evaluation** - Evaluate presentation using PresentationEvaluator

### PDF-Based Pipeline
1. **📑 Generation** - Generate presentation from PDF using PDFGenerator
2. **📄 Conversion** - Convert HTML to PDF using PresentationConverter
3. **📥 Source Download** - Download original arXiv PDF for evaluation
4. **📁 Organization** - Organize files using organized output structure
5. **🔍 Evaluation** - Evaluate presentation with source PDF comparison

## Test Results

### Output Structure
Tests create organized output directories:
```
test_output/
├── test_1_sustainable_energy_solutions/
│   ├── slides/
│   │   ├── presentation.html
│   │   └── presentation.pdf
│   ├── evaluation/
│   │   └── evaluation_results.json
│   └── sources/
│       ├── source_content.txt
│       └── source.pdf
└── test_2_ai_in_healthcare/
    └── ...
```

### Results File
Detailed results are saved to `e2e_test_results.json`:
```json
{
  "full_suite": true,
  "topic_based": {
    "total_tests": 5,
    "passed": 5,
    "failed": 0,
    "results": { ... }
  },
  "pdf_based": {
    "total_tests": 5,
    "passed": 5,
    "failed": 0,
    "results": { ... }
  },
  "summary": {
    "total_tests": 10,
    "total_passed": 10,
    "total_failed": 0
  }
}
```

## Configuration

### Evaluation Providers

The test suite uses the default evaluation provider from your `.env` file:

```bash
# Gemini (default - fast and cost-effective)
EVALUATION_PROVIDER=gemini
EVALUATION_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_gemini_key

# Claude (high quality)
EVALUATION_PROVIDER=claude
EVALUATION_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_anthropic_key

# GPT (alternative)
EVALUATION_PROVIDER=gpt
EVALUATION_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_key
```

### Test Customization

You can modify test cases in `test_e2e_pipeline.py`:

- **`TOPIC_TEST_CASES`** - Add/modify topic-based test scenarios
- **`ARXIV_TEST_CASES`** - Add/modify PDF-based test scenarios

## Troubleshooting

### Common Issues

1. **API Key Missing**
   ```
   ❌ ANTHROPIC_API_KEY not provided
   ```
   **Solution**: Add API key to `.env` file

2. **Evaluation Skipped**
   ```
   stages.evaluation.status: "skipped"
   ```
   **Solution**: Add evaluation provider API key

3. **PDF Download Failed**
   ```
   stages.source_download.status: "failed"
   ```
   **Solution**: Check internet connection and arXiv availability

4. **Conversion Failed**
   ```
   stages.conversion.status: "failed"
   ```
   **Solution**: Install Playwright browsers: `playwright install chromium`

### Debug Mode

For detailed debugging, set log level:
```bash
export LOG_LEVEL=DEBUG
python run_e2e_tests.py
```

## Performance

### Expected Runtime

#### Full Mode (All Tests)
- **Topic-based test**: ~2-3 minutes per test
- **PDF-based test**: ~3-4 minutes per test (includes PDF download)
- **Full suite**: ~25-35 minutes total

#### Light Mode (1 Test Per Type)
- **Topic-based test**: ~2-3 minutes (1 test)
- **PDF-based test**: ~3-4 minutes (1 test)
- **Light suite**: ~5-7 minutes total

#### Cached Mode (Existing Slides)
- **Topic-based test**: ~30 seconds (evaluation only)
- **PDF-based test**: ~45 seconds (evaluation only)
- **Cached light suite**: ~1-2 minutes total

### Resource Usage
- **Storage**: ~50-100MB per test (temporary files)
- **Network**: ~10-20MB per PDF download
- **API calls**: ~5-10 calls per test (generation + evaluation)
- **Cached runs**: ~1-2 API calls per test (evaluation only)

## Contributing

### Adding New Tests

1. **Topic-based tests**: Add to `TOPIC_TEST_CASES` in `test_e2e_pipeline.py`
2. **PDF-based tests**: Add to `ARXIV_TEST_CASES` in `test_e2e_pipeline.py`
3. **Component tests**: Add to respective `test_*.py` files

### Test Guidelines

- Use descriptive test names
- Include variety in themes and purposes
- Test edge cases and error conditions
- Verify file existence and content quality
- Check evaluation scores are reasonable

## CI/CD Integration

The test suite can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: |
    python run_e2e_tests.py
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
``` 