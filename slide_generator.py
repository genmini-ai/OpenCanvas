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

class SlideGenerator:
    def __init__(self, api_key, brave_api_key=None):
        """Initialize the slide generator with Anthropic API key and optional Brave API key"""
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
            print(f"Error assessing knowledge: {e}")
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
            print(f"Error generating search query: {e}")
            return user_text  # Fallback to original text
    
    def web_search(self, query, brave_api_key=None):
        """Perform web search using Brave Search API"""
        if not brave_api_key:
            print("⚠️  Brave API key not provided. Set BRAVE_API_KEY environment variable or pass it as parameter.")
            return []
        
        try:
            print(f"🔍 Searching with Brave API: {query}")
            
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
                print("❌ No search results found")
                return []
            
            print(f"✅ Found {len(web_results)} search results")
            
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
            print(f"❌ Network error during search: {e}")
            return []
        except Exception as e:
            print(f"❌ Error performing search: {e}")
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
            print(f"Error assessing credibility: {e}")
            return search_results[:2] if len(search_results) >= 2 else search_results
    
    def scrape_web_content(self, url):
        """Scrape content from a web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"🌐 Scraping content from: {url}")
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
            print(f"Error scraping content: {e}")
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
            print(f"Error generating blog: {e}")
            return None
    
    def generate_slides_html(self, blog_content, purpose, theme):
        """Generate HTML slide deck from blog content"""
        slide_prompt = f"""Create a beautiful HTML presentation based on this content:

{blog_content}

Purpose of presentation: {purpose}
Visual theme: {theme}

Instructions:
1. Create a self-contained HTML file with embedded CSS and JavaScript
2. Use Reveal.js style (without requiring the actual library)
3. Include elegant transitions between slides
4. Use a color scheme appropriate for the "{theme}" theme
5. Optimize typography for readability
6. Include a title slide and section dividers
7. Use bullet points and concise text (not paragraphs)
8. Create approximately 10-15 slides in total
9. Do not include large blocks of text - break content into concise bullet points
10. Make the slides visually appealing and professional

CONTENT-SPECIFIC VISUAL ENHANCEMENTS:
- For data analysis content: Include interactive charts, graphs, bar charts, line charts, pie charts, and other data visualizations using Chart.js or D3.js (embedded)
- For travel-related content: Add relevant travel images, maps, destination photos, icons (planes, hotels, landmarks), and geographic visualizations
- For workshop content: Include relevant workshop imagery, icons for activities, process diagrams, interactive elements, and engagement visuals

IMPORTANT: The HTML must be a complete, self-contained file that can be opened directly in a browser.
Do not include any explanations, just output the complete HTML code.
        
IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=12000,
                temperature=0.5,
                messages=[{"role": "user", "content": slide_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating slides: {e}")
            return None
    
    def save_html_file(self, html_content, filename="slides.html"):
        """Save HTML content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return filename
        except Exception as e:
            print(f"Error saving HTML file: {e}")
            return None
    
    def generate_complete_presentation(self, user_text, purpose, theme="professional blue"):
        """Complete pipeline: text -> knowledge check -> research (if needed) -> blog -> slides -> HTML"""
        print(f"🚀 Starting presentation generation...")
        print(f"📝 User text: {user_text}")
        print(f"🎯 Purpose: {purpose}")
        print(f"🎨 Theme: {theme}")
        
        # Step 1: Assess knowledge depth
        print("\n🧠 Assessing knowledge depth...")
        knowledge_assessment = self.assess_knowledge_depth(user_text)
        print(f"📊 Knowledge assessment: {knowledge_assessment}")
        
        additional_context = None
        
        # Step 2: If insufficient knowledge, perform web research
        if knowledge_assessment == "INSUFFICIENT":
            print("\n🔍 Insufficient knowledge detected. Initiating web research...")
            
            # Generate search query
            search_query = self.generate_search_query(user_text)
            print(f"🔎 Search query: {search_query}")
            
            # Perform web search
            search_results = self.web_search(search_query, self.brave_api_key)
            
            if search_results:
                # Assess source credibility and select best sources
                best_sources = self.assess_source_credibility(search_results)
                
                if best_sources:
                    additional_context_parts = []
                    
                    for i, source in enumerate(best_sources[:2]):  # Ensure we only process 2 sources
                        print(f"🏆 Selected source {i+1}: {source.get('title', 'N/A')}")
                        print(f"🔗 URL: {source.get('link', 'N/A')}")
                        
                        # Scrape content from each source
                        scraped_content = self.scrape_web_content(source.get('link'))
                        
                        if scraped_content:
                            additional_context_parts.append(f"Source {i+1} - {source.get('title', 'Unknown')}:\n{scraped_content}")
                            print(f"✅ Successfully gathered content from source {i+1} ({len(scraped_content)} characters)")
                        else:
                            print(f"❌ Failed to scrape content from source {i+1}")
                    
                    if additional_context_parts:
                        additional_context = "\n\n" + "="*50 + "\n\n".join(additional_context_parts)
                        print(f"✅ Combined additional context from {len(additional_context_parts)} sources")
                    else:
                        print("❌ Failed to gather content from any selected sources")
                else:
                    print("❌ No suitable sources found for research")
            else:
                print("❌ Web search returned no results")
        else:
            print("✅ Sufficient knowledge available. Proceeding without additional research.")
        
        # Step 3: Generate blog content
        print("\n📖 Generating educational blog content...")
        blog_content = self.generate_blog(user_text, additional_context)
        if not blog_content:
            print("❌ Failed to generate blog content")
            return None
        
        # Step 4: Generate HTML slides
        print("🎭 Creating HTML slide deck...")
        html_content = self.generate_slides_html(blog_content, purpose, theme)
        if not html_content:
            print("❌ Failed to generate slides")
            return None
        
        # Step 5: Save HTML file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"slides_{timestamp}.html"
        
        print(f"💾 Saving HTML file as {html_filename}...")
        saved_html = self.save_html_file(html_content, html_filename)
        if not saved_html:
            print("❌ Failed to save HTML file")
            return None
        
        # Step 6: Open in browser
        print(f"🌐 Opening slides in browser...")
        webbrowser.open(f"file://{Path(html_filename).absolute()}")
        
        results = {
            'knowledge_assessment': knowledge_assessment,
            'research_performed': knowledge_assessment == "INSUFFICIENT",
            'blog_content': blog_content,
            'html_content': html_content,
            'html_file': html_filename,
            'timestamp': timestamp
        }
        
        print(f"\n✅ Presentation generation complete!")
        print(f"🧠 Knowledge assessment: {knowledge_assessment}")
        if knowledge_assessment == "INSUFFICIENT":
            print(f"🔍 Web research was performed")
        print(f"📁 HTML file: {html_filename}")
        print(f"🌐 Slides opened in your default browser")
        
        return results