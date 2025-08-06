"""
Tool Specifications as Code - Machine-readable tool definitions
"""

from typing import Dict, List, Any

# Current tools in production
CURRENT_TOOLS = {
    "WebSearchTool": {
        "purpose": "Retrieve up-to-date information when knowledge is insufficient",
        "input_spec": "(query: str, max_results: int = 10) -> List[SearchResult]",
        "output_spec": "SearchResult(title: str, url: str, snippet: str, relevance: float)",
        "integration": "TopicGenerator.assess_knowledge_depth() -> INSUFFICIENT",
        "performance": "~2-3s, $0.00 (Brave API)",
        "success_rate": "85%",
        "implementation": "TopicGenerator.web_search()"
    },
    
    "WebScraperTool": {
        "purpose": "Extract clean text content from web pages",
        "input_spec": "(url: str, timeout: int = 10) -> ScrapedContent", 
        "output_spec": "ScrapedContent(text: str, success: bool, error: Optional[str])",
        "integration": "After WebSearchTool in research pipeline",
        "performance": "~1-2s per URL, $0.00",
        "success_rate": "70%",
        "implementation": "TopicGenerator.scrape_web_content()"
    },
    
    "ImageValidationTool": {
        "purpose": "Validate and replace broken or inappropriate images in slides",
        "input_spec": "(slide_html: str) -> ValidationResult",
        "output_spec": "ValidationResult(fixed_html: str, replacements: int, issues: List[str])",
        "integration": "generate_slides_html() post-processing",
        "performance": "~3-5s per presentation, ~$0.05", 
        "success_rate": "85%",
        "implementation": "ImageValidationPipeline"
    },
    
    "PDFProcessingTool": {
        "purpose": "Extract and encode PDF content for presentation generation",
        "input_spec": "(pdf_source: str) -> PDFContent",
        "output_spec": "PDFContent(text: str, base64: str, pages: int, success: bool)",
        "integration": "PDFGenerator.generate_presentation()",
        "performance": "~2-10s depending on size, $0.00",
        "success_rate": "95%",
        "implementation": "PDFGenerator.encode_pdf_from_file/url()"
    },
    
    "ClaudeGenerationTool": {
        "purpose": "Generate presentation content using Anthropic API",
        "input_spec": "(prompt: str, max_tokens: int = 8000) -> GenerationResult",
        "output_spec": "GenerationResult(content: str, tokens_used: int, success: bool)",
        "integration": "Core generation in all generators",
        "performance": "~10-15s, $0.10-0.20",
        "success_rate": "98%",
        "implementation": "BaseGenerator"
    }
}

# Tools that were tested but rejected
REJECTED_TOOLS = {
    "MultiStageOutlineGenerator": {
        "purpose": "Generate detailed outline before slide creation",
        "failure_reason": "2x slower, consistency issues between outline and slides",
        "test_period": "2024-06-15 to 2024-06-30",
        "pattern": "Multi-stage approaches hurt consistency in single-context systems",
        "lesson": "Prefer single-pass generation for consistency"
    },
    
    "SlideBySlideSequentialGenerator": {
        "purpose": "Generate each slide individually with full context",
        "failure_reason": "3x slower, 3x cost increase, minimal quality gain (+0.2)",
        "test_period": "2024-07-01 to 2024-07-10", 
        "pattern": "Sequential processing doesn't scale for MVP requirements",
        "lesson": "Parallelism essential, context loading expensive"
    },
    
    "TemplateMatchingSystem": {
        "purpose": "Match content to pre-designed slide templates",
        "failure_reason": "Rigid templates reduced flexibility, -0.3 quality score",
        "test_period": "2024-07-20 to 2024-07-25",
        "pattern": "Static templates can't adapt to diverse content needs", 
        "lesson": "Dynamic generation > rigid templates"
    }
}

# High-priority tools ready for implementation
PROPOSED_TOOLS = {
    "CitationVerificationTool": {
        "purpose": "Detect fake author names and non-existent publications",
        "input_spec": "(text: str) -> List[CitationIssue]",
        "output_spec": "CitationIssue(citation: str, confidence: float, issue_type: str, suggestion: str)",
        "integration": "Post-generation validation in generate_slides_html()",
        "expected_performance": "<500ms, ~$0.01 per check",
        "expected_impact": "Reduce fake citations from 20% to <2%",
        "priority": "high",
        "complexity": "low",
        "implementation_template": """
class CitationVerificationTool:
    def validate_citations(self, text: str) -> List[CitationIssue]:
        # Extract citations with regex
        # Check author name patterns
        # Validate publication venues
        # Return confidence scores
        """
    },
    
    "SlideContentBalanceAnalyzer": {
        "purpose": "Detect text walls and sparse slides for better readability",
        "input_spec": "(slide_html: str) -> BalanceAnalysis",
        "output_spec": "BalanceAnalysis(text_ratio: float, balance_score: float, issues: List[str], suggestions: List[str])",
        "integration": "Post-generation analysis in slide creation",
        "expected_performance": "<100ms per slide, $0.00",
        "expected_impact": "Improve readability scores by +0.3",
        "priority": "high",
        "complexity": "low",
        "implementation_template": """
class SlideContentBalanceAnalyzer:
    def analyze_balance(self, slide_html: str) -> BalanceAnalysis:
        # Count words, bullets, images
        # Calculate text-to-visual ratio
        # Identify walls of text (>150 words)
        # Suggest content redistribution
        """
    },
    
    "ChartReadabilityValidator": {
        "purpose": "Ensure charts have readable fonts and clear axes",
        "input_spec": "(chart_html: str) -> ReadabilityResult",
        "output_spec": "ReadabilityResult(readable: bool, font_size: int, issues: List[str], fixes: List[str])",
        "integration": "During chart generation in generate_slides_html()",
        "expected_performance": "~2s per chart, ~$0.02",
        "expected_impact": "Improve visual scores by +0.5",
        "priority": "medium",
        "complexity": "medium",
        "risk": "May be too slow for MVP (learn from rejected tools)",
        "implementation_template": """
class ChartReadabilityValidator:
    def validate_chart(self, chart_html: str) -> ReadabilityResult:
        # Render chart to image
        # Check font sizes, contrast
        # Validate data representation
        # Return readability score and fixes
        """
    },
    
    "VisualConsistencyChecker": {
        "purpose": "Ensure consistent fonts, colors, and layouts across slides",
        "input_spec": "(all_slides: List[str]) -> ConsistencyReport",
        "output_spec": "ConsistencyReport(consistency_score: float, issues: List[str], standardization_fixes: List[str])",
        "integration": "Final validation after all slides generated",
        "expected_performance": "~1s per presentation, $0.00",
        "expected_impact": "Improve professional design scores by +0.4",
        "priority": "medium",
        "complexity": "medium",
        "implementation_template": """
class VisualConsistencyChecker:
    def check_consistency(self, all_slides: List[str]) -> ConsistencyReport:
        # Extract visual elements
        # Compare across slides
        # Identify inconsistencies
        # Return standardization fixes
        """
    }
}

# Successful patterns to follow
SUCCESSFUL_PATTERNS = [
    "Simple Input/Output: Clear data contracts",
    "Fast Execution: <2s for real-time use",
    "Graceful Failure: Always return result, never crash",
    "Measurable Impact: Clear before/after metrics",
    "Post-Processing: Add to end of pipeline, don't disrupt flow"
]

# Failed patterns to avoid
FAILED_PATTERNS = [
    "Multi-Stage Complexity: Breaks consistency", 
    "Sequential Processing: Too slow for MVP",
    "Rigid Templates: Reduces flexibility",
    "Heavy Dependencies: Increases failure points",
    "Blocking Operations: Must be async or optional"
]

# Tool adoption criteria
ADOPTION_CRITERIA = {
    "quality_impact": "Minimum +0.2 improvement in evaluation scores",
    "speed_impact": "Maximum +10% increase in generation time",
    "cost_impact": "Maximum +5% increase in API costs", 
    "reliability": "Minimum 90% success rate",
    "complexity": "Implementation time < 1 week"
}

# Priority matrix for tool selection
PRIORITY_MATRIX = {
    ("high", "low"): "⭐ DO FIRST",
    ("high", "medium"): "🔶 DO NEXT", 
    ("medium", "low"): "✅ DO LATER",
    ("low", "high"): "❌ DON'T DO"
}