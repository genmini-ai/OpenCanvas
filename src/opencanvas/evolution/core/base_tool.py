"""
Base class for evolution tools
Ensures tools follow the correct pattern and don't break presentations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EvolutionTool(ABC):
    """
    Base class for all evolution tools.
    Tools must inherit from this class to ensure proper integration.
    """
    
    # Tool metadata - must be set by subclasses
    name: str = "UnnamedTool"
    stage: str = "post_html"  # Default stage
    priority: int = 0
    description: str = ""
    
    def __init__(self):
        """Initialize the tool"""
        self.execution_count = 0
        self.last_error = None
    
    @abstractmethod
    def process(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process the content at the specified pipeline stage.
        
        Args:
            content: The content to process (HTML string, dict, etc.)
            context: Optional context with metadata (topic, purpose, etc.)
        
        Returns:
            Modified content. MUST return content even if unchanged.
            Never return None or add debug messages to content.
        """
        pass
    
    def validate_input(self, content: Any) -> bool:
        """
        Validate that input content is appropriate for this tool.
        Override in subclasses for specific validation.
        
        Args:
            content: The content to validate
        
        Returns:
            True if content is valid
        """
        return content is not None
    
    def validate_output(self, content: Any) -> bool:
        """
        Validate that output content is valid.
        Override in subclasses for specific validation.
        
        Args:
            content: The content to validate
        
        Returns:
            True if content is valid
        """
        return content is not None
    
    def safe_process(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Safely process content with validation and error handling.
        This is what the pipeline actually calls.
        
        Args:
            content: The content to process
            context: Optional context
        
        Returns:
            Processed content or original if processing fails
        """
        try:
            # Validate input
            if not self.validate_input(content):
                logger.warning(f"{self.name}: Invalid input, returning unmodified")
                return content
            
            # Process content
            processed = self.process(content, context)
            
            # Validate output
            if not self.validate_output(processed):
                logger.error(f"{self.name}: Invalid output, returning original")
                return content
            
            self.execution_count += 1
            return processed
            
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            self.last_error = str(e)
            # Always return original content on error
            return content


class HTMLProcessingTool(EvolutionTool):
    """
    Base class for tools that process HTML content.
    Includes HTML-specific validation.
    """
    
    stage = "post_html"  # Most HTML tools run after HTML generation
    
    def validate_input(self, content: Any) -> bool:
        """Validate HTML input"""
        if not isinstance(content, str):
            return False
        
        # Basic HTML validation
        return "<html" in content.lower() or "<div" in content.lower()
    
    def validate_output(self, content: Any) -> bool:
        """Validate HTML output"""
        if not isinstance(content, str):
            return False
        
        # Ensure we still have valid HTML
        has_html = "<html" in content.lower() or "<div" in content.lower()
        
        # CRITICAL: Ensure no debug messages in output
        has_debug = any(marker in content for marker in [
            "[TOOL", "[DEBUG", "[INFO", "[ERROR", "ENHANCEMENT:",
            "validated by", "processed by", "enhanced by"
        ])
        
        if has_debug:
            logger.error(f"{self.name}: Debug messages found in output!")
            return False
        
        return has_html


class ContentProcessingTool(EvolutionTool):
    """
    Base class for tools that process text/blog content.
    """
    
    stage = "post_blog"  # Process after blog generation
    
    def validate_input(self, content: Any) -> bool:
        """Validate text content input"""
        return isinstance(content, (str, dict))
    
    def validate_output(self, content: Any) -> bool:
        """Validate text content output"""
        if not isinstance(content, (str, dict)):
            return False
        
        # Ensure no debug messages
        content_str = str(content)
        has_debug = any(marker in content_str for marker in [
            "[TOOL", "[DEBUG", "[INFO", "[ERROR"
        ])
        
        return not has_debug


class ValidationTool(EvolutionTool):
    """
    Base class for validation tools that check but don't modify content.
    """
    
    stage = "pre_evaluation"  # Run before evaluation
    
    def process(self, content: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Validation tools should check content but not modify it.
        
        Args:
            content: Content to validate
            context: Optional context
        
        Returns:
            Original content (unmodified)
        """
        # Run validation
        is_valid = self.validate(content, context)
        
        # Log result but don't modify content
        if is_valid:
            logger.info(f"{self.name}: Validation passed")
        else:
            logger.warning(f"{self.name}: Validation failed")
        
        # ALWAYS return original content
        return content
    
    @abstractmethod
    def validate(self, content: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Perform validation check.
        
        Args:
            content: Content to validate
            context: Optional context
        
        Returns:
            True if validation passes
        """
        pass