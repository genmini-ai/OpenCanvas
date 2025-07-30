# OpenCanvas Tools Specification

Machine-readable tool specifications for the evolution system. Each tool has a clear API contract that agents can understand and implement.

## 📋 Current Tools (Production)

### WebSearchTool
**Purpose**: Retrieve up-to-date information when knowledge is insufficient  
**Input**: `(query: str, max_results: int = 10) -> List[SearchResult]`  
**Output**: `SearchResult(title: str, url: str, snippet: str, relevance: float)`  
**Integration**: `TopicGenerator.assess_knowledge_depth() -> INSUFFICIENT`  
**Performance**: ~2-3s, $0.00 (Brave API)  
**Success Rate**: 85% (depends on query quality)

### WebScraperTool  
**Purpose**: Extract clean text content from web pages  
**Input**: `(url: str, timeout: int = 10) -> ScrapedContent`  
**Output**: `ScrapedContent(text: str, success: bool, error: Optional[str])`  
**Integration**: After `WebSearchTool` in research pipeline  
**Performance**: ~1-2s per URL, $0.00  
**Success Rate**: 70% (blocked by robots.txt, paywalls)

### ImageValidationTool
**Purpose**: Validate and replace broken or inappropriate images in slides  
**Input**: `(slide_html: str) -> ValidationResult`  
**Output**: `ValidationResult(fixed_html: str, replacements: int, issues: List[str])`  
**Integration**: `generate_slides_html()` post-processing  
**Performance**: ~3-5s per presentation, ~$0.05  
**Success Rate**: 85% replacement success

### PDFProcessingTool
**Purpose**: Extract and encode PDF content for presentation generation  
**Input**: `(pdf_source: str) -> PDFContent`  
**Output**: `PDFContent(text: str, base64: str, pages: int, success: bool)`  
**Integration**: `PDFGenerator.generate_presentation()`  
**Performance**: ~2-10s depending on size, $0.00  
**Success Rate**: 95% for standard PDFs

### ClaudeGenerationTool
**Purpose**: Generate presentation content using Anthropic API  
**Input**: `(prompt: str, max_tokens: int = 8000) -> GenerationResult`  
**Output**: `GenerationResult(content: str, tokens_used: int, success: bool)`  
**Integration**: Core generation in all generators  
**Performance**: ~10-15s, $0.10-0.20  
**Success Rate**: 98%

---

## ❌ Rejected Tools (Learn from Failures)

### MultiStageOutlineGenerator ❌  
**Purpose**: Generate detailed outline before slide creation  
**Failure Reason**: 2x slower, consistency issues between outline and slides  
**Pattern**: Multi-stage approaches hurt consistency in single-context systems  
**Lesson**: Prefer single-pass generation for consistency

### SlideBySlideSequentialGenerator ❌  
**Purpose**: Generate each slide individually with full context  
**Failure Reason**: 3x slower, 3x cost increase, minimal quality gain (+0.2)  
**Pattern**: Sequential processing doesn't scale for MVP requirements  
**Lesson**: Parallelism essential, context loading expensive

### TemplateMatchingSystem ❌  
**Purpose**: Match content to pre-designed slide templates  
**Failure Reason**: Rigid templates reduced flexibility, -0.3 quality score  
**Pattern**: Static templates can't adapt to diverse content needs  
**Lesson**: Dynamic generation > rigid templates

---

## 🚀 Proposed Tools (Ready for Implementation)

### CitationVerificationTool ⭐ HIGH PRIORITY
**Purpose**: Detect fake author names and non-existent publications  
**Input**: `(text: str) -> List[CitationIssue]`  
**Output**: `CitationIssue(citation: str, confidence: float, issue_type: str, suggestion: str)`  
**Integration**: Post-generation validation in `generate_slides_html()`  
**Expected Performance**: <500ms, ~$0.01 per check  
**Expected Impact**: Reduce fake citations from 20% to <2%  
**Implementation Template**:
```python
class CitationVerificationTool:
    def validate_citations(self, text: str) -> List[CitationIssue]:
        # Extract citations with regex
        # Check author name patterns
        # Validate publication venues
        # Return confidence scores
```

### SlideContentBalanceAnalyzer ⭐ HIGH PRIORITY  
**Purpose**: Detect text walls and sparse slides for better readability  
**Input**: `(slide_html: str) -> BalanceAnalysis`  
**Output**: `BalanceAnalysis(text_ratio: float, balance_score: float, issues: List[str], suggestions: List[str])`  
**Integration**: Post-generation analysis in slide creation  
**Expected Performance**: <100ms per slide, $0.00  
**Expected Impact**: Improve readability scores by +0.3  
**Implementation Template**:
```python
class SlideContentBalanceAnalyzer:
    def analyze_balance(self, slide_html: str) -> BalanceAnalysis:
        # Count words, bullets, images
        # Calculate text-to-visual ratio
        # Identify walls of text (>150 words)
        # Suggest content redistribution
```

### ChartReadabilityValidator 🔶 MEDIUM PRIORITY
**Purpose**: Ensure charts have readable fonts and clear axes  
**Input**: `(chart_html: str) -> ReadabilityResult`  
**Output**: `ReadabilityResult(readable: bool, font_size: int, issues: List[str], fixes: List[str])`  
**Integration**: During chart generation in `generate_slides_html()`  
**Expected Performance**: ~2s per chart, ~$0.02  
**Expected Impact**: Improve visual scores by +0.5  
**Risk**: May be too slow for MVP (learn from rejected tools)

### VisualConsistencyChecker 🔶 MEDIUM PRIORITY
**Purpose**: Ensure consistent fonts, colors, and layouts across slides  
**Input**: `(all_slides: List[str]) -> ConsistencyReport`  
**Output**: `ConsistencyReport(consistency_score: float, issues: List[str], standardization_fixes: List[str])`  
**Integration**: Final validation after all slides generated  
**Expected Performance**: ~1s per presentation, $0.00  
**Expected Impact**: Improve professional design scores by +0.4

---

## 🔧 Tool Implementation Patterns

### ✅ Successful Patterns (Use These)
1. **Simple Input/Output**: Clear data contracts
2. **Fast Execution**: <2s for real-time use
3. **Graceful Failure**: Always return result, never crash
4. **Measurable Impact**: Clear before/after metrics
5. **Post-Processing**: Add to end of pipeline, don't disrupt flow

### ❌ Failed Patterns (Avoid These)  
1. **Multi-Stage Complexity**: Breaks consistency
2. **Sequential Processing**: Too slow for MVP
3. **Rigid Templates**: Reduces flexibility
4. **Heavy Dependencies**: Increases failure points
5. **Blocking Operations**: Must be async or optional

### 🎯 MVP-Optimized Design
```python
class ToolTemplate:
    def process(self, input_data: InputType) -> OutputType:
        try:
            # Fast, focused processing
            result = self._core_logic(input_data)
            return OutputType(success=True, data=result)
        except Exception as e:
            # Graceful failure
            return OutputType(success=False, error=str(e))
    
    def _core_logic(self, input_data: InputType):
        # Keep this simple and fast
        pass
```

---

## 📊 Tool Selection Criteria

### Adoption Requirements
- **Quality Impact**: Minimum +0.2 improvement in evaluation scores  
- **Speed Impact**: Maximum +10% increase in generation time  
- **Cost Impact**: Maximum +5% increase in API costs  
- **Reliability**: Minimum 90% success rate  
- **Complexity**: Implementation time < 1 week  

### Priority Matrix
| Impact | Complexity | Priority | Examples |
|--------|------------|----------|----------|
| High | Low | ⭐ DO FIRST | CitationVerificationTool |
| High | Medium | 🔶 DO NEXT | ChartReadabilityValidator |
| Medium | Low | ✅ DO LATER | ContentBalanceAnalyzer |
| Low | High | ❌ DON'T DO | ComplexTemplateSystem |

---

## 🔄 Tool Development Checklist

### Before Implementation
- [ ] Clear API specification defined
- [ ] Expected performance benchmarked
- [ ] Integration points identified
- [ ] Success metrics defined
- [ ] Failure modes considered

### During Development  
- [ ] Input validation implemented
- [ ] Error handling added
- [ ] Performance optimized
- [ ] Unit tests written
- [ ] Integration tested

### Before Adoption
- [ ] A/B testing completed
- [ ] Performance verified
- [ ] Quality impact measured
- [ ] Cost impact acceptable
- [ ] Rollback plan ready