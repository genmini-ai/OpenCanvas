"""
Evolved Generation Router - Uses evolved prompts while maintaining production pipeline
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from opencanvas.generators.router import GenerationRouter
from opencanvas.generators.topic_generator import TopicGenerator
from opencanvas.generators.pdf_generator import PDFGenerator
from opencanvas.evolution.core.prompts import PromptManager

logger = logging.getLogger(__name__)

class EvolvedGenerationRouter(GenerationRouter):
    """
    Extension of GenerationRouter that uses evolved prompts from iterations
    while maintaining all production tools and pipeline
    """
    
    def __init__(self, api_key=None, brave_api_key=None, evolution_iteration: Optional[int] = None):
        """Initialize router with evolved generators"""
        
        # Don't call parent __init__ yet - we need to set up evolved generators first
        self.api_key = api_key
        self.brave_api_key = brave_api_key
        
        # Load evolved prompts if available
        self.prompt_manager = PromptManager()
        self.evolution_iteration = evolution_iteration
        
        # Load auto-generated tools from previous iterations
        self.auto_generated_tools = self._load_auto_generated_tools(evolution_iteration)
        
        if evolution_iteration and evolution_iteration > 1:
            # Check if evolved prompts exist for previous iteration
            evolved_prompts = self.prompt_manager.get_prompts(evolution_iteration - 1)
            if evolved_prompts and 'topic_generation' in evolved_prompts:
                logger.info(f"🧬 Loading EVOLVED prompts from iteration {evolution_iteration - 1}")
                
                # Create patched generators with evolved prompts and tools
                self.topic_generator = EvolvedTopicGenerator(
                    api_key, 
                    brave_api_key,
                    evolved_prompt=evolved_prompts.get('topic_generation'),
                    auto_generated_tools=self.auto_generated_tools
                )
                self.pdf_generator = PDFGenerator(api_key)  # Keep PDF generator standard for now
                
                logger.info(f"✅ Using evolved prompts for generation")
            else:
                logger.info(f"⚠️  No evolved prompts found, using baseline")
                self._use_baseline_generators()
        else:
            logger.info(f"📦 Using baseline prompts (first iteration)")
            self._use_baseline_generators()
    
    def _load_auto_generated_tools(self, iteration: Optional[int]) -> List:
        """Load auto-generated tools from previous iterations"""
        tools = []
        if not iteration or iteration <= 1:
            return tools
        
        # Load tools from all previous iterations
        logger.info(f"🔍 Loading auto-generated tools from iterations 1 to {iteration-1}")
        for i in range(1, iteration):
            tools_dir = Path(f"src/opencanvas/evolution/tools/iteration_{i:03d}")
            if tools_dir.exists():
                logger.info(f"  📂 Checking iteration {i}: {tools_dir}")
                # Import all tools from this iteration
                import importlib.util
                for tool_file in tools_dir.glob("*.py"):
                    if tool_file.name != "__init__.py":
                        spec = importlib.util.spec_from_file_location(
                            f"tool_{i}_{tool_file.stem}", 
                            tool_file
                        )
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            # Find tool classes
                            for name in dir(module):
                                obj = getattr(module, name)
                                if isinstance(obj, type) and name != "BaseTool":
                                    tools.append(obj())
                                    logger.info(f"  🔧 Loaded auto-generated tool: {name}")
            else:
                logger.info(f"  📂 No tools found in iteration {i}")
        
        logger.info(f"✅ Total auto-generated tools loaded: {len(tools)}")
        return tools
    
    def _use_baseline_generators(self):
        """Use standard production generators"""
        self.topic_generator = TopicGenerator(self.api_key, self.brave_api_key)
        self.pdf_generator = PDFGenerator(self.api_key)


class EvolvedTopicGenerator(TopicGenerator):
    """
    Topic generator that uses evolved prompts while keeping all other tools
    """
    
    def __init__(self, api_key, brave_api_key=None, evolved_prompt: str = None, auto_generated_tools: List = None):
        """Initialize with evolved prompt and auto-generated tools"""
        super().__init__(api_key, brave_api_key)
        self.evolved_prompt = evolved_prompt
        self.auto_generated_tools = auto_generated_tools or []
        
        if evolved_prompt:
            logger.info(f"📝 EvolvedTopicGenerator using custom prompt ({len(evolved_prompt)} chars)")
        if self.auto_generated_tools:
            logger.info(f"🔧 EvolvedTopicGenerator using {len(self.auto_generated_tools)} auto-generated tools")
    
    def _apply_auto_generated_tools(self, content: str, stage: str = "blog") -> str:
        """Apply auto-generated tools to content at specified stage"""
        
        if not self.auto_generated_tools:
            return content
        
        processed_content = content
        tools_applied = 0
        
        logger.info(f"🔧 Applying {len(self.auto_generated_tools)} tools at {stage} stage...")
        
        for tool in self.auto_generated_tools:
            try:
                logger.info(f"  🛠️  Applying tool: {tool.name}")
                
                # Apply tool to current content
                result = tool.process(processed_content)
                
                # Handle different result formats
                if isinstance(result, str):
                    # Simple string result - replace content
                    processed_content = result
                    tools_applied += 1
                    logger.info(f"    ✅ {tool.name}: Applied (string result)")
                    
                elif isinstance(result, dict):
                    # Dictionary result - check for various formats
                    if result.get('success') and result.get('processed_content'):
                        processed_content = result['processed_content']
                        tools_applied += 1
                        logger.info(f"    ✅ {tool.name}: Applied (dict result)")
                    elif result.get('fixes_applied'):
                        processed_content = result['fixes_applied']
                        tools_applied += 1
                        logger.info(f"    ✅ {tool.name}: Applied fixes")
                    elif 'enhanced_content' in result:
                        processed_content = result['enhanced_content']
                        tools_applied += 1
                        logger.info(f"    ✅ {tool.name}: Applied enhancement")
                    else:
                        logger.info(f"    ⚠️  {tool.name}: No actionable result")
                        
                else:
                    logger.info(f"    ⚠️  {tool.name}: Unknown result format: {type(result)}")
                    
            except Exception as e:
                logger.error(f"    ❌ Tool {tool.name} failed: {e}")
                # Continue with other tools even if one fails
                continue
        
        logger.info(f"✅ Applied {tools_applied}/{len(self.auto_generated_tools)} tools successfully")
        return processed_content
    
    def generate_blog(self, user_text, additional_context=None):
        """Generate blog content with auto-generated tools applied"""
        
        # First generate blog using parent method
        blog_content = super().generate_blog(user_text, additional_context)
        
        # Then apply auto-generated tools to improve the content
        if self.auto_generated_tools and blog_content:
            logger.info("🔧 Applying auto-generated tools to blog content...")
            enhanced_blog_content = self._apply_auto_generated_tools(blog_content, stage="blog")
            
            if enhanced_blog_content != blog_content:
                logger.info("✅ Blog content enhanced by auto-generated tools")
                return enhanced_blog_content
            else:
                logger.info("ℹ️  Blog content unchanged after tool processing")
        
        return blog_content
    
    def generate_slides_html(self, blog_content, purpose, theme):
        """Generate HTML slide deck using evolved prompt and auto-generated tools"""
        
        # Apply auto-generated tools to blog content before slide generation
        processed_blog_content = blog_content
        if self.auto_generated_tools:
            logger.info("🔧 Applying auto-generated tools before slide generation...")
            processed_blog_content = self._apply_auto_generated_tools(blog_content, stage="slides")
        
        if self.evolved_prompt:
            # Use evolved prompt with tool-processed content
            slide_prompt = self.evolved_prompt.format(
                blog_content=processed_blog_content,  # Use processed content!
                purpose=purpose,
                theme=theme
            )
            
            logger.info(f"🧬 Using EVOLVED slide generation prompt with processed content")
        else:
            # Fall back to parent's implementation with processed content
            return super().generate_slides_html(processed_blog_content, purpose, theme)
        
        try:
            logger.info("📡 Using streaming for slide generation with evolved prompt...")
            
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
            
            logger.info(f"✅ Completed generation with evolved prompt: {len(html_content)} characters")
            
            # Clean up HTML if wrapped in code blocks
            cleaned_html = self.clean_html_content(html_content)
            
            # Apply auto-generated tools to final HTML if applicable
            if self.auto_generated_tools:
                logger.info("🔧 Applying auto-generated tools to final HTML output...")
                final_html = self._apply_auto_generated_tools(cleaned_html, stage="html")
                if final_html != cleaned_html:
                    logger.info("✅ HTML output enhanced by auto-generated tools")
                    return final_html
            
            return cleaned_html
        except Exception as e:
            logger.error(f"Error generating slides with evolved prompt: {e}")
            # Fall back to parent implementation
            return super().generate_slides_html(blog_content, purpose, theme)