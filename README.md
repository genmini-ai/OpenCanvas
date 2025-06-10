# OpenCanvas
OpenCanvas transforms your ideas into stunning posters and slides with a single click. This AI-powered tool bridges the gap between content knowledge and visual presentation by automatically generating comprehensive, visually appealing HTML presentations and posters.

## 🚀 Features

- **Intelligent Knowledge Assessment**: Automatically determines if additional research is needed for a given topic / text
- **Deep Search Integration**: Performs targeted deep web searches via Brave Search API when necessary
- **HTML Slide and Poster Generation**: Converts content into responsive, browser-based presentations / posters
- **Multiple Design Themes**: Supports various visual themes for different presentation purposes
- **Auto Evaluation**: Includes tools to assess presentation quality across multiple dimensions

## 📋 Files Structure

- `slide_generator.py`: Core presentation generation engine
- `test_cases.py`: Test suite covering diverse presentation scenarios
- `evaluation.py`: Comprehensive quality assessment system

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export BRAVE_API_KEY="your_brave_api_key"  # Optional for web research
```

## 🔧 Usage

### Basic Usage

```python
from slide_generator import SlideGenerator

# Initialize generator
generator = SlideGenerator(
    api_key="your_anthropic_api_key",
    brave_api_key="your_brave_api_key"  # Optional
)

# Generate a presentation
result = generator.generate_complete_presentation(
    user_text="Topic or detailed description",
    purpose="educational presentation",  # Or: pitch deck, analytical report, etc.
    theme="cool professional"  # Or: bold high contrast, clean minimalist, etc.
)

# The generated presentation is automatically opened in your browser
print(f"Presentation saved as: {result['html_file']}")
```

### Running Tests

```python
from test_cases import run_test_cases

# Run the entire test suite
test_results = run_test_cases()
```

### Running Evaluation

```python
import asyncio
from evaluation import run_comprehensive_test_suite

# Run tests with quality evaluation
asyncio.run(run_comprehensive_test_suite(
    anthropic_api_key="your_anthropic_api_key",
    brave_api_key="your_brave_api_key"
))
```

## 🎨 Supported Presentation Types

OpenCanvas supports various presentation types including:

- **Pitch Decks**: For startup and product pitches
- **Educational Presentations**: For training and workshops
- **Academic Presentations**: For research and conferences
- **Marketing Presentations**: For product launches and campaigns
- **Business Reports**: For status updates and quarterly reviews
- **Creative Showcases**: For portfolios and design work
- **Personal Storytelling**: For narratives and journey sharing

## 🔍 How It Works

1. **Knowledge Assessment**: Claude evaluates if it has sufficient knowledge on the topic
2. **Research (if needed)**: Performs targeted web searches for authoritative sources
3. **Content Creation**: Generates comprehensive educational content
4. **Slide Generation**: Converts content into HTML slides with appropriate styling
5. **Presentation Delivery**: Saves and opens the presentation in your browser

## ⚙️ Requirements

- Python 3.8+
- Anthropic API key
- Brave API key (optional, for web research)
- Required packages:
  - anthropic
  - requests
  - beautifulsoup4
  - playwright (for evaluation)

## 🔄 Planned Improvements
`Higher priority` for full text / paper input
- Better support for figures / diagrams
- Better support for layout optimization
- Support for editing
- Support for exporting to PowerPoint/Google Slides
- More visual themes and layouts

`Lower priority` for topic input
- Upgrade search to deep search


## 🙏 Acknowledgements
- Powered by [Anthropic Claude](https://www.anthropic.com/claude)
- Web research via [Brave Search API](https://brave.com/search/api/)
- Quality evaluation using [Playwright](https://playwright.dev/)
