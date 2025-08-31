import os
import json
import webbrowser
import requests
from pathlib import Path
from anthropic import Anthropic
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import logging

from opencanvas.generators.base import BaseGenerator
from opencanvas.config import Config
from opencanvas.image_validation import ImageValidationPipeline

logger = logging.getLogger(__name__)

# Import evolution tool pipeline (lazy import to avoid circular dependencies)
TOOL_PIPELINE_AVAILABLE = False
ToolStage = None
get_tool_pipeline = None

def _import_tool_pipeline():
    """Lazy import of tool pipeline to avoid circular dependencies"""
    global TOOL_PIPELINE_AVAILABLE, ToolStage, get_tool_pipeline
    if not TOOL_PIPELINE_AVAILABLE:
        try:
            from opencanvas.evolution.core.tool_pipeline import get_tool_pipeline as _get_pipeline, ToolStage as _ToolStage
            get_tool_pipeline = _get_pipeline
            ToolStage = _ToolStage
            TOOL_PIPELINE_AVAILABLE = True
            logger.info("Evolution tool pipeline imported successfully")
        except ImportError as e:
            logger.info(f"Evolution tool pipeline not available: {e}")

class TopicGenerator(BaseGenerator):
    def __init__(self, api_key, brave_api_key=None, enable_image_validation=True, enable_evolution_tools=True, prompt_version=None, skip_prompt_loading=False):
        """Initialize the topic-based slide generator with Anthropic API key and optional Brave API key"""
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)
        self.brave_api_key = brave_api_key or os.getenv('BRAVE_API_KEY')
        
        # Load the appropriate prompt (evolved or baseline) unless skipped
        if not skip_prompt_loading:
            self.generation_prompt = self._load_generation_prompt(prompt_version)
        else:
            logger.info("⏭️ Skipping automatic prompt loading (will be set by evolved router)")
            self.generation_prompt = None  # Will be set by EvolvedTopicGenerator
        
        # Initialize image validation pipeline
        self.enable_image_validation = enable_image_validation
        if self.enable_image_validation:
            try:
                # Let ImageValidationPipeline load API key from config/env
                self.image_validator = ImageValidationPipeline()
                logger.info("✅ Image validation pipeline initialized")
            except Exception as e:
                logger.warning(f"⚠️ Image validation disabled due to error: {e}")
                self.enable_image_validation = False
        
        # Initialize evolution tool pipeline
        self.enable_evolution_tools = enable_evolution_tools
        if self.enable_evolution_tools:
            try:
                # Lazy import to avoid circular dependencies
                _import_tool_pipeline()
                if TOOL_PIPELINE_AVAILABLE:
                    self.tool_pipeline = get_tool_pipeline()
                    # Load evolution tools if they exist
                    self._load_evolution_tools()
                    logger.info("✅ Evolution tool pipeline initialized")
                else:
                    self.enable_evolution_tools = False
            except Exception as e:
                logger.warning(f"⚠️ Evolution tools disabled due to error: {e}")
                self.enable_evolution_tools = False
    
    def _load_evolution_tools(self):
        """Load evolution tools from available iterations"""
        if not self.enable_evolution_tools:
            return
        
        # Check for evolution tools directories
        from pathlib import Path
        tools_base = Path("src/opencanvas/evolution/tools")
        
        if tools_base.exists():
            # Load tools from each iteration directory
            for iteration_dir in sorted(tools_base.glob("iteration_*")):
                if iteration_dir.is_dir():
                    iteration_num = int(iteration_dir.name.split("_")[-1])
                    tools_loaded = self.tool_pipeline.load_evolution_tools(iteration_num)
                    if tools_loaded > 0:
                        logger.info(f"  Loaded {tools_loaded} tools from iteration {iteration_num}")
        
        # Log pipeline status
        status = self.tool_pipeline.get_pipeline_status()
        logger.info(f"  Total tools in pipeline: {status['total_tools']}")
        
    def assess_knowledge_depth(self, user_text):
        """Check if Claude has enough knowledge to write an in-depth blog post"""
        assessment_prompt = f"""Analyze whether you have sufficient knowledge to write a comprehensive, in-depth blog post (800-1200 words) about the following topic:

Topic: {user_text}

Please respond with ONLY one of these two options:
1. "SUFFICIENT" - if you have enough detailed knowledge to write a comprehensive blog post
2. "INSUFFICIENT" - if you need additional research to write a quality in-depth blog post

Consider factors like:
- Depth of your knowledge on this topic
- Recency of information needed
- Specificity of the topic
- Whether this requires current data, statistics, or recent developments

Your response should be exactly one word: either "SUFFICIENT" or "INSUFFICIENT"
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                temperature=0.1,
                messages=[{"role": "user", "content": assessment_prompt}]
            )
            return response.content[0].text.strip().upper()
        except Exception as e:
            logger.error(f"Error assessing knowledge: {e}")
            return "SUFFICIENT"  # Default to sufficient if error occurs
    
    def generate_search_query(self, user_text):
        """Generate an optimized search query for the topic"""
        search_prompt = f"""Generate a single, optimized search query to find the most authoritative and comprehensive information about this topic:

Topic: {user_text}

Create a search query that will help find:
- Authoritative sources (academic, government, established organizations)
- Comprehensive information
- Recent and relevant content

Note that there might be typos in the user input; please decide based on context. Respond with ONLY the search query, nothing else. Make it 3-8 words maximum.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                temperature=0.1,
                messages=[{"role": "user", "content": search_prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return user_text  # Fallback to original text
    
    def web_search(self, query, brave_api_key=None):
        """Perform web search using Brave Search API"""
        if not brave_api_key:
            logger.warning("⚠️  Brave API key not provided. Set BRAVE_API_KEY environment variable or pass it as parameter.")
            return []
        
        try:
            logger.info(f"🔍 Searching with Brave API: {query}")
            
            url = "https://api.search.brave.com/res/v1/web/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": brave_api_key
            }
            
            params = {
                "q": query,
                "count": 10,  # Number of results to return
                "offset": 0,  # Starting offset
                "mkt": "en-US",  # Market/language
                "safesearch": "moderate",  # Safe search level
                "freshness": "pw",  # Past week for fresher content
                "text_decorations": False,  # Don't include text decorations
                "spellcheck": True  # Enable spell checking
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract web results
            web_results = data.get("web", {}).get("results", [])
            
            if not web_results:
                logger.warning("❌ No search results found")
                return []
            
            logger.info(f"✅ Found {len(web_results)} search results")
            
            # Convert to a standard format
            formatted_results = []
            for result in web_results:
                formatted_result = {
                    'title': result.get('title', ''),
                    'link': result.get('url', ''),
                    'snippet': result.get('description', ''),
                    'display_url': result.get('url', ''),
                    'age': result.get('age', ''),
                    'language': result.get('language', 'en')
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error performing search: {e}")
            return []
    
    def assess_source_credibility(self, search_results):
        """Assess and rank search results by credibility"""
        if not search_results:
            return []
        
        # Create a prompt to assess credibility
        results_text = ""
        for i, result in enumerate(search_results[:5]):  # Limit to top 5 results
            results_text += f"{i+1}. Title: {result.get('title', 'N/A')}\n"
            results_text += f"   URL: {result.get('link', 'N/A')}\n"
            results_text += f"   Snippet: {result.get('snippet', 'N/A')}\n\n"
        
        credibility_prompt = f"""Analyze these search results and identify the TOP 2 most relevant and useful sources for comprehensive information about the topic:

{results_text}

Rank them by prioritizing:
1. RELEVANCE: How directly related to the topic and comprehensive the content appears
2. USEFULNESS: How much the source would help someone understand the subject matter
3. CONTENT DEPTH: Evidence of detailed, in-depth coverage
4. SOURCE QUALITY: Domain authority (.edu, .gov, established organizations, expert authors)

Focus on finding the sources that would be most educational and informative for someone learning about this topic.

Respond with ONLY two numbers separated by a comma (e.g., "2,4") representing the two best sources in order of preference.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50,
                temperature=0.1,
                messages=[{"role": "user", "content": credibility_prompt}]
            )
            
            choice = response.content[0].text.strip()
            
            # Parse the response to get two numbers
            import re
            numbers = re.findall(r'\d+', choice)
            
            selected_sources = []
            for num_str in numbers[:2]:  # Take only first 2 numbers
                choice_num = int(num_str)
                if 1 <= choice_num <= len(search_results):
                    selected_sources.append(search_results[choice_num - 1])
            
            # If we don't have 2 sources, add the first one as fallback
            if len(selected_sources) == 0 and search_results:
                selected_sources.append(search_results[0])
            elif len(selected_sources) == 1 and len(search_results) > 1:
                # Add second source if we only got one
                for result in search_results[:2]:
                    if result not in selected_sources:
                        selected_sources.append(result)
                        break
                        
            return selected_sources
                
        except Exception as e:
            logger.error(f"Error assessing credibility: {e}")
            return search_results[:2] if len(search_results) >= 2 else search_results
    
    def scrape_web_content(self, url):
        """Scrape content from a web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logger.info(f"🌐 Scraping content from: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article', 'main', '.content', '#content', 
                '.post-content', '.entry-content', '.article-content'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    content_text = content_elements[0].get_text()
                    break
            
            # If no specific content area found, get all text
            if not content_text:
                content_text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in content_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length to avoid token limits
            if len(content_text) > 8000:
                content_text = content_text[:8000] + "..."
            
            return content_text
            
        except Exception as e:
            logger.error(f"Error scraping content: {e}")
            return None
    
    def generate_blog(self, user_text, additional_context=None):
        """Generate educational blog content from user text, optionally with additional context"""
        
        if additional_context:
            blog_prompt = f"""Write an educational blog based on the following user-provided text, using the additional research context provided.

IMPORTANT: Stay focused on the user's specific topic. Only use information from the additional context that is directly relevant to the user's topic.

User topic: {user_text}

Additional research context from credible sources:
{additional_context}

The blog should be:
- In the same language as the user's input
- Focused primarily on the user's specific topic: "{user_text}"
- Self-contained and comprehensive about this topic
- Well-structured with clear sections
- Educational and informative
- Engaging for readers
- Between 800-1200 words
- Incorporate ONLY the relevant information from the research context that relates to the user's topic
- Cite key facts appropriately when using information from the sources

Guidelines for using additional context:
- Filter the research content to include only what's directly relevant to "{user_text}"
- Don't go off on tangents about unrelated information from the sources
- Use the additional context to enhance and support your explanation of the user's topic
- Maintain focus on what the user actually asked about

Please write a complete educational blog post that stays focused on the user's topic while incorporating relevant insights from the research.
"""
        else:
            blog_prompt = f"""Write an educational blog based on the following user-provided text. The text may be a topic or a long sentence. 
            The blog should be:
            - Self-contained and comprehensive
            - Well-structured with clear sections
            - Educational and informative
            - Engaging for readers
            - Between 800-1200 words
            
            User text: {user_text}
            
            Please write a complete educational blog post.
            """
        
        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                temperature=0.2,
                messages=[{"role": "user", "content": blog_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            return None

    def _load_generation_prompt(self, prompt_version=None):
        """Load generation prompt from file (evolved or baseline)"""
        try:
            # If specific version requested, try to load it
            if prompt_version:
                version_file = Path(f"evolution_runs/evolved_prompts/generation_prompt_v{prompt_version}.txt")
                if version_file.exists():
                    prompt = version_file.read_text()
                    logger.info(f"📝 Loaded specific prompt version v{prompt_version}")
                    return prompt
                else:
                    logger.warning(f"Requested prompt version v{prompt_version} not found, falling back to latest")
            
            # No random loading from global evolved prompts during evolution
            # Evolution system manages prompt loading explicitly
            
            # Fall back to baseline prompt
            baseline_file = Path("src/opencanvas/prompts/baseline/generation_prompt.txt")
            if baseline_file.exists():
                prompt = baseline_file.read_text()
                logger.info("📝 Loaded baseline prompt from file")
                return prompt
            
            # Final fallback to hardcoded prompt
            logger.warning("No prompt files found, using hardcoded fallback")
            return self._get_hardcoded_prompt()
            
        except Exception as e:
            logger.error(f"Failed to load generation prompt: {e}")
            return self._get_hardcoded_prompt()
    
    def _get_hardcoded_prompt(self):
        """Get the hardcoded prompt as final fallback"""
        return """<presentation_task>
Create a stunning, visually captivating HTML presentation that makes viewers stop and say "wow" based on this content:

{blog_content}

Purpose of presentation: {purpose}
Visual theme: {theme}
</presentation_task>

<design_philosophy>
CREATE EMOTIONAL IMPACT:
- Prioritize the "wow factor" through unexpected visual moments and reveals
- Make every slide feel alive with purposeful animations that enhance content meaning
- Choose bold, vibrant colors with strategic contrast to guide viewer attention
- Implement premium design elements (glassmorphism, 3D depth, gradient overlays, micro-animations)
- Create visual storytelling that builds emotional connection through cohesive visual narrative
- Develop a premium, cutting-edge experience with polished transitions and interactions
- Ensure each visual element directly reinforces key messages rather than serving as decoration
</design_philosophy>

<visual_requirements>
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library) with ONLY opacity-based animations (opacity: 0 to opacity: 1)
3. Implement a sophisticated color scheme with 3-5 complementary colors that reinforce the "{theme}" theme
4. Include micro-interactions: hover effects, animated reveals, and subtle cursor-following elements
5. Use expressive, modern typography with varied font weights, sizes, and strategic text highlighting
6. Add layered visual depth through glassmorphism effects (backdrop-filter: blur(8px)), drop shadows, and z-index manipulation
7. Create elegant slide transitions with directional purpose (reveal new content logically)
8. Design 10-15 slides following a 6-column grid system with dynamic layouts that vary between left-aligned, centered, and asymmetrical compositions
9. Implement progressive disclosure with animated bullet points (3-5 per slide maximum)
10. Create an immersive title slide with animated brand elements and visually distinct section dividers
11. Optimize for 1280px × 720px with responsive scaling and graceful element repositioning
12. Add subtle background animations that reinforce slide content and enhance emotional impact
13. Ensure all content fits within 720px height with proper visual hierarchy and breathing space
14. Limit text to 60-80 characters per line with maximum 5-7 lines per slide
15. Create balanced visual layouts with 60% visuals to 40% text ratio using high-quality imagery from Unsplash
16. Use variable opacity levels (20%, 40%, 60%, 80%, 100%) to create visual hierarchy and depth
17. Use visual metaphors that transform abstract concepts into memorable visual elements
18. Implement consistent visual cues for navigation (subtle arrows or indicators)
19. Create custom animated icons that visually represent key concepts
</visual_requirements>

<slide_structure>
- Each slide MUST use a consistent class structure: <div class="slide"> for all slides
- ALL slides MUST transition using ONLY opacity (opacity: 0 to opacity: 1)
- Apply .active class to visible slides (opacity: 1) and inactive to hidden slides (opacity: 0)
- Maintain flat DOM hierarchy - do NOT nest slides within complex containers
- Each slide MUST have a unique ID (slide-1, slide-2, etc.) for navigation tracking
- Use consistent z-index management (base: 1, active: 10) to prevent slide overlap
- Implement standard keyboard navigation (left/right arrows) that works for ALL slides
- Structure ALL slides with this pattern:
  ```html
  <div id="slide-X" class="slide">
    <div class="slide-content">
      <!-- Content here -->
    </div>
  </div>
  ```
- Test navigation thoroughly to verify ALL slides are accessible with arrow keys
</slide_structure>

<content_presentation>
- Transform key points into visual metaphors with supporting icons and graphics
- Structure content with the 3-second rule: viewers should grasp the main point within 3 seconds
- Use the "rule of three" for content organization with progressive reveal animations
- Create clear visual hierarchy through size, color, weight, and positioning
- Include elegant progress indicators that show both current position and total journey
- Break complex ideas into visual frameworks: timelines, process flows, comparison matrices
- Implement the "less is more" principle: one key message per slide with supporting elements
- Create a narrative arc with clear beginning, middle, and end to maintain viewer engagement
- Use strategic repetition of visual motifs to reinforce key themes throughout the presentation
- Incorporate meaningful transitions that visually connect related concepts across slides
- PRESERVE the original structure and hierarchy of the source content
- NEVER reorganize content in ways that change the meaning or emphasis of the original
- Maintain the exact sequence and relationship between main points and supporting details
- Create a visual table of contents slide that previews the presentation structure
- Use consistent visual language for similar concepts throughout the presentation
</content_presentation>

<content_enhancements>
- For data analysis: Create animated charts with staged reveals that tell a clear data story
- For travel content: Implement immersive destination showcases with subtle parallax effects and location markers
- For workshops: Design interactive concept models with animated process flows and visual checkpoints
- For technical content: Create visual code blocks with syntax highlighting and animated execution flows
- For case studies: Develop before/after comparisons with sliding reveals and outcome highlights
- For general content: Use contextually relevant imagery that amplifies rather than merely decorates
- For key statistics: Create dramatic visual counters or comparisons that emphasize significance
- For complex processes: Develop step-by-step visual sequences with clear progression indicators
- For testimonials: Design elegant quote displays with subtle animations that highlight key phrases
- For all content types: Ensure visual elements directly support the exact meaning in the source material
- For key concepts: Create memorable visual anchors that recur throughout the presentation
- For important distinctions: Use side-by-side comparisons with clear visual differentiation
</content_enhancements>

<technical_excellence>
- Implement advanced CSS: variable fonts, backdrop-filter, clip-path, CSS Grid, custom properties
- Create smooth animations using GSAP-inspired techniques with proper easing functions
- Add keyboard navigation with visual indicators and touch/swipe support
- Implement progressive loading with elegant preloaders for media elements
- Ensure smooth performance with requestAnimationFrame and CSS will-change property
- Use CSS custom properties for theme consistency and potential customization
- Implement strategic use of CSS transforms for 3D effects that create depth without overwhelming
- Optimize animation timing functions to create natural, organic movement patterns
- Ensure ALL slides are accessible with standard arrow key navigation
- Use ONLY opacity-based transitions (opacity: 0 to opacity: 1) for slide navigation
- Apply .active class consistently across all slides for navigation compatibility
- DO NOT use transform-based transitions for slide navigation
- Test all slides to verify arrow key navigation works throughout the entire presentation
- Implement consistent slide structure with predictable class naming conventions
- Use data-attributes for semantic markup and easier JavaScript targeting
</technical_excellence>

<motion_design>
- Apply the 12 principles of animation for natural, purposeful movement
- Create staggered entrance animations with 150-300ms delays between elements
- Implement subtle parallax effects (0.1-0.3 factor) for depth perception
- Add entrance animations that reinforce content meaning (growth for positive trends, etc.)
- Design seamless transitions that maintain context between slides
- Use subtle continuous motion (3-5px) for background elements to create "living" slides
- Implement reveal animations that build anticipation and guide attention to key content
- Create micro-animations that respond to user interactions, enhancing engagement
- Use motion to establish visual relationships between related content elements
- NEVER mix different animation methods that could break slide navigation
- Ensure all animations complete within 800ms to maintain presentation pace
- Use consistent easing functions (cubic-bezier(0.25, 0.1, 0.25, 1)) for all animations
- Create animated visual cues that guide viewers through complex information
- Implement subtle background animations that don't compete with foreground content
</motion_design>

<visual_design_patterns>
- Create visual rhythm through consistent spacing (8px, 16px, 24px, 32px, 48px)
- Implement the 60-30-10 color rule (60% primary, 30% secondary, 10% accent)
- Use the golden ratio (1:1.618) for proportional layout divisions
- Apply the rule of thirds for balanced image and text placement
- Create focal points using size contrast (1x, 2x, 4x scale relationships)
- Implement F-pattern and Z-pattern reading flows based on content type
- Use whitespace strategically to create breathing room around key elements
- Create depth through layering with 3-5 distinct z-index levels
- Apply consistent corner radius (4px, 8px, 12px) for related elements
- Use shadow elevation system (2px, 4px, 8px, 16px) to indicate hierarchy
- Implement consistent iconography style (outline, filled, duotone)
- Create visual anchors that recur throughout the presentation
- Use color psychology intentionally (warm colors for energy, cool for trust)
- Apply the 4:1 minimum contrast ratio for all text elements
</visual_design_patterns>

<critical_accuracy_requirements>
- NEVER add numerical data, statistics, or percentages not explicitly stated in the source
- If source says "improved" or "increased" without numbers, DO NOT invent percentages
- Maintain the exact meaning and emphasis of the original content
- Preserve all factual information exactly as presented in the source
- Do not elevate examples to main categories or change the content hierarchy
- If uncertain about a fact or figure, omit rather than fabricate
- Verify all content against source material before finalizing slides
- NEVER create charts or graphs with specific values unless those exact values appear in the source
- DO NOT invent testimonials, quotes, or endorsements not present in the original content
- Maintain the original relationship between main points and supporting details
- NEVER add fictional case studies or examples not mentioned in the source
- DO NOT create visual representations that imply specific metrics not in the source
- Preserve the original tone and perspective of the content
</critical_accuracy_requirements>

<navigation_compatibility>
- CRITICAL: Implement ONLY opacity-based slide transitions (opacity: 0 → 1)
- DO NOT use transform-based transitions (translate, scale, rotate) for slide navigation
- Maintain flat DOM structure for slides (no deep nesting that breaks navigation)
- Use consistent class naming (.slide, .active) across ALL slides
- Implement standard keyboard handlers (left/right arrows) that work for ALL slides
- Test navigation thoroughly to verify ALL slides are accessible with arrow keys
- Ensure slide content appears/disappears with opacity transitions only
- Verify that .active class properly controls slide visibility
- DO NOT implement competing navigation systems that could conflict
- Maintain z-index consistency to prevent slide overlap issues
- Ensure all interactive elements maintain proper tab order for accessibility
- Test navigation with keyboard, mouse, and touch inputs before finalizing
</navigation_compatibility>

<content_verification_checklist>
1. All numerical data comes directly from source (no invented statistics)
2. Original content structure and hierarchy is preserved
3. No fabricated percentages, improvements, or metrics
4. Key messages maintain their original emphasis and importance
5. Examples remain as examples, not elevated to main points
6. All slides are accessible with standard arrow key navigation
7. Opacity-based transitions are used consistently
8. Visual elements directly support and enhance the original content
9. No invented testimonials or quotes
10. Main points and supporting details maintain their original relationship
11. All slides have consistent class structure for navigation
12. Arrow key navigation works for ALL slides in the presentation
13. No fictional case studies or examples added
14. Visual representations accurately reflect source information
15. Original tone and perspective maintained
</content_verification_checklist>

<visual_quality_checklist>
1. Color scheme uses 3-5 complementary colors that reinforce the theme
2. Typography is expressive and modern with varied weights and sizes
3. Visual hierarchy is clear through size, color, weight, and positioning
4. Layouts follow the 6-column grid system with dynamic compositions
5. Glassmorphism effects use backdrop-filter: blur(8px) consistently
6. Text is limited to 60-80 characters per line with 5-7 lines maximum per slide
7. Visual layouts maintain 60% visuals to 40% text ratio
8. Variable opacity levels (20%, 40%, 60%, 80%, 100%) create depth
9. All animations use consistent easing functions
10. Micro-interactions respond to user actions enhancing engagement
11. Visual metaphors effectively transform abstract concepts
12. Progress indicators clearly show current position and total journey
13. Whitespace is used strategically to create visual breathing room
14. Color contrast meets 4:1 minimum ratio for all text elements
15. Visual elements align to the 6-column grid system consistently
16. Focal points are created through size contrast and positioning
17. Shadow elevation system creates consistent depth perception
18. Corner radius is applied consistently across related elements
</visual_quality_checklist>

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser and immediately impresses with its visual sophistication.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
</output_requirements>"""
    
    def _load_evolved_prompt(self):
        """Load the latest evolved prompt if available (legacy method for backward compatibility)"""
        try:
            evolved_dir = Path("evolution_runs") / "evolved_prompts"
            if not evolved_dir.exists():
                return None
            
            # Legacy method - should not randomly load evolved prompts
            logger.warning("_load_evolved_prompt called - this should be managed by evolution system")
            return None
            
            logger.info(f"📝 Using evolved prompt from {latest_file.name}")
            return evolved_prompt
            
        except Exception as e:
            logger.warning(f"Could not load evolved prompt: {e}")
            return None
    
    def generate_slides_html(self, blog_content, purpose, theme):
        """Generate HTML slide deck from blog content"""
        
        # Use the prompt loaded during initialization
        slide_prompt = self.generation_prompt.format(
            blog_content=blog_content,
            purpose=purpose,
            theme=theme
        )
        try:
            logger.info("📡 Using streaming for slide generation...")
            
            # Use streaming for long operations
            stream = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50000,
                temperature=0.5,
                stream=True,
                messages=[{"role": "user", "content": slide_prompt}]
            )
            
            # Collect the streamed response
            html_content = ""
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    html_content += chunk.delta.text
                    # Log progress every 1000 characters
                    if len(html_content) % 1000 == 0:
                        logger.info(f"📝 Generated {len(html_content)} characters...")
            
            logger.info(f"✅ Completed generation: {len(html_content)} characters")
            
            # Clean up HTML if wrapped in code blocks
            return self.clean_html_content(html_content)
        except Exception as e:
            logger.error(f"Error generating slides: {e}")
            return None
    
    def generate_from_topic(self, user_text, purpose, theme="professional blue", output_dir=str(Config.OUTPUT_DIR)):
        """Generate presentation from a topic/text with organized file structure"""
        from opencanvas.utils.file_utils import generate_topic_slug, organize_pipeline_outputs
        from opencanvas.config import Config
        
        logger.info(f"🚀 Starting topic-based presentation generation...")
        logger.info(f"📝 User text: {user_text}")
        logger.info(f"🎯 Purpose: {purpose}")
        logger.info(f"🎨 Theme: {theme}")
        
        # Generate topic slug and timestamp for organized naming
        topic_slug = generate_topic_slug(user_text)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
        
        logger.info(f"📂 Topic slug: {topic_slug}")
        logger.info(f"📁 Output directory: {output_path}")
        
        # Step 1: Assess knowledge depth
        logger.info("\n🧠 Assessing knowledge depth...")
        knowledge_assessment = self.assess_knowledge_depth(user_text)
        logger.info(f"📊 Knowledge assessment: {knowledge_assessment}")
        
        additional_context = None
        
        # Step 2: If insufficient knowledge, perform web research
        if knowledge_assessment == "INSUFFICIENT":
            logger.info("\n🔍 Insufficient knowledge detected. Initiating web research...")
            
            # Generate search query
            search_query = self.generate_search_query(user_text)
            logger.info(f"🔎 Search query: {search_query}")
            
            # Perform web search
            search_results = self.web_search(search_query, self.brave_api_key)
            
            if search_results:
                # Assess source credibility and select best sources
                best_sources = self.assess_source_credibility(search_results)
                
                if best_sources:
                    additional_context_parts = []
                    
                    for i, source in enumerate(best_sources[:2]):  # Ensure we only process 2 sources
                        logger.info(f"🏆 Selected source {i+1}: {source.get('title', 'N/A')}")
                        logger.info(f"🔗 URL: {source.get('link', 'N/A')}")
                        
                        # Scrape content from each source
                        scraped_content = self.scrape_web_content(source.get('link'))
                        
                        if scraped_content:
                            additional_context_parts.append(f"Source {i+1} - {source.get('title', 'Unknown')}:\n{scraped_content}")
                            logger.info(f"✅ Successfully gathered content from source {i+1} ({len(scraped_content)} characters)")
                        else:
                            logger.warning(f"❌ Failed to scrape content from source {i+1}")
                    
                    if additional_context_parts:
                        additional_context = "\n\n" + "="*50 + "\n\n".join(additional_context_parts)
                        logger.info(f"✅ Combined additional context from {len(additional_context_parts)} sources")
                    else:
                        logger.warning("❌ Failed to gather content from any selected sources")
                else:
                    logger.warning("❌ No suitable sources found for research")
            else:
                logger.warning("❌ Web search returned no results")
        else:
            logger.info("✅ Sufficient knowledge available. Proceeding without additional research.")
        
        # Step 3: Generate blog content
        logger.info("\n📖 Generating educational blog content...")
        blog_content = self.generate_blog(user_text, additional_context)
        if not blog_content:
            logger.error("❌ Failed to generate blog content")
            return None
        
        # Apply evolution tools to blog content if available
        if self.enable_evolution_tools and self.tool_pipeline:
            context = {'topic': user_text, 'purpose': purpose}
            blog_content = self.tool_pipeline.execute_stage(
                ToolStage.POST_BLOG, 
                blog_content,
                context
            )
        
        # Step 4: Generate HTML slides
        logger.info("🎭 Creating HTML slide deck...")
        html_content = self.generate_slides_html(blog_content, purpose, theme)
        if not html_content:
            logger.error("❌ Failed to generate slides")
            return None
        
        # Apply evolution tools to HTML content if available
        if self.enable_evolution_tools and self.tool_pipeline:
            context = {'topic': user_text, 'purpose': purpose, 'theme': theme}
            html_content = self.tool_pipeline.execute_stage(
                ToolStage.POST_HTML,
                html_content,
                context
            )
        
        # Step 4.5: Validate and fix images
        validation_report = None
        if self.enable_image_validation:
            logger.info("🖼️ Validating and fixing images...")
            try:
                # Convert HTML to slide format for validation
                slides = [{'html': html_content, 'id': 'main_presentation'}]
                
                # Run validation pipeline
                validated_slides, validation_report = self.image_validator.validate_and_fix_slides(slides)
                
                # Update HTML content with validated version
                if validated_slides and validated_slides[0]['html']:
                    html_content = validated_slides[0]['html']
                    
                    if validation_report.get('successful_replacements', 0) > 0:
                        logger.info(f"✅ Image validation complete: {validation_report['successful_replacements']} images replaced")
                    else:
                        logger.info("✅ Image validation complete: all images valid")
                else:
                    logger.warning("⚠️ Image validation returned empty result")
                    
            except Exception as e:
                logger.warning(f"⚠️ Image validation failed: {e}")
                validation_report = {'error': str(e)}
        else:
            logger.info("🖼️ Image validation disabled")
        
        # Step 5: Organize outputs with proper file structure
        logger.info("📁 Organizing output files...")
        organized_files = organize_pipeline_outputs(
            output_dir=output_path,
            topic_slug=topic_slug,
            timestamp=timestamp,
            html_content=html_content,
            source_content=blog_content  # Save the blog content as source
        )
        
        # Step 6: Open in browser (use the organized HTML file)
        if 'html' in organized_files:
            logger.info(f"🌐 Opening slides in browser...")
            self.open_in_browser(str(organized_files['html']))
        
        results = {
            'knowledge_assessment': knowledge_assessment,
            'research_performed': knowledge_assessment == "INSUFFICIENT",
            'blog_content': blog_content,
            'html_content': html_content,
            'html_file': str(organized_files.get('html', '')),
            'organized_files': organized_files,
            'topic_slug': topic_slug,
            'timestamp': timestamp,
            'image_validation_report': validation_report
        }
        
        # Print organized file summary
        from opencanvas.utils.file_utils import get_file_summary
        logger.info(f"\n✅ Presentation generation complete!")
        logger.info(f"🧠 Knowledge assessment: {knowledge_assessment}")
        if knowledge_assessment == "INSUFFICIENT":
            logger.info(f"🔍 Web research was performed")
        
        # Log image validation summary
        if validation_report and 'error' not in validation_report:
            if validation_report.get('successful_replacements', 0) > 0:
                logger.info(f"🖼️ Image validation: {validation_report['successful_replacements']} images replaced, {validation_report.get('total_images_checked', 0)} total checked")
            else:
                logger.info(f"🖼️ Image validation: All {validation_report.get('total_images_checked', 0)} images valid")
        elif validation_report and 'error' in validation_report:
            logger.info(f"🖼️ Image validation: Failed ({validation_report['error']})")
        
        logger.info(f"\n📁 Organized files:")
        logger.info(get_file_summary(organized_files))
        
        return results
        
