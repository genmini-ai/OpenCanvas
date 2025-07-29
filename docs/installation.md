# Installation Guide

Detailed installation instructions for OpenCanvas.

## System Requirements

- Python 3.8 or higher
- pip package manager
- Chrome/Chromium browser (for PDF conversion)
- Git (optional, for development)

## Installation Options

### Option 1: Quick Install (Recommended)

Install the package directly with CLI support:

```bash
git clone https://github.com/genmini-ai/OpenCanvas.git
cd OpenCanvas
pip install -e .
```

### Option 2: Complete Installation (CLI + API)

For full functionality including the REST API:

```bash
pip install -r requirements-all.txt
```

### Option 3: Core Only

For basic CLI functionality without API dependencies:

```bash
pip install -r requirements.txt
```

### Option 4: API Only

For microservices deployment:

```bash
pip install -r requirements-api.txt
```

## Browser Automation Setup

OpenCanvas requires browser automation for HTML-to-PDF conversion.

### Playwright (Recommended)

```bash
playwright install chromium
```

### Selenium

Download ChromeDriver from [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/) and add to your PATH.

## Environment Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your API keys:**
   ```bash
   # Required
   ANTHROPIC_API_KEY=your_anthropic_api_key_here

   # Optional but recommended
   BRAVE_API_KEY=your_brave_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Configure evaluation provider (optional):**
   ```bash
   EVALUATION_PROVIDER=gemini  # or claude, gpt
   EVALUATION_MODEL=gemini-2.5-flash
   ```

## Get API Keys

### Anthropic (Required)
1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Generate a new key

### Brave Search (Optional)
1. Visit [https://api.search.brave.com/app/keys](https://api.search.brave.com/app/keys)
2. Sign up for free tier
3. Generate an API key

### Gemini (Optional - for evaluation)
1. Visit [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with Google account
3. Get API key from settings

### OpenAI (Optional - for evaluation)
1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key

## Verify Installation

Test your setup:

```bash
# Check configuration
python -c "from opencanvas.config import Config; Config.validate(); print('✅ Configuration valid')"

# Generate a test presentation
opencanvas generate "test topic" --output-dir test_output

# Check if CLI is installed
opencanvas --help
```

## Troubleshooting

### "opencanvas command not found"

Make sure you installed with the `-e` flag:
```bash
pip install -e .
```

Check if it's in your PATH:
```bash
which opencanvas
```

### "ANTHROPIC_API_KEY is required"

Ensure your `.env` file exists in the directory where you run `opencanvas`:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

### "Playwright not available"

Install Chromium browser for Playwright:
```bash
playwright install chromium
```

Or use Selenium as fallback:
```bash
opencanvas convert slides.html --method selenium
```

## Next Steps

- Read the [Quick Start Guide](../README.md#quick-start)
- Explore [Usage Examples](usage/cli.md)
- Check [Configuration Options](configuration.md)
