"""
Tool Pipeline System - Integrates evolution tools into generation pipeline
This ensures tools can process content without breaking the presentation
"""

import logging
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToolStage(Enum):
    """Stages where tools can be applied in the generation pipeline"""
    PRE_GENERATION = "pre_generation"      # Before content generation
    POST_BLOG = "post_blog"                # After blog content creation
    POST_HTML = "post_html"                # After HTML generation
    PRE_EVALUATION = "pre_evaluation"      # Before evaluation
    POST_EVALUATION = "post_evaluation"    # After evaluation

@dataclass
class Tool:
    """Represents an evolution tool"""
    name: str
    stage: ToolStage
    function: Callable
    priority: int = 0  # Higher priority runs first
    enabled: bool = True
    iteration_added: int = 0
    metadata: Dict[str, Any] = None

class ToolPipeline:
    """
    Manages the execution of evolution tools in the generation pipeline.
    Tools are registered at specific stages and executed in order.
    """
    
    def __init__(self):
        """Initialize the tool pipeline"""
        self.tools: Dict[ToolStage, List[Tool]] = {
            stage: [] for stage in ToolStage
        }
        self.execution_log: List[Dict] = []
        
        logger.info("🔧 Tool Pipeline initialized")
    
    def register_tool(self, 
                     name: str,
                     stage: ToolStage,
                     function: Callable,
                     priority: int = 0,
                     iteration_added: int = 0) -> bool:
        """
        Register a tool to run at a specific stage
        
        Args:
            name: Tool name
            stage: Pipeline stage to run at
            function: The tool function to execute
            priority: Execution priority (higher = earlier)
            iteration_added: Evolution iteration when added
        
        Returns:
            True if registered successfully
        """
        try:
            tool = Tool(
                name=name,
                stage=stage,
                function=function,
                priority=priority,
                iteration_added=iteration_added
            )
            
            # Add to appropriate stage
            self.tools[stage].append(tool)
            
            # Sort by priority
            self.tools[stage].sort(key=lambda t: t.priority, reverse=True)
            
            logger.info(f"✅ Registered tool '{name}' at stage {stage.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register tool '{name}': {e}")
            return False
    
    def execute_stage(self, 
                     stage: ToolStage, 
                     content: Any,
                     context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute all tools for a given stage
        
        Args:
            stage: The pipeline stage to execute
            content: The content to process (HTML, text, etc.)
            context: Optional context for tools (topic, purpose, etc.)
        
        Returns:
            Processed content after all tools have run
        """
        stage_tools = [t for t in self.tools[stage] if t.enabled]
        
        if not stage_tools:
            logger.debug(f"No tools registered for stage {stage.value}")
            return content
        
        logger.info(f"🔄 Executing {len(stage_tools)} tools for stage {stage.value}")
        
        processed_content = content
        for tool in stage_tools:
            try:
                logger.info(f"  Running tool: {tool.name}")
                
                # Execute tool with proper error handling
                result = self._execute_tool_safely(
                    tool, 
                    processed_content, 
                    context
                )
                
                # Only update content if tool succeeded
                if result is not None:
                    processed_content = result
                    self._log_execution(tool.name, stage, "success")
                else:
                    logger.warning(f"  ⚠️ Tool '{tool.name}' returned None, skipping")
                    self._log_execution(tool.name, stage, "skipped")
                    
            except Exception as e:
                logger.error(f"  ❌ Tool '{tool.name}' failed: {e}")
                self._log_execution(tool.name, stage, "failed", str(e))
                # Continue with other tools even if one fails
        
        return processed_content
    
    def _execute_tool_safely(self, 
                           tool: Tool, 
                           content: Any,
                           context: Optional[Dict] = None) -> Any:
        """
        Execute a tool with proper error handling and validation
        
        Args:
            tool: The tool to execute
            content: Content to process
            context: Optional context
        
        Returns:
            Processed content or None if failed
        """
        try:
            # Check function signature
            sig = inspect.signature(tool.function)
            params = sig.parameters
            
            # Call with appropriate parameters
            if len(params) == 1:
                # Simple tool - just takes content
                return tool.function(content)
            elif len(params) == 2 and context is not None:
                # Context-aware tool
                return tool.function(content, context)
            else:
                logger.warning(f"Tool '{tool.name}' has unexpected signature")
                return None
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return None
    
    def _log_execution(self, 
                      tool_name: str, 
                      stage: ToolStage,
                      status: str,
                      error: Optional[str] = None):
        """Log tool execution for debugging"""
        from datetime import datetime
        self.execution_log.append({
            "tool": tool_name,
            "stage": stage.value,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def load_evolution_tools(self, iteration: int) -> int:
        """
        Load tools from a specific evolution iteration
        
        Args:
            iteration: Evolution iteration number
        
        Returns:
            Number of tools loaded
        """
        tools_loaded = 0
        
        # Look for tools in iteration directory
        tools_dir = Path(f"src/opencanvas/evolution/tools/iteration_{iteration:03d}")
        
        if not tools_dir.exists():
            logger.warning(f"No tools directory for iteration {iteration}")
            return 0
        
        # Load each tool module
        for tool_file in tools_dir.glob("*.py"):
            if tool_file.name == "__init__.py":
                continue
            
            try:
                # Import the module
                module_name = f"opencanvas.evolution.tools.iteration_{iteration:03d}.{tool_file.stem}"
                module = importlib.import_module(module_name)
                
                # Look for tool class or function
                tool_loaded = self._load_tool_from_module(
                    module, 
                    tool_file.stem,
                    iteration
                )
                
                if tool_loaded:
                    tools_loaded += 1
                    
            except Exception as e:
                logger.error(f"Failed to load tool {tool_file.name}: {e}")
        
        logger.info(f"📦 Loaded {tools_loaded} tools from iteration {iteration}")
        return tools_loaded
    
    def _load_tool_from_module(self, 
                              module: Any, 
                              tool_name: str,
                              iteration: int) -> bool:
        """
        Load a tool from an imported module
        
        Args:
            module: The imported module
            tool_name: Name of the tool
            iteration: Evolution iteration
        
        Returns:
            True if tool was loaded successfully
        """
        # Look for a class that matches the tool name pattern
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and "Tool" in name:
                try:
                    # Instantiate the tool
                    tool_instance = obj()
                    
                    # Get the stage and process method
                    if hasattr(tool_instance, 'stage') and hasattr(tool_instance, 'process'):
                        stage = ToolStage(tool_instance.stage)
                        
                        self.register_tool(
                            name=name,
                            stage=stage,
                            function=tool_instance.process,
                            priority=getattr(tool_instance, 'priority', 0),
                            iteration_added=iteration
                        )
                        return True
                        
                except Exception as e:
                    logger.error(f"Failed to instantiate {name}: {e}")
        
        # Look for standalone functions with metadata
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, 'tool_stage'):
                stage = ToolStage(obj.tool_stage)
                
                self.register_tool(
                    name=name,
                    stage=stage,
                    function=obj,
                    priority=getattr(obj, 'priority', 0),
                    iteration_added=iteration
                )
                return True
        
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool without removing it"""
        for stage_tools in self.tools.values():
            for tool in stage_tools:
                if tool.name == tool_name:
                    tool.enabled = False
                    logger.info(f"⏸️ Disabled tool '{tool_name}'")
                    return True
        return False
    
    def enable_tool(self, tool_name: str) -> bool:
        """Re-enable a disabled tool"""
        for stage_tools in self.tools.values():
            for tool in stage_tools:
                if tool.name == tool_name:
                    tool.enabled = True
                    logger.info(f"▶️ Enabled tool '{tool_name}'")
                    return True
        return False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        status = {
            "total_tools": sum(len(tools) for tools in self.tools.values()),
            "stages": {}
        }
        
        for stage, tools in self.tools.items():
            enabled = [t for t in tools if t.enabled]
            status["stages"][stage.value] = {
                "total": len(tools),
                "enabled": len(enabled),
                "tools": [t.name for t in enabled]
            }
        
        return status
    
    def clear_stage(self, stage: ToolStage):
        """Clear all tools from a specific stage"""
        self.tools[stage] = []
        logger.info(f"🧹 Cleared all tools from stage {stage.value}")
    
    def clear_all(self):
        """Clear all tools from pipeline"""
        for stage in ToolStage:
            self.tools[stage] = []
        logger.info("🧹 Cleared all tools from pipeline")


# Global pipeline instance
_pipeline_instance = None

def get_tool_pipeline() -> ToolPipeline:
    """Get or create the global tool pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ToolPipeline()
    return _pipeline_instance