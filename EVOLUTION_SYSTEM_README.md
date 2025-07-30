# OpenCanvas Evolution System

A multi-agent self-evolution system that systematically improves presentation generation quality through iterative analysis, design, and implementation of improvements.

## 🏗️ Architecture Overview

The evolution system consists of four specialized agents orchestrated to create a complete improvement cycle:

### Core Components

1. **Multi-Agent System** (`src/opencanvas/evolution/multi_agent/`)
   - **Reflection Agent**: Analyzes evaluation results to identify improvement patterns
   - **Improvement Agent**: Designs specific improvements based on reflection analysis  
   - **Implementation Agent**: Creates deployable improvements (prompts, configs, validation rules)
   - **Orchestrator Agent**: Coordinates all agents through the evolution cycle

2. **Prompt Evolution Manager** (`src/opencanvas/evolution/prompt_evolution_manager.py`)
   - Manages evolved prompts in versioned iteration folders (like training checkpoints)
   - Creates folders: `evolution_prompts/iteration_001/`, `iteration_002/`, etc.
   - Tracks evolution history and enables rollback capabilities

3. **Evolved Generator** (`src/opencanvas/evolution/evolved_generator.py`)
   - Uses evolved prompts from iteration folders instead of static prompts
   - Applies post-generation enhancements based on evolved standards
   - Tracks generation statistics and evolution metadata

## 🔄 Evolution Cycle Process

### Phase 1: Reflection 
- Analyzes presentation evaluation results
- Identifies systematic weakness patterns across quality dimensions
- Compares performance across different topics and presentation types
- Generates comprehensive quality analysis report

### Phase 2: Improvement Design
- Designs specific, targeted improvements based on reflection analysis
- Prioritizes improvements by impact potential and implementation complexity
- Creates detailed improvement specifications with expected outcomes
- Maps improvements to specific prompt categories and system components

### Phase 3: Implementation
- Converts improvement designs into deployable artifacts
- Generates enhanced prompts with specific quality requirements
- Creates validation rules and quality control mechanisms
- Produces configuration changes and system modifications

### Phase 4: Integration
- Saves evolved prompts to versioned iteration folders
- Updates system configuration with new improvements
- Creates comprehensive documentation and usage guides
- Enables A/B testing against previous iterations

## 🚀 Getting Started

### Prerequisites
```bash
# Ensure you have the required dependencies
pip install anthropic openai google-generativeai

# Set your API keys
export ANTHROPIC_API_KEY="your_key_here"
```

### Quick Demo
```bash
# Run the complete evolution cycle demonstration
python demo_complete_evolution_cycle.py
```

### Basic Usage

#### 1. Run Multi-Agent Evolution
```python
from opencanvas.evolution.multi_agent_evolution_manager import MultiAgentEvolutionManager

# Initialize evolution manager
manager = MultiAgentEvolutionManager(
    output_dir="evolution_results",
    test_topics=["AI in healthcare", "Sustainable energy"],
    max_iterations=3,
    improvement_threshold=0.2
)

# Run complete evolution process
results = manager.run_multi_agent_evolution()
```

#### 2. Use Evolved Prompts
```python
from opencanvas.evolution.evolved_generator import EvolvedGenerator

# Initialize with specific evolution iteration
generator = EvolvedGenerator(
    api_key="your_api_key", 
    evolution_iteration=2  # Use iteration 2 prompts
)

# Generate with evolved prompts
html_content = generator.generate_slides_html(
    content="AI applications in healthcare",
    purpose="conference presentation", 
    theme="professional blue"
)
```

#### 3. Manage Prompt Evolution
```python
from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager

# Initialize prompt manager
prompt_manager = PromptEvolutionManager("my_evolution_prompts")

# Create new evolution iteration
iteration_dir = prompt_manager.create_evolution_iteration(
    iteration_number=1,
    improvements=improvement_list,
    baseline_scores=current_scores
)

# Get evolved prompts for generation
evolved_prompts = prompt_manager.get_current_prompts(iteration_number=1)
```

## 📊 Testing and Validation

### Run Individual Agent Tests
```bash
python test_multi_agent_evolution.py
```

### A/B Testing Framework
```python
from opencanvas.evolution.evolved_generator import EvolvedGenerationRouter

# Compare baseline vs evolved generation
baseline_router = GenerationRouter(api_key="key")
evolved_router = EvolvedGenerationRouter(api_key="key", evolution_iteration=1)

# Generate with both systems for comparison
baseline_result = baseline_router.generate(topic, purpose, theme, output_dir)
evolved_result = evolved_router.generate(topic, purpose, theme, output_dir)
```

## 📁 File Structure

```
evolution_prompts/
├── iteration_001/
│   ├── topic_generation_prompt.txt
│   ├── pdf_generation_prompt.txt  
│   ├── visual_enhancement_prompt.txt
│   ├── content_validation_prompt.txt
│   ├── quality_control_prompt.txt
│   ├── iteration_metadata.json
│   ├── prompt_comparison_report.json
│   └── USAGE_GUIDE.md
├── iteration_002/
│   └── ... (same structure)
└── ...
```

## 🎯 Key Features

### Real Implementation (Not Just Planning)
- Actually creates new generation prompts saved in iteration folders
- Applies improvements during generation through EvolvedGenerator
- Validates improvements work with A/B testing capabilities

### Multi-Agent Coordination
- Each agent has specialized expertise and system prompts
- Orchestrator coordinates complex multi-phase evolution cycles
- Comprehensive logging and artifact tracking

### Versioned Evolution Management
- Each iteration gets its own folder (like training checkpoints)
- Complete rollback capabilities to any previous iteration
- Evolution history tracking and comparison reports

### Production Integration
- EvolvedGenerator replaces baseline generator seamlessly
- Evolved prompts integrate with existing generation pipeline
- Statistical tracking and performance monitoring

## 🔧 System Configuration

### Agent Configuration
```python
# Each agent can be configured with different models and parameters
reflection_agent = ReflectionAgent(
    api_key="key",
    model="claude-3-5-sonnet-20241022"
)
```

### Evolution Parameters
```python
# Customize evolution behavior
evolution_manager = MultiAgentEvolutionManager(
    max_iterations=5,           # Maximum evolution iterations
    improvement_threshold=0.2,  # Minimum improvement to continue
    test_topics=custom_topics   # Topics for testing
)
```

## 📈 Performance Monitoring

### Generation Statistics
```python
# Get performance metrics from evolved generator
generator = EvolvedGenerator(api_key="key", evolution_iteration=1)
stats = generator.get_generation_stats()

print(f"Success rate: {stats['success_rate']}")
print(f"Evolution iteration: {stats['evolution_iteration_active']}")
```

### Evolution History Analysis
```python
# Analyze evolution effectiveness over time
prompt_manager = PromptEvolutionManager()
history = prompt_manager.get_evolution_history()

for iteration in history['iterations']:
    print(f"Iteration {iteration['iteration_number']}: {iteration['total_improvements']} improvements")
```

## 🚨 Important Notes

### API Requirements
- Requires Anthropic API key for Claude models
- Supports Google Gemini as alternative evaluation provider
- OpenAI integration available for comparison studies

### Quality Assurance
- Evolved prompts include enhanced citation authenticity requirements
- Visual quality standards prevent unreadable charts and poor design
- Content completeness validation ensures comprehensive coverage

### System Safety
- Rollback capabilities to any previous iteration
- A/B testing validation before deploying improvements
- Comprehensive logging and error tracking

## 🤝 Contributing

The evolution system is designed to be extensible:

1. **Add New Agents**: Create specialized agents in `multi_agent/` directory
2. **Extend Prompt Categories**: Add new prompt types in `PromptEvolutionManager`
3. **Custom Improvements**: Implement domain-specific improvement strategies
4. **Enhanced Validation**: Add new quality control mechanisms

## 📚 Documentation

- **Agent System Prompts**: Each agent's specialized expertise defined in system prompts
- **Evolution Methodology**: Systematic approach to quality improvement
- **Integration Guides**: How to integrate with existing presentation generation
- **Performance Analysis**: Methods for measuring improvement effectiveness

## 🎯 Next Steps

1. **Run Demo**: `python demo_complete_evolution_cycle.py`
2. **Test System**: `python test_multi_agent_evolution.py` 
3. **Deploy Evolution**: Use `MultiAgentEvolutionManager` for production
4. **Validate Results**: Run A/B tests with `EvolvedGenerationRouter`

The evolution system represents a shift from manual prompt engineering to systematic, data-driven improvement of presentation generation quality.