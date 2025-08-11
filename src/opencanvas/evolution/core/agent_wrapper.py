"""
Agent Wrapper - Adds robustness with retries and partial progress handling
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class AgentExecutor:
    """
    Wrapper for agent execution with retry logic and partial progress handling
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0, exponential_backoff: bool = True):
        """
        Initialize agent executor with retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        
        logger.info(f"🛡️ AgentExecutor initialized with max_retries={max_retries}, retry_delay={retry_delay}s")
    
    def execute_with_retry(self, 
                          agent_func: Callable,
                          request: Dict[str, Any],
                          agent_name: str = "Agent",
                          allow_partial: bool = True) -> Dict[str, Any]:
        """
        Execute an agent function with retry logic
        
        Args:
            agent_func: The agent function to execute
            request: Request dictionary for the agent
            agent_name: Name of the agent for logging
            allow_partial: Whether to accept partial results on failure
        
        Returns:
            Agent response or partial result
        """
        last_error = None
        partial_result = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 {agent_name} execution attempt {attempt + 1}/{self.max_retries}")
                
                # Execute the agent function
                result = agent_func(request)
                
                # Check if result indicates success
                if result and result.get("success", False):
                    logger.info(f"✅ {agent_name} execution successful on attempt {attempt + 1}")
                    return result
                
                # If not successful but has partial data, save it
                if allow_partial and result and self._has_useful_data(result):
                    partial_result = result
                    logger.warning(f"⚠️ {agent_name} returned partial result on attempt {attempt + 1}")
                
                # Agent returned unsuccessful result
                error = result.get("error", "Unknown error")
                logger.warning(f"⚠️ {agent_name} failed on attempt {attempt + 1}: {error}")
                last_error = error
                
            except Exception as e:
                logger.error(f"❌ {agent_name} threw exception on attempt {attempt + 1}: {e}")
                last_error = str(e)
            
            # Calculate retry delay
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt if self.exponential_backoff else 1)
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
        
        # All retries exhausted
        logger.error(f"❌ {agent_name} failed after {self.max_retries} attempts")
        
        # Return partial result if available
        if allow_partial and partial_result:
            logger.info(f"📊 Returning partial result for {agent_name}")
            partial_result["partial"] = True
            partial_result["retry_count"] = self.max_retries
            partial_result["last_error"] = last_error
            return partial_result
        
        # Return failure result
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} attempts. Last error: {last_error}",
            "agent": agent_name,
            "retry_count": self.max_retries
        }
    
    def _has_useful_data(self, result: Dict[str, Any]) -> bool:
        """
        Check if a result contains useful partial data
        
        Args:
            result: Agent result to check
        
        Returns:
            True if result has useful data
        """
        # Check for common useful fields
        useful_fields = [
            "evaluation_data",
            "improvements",
            "tools_discovered",
            "prompts_evolved",
            "analysis",
            "recommendations",
            "phases"  # For multi-phase agents
        ]
        
        for field in useful_fields:
            if field in result and result[field]:
                return True
        
        return False
    
    def execute_with_checkpoints(self,
                                agent_func: Callable,
                                request: Dict[str, Any],
                                agent_name: str = "Agent",
                                checkpoint_handler: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute agent with checkpoint support for long-running operations
        
        Args:
            agent_func: The agent function to execute
            request: Request dictionary for the agent
            agent_name: Name of the agent for logging
            checkpoint_handler: Optional function to handle checkpoints
        
        Returns:
            Agent response with checkpoint data
        """
        logger.info(f"🏁 Starting {agent_name} with checkpoint support")
        
        # Check for existing checkpoint
        checkpoint_data = None
        if checkpoint_handler:
            checkpoint_data = checkpoint_handler("load", agent_name, None)
            if checkpoint_data:
                logger.info(f"📂 Found checkpoint for {agent_name}, resuming...")
                request["checkpoint_data"] = checkpoint_data
        
        try:
            # Execute with retries
            result = self.execute_with_retry(agent_func, request, agent_name)
            
            # Save checkpoint if successful
            if checkpoint_handler and result.get("success"):
                checkpoint_handler("save", agent_name, result)
                logger.info(f"💾 Saved checkpoint for {agent_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {agent_name} failed with checkpoint: {e}")
            
            # Try to save partial progress
            if checkpoint_handler:
                checkpoint_handler("save_partial", agent_name, {
                    "error": str(e),
                    "request": request,
                    "timestamp": time.time()
                })
            
            return {
                "success": False,
                "error": str(e),
                "agent": agent_name,
                "checkpoint_available": checkpoint_data is not None
            }


def robust_agent_call(max_retries: int = 3, allow_partial: bool = True):
    """
    Decorator for making agent calls robust with automatic retries
    
    Args:
        max_retries: Maximum number of retry attempts
        allow_partial: Whether to accept partial results
    
    Usage:
        @robust_agent_call(max_retries=3)
        def my_agent_function(request):
            # Agent logic here
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            executor = AgentExecutor(max_retries=max_retries)
            
            # Extract agent name from function name
            agent_name = func.__name__.replace("_", " ").title()
            
            # Create request from args/kwargs
            if args and isinstance(args[0], dict):
                request = args[0]
            else:
                request = kwargs
            
            # Execute with retry
            return executor.execute_with_retry(
                lambda r: func(*args, **kwargs),
                request,
                agent_name,
                allow_partial
            )
        
        return wrapper
    return decorator


class PartialProgressTracker:
    """
    Tracks partial progress across agent executions
    """
    
    def __init__(self):
        """Initialize partial progress tracker"""
        self.progress_data = {}
        self.completed_steps = set()
        
    def mark_completed(self, step: str, data: Any = None):
        """Mark a step as completed with optional data"""
        self.completed_steps.add(step)
        if data is not None:
            self.progress_data[step] = data
        logger.info(f"✅ Step completed: {step}")
    
    def is_completed(self, step: str) -> bool:
        """Check if a step is completed"""
        return step in self.completed_steps
    
    def get_progress_data(self, step: str) -> Optional[Any]:
        """Get data for a completed step"""
        return self.progress_data.get(step)
    
    def get_completion_percentage(self, total_steps: int) -> float:
        """Get completion percentage"""
        if total_steps == 0:
            return 0.0
        return (len(self.completed_steps) / total_steps) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        return {
            "completed_steps": list(self.completed_steps),
            "total_completed": len(self.completed_steps),
            "has_data": list(self.progress_data.keys())
        }