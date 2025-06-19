import base64
import os
import time
from typing import Dict, List, Any
from playwright.async_api import async_playwright
from anthropic import Anthropic
from openai import OpenAI
from openai import OpenAIError
import re
from enum import Enum

class LLMProvider(Enum):
    """Enum representing LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

class PPTQualityEvaluator:
    def __init__(self, anthropic_api_key: str="",
                 openai_api_key: str=""):
        """
        Initialize the PPT Quality Evaluator
        
        Args:
            anthropic_api_key: API key for Claude evaluation
        """
        if not anthropic_api_key and not openai_api_key:
            raise ValueError("At least one API key must be provided: "
                             "either 'anthropic_api_key' or 'openai_api_key'")
        if anthropic_api_key:
            self._client = Anthropic(api_key=anthropic_api_key)
            self.model = "claude-sonnet-4-20250514"
            self._provider = LLMProvider.ANTHROPIC
        else:
            self._client = OpenAI(api_key=openai_api_key)
            self.model = "gpt-4.1-mini"
            self._provider = LLMProvider.OPENAI
        self.viewport_size = {"width": 1920, "height": 1080}

        
    async def capture_all_slides(self, html_file_path: str) -> List[Dict[str, Any]]:
        """
        Capture screenshots and content for all slides in a presentation
        
        Args:
            html_file_path: Path to the HTML presentation file
            
        Returns:
            List of slide data with screenshots and content
        """
        print(f"  📸 Capturing slides from: {os.path.basename(html_file_path)}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport=self.viewport_size)
            
            try:
                # Load the presentation
                file_url = f"file://{os.path.abspath(html_file_path)}"
                await page.goto(file_url, wait_until="networkidle")
                
                # Wait for any animations/charts to load
                await page.wait_for_timeout(2000)
                
                # Detect total slide count
                slide_count = await self._detect_slide_count(page)
                print(f"  📊 Detected {slide_count} slides")
                
                slides_data = []
                
                for i in range(slide_count):
                    # Extract slide content
                    slide_content = await self._extract_slide_content(page, i)
                    
                    # Capture screenshot
                    screenshot = await page.screenshot(full_page=True, type="png")
                    screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                    
                    slide_data = {
                        'slide_number': i + 1,
                        'screenshot_base64': screenshot_b64,
                        'html_content': slide_content['html'],
                        'text_content': slide_content['text'],
                        'slide_title': slide_content['title']
                    }
                    slides_data.append(slide_data)
                    
                    # Navigate to next slide (except for last slide)
                    if i < slide_count - 1:
                        await self._navigate_next_slide(page)
                        await page.wait_for_timeout(800)  # Wait for transition
                
                return slides_data
                
            finally:
                await browser.close()
    
    async def _detect_slide_count(self, page) -> int:
        """Detect total number of slides using multiple methods"""
        try:
            # Method 1: Count .slide elements
            slide_elements = await page.query_selector_all('.slide')
            if slide_elements:
                return len(slide_elements)
            
            # Method 2: Look for slide counter (e.g., "2/12")
            slide_number_element = await page.query_selector('.slide-number')
            if slide_number_element:
                text = await slide_number_element.inner_text()
                match = re.search(r'(\d+)/(\d+)', text)
                if match:
                    return int(match.group(2))
            
            # Method 3: Try navigation until next button is disabled
            count = 1
            max_attempts = 50  # Safety limit
            
            while count < max_attempts:
                next_btn = await page.query_selector('.next-btn, .control-btn.next-btn')
                if not next_btn:
                    break
                    
                # Check if button is disabled or if we can't navigate further
                is_disabled = await next_btn.is_disabled()
                if is_disabled:
                    break
                
                # Try to click next
                await next_btn.click()
                await page.wait_for_timeout(500)
                count += 1
                
                # Check if we're still progressing
                current_slide_text = await page.text_content('.slide-number')
                if current_slide_text and f"{count}/" not in current_slide_text:
                    break
            
            # Reset to first slide
            while count > 1:
                prev_btn = await page.query_selector('.prev-btn, .control-btn.prev-btn')
                if prev_btn:
                    await prev_btn.click()
                    await page.wait_for_timeout(200)
                count -= 1
            
            return count if count <= max_attempts else 1
            
        except Exception as e:
            print(f"    ⚠️ Error detecting slide count: {e}")
            return 1
    
    async def _extract_slide_content(self, page, slide_index: int) -> Dict[str, str]:
        """Extract content from current slide"""
        try:
            # Get active slide content
            active_slide = await page.query_selector('.slide.active')
            if not active_slide:
                # Fallback: get all slides and pick by index
                slides = await page.query_selector_all('.slide')
                if slide_index < len(slides):
                    active_slide = slides[slide_index]
            
            if active_slide:
                # Extract HTML content
                html_content = await active_slide.inner_html()
                
                # Extract text content
                text_content = await active_slide.inner_text()
                
                # Try to extract title
                title_element = await active_slide.query_selector('h1, h2')
                title = await title_element.inner_text() if title_element else f"Slide {slide_index + 1}"
                
                return {
                    'html': html_content,
                    'text': text_content.strip(),
                    'title': title.strip()
                }
            
            return {
                'html': '',
                'text': '',
                'title': f"Slide {slide_index + 1}"
            }
            
        except Exception as e:
            print(f"    ⚠️ Error extracting slide content: {e}")
            return {
                'html': '',
                'text': '',
                'title': f"Slide {slide_index + 1}"
            }
    
    async def _navigate_next_slide(self, page):
        """Navigate to next slide"""
        try:
            # Try multiple selector patterns for next button
            next_selectors = [
                '.next-btn',
                '.control-btn.next-btn',
                'button.next-btn',
                '[data-action="next"]',
                '.navigation .next'
            ]
            
            for selector in next_selectors:
                next_btn = await page.query_selector(selector)
                if next_btn:
                    await next_btn.click()
                    return
            
            # Fallback: try keyboard navigation
            await page.keyboard.press('ArrowRight')
            
        except Exception as e:
            print(f"    ⚠️ Error navigating to next slide: {e}")
            # Fallback: keyboard navigation
            await page.keyboard.press('ArrowRight')

    def get_response(self, 
                     prompt: str, 
                     max_tokens: int = 4000, 
                     temperature: float = 0.1) -> str:
        """
        Get response from Claude or OpenAI based on the provided prompt
        
        Args:
            prompt: The input prompt for the model
            max_tokens: Maximum tokens for the response
            temperature: Sampling temperature
            
        Returns:
            Response text from the model
        """
        if self._provider == LLMProvider.ANTHROPIC:

            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif self._provider == LLMProvider.OPENAI:
            response = self._client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].text.strip()
    
    def evaluate_presentation(
        self, 
        slides_data: List[Dict[str, Any]], 
        original_input: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Evaluate the presentation quality using Claude
        
        Args:
            slides_data: List of slide data with screenshots and content
            original_input: Original input (topic, theme, purpose)
            
        Returns:
            Evaluation results with scores and feedback
        """
        print("  🤖 Evaluating with Claude...")
        
        # Create evaluation prompt
        evaluation_prompt = self._create_evaluation_prompt(slides_data, original_input)
        
        try:
            # Prepare messages with images
            messages = self._prepare_evaluation_messages(evaluation_prompt, slides_data)
            
            evaluation_text = self.get_response(
                prompt=messages,
                max_tokens=4000,
                temperature=0.1
            )

            # Extract structured scores if possible
            scores = self._extract_scores_from_evaluation(evaluation_text)
            
            return {
                'overall_evaluation': evaluation_text,
                'scores': scores,
                'slide_count': len(slides_data),
                'evaluation_timestamp': time.time()
            }
            
        except Exception as e:
            print(f"    ❌ Error during evaluation: {e}")
            return {
                'overall_evaluation': f"Evaluation failed: {e}",
                'scores': {},
                'slide_count': len(slides_data),
                'evaluation_timestamp': time.time()
            }
    
    def _create_evaluation_prompt(
        self, 
        slides_data: List[Dict[str, Any]], 
        original_input: Dict[str, str]
    ) -> str:
        """Create the evaluation prompt for Claude"""
        
        slides_text_summary = "\n\n".join([
            f"**Slide {slide['slide_number']}: {slide['slide_title']}**\n{slide['text_content'][:300]}..."
            for slide in slides_data
        ])
        
        prompt = f"""You are an expert presentation designer and evaluator. Please evaluate this generated presentation based on both visual design and content quality.

**ORIGINAL INPUT:**
- Topic: {original_input.get('topic', 'Not specified')}
- Theme: {original_input.get('theme', 'Not specified')}
- Purpose: {original_input.get('purpose', 'Not specified')}

**PRESENTATION OVERVIEW:**
- Total Slides: {len(slides_data)}
- Content Summary: {slides_text_summary}

I will provide you with screenshots of each slide. Please evaluate the presentation on these criteria:

**VISUAL EVALUATION (based on screenshots):**
1. **Theme Adherence** (1-10): Does the visual design match the specified theme?
2. **Visual Hierarchy** (1-10): Clear title/content distinction, logical visual flow
3. **Design Quality** (1-10): Professional appearance, color harmony, typography
4. **Layout Balance** (1-10): Proper white space, element alignment, visual weight

**CONTENT EVALUATION (based on text content):**
5. **Purpose Alignment** (1-10): Does content structure match the intended purpose?
6. **Content Quality** (1-10): Relevance, depth, clarity, grammar
7. **Narrative Flow** (1-10): Logical progression, storytelling effectiveness
8. **Completeness** (1-10): Comprehensive coverage of the topic

**OVERALL USER EXPERIENCE:**
9. **Engagement** (1-10): Would this hold audience attention?
10. **Professional Polish** (1-10): Ready for intended use case?

Please provide:
1. **SCORES**: List each criterion with a score (1-10) and brief justification
2. **STRENGTHS**: Top 3 things done well
3. **IMPROVEMENTS**: Top 3 specific actionable improvements
4. **OVERALL ASSESSMENT**: Summary judgment and recommendation

Format your response clearly with section headers. Be specific and constructive in your feedback."""

        return prompt
    
    def _prepare_evaluation_messages(
        self, 
        prompt: str, 
        slides_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prepare messages with images for Claude API"""
        
        # Start with the main prompt
        content = [{"type": "text", "text": prompt}]
        
        # Add each slide image
        for i, slide in enumerate(slides_data):
            content.append({
                "type": "text", 
                "text": f"\n\n**SLIDE {slide['slide_number']}: {slide['slide_title']}**"
            })
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": slide['screenshot_base64']
                }
            })
        
        return [{"role": "user", "content": content}]
    
    def _extract_scores_from_evaluation(self, evaluation_text: str) -> Dict[str, int]:
        """Extract numerical scores from evaluation text"""
        scores = {}
        score_patterns = [
            r'Theme Adherence.*?(\d+)',
            r'Visual Hierarchy.*?(\d+)',
            r'Design Quality.*?(\d+)',
            r'Layout Balance.*?(\d+)',
            r'Purpose Alignment.*?(\d+)',
            r'Content Quality.*?(\d+)',
            r'Narrative Flow.*?(\d+)',
            r'Completeness.*?(\d+)',
            r'Engagement.*?(\d+)',
            r'Professional Polish.*?(\d+)'
        ]
        
        criteria_names = [
            'theme_adherence', 'visual_hierarchy', 'design_quality', 'layout_balance',
            'purpose_alignment', 'content_quality', 'narrative_flow', 'completeness',
            'engagement', 'professional_polish'
        ]
        
        for i, pattern in enumerate(score_patterns):
            match = re.search(pattern, evaluation_text, re.IGNORECASE)
            if match:
                try:
                    score = int(match.group(1))
                    if 1 <= score <= 10:
                        scores[criteria_names[i]] = score
                except ValueError:
                    continue
        
        return scores

