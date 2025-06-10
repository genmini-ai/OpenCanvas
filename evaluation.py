import asyncio
import base64
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright
from anthropic import Anthropic
import re

class PPTQualityEvaluator:
    def __init__(self, anthropic_api_key: str):
        """
        Initialize the PPT Quality Evaluator
        
        Args:
            anthropic_api_key: API key for Claude evaluation
        """
        self.client = Anthropic(api_key=anthropic_api_key)
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
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.1,
                messages=messages
            )
            
            # Parse the response
            evaluation_text = response.content[0].text.strip()
            
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


async def run_comprehensive_test_suite(anthropic_api_key: str, brave_api_key: str):
    """
    Run complete test suite: generate presentations + evaluate quality
    
    Args:
        anthropic_api_key: API key for Claude (generation + evaluation)
        brave_api_key: API key for Brave search (generation)
    """
    
    # Initialize components
    from slide_generator import SlideGenerator
    
    generator = SlideGenerator(api_key=anthropic_api_key, brave_api_key=brave_api_key)
    evaluator = PPTQualityEvaluator(anthropic_api_key)
    
    # Define test cases with mapped values (not keys)
    test_cases = [
        # Test Case 1: Startup Pitch Deck
        {
            "name": "Startup Pitch Deck",
            "user_text": "AI-powered fitness app that creates personalized workout plans using computer vision to analyze form and provide real-time feedback",
            "purpose": "pitch deck",
            "theme": "bold high contrast"
        },
        
        # Test Case 2: Corporate Training
        {
            "name": "Corporate Training",
            "user_text": "Cybersecurity best practices for remote workers including password management, phishing detection, and secure file sharing protocols",
            "purpose": "educational presentation",
            "theme": "cool professional"
        },
        
        # Test Case 3: Academic Conference
        {
            "name": "Academic Research Presentation",
            "user_text": "Climate change impacts on coral reef ecosystems: a longitudinal study of bleaching events in the Great Barrier Reef from 2010-2024",
            "purpose": "academic presentation",
            "theme": "clean minimalist"
        }
    ]
    
    # Run all test cases
    results = {}
    total_time = 0
    total_evaluation_time = 0
    
    print("🚀 Starting Comprehensive PPT Test Suite")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Topic: {test_case['user_text'][:80]}...")
        print(f"   Purpose: {test_case['purpose']} | Theme: {test_case['theme']}")
        
        # Phase 1: Generate presentation
        start_time = time.time()
        
        try:
            print("  🎨 Generating presentation...")
            result = generator.generate_complete_presentation(
                user_text=test_case['user_text'],
                purpose=test_case['purpose'],
                theme=test_case['theme']
            )
            
            generation_time = time.time() - start_time
            total_time += generation_time
            
            # Save presentation to file
            html_filename = result.get('html_file', f"test_case_{i}_{test_case['name'].replace(' ', '_').lower()}.html")
            
            print(f"  ✅ Generated presentation in {generation_time:.2f}s")
            
            # Phase 2: Evaluate presentation
            eval_start_time = time.time()
            
            # Capture slides and evaluate
            slides_data = await evaluator.capture_all_slides(html_filename)
            evaluation_results = evaluator.evaluate_presentation(
                slides_data, 
                {
                    'topic': test_case['user_text'],
                    'theme': test_case['theme'],
                    'purpose': test_case['purpose']
                }
            )
            
            evaluation_time = time.time() - eval_start_time
            total_evaluation_time += evaluation_time
            
            # Calculate average score
            scores = evaluation_results.get('scores', {})
            avg_score = sum(scores.values()) / len(scores) if scores else 0
            
            print(f"  📊 Evaluation completed in {evaluation_time:.2f}s | Avg Score: {avg_score:.1f}/10")
            
            results[test_case['name']] = {
                'status': 'success',
                'slides_count': len(slides_data) if slides_data else 0,
                'generation_time': generation_time,
                'evaluation_time': evaluation_time,
                'evaluation_scores': scores,
                'average_score': avg_score,
                'html_file': html_filename,
                'full_evaluation': evaluation_results
            }
            
        except Exception as e:
            generation_time = time.time() - start_time
            total_time += generation_time
            
            results[test_case['name']] = {
                'status': 'error',
                'generation_time': generation_time,
                'error': str(e)
            }
            print(f"  ❌ Error after {generation_time:.2f}s: {e}")
    
    # Calculate averages
    successful_tests = [r for r in results.values() if r['status'] == 'success']
    average_generation_time = total_time / len(test_cases) if test_cases else 0
    average_evaluation_time = total_evaluation_time / len(successful_tests) if successful_tests else 0
    
    print_comprehensive_results(results, total_time, average_generation_time, total_evaluation_time, average_evaluation_time)
    
    return results, total_time, average_generation_time, total_evaluation_time, average_evaluation_time


def print_comprehensive_results(results, total_time, avg_gen_time, total_eval_time, avg_eval_time):
    """Print detailed results of the comprehensive test suite"""
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    total = len(results)
    
    # Basic stats
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"⏱️  Total Generation Time: {total_time:.2f}s")
    print(f"⏱️  Average Generation Time: {avg_gen_time:.2f}s per presentation")
    print(f"🤖 Total Evaluation Time: {total_eval_time:.2f}s")
    print(f"🤖 Average Evaluation Time: {avg_eval_time:.2f}s per evaluation")
    
    # Performance analysis
    if successful > 0:
        successful_results = [r for r in results.values() if r['status'] == 'success']
        generation_times = [r['generation_time'] for r in successful_results]
        evaluation_times = [r['evaluation_time'] for r in successful_results if 'evaluation_time' in r]
        avg_scores = [r['average_score'] for r in successful_results if 'average_score' in r]
        
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print("-" * 50)
        if generation_times:
            print(f"Fastest Generation: {min(generation_times):.2f}s")
            print(f"Slowest Generation: {max(generation_times):.2f}s")
        if evaluation_times:
            print(f"Fastest Evaluation: {min(evaluation_times):.2f}s")
            print(f"Slowest Evaluation: {max(evaluation_times):.2f}s")
        if avg_scores:
            print(f"Highest Quality Score: {max(avg_scores):.1f}/10")
            print(f"Lowest Quality Score: {min(avg_scores):.1f}/10")
            print(f"Average Quality Score: {sum(avg_scores)/len(avg_scores):.1f}/10")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 80)
    for name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        
        if result['status'] == 'success':
            gen_time = f"{result['generation_time']:.2f}s"
            eval_time = f"{result.get('evaluation_time', 0):.2f}s" if 'evaluation_time' in result else "N/A"
            avg_score = f"{result.get('average_score', 0):.1f}/10" if 'average_score' in result else "N/A"
            slides = result['slides_count']
            
            print(f"{status_icon} {name}:")
            print(f"    Slides: {slides} | Gen: {gen_time} | Eval: {eval_time} | Quality: {avg_score}")
            
            # Show top scores if available
            if 'evaluation_scores' in result and result['evaluation_scores']:
                scores = result['evaluation_scores']
                top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"    Top Scores: {', '.join([f'{k.replace('_', ' ')}: {v}' for k, v in top_scores])}")
        else:
            print(f"{status_icon} {name}: ERROR - {result['error']}")
    
    # Quality insights
    successful_with_scores = [r for r in results.values() 
                             if r['status'] == 'success' and 'evaluation_scores' in r and r['evaluation_scores']]
    
    if successful_with_scores:
        print(f"\n🎨 QUALITY INSIGHTS:")
        print("-" * 50)
        
        # Aggregate scores by criteria
        criteria_scores = {}
        for result in successful_with_scores:
            for criteria, score in result['evaluation_scores'].items():
                if criteria not in criteria_scores:
                    criteria_scores[criteria] = []
                criteria_scores[criteria].append(score)
        
        # Calculate averages
        criteria_averages = {k: sum(v)/len(v) for k, v in criteria_scores.items()}
        sorted_criteria = sorted(criteria_averages.items(), key=lambda x: x[1], reverse=True)
        
        print("Strongest Areas:")
        for criteria, avg_score in sorted_criteria[:3]:
            print(f"  • {criteria.replace('_', ' ').title()}: {avg_score:.1f}/10")
        
        print("Areas for Improvement:")
        for criteria, avg_score in sorted_criteria[-3:]:
            print(f"  • {criteria.replace('_', ' ').title()}: {avg_score:.1f}/10")


if __name__ == "__main__":
    # Get API keys from environment variables
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    brave_api_key = os.getenv('BRAVE_API_KEY')
    
    if not anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        exit(1)
    
    asyncio.run(run_comprehensive_test_suite(
        anthropic_api_key=anthropic_api_key,
        brave_api_key=brave_api_key
    ))
