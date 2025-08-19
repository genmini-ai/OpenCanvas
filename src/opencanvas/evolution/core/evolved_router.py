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
    
    def __init__(self, api_key=None, brave_api_key=None, evolution_iteration: Optional[int] = None, prompt_only: bool = False, evolution_output_dir: Optional[str] = None, initial_prompt: Optional[str] = None, pdf_mode: bool = False):
        """Initialize router with evolved generators"""
        
        # Don't call parent __init__ yet - we need to set up evolved generators first
        self.api_key = api_key
        self.brave_api_key = brave_api_key
        
        # Store evolution directory for direct prompt loading (like 0815 run)
        self.evolution_output_dir = evolution_output_dir
        self.evolution_iteration = evolution_iteration
        self.prompt_only = prompt_only
        self.initial_prompt = initial_prompt
        self.pdf_mode = pdf_mode
        
        # Load auto-generated tools from previous iterations (skip in prompt-only mode)
        if prompt_only:
            logger.info("📝 Prompt-only mode: Skipping tool loading")
            self.auto_generated_tools = []
        else:
            self.auto_generated_tools = self._load_auto_generated_tools(evolution_iteration)
        
        # Determine which prompt to use
        evolved_prompt_text = None
        
        if initial_prompt:
            # Use provided initial prompt (for iteration 1)
            evolved_prompt_text = initial_prompt
            logger.info(f"🎯 Using provided initial prompt for iteration {evolution_iteration} ({len(initial_prompt)} chars)")
        elif evolution_iteration and evolution_iteration > 1:
            # Load evolved prompt from previous iteration (like 0815 run)
            evolved_prompt_text = self._load_evolved_prompt_direct(evolution_iteration - 1, pdf_mode)
            if evolved_prompt_text:
                mode_text = "PDF" if pdf_mode else "topic"
                logger.info(f"🧬 Loading EVOLVED {mode_text} prompt from iteration {evolution_iteration - 1}")
                logger.info(f"📝 Evolved prompt preview: {evolved_prompt_text[:100]}...")
            else:
                mode_text = "PDF" if pdf_mode else "topic"
                logger.info(f"⚠️  No evolved {mode_text} prompts found from iteration {evolution_iteration - 1}")
        
        if evolved_prompt_text:
            # Create appropriate evolved generators based on mode
            if pdf_mode:
                self.topic_generator = TopicGenerator(api_key, brave_api_key)
                self.pdf_generator = EvolvedPDFGenerator(
                    api_key,
                    evolved_prompt=evolved_prompt_text
                )
                logger.info(f"✅ Using evolved PDF generator with evolved prompts")
            else:
                self.topic_generator = EvolvedTopicGenerator(
                    api_key, 
                    brave_api_key,
                    evolved_prompt=evolved_prompt_text,
                    auto_generated_tools=self.auto_generated_tools
                )
                self.pdf_generator = PDFGenerator(api_key)
                logger.info(f"✅ Using evolved topic generator with evolved prompts")
        else:
            logger.info(f"📦 Using baseline prompts (no evolved/initial prompt available)")
            self._use_baseline_generators()
    
    def _load_auto_generated_tools(self, iteration: Optional[int]) -> List:
        """Load auto-generated tools from previous iterations, checking registry for failures"""
        tools = []
        if not iteration or iteration <= 1:
            return tools
        
        # Load registry to check for failed tools
        try:
            from .registry_initializer import RegistryInitializer
            registry = RegistryInitializer("TOOLS_REGISTRY.md")
            registry_data = registry.parse_registry()
            failed_tools = registry_data.get("failed_tools", {})
            logger.info(f"📚 Loaded registry with {len(failed_tools)} failed tools to avoid")
        except Exception as e:
            logger.warning(f"Could not load registry: {e}")
            failed_tools = {}
        
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
                                # Check if it's a class that has a process method (tool signature)
                                if isinstance(obj, type) and hasattr(obj, 'process') and name not in ["BaseTool", "EvolutionTool", "HTMLProcessingTool", "ContentProcessingTool", "ValidationTool"]:
                                    # Check if this tool is in failed list
                                    if name in failed_tools:
                                        logger.warning(f"  ⚠️ Skipping failed tool: {name} - {failed_tools[name].get('failure_reason', 'Unknown reason')}")
                                    else:
                                        try:
                                            # Instantiate the tool
                                            tool_instance = obj()
                                            # Set iteration info
                                            tool_instance.iteration_added = i
                                            tools.append(tool_instance)
                                            logger.info(f"  🔧 Loaded auto-generated tool: {name} (stage: {getattr(tool_instance, 'stage', 'unknown')})")
                                        except Exception as e:
                                            logger.error(f"  ❌ Failed to instantiate {name}: {e}")
            else:
                logger.info(f"  📂 No tools found in iteration {i}")
        
        logger.info(f"✅ Total auto-generated tools loaded: {len(tools)}")
        return tools
    
    def _load_evolved_prompt_direct(self, iteration_number: int, pdf_mode: bool = False) -> Optional[str]:
        """Load evolved prompt directly from evolved_prompts directory (like 0815 run)"""
        if not self.evolution_output_dir:
            logger.warning("⚠️ No evolution output directory specified")
            return None
        
        try:
            evolved_dir = Path(self.evolution_output_dir) / "evolved_prompts"
            
            # Choose appropriate prompt file based on mode
            if pdf_mode:
                prompt_file = evolved_dir / f"pdf_generation_prompt_v{iteration_number}.txt"
            else:
                prompt_file = evolved_dir / f"generation_prompt_v{iteration_number}.txt"
            
            if prompt_file.exists():
                evolved_prompt = prompt_file.read_text()
                logger.info(f"📝 Loaded evolved prompt: {prompt_file.relative_to(Path(self.evolution_output_dir))} ({len(evolved_prompt)} chars)")
                return evolved_prompt
            else:
                logger.warning(f"⚠️ Evolved prompt not found: {prompt_file}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load evolved prompt: {e}")
            return None
    
    def _use_baseline_generators(self):
        """Use standard production generators"""
        self.topic_generator = TopicGenerator(self.api_key, self.brave_api_key)
        self.pdf_generator = PDFGenerator(self.api_key)


class EvolvedTopicGenerator(TopicGenerator):
    """
    Topic generator that uses evolved prompts while keeping all other tools
    FIXED: Now properly uses ToolPipeline for all tool execution
    """
    
    def __init__(self, api_key, brave_api_key=None, evolved_prompt: str = None, auto_generated_tools: List = None):
        """Initialize with evolved prompt and auto-generated tools"""
        # Initialize parent with evolution tools ENABLED and skip prompt loading
        super().__init__(api_key, brave_api_key, enable_evolution_tools=True, skip_prompt_loading=True)
        self.evolved_prompt = evolved_prompt
        self.auto_generated_tools = auto_generated_tools or []
        
        if evolved_prompt:
            logger.info(f"📝 EvolvedTopicGenerator using provided prompt ({len(evolved_prompt)} chars)")
            # Set the prompt ourselves (parent skipped loading)
            self.generation_prompt = evolved_prompt
        else:
            logger.error(f"❌ EvolvedTopicGenerator initialized without prompt!")
            # This should not happen - fallback to None
            self.generation_prompt = None
        
        # CRITICAL FIX: Register auto-generated tools with the pipeline
        if self.auto_generated_tools and self.enable_evolution_tools and self.tool_pipeline:
            logger.info(f"🔧 Registering {len(self.auto_generated_tools)} auto-generated tools with pipeline")
            self._register_tools_with_pipeline()
    
    def _register_tools_with_pipeline(self):
        """Register auto-generated tools with the validation pipeline"""
        from opencanvas.evolution.core.tool_pipeline import ToolStage
        from opencanvas.evolution.core.base_tool import EvolutionTool
        
        for tool in self.auto_generated_tools:
            try:
                # Determine appropriate stage
                stage = ToolStage.POST_HTML  # Default
                if hasattr(tool, 'stage'):
                    stage_map = {
                        'post_blog': ToolStage.POST_BLOG,
                        'post_html': ToolStage.POST_HTML,
                        'pre_evaluation': ToolStage.PRE_EVALUATION
                    }
                    stage = stage_map.get(tool.stage, ToolStage.POST_HTML)
                
                # Wrap tool process method to ensure it inherits from base class validation
                if isinstance(tool, EvolutionTool):
                    # Tool already has proper validation
                    process_func = tool.safe_process
                else:
                    # Legacy tool - wrap with validation
                    def make_safe_wrapper(t):
                        def safe_wrapper(content, context=None):
                            try:
                                result = t.process(content)
                                
                                # CRITICAL: Type validation - must return string
                                if not isinstance(result, str):
                                    logger.error(f"Tool {t.name} returned {type(result).__name__}, expected str. Blocking tool output.")
                                    logger.error(f"Tool {t.name} result preview: {str(result)[:100]}...")
                                    return content  # Return original content
                                
                                # Check for debug messages
                                if any(marker in result for marker in ['[TOOL', '[DEBUG', 'ENHANCEMENT:']):
                                    logger.warning(f"Tool {t.name} tried to add debug message - blocked")
                                    return content  # Return original
                                    
                                return result
                            except Exception as e:
                                logger.error(f"Tool {t.name} failed: {e}")
                                return content  # Return original on error
                        return safe_wrapper
                    process_func = make_safe_wrapper(tool)
                
                # Register with pipeline
                success = self.tool_pipeline.register_tool(
                    name=getattr(tool, 'name', tool.__class__.__name__),
                    stage=stage,
                    function=process_func,
                    priority=getattr(tool, 'priority', 0),
                    iteration_added=getattr(tool, 'iteration_added', 0)
                )
                
                if success:
                    logger.info(f"  ✅ Registered {tool.name} with pipeline at stage {stage.value}")
                else:
                    logger.warning(f"  ❌ Failed to register {tool.name}")
                    
            except Exception as e:
                logger.error(f"  ❌ Error registering tool {getattr(tool, 'name', 'unknown')}: {e}")
    
    def _apply_auto_generated_tools(self, content: str, stage: str = "blog") -> str:
        """DEPRECATED: Tools are now applied through the pipeline in generate_from_topic"""
        logger.warning("_apply_auto_generated_tools called but tools should use pipeline now")
        return content  # Just return content unchanged
    
    def generate_blog(self, user_text, additional_context=None):
        """Generate blog content - tools are applied via pipeline in generate_from_topic"""
        
        # Just generate blog using parent method
        # Tools will be applied through the pipeline in generate_from_topic
        blog_content = super().generate_blog(user_text, additional_context)
        
        if self.auto_generated_tools:
            logger.info(f"ℹ️ {len(self.auto_generated_tools)} tools registered - will be applied via pipeline")
        
        return blog_content
    
    def generate_slides_html(self, blog_content, purpose, theme):
        """Generate HTML slide deck using evolved prompt - tools applied via pipeline"""
        
        # Tools are now applied through the pipeline in generate_from_topic
        # No need to manually apply them here
        
        if self.evolved_prompt:
            logger.info(f"🧬 Using EVOLVED slide generation prompt ({len(self.evolved_prompt)} chars)")
            # Since we set self.generation_prompt = evolved_prompt in __init__, 
            # just call parent method which will use the evolved prompt
            return super().generate_slides_html(blog_content, purpose, theme)
        else:
            logger.info(f"📦 Using BASELINE slide generation prompt")
            # Fall back to parent's implementation with baseline prompt
            return super().generate_slides_html(blog_content, purpose, theme)


class EvolvedPDFGenerator(PDFGenerator):
    """
    PDF generator that uses evolved prompts while keeping all other functionality
    """
    
    def __init__(self, api_key, evolved_prompt: str = None):
        """Initialize with evolved prompt"""
        super().__init__(api_key)
        self.evolved_prompt = evolved_prompt
        
        if evolved_prompt:
            logger.info(f"📝 EvolvedPDFGenerator using evolved prompt ({len(evolved_prompt)} chars)")
        else:
            logger.error(f"❌ EvolvedPDFGenerator initialized without evolved prompt!")
    
    def generate_slides_html(self, pdf_data, presentation_focus, theme="professional", extract_images=False, output_dir=None):
        """Generate HTML slides directly from PDF content using evolved prompt."""
        
        self.presentation_focus = presentation_focus
        
        # Extract images and captions if enabled (copied from parent)
        image_captions = {}
        extracted_images_dir = None
        if extract_images and output_dir:
            logger.info("🔍 Extracting images and captions from PDF...")
            image_captions, extracted_images_dir, plots = self._extract_images_and_captions(pdf_data, output_dir)
            
            if image_captions:
                logger.info(f"📸 Found {len(image_captions)} images with captions")
            else:
                logger.info("📸 No images found in PDF")
        
        # Build image context for prompt (copied from parent)
        image_context = ""
        if image_captions:
            image_context = "\n\n<extracted_images>\n"
            image_context += "The following images have been extracted from the PDF with their captions and dimensions:\n"
            for image_id, info in image_captions.items():
                dimensions = info.get('dimensions', 'unknown')
                image_context += f"- {image_id}: {info['caption']} (file: {info['path']}, size: {dimensions})\n"
            image_context += "\nPlease incorporate these images into the presentation using their file paths.\n"
            image_context += "Use <img src='../extracted_images/image_id.png' alt='caption'> format.\n"
            image_context += "Consider the image dimensions when placing them in the layout to ensure proper fit.\n"
            image_context += "</extracted_images>\n"
        
        # Use evolved prompt if available, otherwise fallback to hardcoded
        if self.evolved_prompt:
            logger.info("🧬 Using EVOLVED PDF generation prompt")
            try:
                # Import static examples functions for PDF mode
                from .pdf_static_examples import remove_static_sections, add_static_examples
                
                # Remove static sections before formatting to avoid brace escaping issues
                prompt_without_static = remove_static_sections(self.evolved_prompt)
                logger.debug(f"🔧 Removed static sections: {len(self.evolved_prompt)} → {len(prompt_without_static)} chars")
                
                # Format the prompt without static sections
                logger.debug(f"🔧 Formatting evolved prompt with: presentation_focus='{presentation_focus}', theme='{theme}', image_context len={len(image_context)}")
                formatted_prompt = prompt_without_static.format(
                    presentation_focus=presentation_focus,
                    theme=theme,
                    image_context=image_context
                )
                
                # Add static sections back after formatting
                academic_gen_prompt = add_static_examples(formatted_prompt)
                logger.info(f"✅ Successfully formatted evolved prompt with static examples: {len(academic_gen_prompt)} characters")
            except Exception as e:
                logger.error(f"❌ Failed to format evolved prompt: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                logger.error(f"❌ Prompt preview (first 200 chars): {self.evolved_prompt[:200]}...")
                logger.info("🔄 Falling back to hardcoded prompt")
                academic_gen_prompt = self._get_fallback_prompt(presentation_focus, theme, image_context)
        else:
            logger.info("📦 Using fallback hardcoded prompt")
            academic_gen_prompt = self._get_fallback_prompt(presentation_focus, theme, image_context)
        
        try:
            logger.info("🔍 Analyzing PDF and generating slides using evolved prompt...")
            logger.info("📡 Using streaming for long-running operation...")
            
            # Use streaming for long operations (copied from parent)
            stream = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50000,
                temperature=0.7,
                stream=True,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": academic_gen_prompt
                            }
                        ],
                    }
                ],
            )
            
            # Collect the streamed response (copied from parent)
            html_content = ""
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    html_content += chunk.delta.text
                    # Log progress every 1000 characters
                    if len(html_content) % 1000 == 0:
                        logger.info(f"📝 Generated {len(html_content)} characters...")
            
            logger.info(f"✅ Completed evolved PDF generation: {len(html_content)} characters")
            return self.clean_html_content(html_content), None

        except Exception as e:
            return None, f"Error generating slides with evolved prompt: {str(e)}"
    
    def _get_fallback_prompt(self, presentation_focus, theme, image_context):
        """Get fallback hardcoded prompt in case evolved prompt fails"""
        return f'''<presentation_task>
Create a stunning, visually captivating HTML presentation that makes viewers stop and say "wow" based on this PDF document.

**Purpose of presentation:** {presentation_focus}
**Visual theme:** {theme}
</presentation_task>

<design_philosophy>
CREATE EMOTIONAL IMPACT:
- Prioritize the "wow factor" over conventional academic design
- Make every slide feel alive and dynamic with subtle animations
- Choose bold, vibrant colors over muted, safe academic palettes
- Use cutting-edge web design trends (glassmorphism, gradient overlays, micro-animations)
- Push the boundaries of what's possible with modern CSS and JavaScript
- Create a premium, cutting-edge experience that feels expensive and engaging
</design_philosophy>

<output_requirements>
IMPORTANT: The HTML must be a complete, self-contained file that opens directly in a browser and immediately impresses with its sophisticated visual design and smooth interactions.

IMPORTANT: Output ONLY the complete HTML code. Start with <!DOCTYPE html> and end with </html>. No explanations, no markdown formatting around the code.
</output_requirements>
{image_context}
'''