# OpenCanvas Evolution System Documentation

A unified documentation for the multi-agent self-evolution system that systematically improves presentation generation quality.

## 🏗️ System Architecture

The evolution system consists of four core components working together in a unified architecture:

### Core Components

1. **Unified Agent System** (`src/opencanvas/evolution/core/agents.py`)
   - Single `EvolutionAgent` class with type-based behavior 
   - Agents: reflection, improvement, implementation, orchestrator
   - Centralized prompts in `config/agent_prompts.py`
   - Reduced from 6 files to 2 files

2. **Tools Management** (`src/opencanvas/evolution/core/tools.py`)  
   - Unified `ToolsManager` for discovery, testing, adoption
   - Machine-readable specifications in `config/tools_specs.py`
   - Tool registry with success/failure tracking
   - Consolidated from separate registry and discovery systems

3. **Prompt Evolution** (`src/opencanvas/evolution/core/prompts.py`)
   - `PromptManager` for versioned prompt evolution
   - Iteration folders like training checkpoints: `evolution_prompts/iteration_001/`
   - Complete rollback capabilities and evolution history

4. **Evolution Orchestration** (`src/opencanvas/evolution/core/evolution.py`)
   - Main `EvolutionSystem` coordinating all components
   - Complete evolution cycles with validation
   - Integration with existing generation pipeline

## 🔄 Evolution Process

### Phase 1: Reflection Analysis
- Analyzes presentation evaluation results across quality dimensions
- Identifies systematic weakness patterns and improvement opportunities  
- Calculates baseline performance metrics and improvement potential

### Phase 2: Improvement Design
- Designs specific, targeted improvements based on reflection analysis
- Prioritizes improvements by impact vs complexity using priority matrix
- Creates detailed specifications with expected outcomes

### Phase 3: Implementation & Tool Discovery
- Converts improvements into deployable artifacts (enhanced prompts)
- Discovers new tools when prompts alone can't solve quality issues
- Creates tool specifications with clear API contracts and performance estimates

### Phase 4: Integration & Validation
- Saves evolved prompts to versioned iteration folders
- Updates tool registry with discovered/tested/adopted tools
- Enables A/B testing between iterations

## 🚀 Quick Start Guide

### Installation & Setup
```bash
# Ensure dependencies
pip install anthropic openai google-generativeai

# Set API keys
export ANTHROPIC_API_KEY="your_key_here"
```

### Run Evolution Cycle
```python
from opencanvas.evolution.core.evolution import EvolutionSystem

# Initialize and run evolution
system = EvolutionSystem(
    output_dir="evolution_output",
    max_iterations=3,
    improvement_threshold=0.2
)

results = system.run_evolution_cycle()
print(f"Evolution completed: {results['total_iterations']} iterations")
```

### Use Evolved Prompts
```python
from opencanvas.evolution.core.prompts import PromptManager

# Get evolved prompts from specific iteration
prompt_manager = PromptManager()
evolved_prompts = prompt_manager.get_prompts(iteration=2)

# Use in generation
topic_prompt = evolved_prompts['topic_generation'].format(
    topic="AI in healthcare",
    purpose="conference presentation", 
    theme="professional blue"
)
```

## 🛠️ Tool Ecosystem

### Current Production Tools
- **WebSearchTool**: Research when knowledge insufficient (~2-3s, 85% success)
- **WebScraperTool**: Extract content from web pages (~1-2s, 70% success)  
- **ImageValidationTool**: Validate/replace broken images (~3-5s, 85% success)
- **PDFProcessingTool**: Extract PDF content (~2-10s, 95% success)
- **ClaudeGenerationTool**: Core content generation (~10-15s, 98% success)

### High-Priority Proposed Tools
- **CitationVerificationTool**: Detect fake citations (Expected: 20% → <2% fake citations)
- **SlideContentBalanceAnalyzer**: Fix text walls (Expected: +0.3 readability score)
- **ChartReadabilityValidator**: Ensure readable charts (Expected: +0.5 visual score)

### Tool Development Patterns

**✅ Successful Patterns (Follow These)**:
- Simple Input/Output with clear data contracts
- Fast execution (<2s for real-time use)
- Graceful failure (always return result, never crash)
- Measurable impact with before/after metrics
- Post-processing integration (don't disrupt main flow)

**❌ Failed Patterns (Avoid These)**:
- Multi-stage complexity (breaks consistency)
- Sequential processing (too slow for MVP)
- Rigid templates (reduces flexibility)
- Heavy dependencies (increases failure points)

### Tool Adoption Criteria
- **Quality Impact**: Minimum +0.2 improvement in evaluation scores
- **Speed Impact**: Maximum +10% increase in generation time  
- **Cost Impact**: Maximum +5% increase in API costs
- **Reliability**: Minimum 90% success rate

## 📁 File Structure

```
src/opencanvas/evolution/
├── core/
│   ├── evolution.py              # Main evolution orchestration
│   ├── agents.py                 # Unified agent system  
│   ├── tools.py                  # Unified tools management
│   └── prompts.py                # Prompt evolution manager
├── config/
│   ├── agent_prompts.py          # Centralized agent prompts
│   └── tools_specs.py            # Machine-readable tool specs
└── __init__.py                   # Clean package exports

evolution_prompts/                # Generated by system
├── iteration_001/
│   ├── topic_generation_prompt.txt
│   ├── pdf_generation_prompt.txt
│   ├── visual_enhancement_prompt.txt
│   ├── content_validation_prompt.txt
│   ├── quality_control_prompt.txt
│   └── metadata.json
└── iteration_002/
    └── ... (same structure)
```

## 🎯 Key Benefits

### Real Implementation (Not Just Planning)
- Actually creates new evolved prompts in versioned iteration folders
- Tools Manager tracks discovered → tested → adopted tool lifecycle
- Complete integration with existing generation pipeline

### Significant Code Reduction
- **Before**: 4,479 lines across 17 files
- **After**: ~1,500 lines across 7 files  
- **Result**: 66% reduction in complexity while maintaining all functionality

### Multi-Agent Expertise
- Each agent type has specialized system prompts and capabilities
- Orchestrated workflows with comprehensive logging
- Systematic progression from analysis → design → implementation

### Tool Discovery & Innovation
- Evolution system discovers new tools when prompt improvements insufficient
- Machine-readable tool specifications enable agent understanding
- Success/failure pattern tracking prevents repeating mistakes

## 📊 Performance & Monitoring

### System Status
```python
from opencanvas.evolution.core.evolution import EvolutionSystem

system = EvolutionSystem()
status = system.get_system_status()

print(f"Tools in production: {len(status['components']['tools_manager']['current_tools'])}")
print(f"Evolution iterations: {status['components']['prompt_manager']['current_iteration']}")
```

### Evolution History
```python
from opencanvas.evolution.core.prompts import PromptManager

prompt_manager = PromptManager()
history = prompt_manager.get_evolution_history()

for iteration in history['iterations']:
    print(f"Iteration {iteration['iteration_number']}: {iteration['total_improvements']} improvements")
```

## 🚨 Important Notes

### API Requirements
- Anthropic API key required for Claude models
- Google Gemini supported as alternative evaluation provider
- System gracefully handles API failures with comprehensive error logging

### Quality Assurance
- Enhanced citation authenticity requirements prevent fake citations
- Visual quality standards ensure readable charts and professional design
- Content completeness validation ensures comprehensive topic coverage

### System Safety
- Complete rollback capabilities to any previous iteration
- A/B testing validation before deploying improvements
- Comprehensive logging and error tracking throughout evolution cycles

## 🔧 Advanced Usage

### Custom Agent Configuration
```python
from opencanvas.evolution.core.agents import EvolutionAgent

# Create specialized agent
reflection_agent = EvolutionAgent(
    agent_type="reflection", 
    api_key="your_key",
    model="claude-3-5-sonnet-20241022"
)

# Process specific analysis
result = reflection_agent.process({
    "action": "analyze_evaluations",
    "evaluations": evaluation_data,
    "topics": test_topics
})
```

### Tool Testing Framework
```python
from opencanvas.evolution.core.tools import ToolsManager

tools_manager = ToolsManager()

# Propose new tool
proposal_result = tools_manager.propose_tool({
    "name": "MyNewTool",
    "purpose": "Solve specific quality issue",
    "expected_impact": "high",
    "complexity": "low"
})

# Test tool with results
test_result = tools_manager.test_tool("MyNewTool", {
    "quality_improvement": 0.3,
    "speed_impact_percent": 5,
    "success_rate": 95
})
```

## 📈 Evolution Metrics

### Current System Performance
- **Average Generation Time**: 15-20 seconds
- **Average Quality Score**: 3.2/5.0 baseline
- **Tool Success Rate**: 87% across all tools
- **Cost per Generation**: $0.15-0.25

### Improvement Tracking
- Each iteration tracks improvement from previous baseline
- Quality improvements measured across visual, content, and overall dimensions
- Tool adoption tracked with success/failure reasons
- Complete audit trail of all evolution decisions

## 🎯 Next Steps

1. **Run Evolution**: Use `EvolutionSystem.run_evolution_cycle()` for systematic improvement
2. **Monitor Tools**: Check `ToolsManager.get_implementation_queue()` for high-priority tools
3. **Validate Results**: Compare evolution iterations with A/B testing
4. **Deploy Improvements**: Use evolved prompts in production generation

The evolution system represents a shift from manual engineering to systematic, data-driven improvement of presentation generation quality through multi-agent collaboration and tool innovation.

---

*Last Updated: 2025-01-30 - Unified documentation consolidating EVOLUTION_SYSTEM_README.md, CLEAN_EVOLUTION_SUMMARY.md, TOOLS_REGISTRY.md, and TOOLS_SPECIFICATION.md*