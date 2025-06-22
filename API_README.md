# OpenCanvas API Documentation

The OpenCanvas API provides a RESTful interface to all OpenCanvas functionality, allowing you to generate presentations, convert them to PDF, evaluate their quality, and run complete pipelines programmatically.

## Quick Start

### 1. Install Dependencies

Choose the appropriate installation method:

**For API only (microservices):**
```bash
pip install -r requirements-api.txt
```

**For complete installation (CLI + API):**
```bash
pip install -r requirements-all.txt
```

**For separate installation:**
```bash
# Install core dependencies first
pip install -r requirements.txt

# Then install API dependencies
pip install -r requirements-api.txt
```

### 2. Start the API Server

```bash
# Using the standalone server script
python server.py

# Or using the main CLI
python -m src.main api

# Or with custom settings
python server.py --host 0.0.0.0 --port 8080 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### System Endpoints

#### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "message": "OpenCanvas API",
  "version": "1.0.0",
  "description": "A comprehensive presentation generation and evaluation system",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/api/v1/health"
}
```

#### GET `/api/v1/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Configuration Endpoints

#### GET `/api/v1/themes`
Get available presentation themes.

**Response:**
```json
{
  "themes": [
    "professional blue",
    "clean minimalist",
    "bold high contrast",
    "cool professional",
    "natural earth",
    "muted morandi tones",
    "modern contemporary",
    "warm earth tones",
    "soft pastels",
    "academic"
  ],
  "default": "professional blue"
}
```

#### GET `/api/v1/purposes`
Get available presentation purposes.

**Response:**
```json
{
  "purposes": [
    "academic presentation",
    "conference presentation",
    "corporate presentation",
    "research seminar",
    "pitch deck",
    "general presentation"
  ],
  "default": "general presentation"
}
```

#### GET `/api/v1/conversion-methods`
Get available conversion methods.

**Response:**
```json
{
  "methods": ["selenium", "playwright"],
  "default": "selenium"
}
```

### Generation Endpoints

#### POST `/api/v1/generate`
Generate a presentation from a topic or PDF source.

**Request Body:**
```json
{
  "input_source": "AI in healthcare applications",
  "purpose": "academic presentation",
  "theme": "clean minimalist",
  "output_dir": "output"
}
```

**Response:**
```json
{
  "success": true,
  "html_file": "output/presentation_20240115_103000.html",
  "research_performed": true,
  "message": "Presentation generated successfully"
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "input_source": "Machine learning in healthcare",
       "purpose": "academic presentation",
       "theme": "professional blue"
     }'
```

### Conversion Endpoints

#### POST `/api/v1/convert`
Convert an HTML presentation to PDF format.

**Request Body:**
```json
{
  "html_file": "output/presentation_20240115_103000.html",
  "output_filename": "presentation.pdf",
  "method": "selenium",
  "zoom_factor": 1.2,
  "output_dir": "output",
  "cleanup": true
}
```

**Response:**
```json
{
  "success": true,
  "pdf_file": "output/presentation.pdf",
  "zoom_level": 1.2,
  "message": "PDF conversion completed successfully"
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/convert" \
     -H "Content-Type: application/json" \
     -d '{
       "html_file": "output/presentation.html",
       "zoom_factor": 1.5,
       "method": "playwright"
     }'
```

### Evaluation Endpoints

#### POST `/api/v1/evaluate`
Evaluate the quality of a presentation.

**Request Body:**
```json
{
  "eval_folder": "output",
  "output_filename": "evaluation_results.json",
  "model": "claude-3-5-sonnet-20241022"
}
```

**Response:**
```json
{
  "success": true,
  "evaluation_results": {
    "visual_scores": {
      "design_score": 4.2,
      "layout_score": 4.0,
      "readability_score": 4.5,
      "overall_visual_score": 4.2
    },
    "content_free_scores": {
      "structure_score": 4.3,
      "narrative_score": 4.1,
      "coverage_score": 4.4,
      "overall_content_score": 4.3
    },
    "overall_scores": {
      "visual": 4.2,
      "content_reference_free": 4.3,
      "overall_presentation": 4.25
    }
  },
  "output_file": "output/evaluation_results.json",
  "message": "Evaluation completed successfully"
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/evaluate" \
     -H "Content-Type: application/json" \
     -d '{
       "eval_folder": "output",
       "model": "claude-3-5-sonnet-20241022"
     }'
```

### Pipeline Endpoints

#### POST `/api/v1/pipeline`
Run the complete presentation pipeline (generate → convert → evaluate).

**Request Body:**
```json
{
  "input_source": "Quantum computing applications",
  "purpose": "conference presentation",
  "theme": "modern contemporary",
  "source_pdf": "quantum_paper.pdf",
  "evaluate": true,
  "output_dir": "output",
  "zoom_factor": 1.3,
  "method": "playwright"
}
```

**Response:**
```json
{
  "success": true,
  "html_file": "output/presentation_20240115_103000.html",
  "pdf_file": "output/presentation.pdf",
  "evaluation_results": {
    "visual_scores": { ... },
    "content_free_scores": { ... },
    "overall_scores": { ... }
  },
  "research_performed": true,
  "message": "Pipeline completed successfully"
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/pipeline" \
     -H "Content-Type: application/json" \
     -d '{
       "input_source": "Sustainable energy solutions",
       "purpose": "corporate presentation",
       "theme": "natural earth",
       "evaluate": true
     }'
```

### File Download Endpoints

#### GET `/api/v1/files/{file_path}`
Download a generated file from the output directory.

**Example:**
```bash
# Download generated PDF
curl -O "http://localhost:8000/api/v1/files/presentation.pdf"

# Download evaluation results
curl -O "http://localhost:8000/api/v1/files/evaluation_results.json"
```

## Error Handling

All endpoints return consistent error responses:

**Error Response Format:**
```json
{
  "error": "HTTP 400",
  "detail": "Invalid input source",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (file not found)
- `500` - Internal Server Error

## Python Client Examples

### Basic Usage

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Generate a presentation
def generate_presentation(topic, purpose="academic presentation"):
    response = requests.post(f"{BASE_URL}/generate", json={
        "input_source": topic,
        "purpose": purpose,
        "theme": "professional blue"
    })
    return response.json()

# Convert to PDF
def convert_to_pdf(html_file):
    response = requests.post(f"{BASE_URL}/convert", json={
        "html_file": html_file,
        "zoom_factor": 1.2
    })
    return response.json()

# Evaluate presentation
def evaluate_presentation(eval_folder):
    response = requests.post(f"{BASE_URL}/evaluate", json={
        "eval_folder": eval_folder
    })
    return response.json()

# Run complete pipeline
def run_pipeline(topic, evaluate=True):
    response = requests.post(f"{BASE_URL}/pipeline", json={
        "input_source": topic,
        "purpose": "academic presentation",
        "evaluate": evaluate
    })
    return response.json()

# Example usage
if __name__ == "__main__":
    # Generate presentation
    result = generate_presentation("AI in healthcare")
    print(f"Generated: {result['html_file']}")
    
    # Convert to PDF
    pdf_result = convert_to_pdf(result['html_file'])
    print(f"PDF created: {pdf_result['pdf_file']}")
    
    # Run complete pipeline
    pipeline_result = run_pipeline("Machine learning ethics", evaluate=True)
    print(f"Pipeline completed: {pipeline_result['message']}")
```

### Advanced Usage with Error Handling

```python
import requests
import time
from typing import Dict, Any

class OpenCanvasClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def generate(self, topic: str, purpose: str = "academic presentation", 
                theme: str = "professional blue") -> Dict[str, Any]:
        """Generate presentation from topic"""
        return self._make_request("POST", "/generate", json={
            "input_source": topic,
            "purpose": purpose,
            "theme": theme
        })
    
    def convert(self, html_file: str, zoom_factor: float = 1.2) -> Dict[str, Any]:
        """Convert HTML to PDF"""
        return self._make_request("POST", "/convert", json={
            "html_file": html_file,
            "zoom_factor": zoom_factor
        })
    
    def evaluate(self, eval_folder: str) -> Dict[str, Any]:
        """Evaluate presentation"""
        return self._make_request("POST", "/evaluate", json={
            "eval_folder": eval_folder
        })
    
    def pipeline(self, topic: str, evaluate: bool = True) -> Dict[str, Any]:
        """Run complete pipeline"""
        return self._make_request("POST", "/pipeline", json={
            "input_source": topic,
            "evaluate": evaluate
        })
    
    def download_file(self, file_path: str, save_path: str = None):
        """Download a file"""
        if save_path is None:
            save_path = file_path.split("/")[-1]
        
        response = self.session.get(f"{self.base_url}/files/{file_path}")
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {save_path}")

# Usage example
client = OpenCanvasClient()

try:
    # Generate and convert
    result = client.generate("Quantum computing basics")
    print(f"Generated: {result['html_file']}")
    
    pdf_result = client.convert(result['html_file'])
    print(f"PDF: {pdf_result['pdf_file']}")
    
    # Download the PDF
    client.download_file("presentation.pdf", "my_presentation.pdf")
    
except Exception as e:
    print(f"Error: {e}")
```

## JavaScript/Node.js Examples

### Basic Usage

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

class OpenCanvasAPI {
    constructor(baseUrl = BASE_URL) {
        this.baseUrl = baseUrl;
        this.client = axios.create({ baseURL: baseUrl });
    }
    
    async generate(topic, purpose = 'academic presentation', theme = 'professional blue') {
        const response = await this.client.post('/generate', {
            input_source: topic,
            purpose: purpose,
            theme: theme
        });
        return response.data;
    }
    
    async convert(htmlFile, zoomFactor = 1.2) {
        const response = await this.client.post('/convert', {
            html_file: htmlFile,
            zoom_factor: zoomFactor
        });
        return response.data;
    }
    
    async evaluate(evalFolder) {
        const response = await this.client.post('/evaluate', {
            eval_folder: evalFolder
        });
        return response.data;
    }
    
    async pipeline(topic, evaluate = true) {
        const response = await this.client.post('/pipeline', {
            input_source: topic,
            evaluate: evaluate
        });
        return response.data;
    }
}

// Usage example
async function main() {
    const api = new OpenCanvasAPI();
    
    try {
        // Generate presentation
        const result = await api.generate('AI in healthcare');
        console.log('Generated:', result.html_file);
        
        // Convert to PDF
        const pdfResult = await api.convert(result.html_file);
        console.log('PDF created:', pdfResult.pdf_file);
        
        // Run pipeline
        const pipelineResult = await api.pipeline('Machine learning ethics', true);
        console.log('Pipeline completed:', pipelineResult.message);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

main();
```

## Configuration

The API uses the same configuration as the CLI. Set environment variables in your `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
BRAVE_API_KEY=your_brave_key
DEFAULT_THEME=professional blue
DEFAULT_PURPOSE=general presentation
OUTPUT_DIR=output
DEFAULT_ZOOM=1.2
DEFAULT_CONVERSION_METHOD=selenium
EVALUATION_MODEL=claude-3-5-sonnet-20241022
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

#### Complete Installation
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-all.txt .
RUN pip install -r requirements-all.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
```

#### API-Only Installation (Microservices)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

# Copy only necessary files for API
COPY src/api/ ./src/api/
COPY src/config.py ./src/config.py
COPY src/utils/ ./src/utils/
COPY server.py .

EXPOSE 8000

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  opencanvas-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    volumes:
      - ./output:/app/output
```

## Troubleshooting

### Common Issues

1. **API not starting**: Check if all dependencies are installed
   ```bash
   # For API only
   pip install -r requirements-api.txt
   
   # For complete installation
   pip install -r requirements-all.txt
   ```

2. **Configuration errors**: Ensure environment variables are set
   ```bash
   export ANTHROPIC_API_KEY=your_key
   ```

3. **File not found errors**: Check if output directory exists
   ```bash
   mkdir -p output
   ```

4. **Browser automation issues**: Install browser drivers
   ```bash
   playwright install chromium
   ```

5. **Missing dependencies**: Install the appropriate requirements file
   ```bash
   # For CLI only
   pip install -r requirements.txt
   
   # For API only
   pip install -r requirements-api.txt
   
   # For everything
   pip install -r requirements-all.txt
   ```

### Debug Mode

Start the server with debug logging:

```bash
python server.py --log-level debug --reload
```

### Health Check

Test if the API is running:

```bash
curl http://localhost:8000/api/v1/health
```

## Rate Limiting and Security

For production deployments, consider:

1. **Rate limiting**: Implement rate limiting middleware
2. **Authentication**: Add API key authentication
3. **CORS**: Configure CORS for your domain
4. **Input validation**: Validate all inputs
5. **File upload limits**: Set appropriate file size limits

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Test with the health endpoint
4. Verify configuration and environment variables 