# Visual Adversarial Testing Framework

## Overview

This framework tests multiple visual evaluation prompts against adversarial attacks to identify the most robust and discriminative prompt for presentation quality assessment.

## Problem Statement

The current visual evaluation system exhibits systematic misalignment:
- Rewards oversized fonts (6rem+) as "more readable"
- Cannot distinguish professional restraint from amateur excess
- Scores chaotic designs higher than clean ones
- Misses fundamental design violations

## Solution Approach

1. **Multiple Prompt Candidates**: 5 different evaluation prompts, each addressing specific issues
2. **Visual Adversarial Attacks**: 6 attack types generated using Claude
3. **Statistical Analysis**: Data-driven selection without hard-coded thresholds
4. **Automated Selection**: Best prompt chosen based on composite alignment score

## Components

### 1. Visual Evaluation Prompts (`src/opencanvas/evaluation/visual_eval_prompts.py`)
- **V1 Original**: Current production baseline
- **V2 Restraint**: Emphasizes design restraint and sophistication
- **V3 Cognitive**: Focuses on cognitive load management
- **V4 Modern**: Uses modern TED-style design principles
- **V5 Hybrid**: Balanced approach with explicit penalties

### 2. Adversarial Attack Generator (`examples/visual_adversarial_generator.py`)
Generates 6 types of visual attacks using Claude:
- **Font Gigantism**: Titles at 6rem+, body at 3rem+
- **Color Chaos**: 8+ bright colors, neon combinations
- **Information Overload**: 200+ words per slide
- **Decoration Disaster**: Excessive shadows, borders, effects
- **Hierarchy Anarchy**: Everything same size and bold
- **White Space Elimination**: Zero margins and padding

### 3. Statistical Tester (`examples/visual_adversarial_tester.py`)
Evaluates all prompts and calculates:
- **Cohen's d**: Effect size between good/bad distributions
- **ROC-AUC**: Classification accuracy
- **Mann-Whitney U**: Statistical significance
- **Attack Sensitivity**: Average score degradation
- **Consistency Metrics**: Scoring stability
- **Composite Alignment Score**: Weighted combination

## Usage

### Quick Start (Full Pipeline)
```bash
# Run complete pipeline with default settings
python examples/run_visual_adversarial_test.py --mode full
```

### Step-by-Step Execution

#### 1. Generate Adversarial Attacks
```bash
# Generate attacks from evolution run slides
python examples/visual_adversarial_generator.py \
    --source evolution_runs/pdf_tracked_evolution_20250826_102641 \
    --output test_output/visual_adversarial_testing
```

#### 2. Test All Prompts
```bash
# Evaluate all prompt candidates
python examples/visual_adversarial_tester.py \
    --test-dir test_output/visual_adversarial_testing
```

### Advanced Options
```bash
# Skip PDF conversion for faster testing
python examples/run_visual_adversarial_test.py --mode full --skip-pdf

# Only generate attacks (no evaluation)
python examples/run_visual_adversarial_test.py --mode generate

# Only run evaluation (attacks already generated)
python examples/run_visual_adversarial_test.py --mode test
```

## Output Structure

```
test_output/visual_adversarial_testing/
├── original_slides/           # Clean presentations
├── adversarial_attacks/       # Attack variants
│   ├── font_gigantism/
│   ├── color_chaos/
│   ├── information_overload/
│   ├── decoration_disaster/
│   ├── hierarchy_anarchy/
│   └── white_space_elimination/
├── pdf_conversions/           # PDF versions
├── evaluation_results/
│   ├── raw_scores.json       # All evaluation scores
│   ├── statistical_metrics.json
│   ├── alignment_scores.json # Final prompt rankings
│   ├── analysis_report.md    # Detailed analysis
│   └── visualizations/
│       ├── distributions.png # Score distributions
│       ├── metrics_radar.png # Performance comparison
│       └── alignment_scores.png
└── generation_metadata.json
```

## Statistical Metrics Explained

### Effect Size (Cohen's d)
- Measures separation between original and attacked distributions
- d > 0.8 = large effect (good discrimination)
- Formula: `(mean_original - mean_attacked) / pooled_std`

### ROC-AUC Score
- Area under receiver operating characteristic curve
- 1.0 = perfect classification, 0.5 = random
- Measures ability to distinguish good from bad

### Attack Sensitivity
- Percentage score degradation on attacked slides
- Higher = more sensitive to design problems
- Formula: `(original_score - attacked_score) / original_score`

### Composite Alignment Score
Weighted combination of all metrics:
- 25% Effect size (separation)
- 25% ROC-AUC (classification)
- 20% Attack sensitivity
- 10% Consistency
- 10% Mean gap
- 5% Dynamic range
- 5% Non-overlap

## Interpreting Results

The analysis report shows:
1. **Best Performing Prompt**: Highest composite alignment score
2. **Statistical Significance**: p-values for each prompt
3. **Per-Attack Performance**: How each prompt handles specific attacks
4. **Visualizations**: Distribution plots and metric comparisons

### Example Output
```
Best Performing Prompt: v5_hybrid
Alignment Score: 0.823

Key Metrics:
- Cohen's d: 2.34 (strong separation)
- ROC-AUC: 0.91 (excellent classification)
- Attack Sensitivity: 45% average degradation
- All attacks scored <2.5 (correctly identified)
```

## Requirements

- Python 3.8+
- Claude API key (for attack generation)
- Evaluation API key (Claude/GPT/Gemini)
- Dependencies: `pip install -r requirements.txt`

## Configuration

Set environment variables in `.env`:
```bash
ANTHROPIC_API_KEY=your_key_here  # For attack generation
EVALUATION_PROVIDER=gemini       # or claude/gpt
GEMINI_API_KEY=your_key_here    # For evaluation
```

## Troubleshooting

### No slides found
- Check source evolution run path exists
- Verify iteration_5 contains HTML files

### API errors
- Verify API keys are set correctly
- Check rate limits and quotas

### Low discrimination scores
- Ensure attacks are being applied correctly
- Verify HTML content is properly modified
- Check evaluation API is returning valid scores

## Next Steps

1. **Production Integration**: Replace current prompt with best performer
2. **Continuous Monitoring**: Regular testing against new attacks
3. **Prompt Evolution**: Use insights to create even better prompts
4. **Human Validation**: Correlate with human design assessments