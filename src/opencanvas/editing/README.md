# Presentation Editing Module

The editing module provides intelligent presentation styling and modification capabilities using Claude Sonnet 4. It offers two modes:

- **Assist Mode**: Provides style recommendations and implements chosen styles
- **Autonomy Mode**: Directly modifies content and images (coming soon)

## 🎨 Assist Mode - Two-Step Style Editing

### Step 1: Style Analysis & Recommendations

Analyzes your presentation content and provides 3 diverse style recommendations:

```python
from opencanvas.editing import AssistModeStyleEditor

editor = AssistModeStyleEditor()

# Get 3 diverse style recommendations
content_analysis, recommendations = editor.get_style_recommendations(
    html_content=presentation_html,
    topic="AI in animal care",
    purpose="educational presentation", 
    audience="veterinary professionals"
)

# View recommendations
for rec in recommendations:
    print(f"Style: {rec.style_name}")
    print(f"Category: {rec.style_category}")
    print(f"Colors: {rec.color_palette}")
    print(f"Rationale: {rec.visual_rationale}")
```

### Step 2: Style Implementation

Implements your chosen style with professional CSS and animations:

```python
# Choose a recommendation
chosen_style = recommendations[0]  # e.g., "Clinical Precision"

# Implement the style
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

### Demo Script

Run the included demo to see the system in action:

```bash
cd src/opencanvas/editing
python demo.py
```

This will:
1. Analyze a sample "AI in Animal Care" presentation
2. Generate 3 diverse style recommendations  
3. Implement the first recommendation
4. Save both original and styled versions to `demo_output/`

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

- **Step 1 (Analysis)**: ~5-10 seconds, 4k tokens
- **Step 2 (Implementation)**: ~10-15 seconds, 8k tokens  
- **Model**: Claude Sonnet 4 for optimal quality and capability
- **Cost**: ~$0.05-0.10 per complete two-step styling

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