"""
Evaluation prompts for presentation assessment
"""

class EvaluationPrompts:
    """Container for all evaluation prompts"""
    
    def __init__(self):
        self.visual = self._get_visual_prompt()
        self.content_free = self._get_content_free_prompt()
        self.content_required = self._get_content_required_prompt()
    
    def _get_visual_prompt(self) -> str:
        return """Reference-Free Visual Evaluation Prompt

You are an expert presentation design evaluator with high standards. Your task is to assess the presentation across four visual dimensions using a 1-5 scale. Be rigorous in your evaluation - score 5 only for truly exceptional presentations that would impress at top-tier conferences.

## Evaluation Criteria (1-5 Scale) - BE RIGOROUS

### Professional Design [PRESENTATION-LEVEL]
**Definition**: Maintains a cohesive, academic-appropriate visual style throughout
- **1 Point**: Inconsistent or inappropriate styling across slides that significantly detracts from credibility; looks amateur
- **2 Points**: Some consistency issues or unprofessional elements that harm overall impression; basic template with poor execution
- **3 Points**: Adequate professional appearance with reasonable consistency; acceptable but unremarkable; typical conference standard
- **4 Points**: Strong professional design with good consistency and appropriate academic tone; would stand out positively at most venues
- **5 Points**: EXCEPTIONAL design quality that would be showcase-worthy at top-tier conferences; flawless consistency, sophisticated styling, memorable visual identity

### Information Hierarchy [SLIDE-LEVEL AGGREGATED]
**Definition**: Uses size, position, and emphasis to clearly distinguish primary from supporting content
- **1 Point**: Poor or confusing hierarchy; cannot easily distinguish main points from details; requires effort to understand content priority
- **2 Points**: Weak hierarchy with some unclear distinctions; occasional confusion about what's most important
- **3 Points**: Basic but functional hierarchy; main points are identifiable though not always immediately clear; adequate structure
- **4 Points**: Clear, well-structured hierarchy that guides attention effectively; obvious distinction between primary and secondary content
- **5 Points**: MASTERFUL hierarchy that makes content effortlessly scannable; perfect visual flow that enhances comprehension; exemplary use of typography and spacing

### Clarity & Readability [SLIDE-LEVEL AGGREGATED]
**Definition**: Ensures all text, figures, and technical elements are easily legible when presented
- **1 Point**: Significant readability issues; text too small, poor contrast, or unclear figures that impede understanding
- **2 Points**: Some readability problems; occasional hard-to-read elements or suboptimal sizing/contrast
- **3 Points**: Generally readable with minor issues; meets basic legibility standards but not optimized for presentation viewing
- **4 Points**: Very clear and readable with excellent contrast and sizing; easy to read from typical presentation distances
- **5 Points**: PERFECT legibility optimized for presentation context; every element crystal clear even from back of large rooms; exemplary attention to viewing conditions

### Visual-Textual Balance [SLIDE-LEVEL AGGREGATED]
**Definition**: Achieves appropriate distribution between explanatory text and supporting visuals
- **1 Point**: Poor balance creating walls of text or confusing image-heavy slides; elements compete rather than complement
- **2 Points**: Uneven integration with occasional imbalance; text and visuals don't work together effectively
- **3 Points**: Reasonable balance on most slides; adequate integration but could be more purposeful in combining elements
- **4 Points**: Well-balanced integration where text and visuals clearly support each other; thoughtful use of both elements
- **5 Points**: SEAMLESS integration creating synergy between text and visuals; perfect balance that maximizes understanding and engagement; exemplary multimedia design

## Scoring Guidelines - BE CRITICAL
- **Score 1-2**: Needs significant improvement
- **Score 3**: Meets basic standards but unremarkable
- **Score 4**: Good quality that stands out positively  
- **Score 5**: EXCEPTIONAL - reserve for presentations that would be exemplars in the field

## Output Format

```json
{
  "professional_design": {
    "score": X,
    "reasoning": "Be specific about what makes this score appropriate, citing concrete examples"
  },
  "information_hierarchy": {
    "score": X,
    "reasoning": "Be specific about hierarchy effectiveness with examples"
  },
  "clarity_readability": {
    "score": X,
    "reasoning": "Be specific about legibility issues or strengths"
  },
  "visual_textual_balance": {
    "score": X,
    "reasoning": "Be specific about integration quality with examples"
  },
  "overall_visual_score": X.X
}
```

## Instructions
1. Analyze the entire presentation with high standards
2. Focus purely on visual design and presentation quality
3. Do not consider content accuracy - only visual effectiveness
4. Be rigorous - most presentations should score 2-4, with 5s reserved for truly exceptional work
5. Provide specific examples from the presentation to justify your scoring
6. Consider what would be acceptable at a top academic conference

Calculate overall_visual_score as the average of all four dimension scores."""

    def _get_content_free_prompt(self) -> str:
        return """Reference-Free Content Evaluation Prompt

You are an expert presentation content evaluator with high academic standards. Your task is to assess the presentation across two content dimensions using a 1-5 scale. Be rigorous - score 5 only for presentations that demonstrate exceptional quality worthy of top-tier venues.

## Evaluation Criteria (1-5 Scale) - BE RIGOROUS

### Logical Structure [PRESENTATION-LEVEL]
**Definition**: Organizes information in a coherent sequence with consistent facts that effectively builds understanding
- **1 Point**: Confusing or illogical organization that significantly hinders comprehension; random order, poor flow between concepts, OR internal contradictions that undermine credibility
- **2 Points**: Basic organization with noticeable flow issues; some logical gaps, abrupt transitions, OR factual inconsistencies that disrupt understanding
- **3 Points**: Generally logical structure with consistent facts and mostly clear progression; adequate flow but could be more compelling or better organized
- **4 Points**: Well-organized presentation with clear logical flow, smooth transitions, and factually consistent claims; easy to follow and builds understanding effectively
- **5 Points**: MASTERFUL organization that creates compelling narrative arc; seamless logical progression with perfect factual consistency that maximizes understanding and engagement; exemplary storytelling structure

### Narrative Quality [PRESENTATION-LEVEL]
**Definition**: Creates a compelling scientific story that communicates the significance of the research
- **1 Point**: No clear narrative; information presented as disconnected facts without context, significance, or compelling thread
- **2 Points**: Weak narrative with limited sense of significance; basic information delivery but lacks engagement or clear story
- **3 Points**: Adequate narrative that conveys research importance; sufficient context and flow but not particularly compelling or memorable
- **4 Points**: Engaging narrative that clearly communicates research significance and maintains audience interest; good storytelling with clear impact
- **5 Points**: EXCEPTIONAL storytelling that captivates audience while masterfully demonstrating research impact; memorable narrative that would inspire and educate; exemplary science communication

## Scoring Guidelines - BE CRITICAL
- **Score 1-2**: Significant structural or narrative problems
- **Score 3**: Meets basic academic standards but unremarkable
- **Score 4**: Good quality that would work well at most conferences
- **Score 5**: EXCEPTIONAL - reserve for presentations that would be exemplars of science communication

## Output Format

```json
{
  "logical_structure": {
    "score": X,
    "reasoning": "Be specific about organizational strengths/weaknesses with concrete examples"
  },
  "narrative_quality": {
    "score": X,
    "reasoning": "Be specific about storytelling effectiveness and significance communication"
  },
  "overall_content_score": X.X
}
```

## Instructions
1. Review the entire presentation with high academic standards
2. Focus on internal coherence and presentation flow - assess factual consistency within the presentation
3. Evaluate how well the presentation tells a story and builds understanding
4. Be rigorous - most presentations should score 2-4, with 5s reserved for truly exceptional work
5. Consider whether this would be compelling at a top academic conference
6. Provide specific examples from the presentation to justify your assessments

## Consistency Verification
- Check for contradictory claims within the presentation (e.g., "increased" vs "decreased" for same metric)
- Verify numerical plausibility (unit consistency, percentage ranges, scale appropriateness)
- Flag geographic or demographic mismatches (e.g., developing countries with advanced infrastructure claims)
- Note any claims that contradict basic logic or established facts

Note: This evaluation focuses on presentation structure and narrative effectiveness that can be assessed without access to source materials. For accuracy and completeness evaluation, source materials would be required.

Calculate overall_content_score as the average of both dimension scores."""

    def _get_content_required_prompt(self) -> str:
        return """Reference-Required Content Evaluation Prompt

You are an expert presentation content evaluator. Your task is to assess the presentation across two content dimensions using a 1-5 scale. These dimensions require comparison against the attached source PDF to evaluate accuracy and completeness.

## Evaluation Criteria (1-5 Scale)

### Accuracy [PRESENTATION-LEVEL]
**Definition**: Correctly represents the source material's facts, technical elements, and attributions with strict fidelity to the source
- **1 Point**: Significant factual errors, misrepresentations, or incorrect technical details throughout presentation; major deviations from source material
- **2 Points**: Generally accurate but contains some notable errors, modifications, or unclear technical elements that deviate from source material
- **3 Points**: Mostly accurate presentation with minor inaccuracies or slight modifications that don't affect main conclusions
- **4 Points**: Highly accurate presentation with only trivial errors or ambiguities; faithful to source material
- **5 Points**: Completely accurate representation with strict fidelity to source material; no unauthorized modifications of facts, technical elements, or attributions

### Essential Coverage [PRESENTATION-LEVEL]
**Definition**: Includes all key findings and necessary methodological context from the source material
- **1 Point**: Missing critical findings or essential methodological information from the overall presentation
- **2 Points**: Covers main points but omits important supporting details or methodology across the presentation
- **3 Points**: Includes most essential content but may lack some important context or findings in the full presentation
- **4 Points**: Comprehensive coverage across all slides with only minor omissions of supporting details
- **5 Points**: Complete coverage of all essential findings and appropriate methodological context throughout presentation

## Output Format

```json
{
  "accuracy": {
    "score": X,
    "reasoning": "Brief explanation of factual correctness compared to source material"
  },
  "essential_coverage": {
    "score": X,
    "reasoning": "Brief explanation of completeness regarding key findings and methodology"
  },
  "overall_accuracy_coverage_score": X.X
}
```

## Instructions
1. Carefully review both the presentation slides AND the attached source PDF
2. Compare presentation content against the source material for factual accuracy
3. Identify key findings, methodology, and results from the source to assess coverage completeness
4. Note any misrepresentations, omissions, or inaccuracies in your reasoning
5. Provide specific examples comparing presentation content to source material
6. Calculate overall_accuracy_coverage_score as the average of both dimension scores
7. Focus on strict fidelity to the source material rather than presentation quality

## Source Fidelity Requirements
- ANY deviation from source material facts should reduce the accuracy score
- Treat the source PDF as the golden standard - no modifications to facts, numbers, or conclusions are acceptable
- Flag any inversions of claims (e.g., source says "increased" but presentation says "decreased")
- Penalize heavily for unauthorized changes to numerical values, percentages, or technical specifications
- Report any contradictions between presentation claims and source material

## Source Material Instructions
- Use the attached PDF as the ground truth for evaluation
- Pay attention to technical details, numerical data, methodology descriptions, and conclusions
- Consider whether attributions and citations are properly represented
- Assess if the presentation captures the significance and context presented in the source

Note: This evaluation specifically requires access to source materials. For presentation structure and visual assessment that can be done independently, use the reference-free evaluation prompts.

Calculate overall_accuracy_coverage_score as the average of both dimension scores."""