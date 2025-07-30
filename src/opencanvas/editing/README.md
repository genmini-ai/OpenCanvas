# Presentation Editing Module

The editing module provides intelligent presentation styling and modification capabilities using Claude Sonnet 4. It offers two modes:

- **Assist Mode**: Provides style recommendations and implements chosen styles
- **Autonomy Mode**: Directly modifies content and images (coming soon)

## 🎨 Assist Mode - Complete Style Editing Experience

### Preview Mode: Visual Style Comparison

**NEW**: Preview all 3 style recommendations before committing to full implementation:

```python
from opencanvas.editing import AssistModeStyleEditor

editor = AssistModeStyleEditor()

# Step 1: Get style recommendations
content_analysis, recommendations = editor.get_style_recommendations(
    html_content=presentation_html,
    topic="AI in animal care",
    purpose="educational presentation", 
    audience="veterinary professionals"
)

# Step 2: Generate previews for all styles (first slide only)
previews = editor.generate_style_previews(
    original_html=presentation_html,
    recommendations=recommendations
)

# Save previews for browser comparison
for style_name, preview_html in previews.items():
    with open(f"preview_{style_name.replace(' ', '_').lower()}.html", "w") as f:
        f.write(preview_html)
```

### Full Implementation

After choosing your preferred style from previews:

```python
# Choose a recommendation
chosen_style = recommendations[0]  # Based on preview comparison

# Implement the style on full presentation
modified_html, summary = editor.implement_chosen_style(
    original_html=presentation_html,
    chosen_style=chosen_style
)

# Save the styled presentation
with open("styled_presentation.html", "w") as f:
    f.write(modified_html)
```

## 🚀 Quick Start

### Basic Usage

```python
from opencanvas.editing import AssistModeStyleEditor

# Initialize with your API key (or uses Config.ANTHROPIC_API_KEY)
editor = AssistModeStyleEditor()

# Two-step process
content_analysis, recommendations = editor.get_style_recommendations(
    html_content="<html>...</html>",
    topic="Your presentation topic",
    purpose="educational|corporate|conference",
    audience="target audience description"
)

# Pick a style and implement it
chosen_style = recommendations[1]  # Pick any of the 3
modified_html, summary = editor.implement_chosen_style(
    original_html="<html>...</html>",
    chosen_style=chosen_style
)
```

### Test Scripts

Several scripts are available to test different aspects of the editing system:

#### **Complete Workflow (Recommended)**
```bash
cd src/opencanvas/editing
python complete_workflow.py
```
The full experience: analyze → preview all 3 styles → choose → implement full presentation

#### **Preview Only**
```bash
python preview_test.py
```
Generate and compare all 3 style previews without full implementation

#### **Quick Test**
```bash
python quick_test.py
```
Automatically apply the first style recommendation for rapid testing

#### **Basic Demo**
```bash
python demo.py
```
Simple demonstration with sample content

## 🎯 Style Categories

The system generates recommendations across three categories for maximum diversity:

### Conservative
- Professional, trustworthy appearance
- Subtle animations and transitions
- Classic color palettes (blues, grays, whites)
- Clean, readable typography
- Best for: Corporate, medical, academic contexts

### Balanced  
- Modern but approachable design
- Moderate animation and visual interest
- Thoughtful color combinations
- Contemporary typography
- Best for: General business, educational content

### Bold
- Creative, attention-grabbing design
- Dynamic animations and interactions
- Vibrant, expressive color schemes
- Modern, distinctive typography  
- Best for: Creative industries, startups, marketing

## ⚙️ Configuration

### API Key Setup

The editor uses Claude Sonnet 4 (`claude-sonnet-4-20250514`). Set your API key:

```python
# Option 1: Via config (recommended)
from opencanvas.config import Config
# Ensure Config.ANTHROPIC_API_KEY is set

# Option 2: Direct initialization  
editor = AssistModeStyleEditor(anthropic_api_key="your-key-here")
```

### Customization Options

```python
# Customize the analysis context
content_analysis, recommendations = editor.get_style_recommendations(
    html_content=html,
    topic="Specific topic name",
    purpose="educational|corporate|conference|pitch|academic",
    audience="Detailed audience description for better targeting"
)
```

## 📊 Style Recommendation Structure

Each recommendation includes:

```python
class StyleRecommendation:
    style_name: str              # "Clinical Precision"
    style_category: str          # "conservative|balanced|bold"  
    color_palette: dict          # Primary, secondary, accent, background, text colors
    animation_philosophy: str    # Movement approach description
    animation_details: list      # Specific animation types
    typography_approach: str     # Font strategy
    font_suggestions: dict       # Heading and body font recommendations
    visual_rationale: str        # Why this style works (100-150 words)
    mood_keywords: list          # ["Professional", "Trustworthy", "Clean"]
    best_suited_for: str         # Ideal audience/context
```

## 🎨 Implementation Features

The style implementation includes:

### Color System
- Complete palette application throughout presentation
- WCAG AA accessibility compliance (4.5:1 contrast minimum)
- Strategic color usage for information hierarchy
- Hover states and interaction feedback

### Advanced Animations
- CSS3 animations matching the chosen philosophy
- Slide-level transitions and element animations
- Professional easing and timing
- Performance-optimized with `transform` and `opacity`

### Typography System
- Professional font loading and fallbacks
- Complete typographic scale with consistent spacing
- Information hierarchy optimization
- Cross-device readability

### CSS Architecture
- Clean, maintainable CSS structure
- CSS custom properties for easy theming
- Semantic class naming (BEM methodology)
- Responsive design considerations

## 🛠️ Development

### File Structure

```
editing/
├── __init__.py              # Module exports
├── prompts.py               # Claude prompts for both modes
├── assist_mode.py           # Two-step assist mode implementation
├── demo.py                  # Demo script
└── README.md               # This file
```

### Adding New Features

1. **New Prompt Templates**: Add to `EditingPrompts` class in `prompts.py`
2. **Style Categories**: Extend the recommendation system in `assist_mode.py`
3. **Implementation Features**: Enhance the Step 2 prompt for new CSS capabilities

### Future: Autonomy Mode

Coming soon - direct content and image editing:
- Text optimization and rewriting
- Image replacement via Claude image retriever integration
- Structural reorganization
- Content enhancement while preserving core message

## 📈 Performance

- **Style Analysis**: ~5-10 seconds, 4k tokens
- **Preview Generation**: ~10-20 seconds per style, 6k tokens (3 styles = 30-60s total)
- **Full Implementation**: ~15-30 seconds, 8k tokens  
- **Model**: Claude Sonnet 4 for optimal quality and capability
- **Cost**: 
  - Preview mode: ~$0.15-0.25 (generates all 3 previews)
  - Full implementation: ~$0.05-0.10 per style
  - Complete workflow: ~$0.20-0.35 total

## 🎯 Best Practices

1. **Provide Context**: Give specific topic, purpose, and audience details
2. **Review All Options**: The 3 recommendations offer genuinely different approaches
3. **Test Accessibility**: Generated styles meet WCAG AA standards
4. **Preview Results**: Always preview styled presentations before use
5. **Iterative Refinement**: Try different recommendations for comparison

## 🔧 Troubleshooting

### Common Issues

**"No Anthropic API key found"**
- Set `ANTHROPIC_API_KEY` environment variable
- Or pass key directly to `AssistModeStyleEditor(api_key="...")`

**"Invalid JSON in style recommendations"**
- Claude occasionally returns malformed JSON
- The system includes retry logic and error handling
- Check your input HTML is well-formed

**"No HTML markers found"**
- Step 2 couldn't find HTML in Claude's response
- Usually resolves with retry
- Ensure original HTML is complete and valid

### Getting Help

- Check the demo script for working examples
- Review the prompts in `prompts.py` for expected formats
- Enable debug logging: `logging.getLogger('opencanvas.editing').setLevel(logging.DEBUG)` 