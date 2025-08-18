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
    
    def __init__(self, api_key=None, brave_api_key=None, evolution_iteration: Optional[int] = None, prompt_only: bool = False, evolution_output_dir: Optional[str] = None, initial_prompt: Optional[str] = None):
        """Initialize router with evolved generators"""
        
        # Don't call parent __init__ yet - we need to set up evolved generators first
        self.api_key = api_key
        self.brave_api_key = brave_api_key
        
        # Store evolution directory for direct prompt loading (like 0815 run)
        self.evolution_output_dir = evolution_output_dir
        self.evolution_iteration = evolution_iteration
        self.prompt_only = prompt_only
        self.initial_prompt = initial_prompt
        
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
            evolved_prompt_text = self._load_evolved_prompt_direct(evolution_iteration - 1)
            if evolved_prompt_text:
                logger.info(f"🧬 Loading EVOLVED prompt from iteration {evolution_iteration - 1}")
                logger.info(f"📝 Evolved prompt preview: {evolved_prompt_text[:100]}...")
            else:
                logger.info(f"⚠️  No evolved prompts found from iteration {evolution_iteration - 1}")
        
        if evolved_prompt_text:
            # Create patched generators with evolved/initial prompts and tools
            self.topic_generator = EvolvedTopicGenerator(
                api_key, 
                brave_api_key,
                evolved_prompt=evolved_prompt_text,
                auto_generated_tools=self.auto_generated_tools
            )
            self.pdf_generator = PDFGenerator(api_key)  # Keep PDF generator standard for now
            
            logger.info(f"✅ Using evolved/initial prompts for generation")
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
    
    def _load_evolved_prompt_direct(self, iteration_number: int) -> Optional[str]:
        """Load evolved prompt directly from evolved_prompts directory (like 0815 run)"""
        if not self.evolution_output_dir:
            logger.warning("⚠️ No evolution output directory specified")
            return None
        
        try:
            evolved_dir = Path(self.evolution_output_dir) / "evolved_prompts"
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