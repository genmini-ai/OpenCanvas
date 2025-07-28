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

from .base import BaseGenerator

logger = logging.getLogger(__name__)

class TopicGenerator(BaseGenerator):
    def __init__(self, api_key, brave_api_key=None):
        """Initialize the topic-based slide generator with Anthropic API key and optional Brave API key"""
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)
        self.brave_api_key = brave_api_key or os.getenv('BRAVE_API_KEY')
        
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

    def generate_slides_html(self, blog_content, purpose, theme):
        """Generate HTML slide deck from blog content"""
        slide_prompt = f"""<presentation_task>
Create a stunning, visually captivating HTML presentation that makes viewers stop and say "wow" based on this content:

{blog_content}

Purpose of presentation: {purpose}
Visual theme: {theme}
</presentation_task>

<design_philosophy>
CREATE EMOTIONAL IMPACT:
- Prioritize the "wow factor" over conventional design
- Make every slide feel alive and dynamic with subtle animations
- Choose bold, vibrant colors over muted, safe options
- Use cutting-edge web design trends (glassmorphism, gradient overlays, micro-animations)
- Push the boundaries of what's possible with modern CSS and JavaScript
- Create a premium, cutting-edge experience that feels expensive
</design_philosophy>

<visual_requirements>
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library) with modern slide transitions and physics-based animations
3. Implement a sophisticated color scheme with gradients and depth for the "{theme}" theme
4. Include micro-interactions: hover effects, animated reveals, parallax scrolling
5. Use expressive, modern typography with varied font weights and sizes
6. Add glassmorphism effects, subtle shadows, and layered visual depth
7. Include elegant transitions between slides (avoid basic fades)
8. Create approximately 10-15 slides with dynamic, non-static layouts
9. Use animated bullet points that reveal progressively - break content into concise bullet points, not paragraphs
10. Include a stunning title slide with animated elements and section dividers with visual flair
11. Optimize for 1280px × 720px with responsive scaling
12. Add subtle background animations or patterns that enhance without distracting
13. HEIGHT-AWARE LAYOUT: Ensure all content fit within the 720px height by adjusting complexity
14. Do not include large blocks of text - keep slides visually appealing and professional
15. BALANCED VISUAL LAYOUT: Prioritize visual balance over text density - use images from https://images.unsplash.com/ (only when certain about photo ID), tables, charts, and visual elements to break up text and create engaging slide compositions
</visual_requirements>

<content_presentation>
- Transform text into visually engaging elements with icons, graphics, and spacing
- Use concise bullet points with animated reveals (maximum ~100 words per slide)
- Create visual hierarchy through size, color, and positioning
- Include progress indicators and slide counters with elegant styling
- Break up content with visual elements: images, tables, charts, and graphics instead of text blocks
- Leverage visual storytelling with appropriate imagery and data visualizations
</content_presentation>

<content_enhancements>
- For data analysis: Create beautiful, animated charts with smooth transitions using Chart.js or D3.js
- For travel content: Add immersive imagery, interactive maps, destination animations, and travel icons
- For workshops: Include engaging process diagrams, interactive elements, and activity visualizations
- For general content: Use relevant, high-quality images from Unsplash when photo IDs are known with certainty
</content_enhancements>

<technical_excellence>
- Use advanced CSS features: backdrop-filter, clip-path, CSS Grid, Flexbox, custom properties
- Implement smooth JavaScript animations with requestAnimationFrame
- Add keyboard navigation with visual feedback
- Include preloaders and smooth state transitions
- Ensure the presentation feels responsive and premium
</technical_excellence>

<motion_design>
- Everything should have subtle movement and life
- Use staggered animations for lists and elements
- Implement smooth cursor tracking effects
- Add entrance animations for each slide element
- Create seamless transitions that maintain visual flow
</motion_design>

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser and immediately impresses with its visual sophistication.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
</output_requirements>
"""
        
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
    
    def generate_from_topic(self, user_text, purpose, theme="professional blue", output_dir="output"):
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
        
        # Step 4: Generate HTML slides
        logger.info("🎭 Creating HTML slide deck...")
        html_content = self.generate_slides_html(blog_content, purpose, theme)
        if not html_content:
            logger.error("❌ Failed to generate slides")
            return None
        
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
            'timestamp': timestamp
        }
        
        # Print organized file summary
        from opencanvas.utils.file_utils import get_file_summary
        logger.info(f"\n✅ Presentation generation complete!")
        logger.info(f"🧠 Knowledge assessment: {knowledge_assessment}")
        if knowledge_assessment == "INSUFFICIENT":
            logger.info(f"🔍 Web research was performed")
        logger.info(f"\n📁 Organized files:")
        logger.info(get_file_summary(organized_files))
        
        return results
        
