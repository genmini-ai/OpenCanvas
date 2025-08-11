"""
Persistent Tools Registry Manager
Maintains tool knowledge across evolution runs
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ToolRecord:
    """Record of a tool's status and performance"""
    name: str
    status: str  # ACTIVE, PROPOSED, FAILED, RETIRED
    purpose: str
    impact: float
    iteration_added: int
    success_rate: float = 0.0
    failure_reason: Optional[str] = None
    implementation_strategy: Optional[Dict] = None
    performance_history: List[Dict] = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []

class ToolsRegistry:
    """
    Persistent registry of all tools across evolution runs.
    This maintains institutional knowledge about what works and what doesn't.
    """
    
    def __init__(self, registry_path: str = "TOOLS_REGISTRY.md"):
        """Initialize the tools registry"""
        self.registry_path = Path(registry_path)
        self.registry_json_path = Path("tools_registry.json")  # Structured data backup
        self.tools = self._load_registry()
        
        logger.info(f"📚 Tools Registry initialized with {len(self.tools)} tools")
        self._log_registry_summary()
    
    def _load_registry(self) -> Dict[str, ToolRecord]:
        """Load registry from JSON (primary) or parse from MD (fallback)"""
        tools = {}
        
        # Try loading from JSON first (structured data)
        if self.registry_json_path.exists():
            try:
                with open(self.registry_json_path, 'r') as f:
                    data = json.load(f)
                    for name, tool_data in data.items():
                        tools[name] = ToolRecord(**tool_data)
                logger.info(f"✅ Loaded {len(tools)} tools from JSON registry")
                return tools
            except Exception as e:
                logger.warning(f"Failed to load JSON registry: {e}, falling back to MD")
        
        # Initialize with baseline tools if no registry exists
        if not self.registry_path.exists():
            logger.info("📝 Initializing new tools registry")
            tools = self._initialize_baseline_tools()
            self._save_registry(tools)
        
        return tools
    
    def _initialize_baseline_tools(self) -> Dict[str, ToolRecord]:
        """Initialize with known baseline tools"""
        return {
            "ImageValidationPipeline": ToolRecord(
                name="ImageValidationPipeline",
                status="ACTIVE",
                purpose="Validates and replaces broken/placeholder images",
                impact=0.3,
                iteration_added=0,
                success_rate=0.95
            ),
            "CitationExtractor": ToolRecord(
                name="CitationExtractor",
                status="ACTIVE", 
                purpose="Extracts citations from source materials",
                impact=0.2,
                iteration_added=0,
                success_rate=0.88
            )
        }
    
    def _save_registry(self, tools: Dict[str, ToolRecord]):
        """Save registry to both JSON and update MD"""
        # Save to JSON for structured access
        json_data = {name: asdict(tool) for name, tool in tools.items()}
        with open(self.registry_json_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        # Update MD file for human readability
        self._update_markdown_registry(tools)
        
        logger.info(f"💾 Saved registry with {len(tools)} tools")
    
    def _update_markdown_registry(self, tools: Dict[str, ToolRecord]):
        """Update the markdown registry file"""
        # This would parse and update the MD file
        # For now, we'll append updates to a log section
        if not self.registry_path.exists():
            return
            
        with open(self.registry_path, 'a') as f:
            f.write(f"\n\n---\n## 📝 Update Log\n")
            f.write(f"*Updated: {datetime.now().isoformat()}*\n\n")
            
            active = [t for t in tools.values() if t.status == "ACTIVE"]
            proposed = [t for t in tools.values() if t.status == "PROPOSED"]
            failed = [t for t in tools.values() if t.status == "FAILED"]
            
            f.write(f"- Active Tools: {len(active)}\n")
            f.write(f"- Proposed Tools: {len(proposed)}\n")
            f.write(f"- Failed Tools: {len(failed)}\n")
    
    def _log_registry_summary(self):
        """Log summary of current registry state"""
        active = [t for t in self.tools.values() if t.status == "ACTIVE"]
        proposed = [t for t in self.tools.values() if t.status == "PROPOSED"]
        failed = [t for t in self.tools.values() if t.status == "FAILED"]
        
        logger.info(f"  📊 Registry Summary:")
        logger.info(f"    - Active Tools: {len(active)}")
        logger.info(f"    - Proposed Tools: {len(proposed)}")
        logger.info(f"    - Failed Tools: {len(failed)}")
        
        if active:
            avg_impact = sum(t.impact for t in active) / len(active)
            logger.info(f"    - Average Active Tool Impact: +{avg_impact:.2f}")
    
    def propose_tool(self, name: str, purpose: str, expected_impact: float, 
                    strategy: Dict, iteration: int) -> bool:
        """Propose a new tool"""
        
        # Check if tool already exists
        if name in self.tools:
            existing = self.tools[name]
            if existing.status == "FAILED":
                logger.warning(f"⚠️ Tool {name} previously failed: {existing.failure_reason}")
                return False
            elif existing.status == "ACTIVE":
                logger.info(f"✅ Tool {name} already active")
                return True
        
        # Create new tool record
        tool = ToolRecord(
            name=name,
            status="PROPOSED",
            purpose=purpose,
            impact=expected_impact,
            iteration_added=iteration,
            implementation_strategy=strategy
        )
        
        self.tools[name] = tool
        self._save_registry(self.tools)
        
        logger.info(f"💡 Proposed new tool: {name} (expected impact: +{expected_impact:.2f})")
        return True
    
    def activate_tool(self, name: str, actual_impact: float) -> bool:
        """Activate a proposed tool after successful implementation"""
        
        if name not in self.tools:
            logger.error(f"Tool {name} not found in registry")
            return False
        
        tool = self.tools[name]
        tool.status = "ACTIVE"
        tool.impact = actual_impact
        tool.success_rate = 1.0  # Initial success
        
        # Add to performance history
        tool.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "activated",
            "impact": actual_impact
        })
        
        self._save_registry(self.tools)
        logger.info(f"✅ Activated tool: {name} (actual impact: +{actual_impact:.2f})")
        return True
    
    def mark_tool_failed(self, name: str, reason: str, impact: float) -> bool:
        """Mark a tool as failed"""
        
        if name not in self.tools:
            # Create record for failed tool not in registry
            tool = ToolRecord(
                name=name,
                status="FAILED",
                purpose="Unknown",
                impact=impact,
                iteration_added=-1,
                failure_reason=reason
            )
            self.tools[name] = tool
        else:
            tool = self.tools[name]
            tool.status = "FAILED"
            tool.failure_reason = reason
            tool.impact = impact
        
        # Add to performance history
        tool.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "failed",
            "reason": reason,
            "impact": impact
        })
        
        self._save_registry(self.tools)
        logger.warning(f"❌ Marked tool as failed: {name} (impact: {impact:.2f})")
        logger.warning(f"   Reason: {reason}")
        return True
    
    def get_active_tools(self) -> List[ToolRecord]:
        """Get all active tools"""
        return [t for t in self.tools.values() if t.status == "ACTIVE"]
    
    def get_proposed_tools(self) -> List[ToolRecord]:
        """Get all proposed tools"""
        return [t for t in self.tools.values() if t.status == "PROPOSED"]
    
    def get_failed_tools(self) -> List[ToolRecord]:
        """Get all failed tools to avoid"""
        return [t for t in self.tools.values() if t.status == "FAILED"]
    
    def get_high_impact_opportunities(self) -> List[ToolRecord]:
        """Get proposed tools with high expected impact"""
        proposed = self.get_proposed_tools()
        return sorted(proposed, key=lambda t: t.impact, reverse=True)[:5]
    
    def update_tool_performance(self, name: str, before_score: float, 
                               after_score: float) -> float:
        """Update tool performance metrics"""
        
        if name not in self.tools:
            logger.error(f"Tool {name} not found in registry")
            return 0.0
        
        tool = self.tools[name]
        actual_impact = after_score - before_score
        
        # Update performance history
        tool.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "before": before_score,
            "after": after_score,
            "impact": actual_impact
        })
        
        # Update success rate (simple average for now)
        successful_runs = sum(1 for h in tool.performance_history 
                            if h.get("impact", 0) > 0)
        total_runs = len(tool.performance_history)
        tool.success_rate = successful_runs / total_runs if total_runs > 0 else 0
        
        # Update average impact
        impacts = [h.get("impact", 0) for h in tool.performance_history]
        tool.impact = sum(impacts) / len(impacts) if impacts else 0
        
        self._save_registry(self.tools)
        
        logger.info(f"📊 Updated {name} performance: {actual_impact:+.2f} impact")
        return actual_impact
    
    def get_tool_recommendations(self, current_weaknesses: Dict[str, float]) -> List[Dict]:
        """Get tool recommendations based on current weaknesses"""
        
        recommendations = []
        
        # Check each weakness against proposed tools
        weakness_to_tool_mapping = {
            "visual_quality": ["VisualComplexityAnalyzer", "ChartDataExtractor", "DataVisualizationGenerator"],
            "text_heavy": ["ChartDataExtractor", "EngagementOptimizer", "IconMatcher"],
            "accuracy": ["SourceFidelityChecker", "ReferenceValidator"],
            "consistency": ["ConsistencyEnforcer"],
            "engagement": ["EngagementOptimizer", "TransitionGenerator"]
        }
        
        for weakness, severity in current_weaknesses.items():
            if severity > 0.3:  # Significant weakness
                tool_names = weakness_to_tool_mapping.get(weakness, [])
                for tool_name in tool_names:
                    # Check if tool is proposed but not failed
                    if tool_name in self.tools:
                        tool = self.tools[tool_name]
                        if tool.status == "PROPOSED":
                            recommendations.append({
                                "tool": tool_name,
                                "purpose": tool.purpose,
                                "expected_impact": tool.impact,
                                "addresses": weakness,
                                "priority": "HIGH" if severity > 0.5 else "MEDIUM"
                            })
        
        return sorted(recommendations, key=lambda r: r["expected_impact"], reverse=True)
    
    def learn_from_failure(self, tool_name: str, failure_pattern: Dict):
        """Learn from tool failures to avoid similar mistakes"""
        
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            
            # Extract failure patterns
            failure_type = failure_pattern.get("type", "unknown")
            
            # Add to registry's failure patterns
            if not hasattr(self, "failure_patterns"):
                self.failure_patterns = []
            
            self.failure_patterns.append({
                "tool": tool_name,
                "type": failure_type,
                "pattern": failure_pattern,
                "lesson": failure_pattern.get("lesson", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"📝 Learned from {tool_name} failure: {failure_type}")
    
    def should_implement_tool(self, tool_name: str) -> Dict[str, Any]:
        """Decide if a tool should be implemented based on registry knowledge"""
        
        decision = {
            "implement": False,
            "reason": "",
            "risk_level": "unknown",
            "expected_impact": 0.0
        }
        
        if tool_name not in self.tools:
            # New tool, check against failure patterns
            decision["implement"] = True
            decision["reason"] = "New tool, no known failures"
            decision["risk_level"] = "medium"
            decision["expected_impact"] = 0.3  # Default
        else:
            tool = self.tools[tool_name]
            
            if tool.status == "FAILED":
                decision["implement"] = False
                decision["reason"] = f"Previously failed: {tool.failure_reason}"
                decision["risk_level"] = "high"
            elif tool.status == "ACTIVE":
                decision["implement"] = False
                decision["reason"] = "Already active"
                decision["risk_level"] = "none"
            elif tool.status == "PROPOSED":
                decision["implement"] = True
                decision["reason"] = "Proposed tool ready for implementation"
                decision["risk_level"] = "low" if tool.impact > 0.3 else "medium"
                decision["expected_impact"] = tool.impact
        
        return decision