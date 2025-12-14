# OpenCanvas

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> AI-powered presentation generation from topics or PDFs. Beautiful slides in minutes, not hours.

## ✨ Key Features

- 🎨 **Generate from Topics or PDFs** - Text input or research papers
- 🖼️ **Image Mode** - PNG slides with Gemini AI + automatic PDF
- 🎯 **Smart Figure Matching** - Automatically extracts and matches figures to slides
- 📊 **Quality Evaluation** - AI-powered assessment and improvement
- 🚀 **REST API** - Full programmatic access

![Example Slide with Extracted Figures](docs/images/example_slide_with_figures.png)
*Slide automatically generated with extracted figures from research paper*

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
pip install -e .
```

### Setup

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY (required)
# Add your GEMINI_API_KEY (for image mode)
```

Get API keys:
- Anthropic: [console.anthropic.com](https://console.anthropic.com/)
- Gemini: [aistudio.google.com](https://aistudio.google.com/)

### Generate Your First Presentation

```bash
# From a topic
opencanvas generate "AI in healthcare" --purpose "academic presentation"

# From a research paper (with automatic figure extraction)
opencanvas generate "https://arxiv.org/pdf/2412.06769" \
  --output-format image \
  --purpose "research seminar"

# Complete pipeline with evaluation
opencanvas pipeline "quantum computing" --purpose "conference talk" --evaluate
```

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup
- **[CLI Reference](docs/usage/cli.md)** - All commands
- **[Image Generation](docs/usage/image-generation.md)** - Figure matching & PNG slides
- **[API Guide](API_README.md)** - REST API
- **[Evolution System](docs/architecture/evolution-system.md)** - Auto-improvement
- **[Examples](examples/)** - Usage examples

## 🎯 Common Use Cases

```bash
# Academic presentation from paper
opencanvas generate "paper.pdf" --output-format image --purpose "seminar"

# Corporate presentation
opencanvas generate "quarterly results" --purpose "board meeting" --theme "professional blue"

# Conference talk with evaluation
opencanvas pipeline "research topic" --purpose "conference" --evaluate
```

## 📁 Output

```
output/
└── topic_20241213_225914/
    ├── slides/              # PNG slides or HTML
    ├── extracted_images/    # Figures from PDFs
    ├── sources/             # Source content & blueprints
    └── presentation.pdf     # Final PDF
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
pip install -r requirements-all.txt
python run_tests.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Built With

- [Anthropic Claude](https://www.anthropic.com/) - AI generation
- [Google Gemini](https://ai.google.dev/) - Image generation
- [Docling](https://github.com/DS4SD/docling) - Figure extraction
- [FastAPI](https://fastapi.tiangolo.com/) - REST API

---

**⭐ Star this repo** if you find it useful!

**📚 [Full Documentation](docs/)** | **🐛 [Report Issues](https://github.com/genmini-ai/OpenCanvas/issues)** | **💬 [Discussions](https://github.com/genmini-ai/OpenCanvas/discussions)**
