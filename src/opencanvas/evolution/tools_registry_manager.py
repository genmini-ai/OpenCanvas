"""
Tools Registry Manager - Maintains the TOOLS_REGISTRY.md file with discovered and implemented tools
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolsRegistryManager:
    """
    Manages the tools registry markdown file, tracking current tools,
    proposed tools, test results, and future implementation plans
    """
    
    def __init__(self, registry_path: str = "TOOLS_REGISTRY.md"):
        """Initialize tools registry manager"""
        self.registry_path = Path(registry_path)
        self.ensure_registry_exists()
        
    def ensure_registry_exists(self):
        """Ensure the registry file exists with basic structure"""
        if not self.registry_path.exists():
            logger.info(f"Creating new tools registry at {self.registry_path}")
            self.create_initial_registry()
    
    def create_initial_registry(self):
        """Create initial registry structure"""
        initial_content = """# OpenCanvas Tools Registry

This document tracks all tools in the OpenCanvas presentation generation system.

## 📋 Current Tools (In Production)

## 🧪 Proposed Tools (Tested but Not Adopted)

## 🚀 Future Tools (Planned Implementation)

## 📊 Tool Development Pipeline

## 📈 Evolution Metrics

## 🔄 Update History

### {date}
- Registry initialized by evolution system
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
        with open(self.registry_path, 'w') as f:
            f.write(initial_content)
    
    def add_proposed_tool(self, tool_spec: Dict[str, Any]):
        """Add a newly proposed tool to the registry"""
        
        logger.info(f"📝 Adding proposed tool to registry: {tool_spec.get('name', 'Unknown')}")
        
        # Read current registry
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Find the Future Tools section
        future_section_start = content.find("## 🚀 Future Tools (Planned Implementation)")
        if future_section_start == -1:
            logger.error("Could not find Future Tools section in registry")
            return
        
        # Find next section
        next_section = content.find("## ", future_section_start + 1)
        if next_section == -1:
            next_section = len(content)
        
        # Create tool entry
        tool_entry = self._format_proposed_tool(tool_spec)
        
        # Insert the new tool
        new_content = (
            content[:next_section] + 
            "\n" + tool_entry + "\n" +
            content[next_section:]
        )
        
        # Write updated registry
        with open(self.registry_path, 'w') as f:
            f.write(new_content)
        
        # Add to update history
        self.add_update_entry(f"Added proposed tool: {tool_spec.get('name', 'Unknown')}")
        
        logger.info(f"✅ Tool added to registry: {tool_spec.get('name', 'Unknown')}")
    
    def _format_proposed_tool(self, tool_spec: Dict[str, Any]) -> str:
        """Format a tool specification for the registry in machine-readable format"""
        
        name = tool_spec.get('name', 'Unnamed Tool')
        purpose = tool_spec.get('purpose', 'No purpose specified')
        expected_impact = tool_spec.get('expected_impact', 'unknown').upper()
        complexity = tool_spec.get('complexity', 'unknown').upper()
        
        # Determine priority emoji
        impact_level = expected_impact.lower()
        complexity_level = complexity.lower()
        if impact_level == 'high' and complexity_level == 'low':
            priority_emoji = "⭐ HIGH PRIORITY"
        elif impact_level == 'high' and complexity_level == 'medium':
            priority_emoji = "🔶 MEDIUM PRIORITY"  
        elif impact_level == 'medium' and complexity_level == 'low':
            priority_emoji = "✅ LOW PRIORITY"
        else:
            priority_emoji = "🔶 MEDIUM PRIORITY"
        
        # Format input/output specification
        implementation = tool_spec.get('implementation', {})
        input_spec = f"`({implementation.get('params', 'input: Any')}) -> {implementation.get('return_type', implementation.get('class_name', name.replace(' ', '')) + 'Result'}}`"
        output_spec = f"`{implementation.get('return_type', implementation.get('class_name', name.replace(' ', '')) + 'Result'}({implementation.get('return_fields', 'success: bool, data: Any')})`"
        
        # Performance specs
        speed_impact = tool_spec.get('speed_impact', 'Unknown')
        cost_estimate = tool_spec.get('cost_estimate', 'Unknown')
        
        # Implementation template
        class_name = implementation.get('class_name', name.replace(' ', ''))
        main_method = implementation.get('main_method', 'process')
        
        return f"""### {name} {priority_emoji}
**Purpose**: {purpose}  
**Input**: {input_spec}  
**Output**: {output_spec}  
**Integration**: {tool_spec.get('integration_points', ['TBD'])[0]}  
**Expected Performance**: {speed_impact}, {cost_estimate}  
**Expected Impact**: {tool_spec.get('expected_impact_detail', f'{expected_impact} impact on evaluation scores')}  
**Implementation Template**:
```python
class {class_name}:
    def {main_method}(self, {implementation.get('params', 'input_data')}) -> {implementation.get('return_type', class_name + 'Result')}:
        # {implementation.get('description', 'Process input')}
        # {implementation.get('logic', 'return result')}
```
"""
    
    def update_tool_test_results(self, tool_name: str, test_results: Dict[str, Any]):
        """Update a tool's test results and move to appropriate section"""
        
        logger.info(f"📊 Updating test results for tool: {tool_name}")
        
        # Read current registry
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Determine if tool was adopted based on results
        adopted = test_results.get('adopted', False)
        
        if adopted:
            # Move to Current Tools section
            self._move_tool_to_current(tool_name, test_results)
        else:
            # Move to Proposed Tools (Tested but Not Adopted) section
            self._move_tool_to_rejected(tool_name, test_results)
        
        # Add to update history
        status = "adopted" if adopted else "rejected"
        self.add_update_entry(f"Tool {tool_name} tested and {status}")
    
    def _move_tool_to_current(self, tool_name: str, test_results: Dict[str, Any]):
        """Move a tool to the Current Tools section after successful testing"""
        
        # Format the tool entry for current tools
        tool_entry = f"""### {len(self.get_current_tools()) + 1}. {tool_name}
- **Purpose**: {test_results.get('purpose', 'Unknown')}
- **Implementation**: {test_results.get('implementation_details', 'See code')}
- **Impact**: {test_results.get('impact_summary', 'Unknown')}
- **Metrics**: {test_results.get('metrics_summary', 'No metrics')}
- **Added**: v{test_results.get('version', '1.0')} (Evolution iteration {test_results.get('iteration', 'Unknown')})
"""
        
        # Read and update registry
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Find Current Tools section
        current_section = content.find("## 📋 Current Tools (In Production)")
        next_section = content.find("## 🧪 Proposed Tools", current_section)
        
        # Insert the new tool
        new_content = (
            content[:next_section] + 
            "\n" + tool_entry + "\n---\n\n" +
            content[next_section:]
        )
        
        # Write updated registry
        with open(self.registry_path, 'w') as f:
            f.write(new_content)
    
    def _move_tool_to_rejected(self, tool_name: str, test_results: Dict[str, Any]):
        """Move a tool to the rejected section with test results"""
        
        # Format the rejection entry
        results_list = []
        for metric, value in test_results.get('metrics', {}).items():
            if isinstance(value, bool):
                emoji = "✅" if value else "❌"
                results_list.append(f"  - {emoji} {metric}")
            else:
                results_list.append(f"  - {metric}: {value}")
        
        tool_entry = f"""### {len(self.get_rejected_tools()) + 1}. {tool_name}
- **Purpose**: {test_results.get('purpose', 'Unknown')}
- **Testing Period**: {test_results.get('test_period', 'Unknown')}
- **Results**: 
{chr(10).join(results_list)}
- **Decision**: Not adopted due to {test_results.get('rejection_reason', 'unspecified reasons')}
- **Lessons Learned**: {test_results.get('lessons_learned', 'No lessons recorded')}
"""
        
        # Read and update registry
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Find Proposed Tools section
        proposed_section = content.find("## 🧪 Proposed Tools (Tested but Not Adopted)")
        next_section = content.find("## 🚀 Future Tools", proposed_section)
        
        # Insert the new tool
        new_content = (
            content[:next_section] + 
            "\n" + tool_entry + "\n" +
            content[next_section:]
        )
        
        # Write updated registry
        with open(self.registry_path, 'w') as f:
            f.write(new_content)
    
    def get_current_tools(self) -> List[str]:
        """Get list of current tools in production"""
        # Simple implementation - could be enhanced with parsing
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Extract tool names from Current Tools section
        # This is a simplified implementation
        tools = []
        in_current_section = False
        for line in content.split('\n'):
            if "## 📋 Current Tools" in line:
                in_current_section = True
            elif "## " in line and in_current_section:
                break
            elif in_current_section and line.startswith("### ") and ". " in line:
                tool_name = line.split(". ", 1)[1].strip()
                tools.append(tool_name)
        
        return tools
    
    def get_rejected_tools(self) -> List[str]:
        """Get list of rejected tools"""
        # Similar implementation to get_current_tools
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        tools = []
        in_rejected_section = False
        for line in content.split('\n'):
            if "## 🧪 Proposed Tools" in line:
                in_rejected_section = True
            elif "## " in line and in_rejected_section:
                break
            elif in_rejected_section and line.startswith("### ") and ". " in line:
                tool_name = line.split(". ", 1)[1].strip()
                tools.append(tool_name)
        
        return tools
    
    def add_update_entry(self, entry: str):
        """Add an entry to the update history"""
        
        with open(self.registry_path, 'r') as f:
            content = f.read()
        
        # Find update history section
        history_section = content.find("## 🔄 Update History")
        if history_section == -1:
            logger.error("Could not find Update History section")
            return
        
        # Find the right place to insert (after the date)
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_header = f"### {date_str}"
        
        # Check if today's date already exists
        date_pos = content.find(date_header, history_section)
        
        if date_pos == -1:
            # Add new date section
            next_date = content.find("### ", history_section + 20)
            if next_date == -1:
                next_date = len(content)
            
            new_entry = f"\n### {date_str}\n- {entry}\n"
            new_content = (
                content[:next_date] + 
                new_entry +
                content[next_date:]
            )
        else:
            # Add to existing date section
            next_line = content.find("\n", date_pos)
            # Find next section or date
            next_section = content.find("\n### ", next_line)
            if next_section == -1:
                next_section = content.find("\n## ", next_line)
            if next_section == -1:
                next_section = len(content)
            
            new_content = (
                content[:next_section] + 
                f"- {entry}\n" +
                content[next_section:]
            )
        
        with open(self.registry_path, 'w') as f:
            f.write(new_content)
    
    def generate_tool_summary(self) -> Dict[str, Any]:
        """Generate a summary of tools for reporting"""
        
        return {
            "current_tools": self.get_current_tools(),
            "rejected_tools": self.get_rejected_tools(),
            "total_current": len(self.get_current_tools()),
            "total_rejected": len(self.get_rejected_tools()),
            "registry_path": str(self.registry_path),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_tool_specifications(self, spec_file: str = "TOOLS_SPECIFICATION.md") -> Dict[str, Any]:
        """Parse the TOOLS_SPECIFICATION.md file to extract tool information for agents"""
        
        spec_path = Path(spec_file)
        if not spec_path.exists():
            logger.warning(f"Tool specification file not found: {spec_file}")
            return {"current_tools": [], "rejected_tools": [], "proposed_tools": []}
        
        with open(spec_path, 'r') as f:
            content = f.read()
        
        # Parse the structured specification file
        tools_data = {
            "current_tools": self._parse_tools_section(content, "## 📋 Current Tools (Production)"),
            "rejected_tools": self._parse_tools_section(content, "## ❌ Rejected Tools (Learn from Failures)"),
            "proposed_tools": self._parse_tools_section(content, "## 🚀 Proposed Tools (Ready for Implementation)"),
            "successful_patterns": self._parse_patterns_section(content, "### ✅ Successful Patterns"),
            "failed_patterns": self._parse_patterns_section(content, "### ❌ Failed Patterns")
        }
        
        return tools_data
    
    def _parse_tools_section(self, content: str, section_header: str) -> List[Dict[str, Any]]:
        """Parse a tools section from the specification file"""
        
        tools = []
        
        # Find the section
        section_start = content.find(section_header)
        if section_start == -1:
            return tools
        
        # Find next major section
        next_section = content.find("## ", section_start + len(section_header))
        if next_section == -1:
            section_content = content[section_start:]
        else:
            section_content = content[section_start:next_section]
        
        # Parse individual tools (### headers)
        tool_parts = section_content.split("### ")[1:]  # Skip first empty part
        
        for tool_part in tool_parts:
            if not tool_part.strip():
                continue
                
            lines = tool_part.strip().split('\n')
            if not lines:
                continue
            
            # Extract tool name and priority from first line
            first_line = lines[0].strip()
            name = first_line.split(' ')[0]  # Remove priority emojis
            priority = "unknown"
            if "⭐" in first_line:
                priority = "high"
            elif "🔶" in first_line:
                priority = "medium"
            elif "✅" in first_line:
                priority = "low"
            
            # Parse tool details
            tool_info = {
                "name": name,
                "priority": priority,
                "purpose": "",
                "input_spec": "",
                "output_spec": "",
                "integration": "",
                "performance": "",
                "success_rate": ""
            }
            
            # Extract information from lines
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("**Purpose**:"):
                    tool_info["purpose"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Input**:"):
                    tool_info["input_spec"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Output**:"):
                    tool_info["output_spec"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Integration**:"):
                    tool_info["integration"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Performance**:") or line.startswith("**Expected Performance**:"):
                    tool_info["performance"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Success Rate**:"):
                    tool_info["success_rate"] = line.split(":", 1)[1].strip()
            
            tools.append(tool_info)
        
        return tools
    
    def _parse_patterns_section(self, content: str, section_header: str) -> List[str]:
        """Parse patterns section from the specification file"""
        
        patterns = []
        
        # Find the section
        section_start = content.find(section_header)
        if section_start == -1:
            return patterns
        
        # Find next section
        next_section = content.find("### ", section_start + len(section_header))
        if next_section == -1:
            next_section = content.find("## ", section_start + len(section_header))
        
        if next_section == -1:
            section_content = content[section_start:]
        else:
            section_content = content[section_start:next_section]
        
        # Extract bullet points
        lines = section_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. '):
                patterns.append(line[3:].strip())  # Remove number prefix
        
        return patterns
    
    def get_tools_for_agent_context(self) -> str:
        """Get a concise summary of tools for agent prompts"""
        
        tools_data = self.get_tool_specifications()
        
        context = "CURRENT TOOL ECOSYSTEM:\n\n"
        
        # Current tools
        context += "Current Tools in Production:\n"
        for tool in tools_data["current_tools"][:5]:  # Limit to top 5
            context += f"- {tool['name']}: {tool['purpose']}\n"
            context += f"  Input: {tool['input_spec']}\n"
            context += f"  Performance: {tool['performance']}\n\n"
        
        # Failed patterns to avoid
        context += "AVOID THESE FAILED PATTERNS:\n"
        for pattern in tools_data["failed_patterns"]:
            context += f"- {pattern}\n"
        
        # Successful patterns to follow
        context += "\nFOLLOW THESE SUCCESSFUL PATTERNS:\n"
        for pattern in tools_data["successful_patterns"]:
            context += f"- {pattern}\n"
        
        return context


class ToolDiscoveryTracker:
    """
    Tracks tool discoveries during evolution iterations
    """
    
    def __init__(self):
        self.discovered_tools = []
        self.iteration_number = None
    
    def set_iteration(self, iteration: int):
        """Set current iteration number"""
        self.iteration_number = iteration
    
    def record_tool_discovery(self, tool_spec: Dict[str, Any]):
        """Record a newly discovered tool"""
        
        tool_spec['iteration'] = self.iteration_number
        tool_spec['discovered_at'] = datetime.now().isoformat()
        self.discovered_tools.append(tool_spec)
        
        logger.info(f"🔧 Tool discovered: {tool_spec.get('name', 'Unknown')}")
    
    def get_discoveries_for_iteration(self, iteration: int) -> List[Dict[str, Any]]:
        """Get all tools discovered in a specific iteration"""
        return [t for t in self.discovered_tools if t.get('iteration') == iteration]
    
    def prioritize_discoveries(self) -> List[Dict[str, Any]]:
        """Prioritize discovered tools by expected impact and complexity"""
        
        # Sort by impact (high to low) and complexity (low to high)
        def priority_score(tool):
            impact_scores = {'high': 3, 'medium': 2, 'low': 1}
            complexity_scores = {'low': 3, 'medium': 2, 'high': 1}
            
            impact = impact_scores.get(tool.get('expected_impact', 'low').lower(), 1)
            complexity = complexity_scores.get(tool.get('complexity', 'high').lower(), 1)
            
            return impact * complexity
        
        prioritized = sorted(self.discovered_tools, key=priority_score, reverse=True)
        
        # Assign priority numbers
        for i, tool in enumerate(prioritized):
            tool['priority'] = i + 1
        
        return prioritized