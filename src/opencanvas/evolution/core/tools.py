"""
Unified Tools Management - Single manager for tool discovery, testing, and adoption
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from opencanvas.evolution.config.tools_specs import (
    CURRENT_TOOLS, REJECTED_TOOLS, PROPOSED_TOOLS, 
    SUCCESSFUL_PATTERNS, FAILED_PATTERNS, ADOPTION_CRITERIA, PRIORITY_MATRIX
)

logger = logging.getLogger(__name__)

class ToolsManager:
    """
    Unified manager for the complete tool ecosystem:
    - Current tools in production
    - Proposed tools from evolution
    - Rejected tools with lessons learned
    - Tool testing and adoption decisions
    """
    
    def __init__(self, registry_file: str = None):
        """Initialize tools manager"""
        # Use TOOLS.md in project root by default
        if registry_file:
            self.registry_file = Path(registry_file)
        else:
            # Find TOOLS.md in project root
            current_dir = Path(__file__).parent
            while current_dir.parent != current_dir:
                tools_md = current_dir / "TOOLS.md"
                if tools_md.exists():
                    self.registry_file = tools_md
                    break
                current_dir = current_dir.parent
            else:
                # Default to current directory if not found
                self.registry_file = Path("TOOLS.md")
        self.current_tools = CURRENT_TOOLS.copy()
        self.rejected_tools = REJECTED_TOOLS.copy()
        self.proposed_tools = PROPOSED_TOOLS.copy()
        self.tool_history = []
        
        # Create registry file if it doesn't exist
        if not self.registry_file.exists():
            self._create_initial_registry()
    
    def propose_tool(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a new tool based on evolution analysis"""
        
        tool_name = tool_spec.get("name", "UnnamedTool")
        logger.info(f"🔧 Proposing new tool: {tool_name}")
        
        # Validate tool specification
        validation_result = self._validate_tool_spec(tool_spec)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": f"Invalid tool specification: {validation_result['issues']}"
            }
        
        # Check for duplicates
        if tool_name in self.current_tools or tool_name in self.proposed_tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} already exists"
            }
        
        # Determine priority based on impact and complexity
        priority = self._calculate_priority(tool_spec)
        tool_spec["priority"] = priority
        tool_spec["proposed_at"] = datetime.now().isoformat()
        
        # Add to proposed tools
        self.proposed_tools[tool_name] = tool_spec
        
        # Update registry
        self._update_registry()
        
        # Record in history
        self.tool_history.append({
            "action": "propose",
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "priority": priority
        })
        
        logger.info(f"✅ Tool {tool_name} proposed with {priority} priority")
        
        return {
            "success": True,
            "tool_name": tool_name,
            "priority": priority,
            "recommendation": self._get_implementation_recommendation(tool_spec)
        }
    
    def test_tool(self, tool_name: str, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Record test results for a tool and make adoption decision"""
        
        logger.info(f"🧪 Recording test results for: {tool_name}")
        
        if tool_name not in self.proposed_tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} not found in proposed tools"
            }
        
        # Analyze test results against adoption criteria
        adoption_decision = self._analyze_test_results(test_results)
        
        tool_spec = self.proposed_tools[tool_name]
        tool_spec["test_results"] = test_results
        tool_spec["tested_at"] = datetime.now().isoformat()
        
        if adoption_decision["adopt"]:
            # Move to current tools
            self._adopt_tool(tool_name, tool_spec, test_results)
            status = "adopted"
        else:
            # Move to rejected tools
            self._reject_tool(tool_name, tool_spec, test_results, adoption_decision["reason"])
            status = "rejected"
        
        # Remove from proposed
        del self.proposed_tools[tool_name]
        
        # Update registry
        self._update_registry()
        
        # Record in history
        self.tool_history.append({
            "action": "test_complete",
            "tool": tool_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "results": test_results
        })
        
        logger.info(f"✅ Tool {tool_name} {status}")
        
        return {
            "success": True,
            "tool_name": tool_name,
            "decision": status,
            "reason": adoption_decision.get("reason", ""),
            "metrics": test_results
        }
    
    def get_context_for_agents(self) -> str:
        """Get concise tool ecosystem context for agent prompts"""
        
        context = "CURRENT TOOL ECOSYSTEM:\n\n"
        
        # Current tools
        context += "Production Tools:\n"
        for name, spec in list(self.current_tools.items())[:5]:  # Top 5
            context += f"- {name}: {spec['purpose']}\n"
            context += f"  Input: {spec['input_spec']}\n"
            context += f"  Performance: {spec['performance']}\n\n"
        
        # Failed patterns to avoid
        context += "AVOID THESE FAILED PATTERNS:\n"
        for pattern in FAILED_PATTERNS:
            context += f"- {pattern}\n"
        
        # Successful patterns to follow
        context += "\nFOLLOW THESE SUCCESSFUL PATTERNS:\n"
        for pattern in SUCCESSFUL_PATTERNS:
            context += f"- {pattern}\n"
        
        # High-priority proposed tools
        high_priority_tools = [name for name, spec in self.proposed_tools.items() 
                              if spec.get("priority") == "high"]
        if high_priority_tools:
            context += f"\nHIGH-PRIORITY TOOLS IN PIPELINE: {', '.join(high_priority_tools[:3])}\n"
        
        return context
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get comprehensive tool ecosystem summary"""
        
        return {
            "ecosystem_stats": {
                "current_tools": len(self.current_tools),
                "proposed_tools": len(self.proposed_tools),
                "rejected_tools": len(self.rejected_tools),
                "total_history_entries": len(self.tool_history)
            },
            "tool_counts_by_priority": {
                "high": len([t for t in self.proposed_tools.values() if t.get("priority") == "high"]),
                "medium": len([t for t in self.proposed_tools.values() if t.get("priority") == "medium"]),
                "low": len([t for t in self.proposed_tools.values() if t.get("priority") == "low"])
            },
            "current_tools": list(self.current_tools.keys()),
            "proposed_tools": list(self.proposed_tools.keys()),
            "rejected_tools": list(self.rejected_tools.keys()),
            "recent_activity": self.tool_history[-5:] if self.tool_history else []
        }
    
    def get_implementation_queue(self) -> List[Dict[str, Any]]:
        """Get prioritized queue of tools ready for implementation"""
        
        # Sort proposed tools by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        queue = []
        for name, spec in self.proposed_tools.items():
            priority = spec.get("priority", "low")
            queue.append({
                "name": name,
                "priority": priority,
                "priority_score": priority_order.get(priority, 1),
                "purpose": spec.get("purpose", ""),
                "expected_impact": spec.get("expected_impact", ""),
                "complexity": spec.get("complexity", ""),
                "proposed_at": spec.get("proposed_at", "")
            })
        
        # Sort by priority score (high first)
        queue.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return queue
    
    def _validate_tool_spec(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool specification completeness"""
        
        required_fields = ["name", "purpose", "expected_impact", "complexity"]
        issues = []
        
        for field in required_fields:
            if field not in tool_spec or not tool_spec[field]:
                issues.append(f"Missing {field}")
        
        # Validate expected_impact values
        if "expected_impact" in tool_spec:
            if tool_spec["expected_impact"].lower() not in ["high", "medium", "low"]:
                issues.append("expected_impact must be high, medium, or low")
        
        # Validate complexity values  
        if "complexity" in tool_spec:
            if tool_spec["complexity"].lower() not in ["high", "medium", "low"]:
                issues.append("complexity must be high, medium, or low")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _calculate_priority(self, tool_spec: Dict[str, Any]) -> str:
        """Calculate tool priority based on impact and complexity"""
        
        impact = tool_spec.get("expected_impact", "low").lower()
        complexity = tool_spec.get("complexity", "high").lower()
        
        priority_key = (impact, complexity)
        priority_label = PRIORITY_MATRIX.get(priority_key, "🔶 DO NEXT")
        
        if "DO FIRST" in priority_label:
            return "high"
        elif "DO NEXT" in priority_label:
            return "medium"
        elif "DO LATER" in priority_label:
            return "low"
        else:
            return "low"  # DON'T DO -> low priority for now
    
    def _analyze_test_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results against adoption criteria"""
        
        # Check quality impact
        quality_improvement = test_results.get("quality_improvement", 0)
        if quality_improvement < 0.2:
            return {
                "adopt": False,
                "reason": f"Quality improvement {quality_improvement} below minimum 0.2"
            }
        
        # Check speed impact
        speed_increase = test_results.get("speed_impact_percent", 0)
        if speed_increase > 10:
            return {
                "adopt": False,
                "reason": f"Speed impact {speed_increase}% exceeds maximum 10%"
            }
        
        # Check cost impact
        cost_increase = test_results.get("cost_impact_percent", 0)
        if cost_increase > 5:
            return {
                "adopt": False,
                "reason": f"Cost impact {cost_increase}% exceeds maximum 5%"
            }
        
        # Check reliability
        success_rate = test_results.get("success_rate", 0)
        if success_rate < 90:
            return {
                "adopt": False,
                "reason": f"Success rate {success_rate}% below minimum 90%"
            }
        
        return {
            "adopt": True,
            "reason": "All adoption criteria met"
        }
    
    def _adopt_tool(self, tool_name: str, tool_spec: Dict[str, Any], test_results: Dict[str, Any]):
        """Move tool to current tools (adopted)"""
        
        self.current_tools[tool_name] = {
            "purpose": tool_spec.get("purpose", ""),
            "input_spec": tool_spec.get("implementation", {}).get("params", "input") + " -> " + tool_spec.get("implementation", {}).get("return_type", "Result"),
            "output_spec": tool_spec.get("implementation", {}).get("return_type", "Result"),
            "integration": tool_spec.get("integration_points", ["unknown"])[0],
            "performance": test_results.get("actual_performance", "measured in testing"),
            "success_rate": f"{test_results.get('success_rate', 0)}%",
            "implementation": tool_spec.get("implementation", {}).get("class_name", tool_name),
            "adopted_at": datetime.now().isoformat(),
            "quality_improvement": test_results.get("quality_improvement", 0)
        }
    
    def _reject_tool(self, tool_name: str, tool_spec: Dict[str, Any], test_results: Dict[str, Any], reason: str):
        """Move tool to rejected tools"""
        
        self.rejected_tools[tool_name] = {
            "purpose": tool_spec.get("purpose", ""),
            "failure_reason": reason,
            "test_period": f"{tool_spec.get('proposed_at', 'unknown')} to {datetime.now().isoformat()}",
            "test_results": test_results,
            "pattern": self._identify_failure_pattern(reason),
            "lesson": self._extract_lesson(reason, test_results)
        }
    
    def _identify_failure_pattern(self, reason: str) -> str:
        """Identify the failure pattern for learning"""
        if "speed" in reason.lower():
            return "Performance too slow for MVP requirements"
        elif "cost" in reason.lower():
            return "Cost increase exceeds acceptable limits"
        elif "quality" in reason.lower():
            return "Insufficient quality improvement"
        elif "success rate" in reason.lower():
            return "Reliability below production standards"
        else:
            return "Failed to meet adoption criteria"
    
    def _extract_lesson(self, reason: str, test_results: Dict[str, Any]) -> str:
        """Extract lesson learned from failure"""
        if "speed" in reason.lower():
            return "Consider async processing or lighter-weight alternatives"
        elif "cost" in reason.lower():
            return "Optimize API usage or find cost-effective alternatives"
        elif "quality" in reason.lower():
            return "Reassess approach or combine with other improvements"
        else:
            return "Validate assumptions before implementation"
    
    def _get_implementation_recommendation(self, tool_spec: Dict[str, Any]) -> str:
        """Get implementation recommendation for a tool"""
        
        priority = tool_spec.get("priority", "low")
        complexity = tool_spec.get("complexity", "unknown")
        
        if priority == "high" and complexity == "low":
            return "IMPLEMENT IMMEDIATELY - High impact, low complexity"
        elif priority == "high":
            return "PLAN FOR NEXT SPRINT - High impact, but needs careful implementation"
        elif complexity == "low":
            return "GOOD CANDIDATE FOR QUICK WIN - Low complexity implementation"
        else:
            return "EVALUATE FURTHER - Consider cost/benefit tradeoffs"
    
    def _create_initial_registry(self):
        """Create initial tools registry file"""
        
        content = f"""# OpenCanvas Tools Registry

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## 📋 Current Tools ({len(self.current_tools)})

Production tools actively used in the system.

## 🚀 Proposed Tools ({len(self.proposed_tools)})

Tools identified by evolution system, ready for implementation.

## ❌ Rejected Tools ({len(self.rejected_tools)})

Tools that were tested but not adopted - learn from these failures.

## 📊 Tool Ecosystem Stats

- Total tools tracked: {len(self.current_tools) + len(self.proposed_tools) + len(self.rejected_tools)}
- Success rate: {len(self.current_tools) / max(1, len(self.current_tools) + len(self.rejected_tools)) * 100:.1f}%
- Tools in pipeline: {len(self.proposed_tools)}

---
*Generated by ToolsManager*
"""
        
        with open(self.registry_file, 'w') as f:
            f.write(content)
        
        logger.info(f"📝 Created initial registry: {self.registry_file}")
    
    def _update_registry(self):
        """Update the tools registry file"""
        
        try:
            content = f"""# OpenCanvas Tools Registry

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## 📋 Current Tools ({len(self.current_tools)})

"""
            
            # Add current tools
            for name, spec in self.current_tools.items():
                content += f"### {name}\n"
                content += f"**Purpose**: {spec['purpose']}\n"
                content += f"**Performance**: {spec['performance']}\n"
                content += f"**Success Rate**: {spec['success_rate']}\n\n"
            
            content += f"## 🚀 Proposed Tools ({len(self.proposed_tools)})\n\n"
            
            # Add proposed tools
            for name, spec in self.proposed_tools.items():
                priority_emoji = "⭐" if spec.get("priority") == "high" else "🔶" if spec.get("priority") == "medium" else "✅"
                content += f"### {name} {priority_emoji}\n"
                content += f"**Purpose**: {spec['purpose']}\n"
                content += f"**Expected Impact**: {spec.get('expected_impact', 'unknown')}\n"
                content += f"**Complexity**: {spec.get('complexity', 'unknown')}\n\n"
            
            content += f"## ❌ Rejected Tools ({len(self.rejected_tools)})\n\n"
            
            # Add rejected tools
            for name, spec in self.rejected_tools.items():
                content += f"### {name}\n"
                content += f"**Purpose**: {spec['purpose']}\n"
                content += f"**Failure Reason**: {spec['failure_reason']}\n"
                content += f"**Lesson**: {spec['lesson']}\n\n"
            
            # Add stats
            total_tools = len(self.current_tools) + len(self.rejected_tools)
            success_rate = len(self.current_tools) / max(1, total_tools) * 100
            
            content += f"""## 📊 Tool Ecosystem Stats

- Total tools tracked: {len(self.current_tools) + len(self.proposed_tools) + len(self.rejected_tools)}
- Success rate: {success_rate:.1f}%
- Tools in pipeline: {len(self.proposed_tools)}
- Recent activity: {len(self.tool_history)} total actions

---
*Generated by ToolsManager*
"""
            
            with open(self.registry_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update registry: {e}")


class ToolDiscovery:
    """Helper class for discovering new tools during evolution"""
    
    @staticmethod
    def discover_from_weaknesses(weakness_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover potential tools based on weakness patterns"""
        
        discoveries = []
        
        for weakness in weakness_patterns:
            category = weakness.get("category", "")
            dimension = weakness.get("dimension", "")
            avg_score = weakness.get("avg_score", 0)
            
            # Map common weakness patterns to tool opportunities
            if dimension == "clarity_readability" and avg_score < 3.0:
                discoveries.append({
                    "name": "ChartReadabilityValidator",
                    "purpose": "Ensure charts and visualizations are readable",
                    "target_problem": f"Clarity/readability scoring {avg_score:.2f}/5",
                    "expected_impact": "high",
                    "complexity": "medium"
                })
            
            if "fake" in str(weakness.get("root_causes", [])).lower():
                discoveries.append({
                    "name": "CitationVerificationTool", 
                    "purpose": "Detect and prevent fake citations",
                    "target_problem": "Fake citations in generated content",
                    "expected_impact": "high",
                    "complexity": "low"
                })
            
            if dimension == "visual_textual_balance" and avg_score < 3.5:
                discoveries.append({
                    "name": "ContentBalanceAnalyzer",
                    "purpose": "Detect and fix text walls and content imbalance",
                    "target_problem": f"Visual-textual balance scoring {avg_score:.2f}/5",
                    "expected_impact": "medium", 
                    "complexity": "low"
                })
        
        # Remove duplicates
        seen_names = set()
        unique_discoveries = []
        for discovery in discoveries:
            if discovery["name"] not in seen_names:
                seen_names.add(discovery["name"])
                unique_discoveries.append(discovery)
        
        return unique_discoveries