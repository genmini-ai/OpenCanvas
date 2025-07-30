"""
Base Agent class for the multi-agent evolution system
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from opencanvas.config import Config

logger = logging.getLogger(__name__)

class BaseEvolutionAgent(ABC):
    """Base class for all evolution agents"""
    
    def __init__(self, name: str, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize base agent"""
        self.name = name
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.model = model
        
        if self.api_key:
            self.claude = Anthropic(api_key=self.api_key)
        else:
            self.claude = None
            logger.warning(f"{self.name} agent: No API key provided")
        
        # Agent history for context
        self.history = []
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the specialized system prompt for this agent"""
        pass
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def call_claude(self, user_prompt: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call Claude API with agent's system prompt"""
        if not self.claude:
            return {"error": "No Claude API client available"}
        
        try:
            # Build context-aware prompt
            full_prompt = self._build_context_prompt(user_prompt, context_data)
            
            message = self.claude.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.1,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON if present
            if "{" in response_text and "}" in response_text:
                try:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    json_str = response_text[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                    
                    # Add raw response for debugging
                    parsed_result["_raw_response"] = response_text
                    return parsed_result
                except json.JSONDecodeError:
                    # If JSON parsing fails, return structured response
                    pass
            
            # Return structured response even if no JSON
            return {
                "response": response_text,
                "agent": self.name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"{self.name} agent API call failed: {e}")
            return {
                "error": str(e),
                "agent": self.name,
                "success": False
            }
    
    def _build_context_prompt(self, user_prompt: str, context_data: Dict[str, Any] = None) -> str:
        """Build context-aware prompt with relevant history and data"""
        prompt_parts = []
        
        # Add context data if provided
        if context_data:
            prompt_parts.append("CONTEXT DATA:")
            prompt_parts.append(json.dumps(context_data, indent=2))
            prompt_parts.append("")
        
        # Add recent history if available
        if self.history:
            prompt_parts.append("PREVIOUS CONTEXT (last 2 interactions):")
            for entry in self.history[-2:]:
                prompt_parts.append(f"- {entry['action']}: {entry['summary']}")
            prompt_parts.append("")
        
        # Add main prompt
        prompt_parts.append("CURRENT REQUEST:")
        prompt_parts.append(user_prompt)
        
        return "\n".join(prompt_parts)
    
    def add_to_history(self, action: str, summary: str, full_data: Dict[str, Any] = None):
        """Add interaction to agent history"""
        entry = {
            "action": action,
            "summary": summary,
            "timestamp": json.dumps({"time": "now"}),  # Simplified for now
            "full_data": full_data
        }
        
        self.history.append(entry)
        
        # Keep only last 10 entries
        if len(self.history) > 10:
            self.history = self.history[-10:]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities"""
        return {
            "name": self.name,
            "model": self.model,
            "api_available": self.claude is not None,
            "history_length": len(self.history),
            "last_action": self.history[-1]["action"] if self.history else None
        }
    
    def reset_history(self):
        """Reset agent history"""
        self.history = []
        logger.info(f"{self.name} agent history reset")