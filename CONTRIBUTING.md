# Contributing to OpenCanvas

Thank you for your interest in contributing to OpenCanvas! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- **Bug Reports** - Report issues you encounter
- **Feature Requests** - Suggest new features or improvements
- **Code Contributions** - Submit pull requests
- **Documentation** - Improve or expand documentation
- **Testing** - Write tests or test new features
- **Examples** - Add usage examples

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/OpenCanvas.git
cd OpenCanvas
```

### 2. Set Up Development Environment

```bash
# Install all dependencies
pip install -r requirements-all.txt

# Install browser automation
playwright install chromium

# Set up pre-commit hooks (optional)
pre-commit install
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Add your API keys to .env
# At minimum: ANTHROPIC_API_KEY
```

### 4. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-description
```

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Example

```python
def generate_presentation(topic: str, purpose: str = "general") -> dict:
    """
    Generate a presentation from a topic.

    Args:
        topic: The presentation topic
        purpose: Purpose of the presentation (default: "general")

    Returns:
        dict: Generation results with HTML file path

    Raises:
        ValueError: If topic is empty
    """
    if not topic:
        raise ValueError("Topic cannot be empty")

    # Implementation
    pass
```

### Code Formatting

We recommend using:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code
black src/

# Sort imports
isort src/

# Lint
flake8 src/
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific tests
python run_tests.py topic      # Topic generation
python run_tests.py pdf        # PDF generation
python run_tests.py light      # Quick validation

# Run with pytest
pytest tests/
```

### Writing Tests

Add tests for new features in the `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
from opencanvas.generators import TopicGenerator

def test_new_feature():
    """Test description"""
    generator = TopicGenerator(api_key="test_key")
    result = generator.new_feature()
    assert result is not None
```

## 📋 Pull Request Process

### 1. Prepare Your Changes

```bash
# Make sure your code is formatted
black src/
isort src/

# Run tests
python run_tests.py

# Commit your changes
git add .
git commit -m "feat: add new feature description"
```

### 2. Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add support for PowerPoint export
fix: resolve PDF conversion timeout issue
docs: update installation guide
test: add tests for evolution system
```

### 3. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
```

### 4. PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How have you tested this?
- [ ] Existing tests pass
- [ ] Added new tests
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
```

## 🐛 Reporting Bugs

### Before Submitting

1. Check existing [issues](https://github.com/genmini-ai/OpenCanvas/issues)
2. Update to the latest version
3. Verify the bug is reproducible

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Use config '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.10]
- OpenCanvas version: [e.g., 1.0.0]

**Additional Context**
Error logs, screenshots, etc.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Examples, mockups, references, etc.
```

## 📚 Documentation

### Improving Documentation

Documentation contributions are highly valued:

- Fix typos or unclear explanations
- Add missing information
- Improve examples
- Add troubleshooting tips

Documentation files:
- `README.md` - Main overview
- `docs/` - Detailed guides
- `API_README.md` - API documentation
- Code docstrings

## 🎨 Code Review Process

### What We Look For

- **Functionality** - Does it work as intended?
- **Tests** - Are there adequate tests?
- **Documentation** - Is it well documented?
- **Style** - Does it follow code style?
- **Performance** - Is it efficient?
- **Security** - Are there security concerns?

### Review Timeline

- Initial response: Within 2-3 days
- Full review: Within 1 week
- Merge: After approval and CI passes

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

### Communication

- **GitHub Issues** - Bug reports, feature requests
- **Pull Requests** - Code contributions
- **Discussions** - General questions, ideas

## 🔧 Development Tips

### Useful Commands

```bash
# Validate configuration
python -c "from opencanvas.config import Config; Config.validate()"

# Run specific test
pytest tests/test_topics.py::test_specific_function

# Check code coverage
pytest --cov=src tests/

# Build documentation locally
cd docs && python -m http.server
```

### Debugging

```bash
# Enable verbose logging
opencanvas --verbose generate "test topic"

# Use Python debugger
python -m pdb src/opencanvas/main.py generate "test topic"
```

### Project Structure

```
OpenCanvas/
├── src/
│   ├── opencanvas/        # Core package
│   │   ├── generators/    # Generation logic
│   │   ├── conversion/    # PDF conversion
│   │   ├── evaluation/    # Quality evaluation
│   │   └── evolution/     # Evolution system
│   └── api/               # REST API
├── tests/                 # Test suite
├── docs/                  # Documentation
└── examples/              # Usage examples
```

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions make OpenCanvas better for everyone. We appreciate your time and effort!

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Check existing documentation
- Review merged PRs for examples

---

Happy contributing! 🎉
