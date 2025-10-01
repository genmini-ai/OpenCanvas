# Evolution System

OpenCanvas includes an autonomous improvement system that learns from evaluation results and evolves its capabilities over time.

## Overview

The evolution system is an ML-inspired self-improvement framework that automatically:
- **Evaluates** current presentation quality
- **Reflects** on weaknesses and opportunities
- **Designs** targeted improvements (prompts and tools)
- **Implements** changes autonomously
- **Tracks** performance over iterations

Think of it as "offline RL for presentation generation" - a system that learns from feedback without requiring external reinforcement.

## Architecture

### Core Components

```
src/opencanvas/evolution/
├── core/
│   ├── evolution.py              # Main orchestrator
│   ├── agents.py                 # Multi-agent system
│   ├── prompts.py                # Prompt version management
│   ├── tools.py                  # Tool discovery & management
│   ├── tool_implementation.py    # Autonomous tool creation
│   └── evolved_router.py         # Enhanced generation router
└── config/
    ├── agent_prompts.py          # Agent system prompts
    └── tools_specs.py            # Tool specifications
```

### Agent System

**1. Reflection Agent**
- Analyzes evaluation results across quality dimensions
- Identifies systematic weakness patterns
- Calculates improvement potential

**2. Improvement Agent**
- Designs specific targeted improvements
- Prioritizes by impact vs complexity
- Creates detailed specifications

**3. Implementation Agent**
- Converts improvements to deployable artifacts
- Generates and tests new tools
- Updates prompts based on feedback

**4. Orchestrator Agent**
- Coordinates multi-agent workflow
- Manages iteration checkpoints
- Validates improvements

## How It Works

### Evolution Cycle

```
┌─────────────────────────────────────────┐
│ 1. Generate Test Presentations         │
│    - Use current best prompts/tools    │
│    - Multiple topics for coverage      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 2. Evaluate Quality                     │
│    - Visual design assessment           │
│    - Content structure analysis         │
│    - Reference accuracy check           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 3. Reflect on Weaknesses                │
│    - Identify patterns in low scores    │
│    - Calculate improvement opportunities │
│    - Prioritize areas for enhancement   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 4. Design Improvements                  │
│    - Prompt enhancements                │
│    - New tool specifications            │
│    - Expected impact estimates          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 5. Implement Changes                    │
│    - Evolve prompts with feedback       │
│    - Generate and test new tools        │
│    - Validate improvements              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ 6. Track Performance                    │
│    - Measure before/after scores        │
│    - Log successful patterns            │
│    - Update checkpoints                 │
└──────────────┬──────────────────────────┘
               │
               └──────► Next Iteration
```

### Checkpoint System

Like ML training, evolution uses checkpoints for reproducibility:

```
evolution_runs/experiment_name/
├── config.json                    # Experiment configuration
├── training.log                   # Complete evolution log
├── evolution/
│   ├── iteration_1/
│   │   ├── evaluation_results.json
│   │   └── presentations/
│   ├── iteration_2/
│   │   ├── evaluation_results.json
│   │   └── presentations/
│   └── evolved_prompts/
│       ├── generation_prompt_v1.txt
│       ├── generation_prompt_v2.txt
│       └── ...
├── summary.json                   # Final results
└── auto_generated_tools/          # Deployed tools
```

## Usage

### Basic Evolution Run

```bash
# Run evolution with default settings
opencanvas evolve --max-iterations 3 --improvement-threshold 0.15
```

### Custom Topics

```bash
# Evolve on specific topics
opencanvas evolve --topics "AI,healthcare,quantum computing" --max-iterations 5
```

### Resume from Checkpoint

```bash
# Continue from previous run
opencanvas evolve --resume evolution_runs/my_experiment --start-iteration 4
```

### Programmatic Usage

```python
from opencanvas.evolution.core.evolution import EvolutionSystem

# Initialize
system = EvolutionSystem(
    output_dir="evolution_output",
    max_iterations=3,
    improvement_threshold=0.2
)

# Run evolution
results = system.run_evolution_cycle()

# Access evolved prompts
from opencanvas.evolution.core.prompts import PromptManager
prompt_manager = PromptManager()
best_prompts = prompt_manager.get_prompts(iteration=results['best_iteration'])
```

## Tool Creation

### Autonomous Tool Generation

The system can automatically create new tools when prompt improvements aren't sufficient:

**9-Step Pipeline:**
1. **Specification** - Design tool API and interface
2. **Code Generation** - Create Python implementation
3. **Static Analysis** - Check for syntax errors
4. **Unit Tests** - Generate and run tests
5. **Integration Tests** - Test with real scenarios
6. **Performance Check** - Measure speed and accuracy
7. **Documentation** - Auto-generate usage docs
8. **Deployment** - Install in production pipeline
9. **Monitoring** - Track effectiveness

### Resource Constraints

Auto-generated tools can **only** use:
- Claude, GPT, Gemini APIs
- Brave Search API
- Python standard library
- Configured services (no external service setup)

### Tool Registry

```python
# View available tools
from opencanvas.evolution.core.tools import ToolsManager

manager = ToolsManager()
tools = manager.discover_tools()

for tool in tools:
    print(f"{tool.name}: {tool.description}")
    print(f"  Success rate: {tool.success_rate}")
    print(f"  Avg latency: {tool.avg_latency}s")
```

## Prompt Evolution

### Version Management

Prompts are versioned like code:

```
evolution_prompts/
├── iteration_001/
│   ├── generation_prompt.txt
│   └── metadata.json
├── iteration_002/
│   ├── generation_prompt.txt
│   └── metadata.json
└── current -> iteration_002/
```

### A/B Testing

```python
# Compare prompt versions
from opencanvas.evolution.core.prompts import PromptManager

pm = PromptManager()

# Test baseline vs evolved
results_v0 = generate_with_prompts(pm.get_prompts(iteration=0))
results_v2 = generate_with_prompts(pm.get_prompts(iteration=2))

# Compare scores
print(f"Baseline: {results_v0['overall_score']}")
print(f"Evolved:  {results_v2['overall_score']}")
```

## Performance Tracking

### Metrics Tracked

- **Visual Quality**: Design, layout, readability
- **Content Quality**: Structure, narrative, coverage
- **Accuracy**: Alignment with source material
- **Tool Performance**: Success rate, latency
- **System Reliability**: Agent success rates

### Example Results

```
Iteration 1 → 2:
  Visual:  3.2 → 4.1 (+0.9)
  Content: 3.5 → 4.3 (+0.8)
  Overall: 3.4 → 4.2 (+0.8)

Tools Created: 3
  - CitationEnhancer (success: 87%)
  - VisualBalancer (success: 92%)
  - NarrativeFlow (success: 79%)
```

## Best Practices

### 1. Start Small
- Begin with 2-3 iterations
- Use small test topic set
- Validate improvements before scaling

### 2. Monitor Checkpoints
- Review evolution logs regularly
- Check for regression
- Validate tool performance

### 3. Topic Diversity
- Use varied topics for evolution
- Include edge cases
- Test on production-like content

### 4. Threshold Tuning
- Lower threshold (0.1): More iterations, incremental gains
- Higher threshold (0.3): Fewer iterations, significant improvements only

### 5. Resource Management
- Evolution requires API credits
- Each iteration = multiple generation + evaluation calls
- Budget accordingly

## Troubleshooting

### Low Improvement

**Symptoms:** Scores don't improve across iterations

**Solutions:**
- Lower improvement threshold
- Increase topic diversity
- Check evaluation consistency
- Review reflection analysis

### Tool Creation Failures

**Symptoms:** Tools fail validation pipeline

**Solutions:**
- Check API keys are valid
- Verify resource constraints
- Review tool specifications
- Check implementation logs

### Checkpoint Issues

**Symptoms:** Can't resume from checkpoint

**Solutions:**
- Verify config.json exists
- Check directory permissions
- Ensure compatible version
- Review training.log for errors

## Advanced Topics

### Custom Agents

Extend the agent system:

```python
from opencanvas.evolution.core.agents import EvolutionAgent

class CustomReflectionAgent(EvolutionAgent):
    def reflect(self, evaluation_results):
        # Custom reflection logic
        pass
```

### Custom Evaluation Metrics

Add domain-specific quality measures:

```python
from opencanvas.evaluation.evaluator import PresentationEvaluator

class CustomEvaluator(PresentationEvaluator):
    def evaluate_custom_dimension(self, presentation):
        # Custom evaluation logic
        pass
```

### Integration with CI/CD

```yaml
# .github/workflows/evolution.yml
name: Weekly Evolution
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  evolve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evolution
        run: |
          opencanvas evolve --max-iterations 2
          git add evolution_runs/
          git commit -m "Auto: Evolution checkpoint"
```

## Related Documentation

- [Tool Implementation Design](../../TOOL_IMPLEMENTATION_DESIGN.md)
- [Agent System Prompts](../../src/opencanvas/evolution/config/agent_prompts.py)
- [Evolution API](../../src/opencanvas/evolution/core/evolution.py)
- [Original Evolution Docs](../../EVOLUTION_DOCS.md) (archived)

## References

Original evolution system development:
- [EVOLUTION_TAKEAWAY.md](../../EVOLUTION_TAKEAWAY.md) - Key learnings
- [EVOLUTION_SYSTEM_HANDOVER.md](../../EVOLUTION_SYSTEM_HANDOVER.md) - Technical handover
- [MULTI_AGENT_EVOLUTION_ROADMAP.md](../../MULTI_AGENT_EVOLUTION_ROADMAP.md) - Implementation roadmap
