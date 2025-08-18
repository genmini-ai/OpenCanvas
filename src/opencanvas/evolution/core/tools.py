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
    
    Now uses RegistryInitializer for proper TOOLS_REGISTRY.md management
    """
    
    def __init__(self, registry_file: str = None):
        """Initialize tools manager with registry integration"""
        # Use TOOLS_REGISTRY.md as default instead of TOOLS.md
        registry_path = registry_file if registry_file else "TOOLS_REGISTRY.md"
        
        # Initialize with RegistryInitializer for proper registry management
        try:
            from .registry_initializer import RegistryInitializer
            self.registry = RegistryInitializer(registry_path)
            logger.info(f"📚 ToolsManager integrated with RegistryInitializer")
        except Exception as e:
            logger.error(f"Failed to initialize RegistryInitializer: {e}")
            self.registry = None
        
        # Keep backward compatibility with existing interface
        self.current_tools = CURRENT_TOOLS.copy()
        self.rejected_tools = REJECTED_TOOLS.copy()
        self.proposed_tools = {}  # Start empty, populated during evolution
        self.tool_history = []
    
    def propose_tool(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a new tool based on evolution analysis"""
        
        tool_name = tool_spec.get("name", "UnnamedTool")
        logger.info(f"🔧 Proposing new tool: {tool_name}")
        
        # Validate tool specification with error handling
        try:
            validation_result = self._validate_tool_spec(tool_spec)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid tool specification: {validation_result['issues']}"
                }
        except Exception as e:
            logger.error(f"Tool validation failed for {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Tool validation error: {str(e)}"
            }
        
        # Check for duplicates using registry
        if self.registry:
            registry_data = self.registry.parse_registry()
            failed_tools = registry_data.get("failed_tools", {})
            active_tools = registry_data.get("active_tools", {})
            
            if tool_name in failed_tools:
                lesson = failed_tools[tool_name].get("lesson_learned", "No lesson recorded")
                return {
                    "success": False,
                    "error": f"Tool {tool_name} was previously tested and failed. Lesson: {lesson}"
                }
            if tool_name in active_tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is already an active tool"
                }
        
        # Check local proposed tools
        if tool_name in self.proposed_tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} already proposed in this session"
            }
        
        # Extract gap information if available
        if "targets_gaps" in tool_spec:
            gaps = tool_spec["targets_gaps"]
            if gaps and len(gaps) > 0:
                first_gap = gaps[0]
                tool_spec["targets_gap"] = first_gap.get("dimension", "Unknown")
                tool_spec["baseline_score"] = first_gap.get("avg_score", "N/A")
                tool_spec["target_score"] = first_gap.get("improvement_potential", "N/A")
        
        # Set default priority for MCP tools (can be overridden by tool specification)
        priority = tool_spec.get("priority", "medium")
        tool_spec["priority"] = priority
        tool_spec["proposed_at"] = datetime.now().isoformat()
        tool_spec["solution_type"] = tool_spec.get("solution_type", "tool")
        
        # Add to proposed tools locally
        self.proposed_tools[tool_name] = tool_spec
        
        # Update registry using RegistryInitializer
        if self.registry:
            registry_success = self.registry.add_proposed_tool(tool_name, tool_spec)
            if not registry_success:
                logger.warning(f"Failed to add {tool_name} to registry, but keeping in local proposed tools")
        
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
            # Tool passed testing - would be adopted
            # For now, just log success (actual adoption would integrate with system)
            status = "adopted"
            logger.info(f"🎉 Tool {tool_name} passed testing and would be adopted")
        else:
            # Tool failed testing - add to failed tools in registry  
            status = "rejected"
            failure_reason = adoption_decision["reason"]
            lesson_learned = f"Failed due to: {failure_reason}. Consider alternative approaches."
            
            if self.registry:
                self.registry.mark_tool_failed(tool_name, failure_reason, lesson_learned)
            
            # Also add to local rejected tools
            self.rejected_tools[tool_name] = {
                "purpose": tool_spec.get("purpose", "Unknown"),
                "failure_reason": failure_reason,
                "test_period": datetime.now().strftime("%Y-%m-%d"),
                "pattern": "Evolution-discovered tool that failed testing",
                "lesson": lesson_learned
            }
        
        # Remove from proposed tools
        del self.proposed_tools[tool_name]
        
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
    
    def get_context_for_agents(self, evaluation_weaknesses: List[Dict] = None, missing_capabilities: List[str] = None) -> str:
        """Get concise tool ecosystem context for agent prompts, including evaluation gaps"""
        
        context = "CURRENT TOOL ECOSYSTEM:\n\n"
        
        # Read from registry instead of hardcoded data
        if self.registry:
            registry_data = self.registry.parse_registry()
            
            # Active tools from registry
            context += "Production Tools:\n"
            for name, spec in list(registry_data.get("active_tools", {}).items())[:5]:  # Top 5
                context += f"- {name}: {spec.get('purpose', 'No description')}\n"
                if 'input' in spec:
                    context += f"  Input: {spec['input']}\n"
                if 'output' in spec:
                    context += f"  Output: {spec['output']}\n"
                if 'usage' in spec:
                    context += f"  Usage: {spec['usage']}\n"
                context += "\n"
            
            # Failed tools and lessons learned from registry
            context += "AVOID THESE FAILED PATTERNS (from registry):\n"
            for name, spec in registry_data.get("failed_tools", {}).items():
                if 'lesson_learned' in spec:
                    context += f"- {spec['lesson_learned']}\n"
            
            # Proposed tools from registry
            proposed_tools = registry_data.get("proposed_tools", {})
            if proposed_tools:
                context += f"\nPROPOSED TOOLS IN PIPELINE: {', '.join(list(proposed_tools.keys())[:3])}\n"
        else:
            # Fallback to hardcoded if registry not available
            context += "Production Tools:\n"
            for name, spec in list(self.current_tools.items())[:5]:  # Top 5
                context += f"- {name}: {spec['purpose']}\n"
                context += f"  Input: {spec['input_spec']}\n"
                context += f"  Performance: {spec['performance']}\n\n"
        
        # Add evaluation-driven context - THIS IS THE KEY ADDITION
        if evaluation_weaknesses:
            context += "\n🎯 QUALITY GAPS IDENTIFIED FROM EVALUATION:\n"
            for weakness in evaluation_weaknesses[:5]:  # Top 5 weaknesses
                dimension = weakness.get('dimension', 'Unknown')
                score = weakness.get('avg_score', 0)
                gap = weakness.get('description', 'No description')
                context += f"- {dimension} (Score: {score:.2f}/5.0): {gap}\n"
            context += "\n"
        
        if missing_capabilities:
            context += "🔧 MISSING CAPABILITIES TO ADDRESS:\n"
            for capability in missing_capabilities[:5]:  # Top 5 missing capabilities
                context += f"- {capability}\n"
            context += "\n"
        
        # Add patterns from config (these can stay hardcoded as general guidelines)
        context += "FOLLOW THESE SUCCESSFUL PATTERNS:\n"
        for pattern in SUCCESSFUL_PATTERNS:
            context += f"- {pattern}\n"
        
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
            priority = spec.get("priority", "medium")
            queue.append({
                "name": name,
                "priority": priority,
                "priority_score": priority_order.get(priority, 2),
                "purpose": spec.get("purpose", ""),
                "input": spec.get("input", ""),
                "output": spec.get("output", ""),
                "usage": spec.get("usage", ""),
                "proposed_at": spec.get("proposed_at", "")
            })
        
        # Sort by priority score (high first)
        queue.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return queue
    
    def _validate_tool_spec(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool specification against MCP tool format"""
        
        # Required fields for MCP tool specification (based on TOOLS_REGISTRY.md)
        required_fields = ["name", "purpose", "input", "output", "usage"]
        issues = []
        
        # Check required fields
        for field in required_fields:
            if field not in tool_spec or not tool_spec[field]:
                issues.append(f"Missing required MCP field: {field}")
        
        # Validate specific field formats
        if "purpose" in tool_spec:
            purpose = tool_spec["purpose"]
            if not isinstance(purpose, str) or len(purpose.strip()) < 10:
                issues.append("purpose must be a descriptive string (at least 10 characters)")
        
        if "input" in tool_spec:
            input_spec = tool_spec["input"]
            if not isinstance(input_spec, str):
                issues.append("input must be a string describing parameters")
        
        if "output" in tool_spec:
            output_spec = tool_spec["output"]
            if not isinstance(output_spec, str):
                issues.append("output must be a string describing return value")
        
        if "usage" in tool_spec:
            usage_example = tool_spec["usage"]
            if not isinstance(usage_example, str) or "(" not in usage_example:
                issues.append("usage must be a string with example function call")
        
        # Optional fields validation
        if "failure_reason" in tool_spec:
            if not isinstance(tool_spec["failure_reason"], str):
                issues.append("failure_reason must be a string")
        
        if "lesson_learned" in tool_spec:
            if not isinstance(tool_spec["lesson_learned"], str):
                issues.append("lesson_learned must be a string")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _calculate_priority(self, tool_spec: Dict[str, Any]) -> str:
        """Calculate tool priority - simplified for MCP tools"""
        
        # For MCP tools, priority can be explicitly set or defaults to medium
        return tool_spec.get("priority", "medium")
    
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
    """Helper class for discovering new tools during evolution with registry awareness"""
    
    @staticmethod
    def discover_from_weaknesses(weakness_patterns: List[Dict[str, Any]], registry_path: str = "TOOLS_REGISTRY.md") -> List[Dict[str, Any]]:
        """Discover potential tools based on weakness patterns with registry awareness"""
        
        # Get registry information to avoid suggesting failed/existing tools
        try:
            from .registry_initializer import RegistryInitializer
            registry = RegistryInitializer(registry_path)
            failed_tools = registry.get_failed_tools()
            active_tools = registry.get_active_tools()
            
            logger.info(f"🔍 Registry awareness: avoiding {len(failed_tools)} failed tools and {len(active_tools)} active tools")
        except Exception as e:
            logger.warning(f"Registry awareness disabled due to error: {e}")
            failed_tools = []
            active_tools = []
        
        discoveries = []
        
        for weakness in weakness_patterns:
            category = weakness.get("category", "")
            dimension = weakness.get("dimension", "")
            avg_score = weakness.get("avg_score", 0)
            root_causes = weakness.get("root_causes", [])
            
            # Generate diverse tool suggestions based on weaknesses
            candidate_tools = []
            
            # Visual quality issues
            if dimension == "clarity_readability" and avg_score < 3.0:
                candidate_tools.extend([
                    {
                        "name": "ChartReadabilityValidator",
                        "purpose": "Ensure charts and visualizations are readable",
                        "target_problem": f"Clarity/readability scoring {avg_score:.2f}/5",
                        "expected_impact": "high",
                        "complexity": "medium"
                    },
                    {
                        "name": "FontSizeOptimizer", 
                        "purpose": "Automatically optimize font sizes for readability",
                        "target_problem": f"Poor readability with score {avg_score:.2f}/5",
                        "expected_impact": "medium",
                        "complexity": "low"
                    }
                ])
            
            # Citation and accuracy issues (diverse approaches, not hardcoded)
            if any("fake" in str(cause).lower() or "citation" in str(cause).lower() or "accuracy" in str(cause).lower() 
                   for cause in root_causes):
                candidate_tools.extend([
                    {
                        "name": "SourceVerificationTool",
                        "purpose": "Verify information against source materials",
                        "target_problem": "Accuracy issues in generated content",
                        "expected_impact": "high", 
                        "complexity": "medium"
                    },
                    {
                        "name": "FactCheckingValidator",
                        "purpose": "Cross-reference facts with reliable sources",
                        "target_problem": "Potential fake or unverified information",
                        "expected_impact": "high",
                        "complexity": "high"
                    },
                    {
                        "name": "ReferenceTracker",
                        "purpose": "Track source material for every claim",
                        "target_problem": "Missing source attribution",
                        "expected_impact": "medium",
                        "complexity": "low"
                    }
                ])
            
            # Visual-textual balance issues
            if dimension == "visual_textual_balance" and avg_score < 3.5:
                candidate_tools.extend([
                    {
                        "name": "ContentBalanceAnalyzer",
                        "purpose": "Detect and fix text walls and content imbalance",
                        "target_problem": f"Visual-textual balance scoring {avg_score:.2f}/5",
                        "expected_impact": "medium",
                        "complexity": "low"
                    },
                    {
                        "name": "VisualElementInjector",
                        "purpose": "Automatically add visual elements to text-heavy slides",
                        "target_problem": f"Text-heavy slides with balance score {avg_score:.2f}/5",
                        "expected_impact": "high",
                        "complexity": "medium"
                    }
                ])
            
            # Engagement and presentation issues
            if any("engagement" in str(cause).lower() or "boring" in str(cause).lower() 
                   for cause in root_causes) or avg_score < 3.2:
                candidate_tools.extend([
                    {
                        "name": "InteractivityEnhancer",
                        "purpose": "Add interactive elements to presentations",
                        "target_problem": "Low engagement scores",
                        "expected_impact": "high",
                        "complexity": "high"
                    },
                    {
                        "name": "ColorSchemeOptimizer", 
                        "purpose": "Optimize color schemes for visual appeal",
                        "target_problem": "Visual appeal issues",
                        "expected_impact": "medium",
                        "complexity": "low"
                    }
                ])
            
            # Filter out failed and active tools before adding to discoveries
            for tool in candidate_tools:
                tool_name = tool["name"]
                if tool_name not in failed_tools and tool_name not in active_tools:
                    discoveries.append(tool)
                else:
                    logger.info(f"🚫 Skipping {tool_name}: already in {'failed' if tool_name in failed_tools else 'active'} tools")
        
        # Remove duplicates and prioritize by expected impact
        seen_names = set()
        unique_discoveries = []
        
        # Sort by expected impact (high -> medium -> low) and complexity (low -> medium -> high)
        impact_priority = {"high": 3, "medium": 2, "low": 1}
        complexity_priority = {"low": 3, "medium": 2, "high": 1}
        
        sorted_discoveries = sorted(discoveries, key=lambda x: (
            impact_priority.get(x.get("expected_impact", "low"), 1),
            complexity_priority.get(x.get("complexity", "high"), 1)
        ), reverse=True)
        
        for discovery in sorted_discoveries:
            if discovery["name"] not in seen_names:
                seen_names.add(discovery["name"])
                unique_discoveries.append(discovery)
        
        return unique_discoveries