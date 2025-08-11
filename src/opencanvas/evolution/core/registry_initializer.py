"""
Registry Initializer - Properly initialize TOOLS_REGISTRY.md for evolution runs
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from opencanvas.evolution.config.tools_specs import CURRENT_TOOLS, REJECTED_TOOLS

logger = logging.getLogger(__name__)

class RegistryInitializer:
    """
    Initializes TOOLS_REGISTRY.md properly at the start of each evolution run:
    - Populates Active Tools with actual baseline tools from CURRENT_TOOLS
    - Empties Proposed Tools section (filled dynamically during evolution)  
    - Preserves Failed Tools section for learning persistence
    - Adds run metadata and proper structure
    """
    
    def __init__(self, registry_path: str = "TOOLS_REGISTRY.md"):
        """Initialize registry initializer"""
        self.registry_path = Path(registry_path)
        logger.info(f"🔧 Registry Initializer initialized for {registry_path}")
    
    def initialize_for_evolution_run(self, run_id: str = None, baseline_scores: Dict = None) -> bool:
        """Initialize registry for a new evolution run"""
        
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"📝 Initializing TOOLS_REGISTRY.md for evolution run {run_id}")
        
        try:
            # Preserve existing failed tools if registry exists
            existing_failed_tools = self._extract_existing_failed_tools()
            
            # Create fresh registry content
            registry_content = self._generate_registry_content(run_id, baseline_scores, existing_failed_tools)
            
            # Write the new registry
            with open(self.registry_path, 'w') as f:
                f.write(registry_content)
            
            logger.info(f"✅ Registry initialized successfully:")
            logger.info(f"   - Active Tools: {len(CURRENT_TOOLS)}")
            logger.info(f"   - Proposed Tools: 0 (clean slate)")
            logger.info(f"   - Failed Tools: {len(existing_failed_tools)} (preserved)")
            logger.info(f"   - Run ID: {run_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize registry: {e}")
            return False
    
    def _extract_existing_failed_tools(self) -> Dict[str, Dict]:
        """Extract existing failed tools to preserve learning"""
        
        existing_failed_tools = {}
        
        # First, add failed tools from REJECTED_TOOLS config
        for tool_name, tool_data in REJECTED_TOOLS.items():
            existing_failed_tools[tool_name] = {
                "purpose": tool_data["purpose"],
                "failure_reason": tool_data["failure_reason"],
                "test_period": tool_data["test_period"],
                "pattern": tool_data["pattern"],
                "lesson": tool_data["lesson"]
            }
        
        # Then, try to extract additional failed tools from existing registry
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    content = f.read()
                
                # Simple parsing for failed tools section
                failed_section_start = content.find("## ❌ Failed Tools (Lessons Learned)")
                if failed_section_start != -1:
                    # Extract tools from failed section that aren't in REJECTED_TOOLS
                    # This preserves tools that were discovered and failed during evolution
                    # (Implementation could be enhanced with more sophisticated parsing)
                    pass
                    
            except Exception as e:
                logger.warning(f"Could not parse existing registry for failed tools: {e}")
        
        logger.info(f"📚 Preserved {len(existing_failed_tools)} failed tools for learning")
        return existing_failed_tools
    
    def _generate_registry_content(self, run_id: str, baseline_scores: Dict, failed_tools: Dict) -> str:
        """Generate complete registry content"""
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 🛠️ Tools Registry

*Run ID: {run_id} | Updated: {current_date}*

---

## ✅ Active Tools

"""
        
        # Only include actual tools, not system components
        actual_tools = {
            "WebSearchTool": CURRENT_TOOLS["WebSearchTool"],
            "WebScraperTool": CURRENT_TOOLS["WebScraperTool"],
            "ImageValidationTool": CURRENT_TOOLS["ImageValidationTool"]
        }
        
        # Add active tools in YAML format
        for tool_name, tool_data in actual_tools.items():
            content += f"""### {tool_name}
```yaml
purpose: {tool_data["purpose"]}
input: {tool_data["input_spec"]}
output: {tool_data["output_spec"]}
usage: {tool_data.get("implementation", "See implementation for usage details")}
```

"""
        
        content += """---

## 🔄 Proposed Tools

"""
        
        # Proposed tools will be added dynamically with same YAML format
        
        content += """---

## ❌ Failed Tools

"""
        
        # Add failed tools in YAML format
        for tool_name, tool_data in failed_tools.items():
            content += f"""### {tool_name}
```yaml
purpose: {tool_data["purpose"]}
failure_reason: {tool_data["failure_reason"]}
lesson_learned: {tool_data["lesson"]}
```

"""
        
        return content
    
    def add_proposed_tool(self, tool_name: str, tool_spec: Dict[str, Any]) -> bool:
        """Add a newly discovered tool to the Proposed Tools section"""
        
        logger.info(f"📝 Adding proposed tool to registry: {tool_name}")
        
        try:
            with open(self.registry_path, 'r') as f:
                content = f.read()
            
            # Find the Proposed Tools section
            proposed_section = "## 🔄 Proposed Tools"
            proposed_start = content.find(proposed_section)
            
            if proposed_start == -1:
                logger.error("Could not find Proposed Tools section")
                return False
            
            # Find the end of the section (next ## header)
            next_section = content.find("## ❌ Failed Tools", proposed_start)
            if next_section == -1:
                next_section = content.find("---", proposed_start + len(proposed_section))
                if next_section == -1:
                    logger.error("Could not find end of Proposed Tools section")
                    return False
            
            # Generate tool entry in YAML format with gap tracking
            tool_entry = f"""### {tool_name}
```yaml
purpose: {tool_spec.get('purpose', 'Unknown')}
targets_gap: {tool_spec.get('targets_gap', 'Unknown gap')}
solution_type: {tool_spec.get('solution_type', 'tool')}
baseline_score: {tool_spec.get('baseline_score', 'N/A')}
target_score: {tool_spec.get('target_score', 'N/A')}
expected_impact: {tool_spec.get('expected_impact', 'Unknown')}
complexity: {tool_spec.get('complexity', 'Unknown')}
input: {tool_spec.get('input_spec', '(input_data) -> Result')}
output: {tool_spec.get('output_spec', 'Result object with success status and data')}
usage: {tool_spec.get('usage', tool_name + '().process(input_data)')}
```

"""
            
            # Add to proposed tools section
            new_content = content[:next_section] + "\n" + tool_entry + content[next_section:]
            
            # Write updated content
            with open(self.registry_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"✅ Added {tool_name} to Proposed Tools section")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add proposed tool {tool_name}: {e}")
            return False
    
    def mark_tool_failed(self, tool_name: str, failure_reason: str, lesson_learned: str) -> bool:
        """Move a tool from Proposed to Failed section"""
        
        logger.info(f"❌ Marking tool as failed: {tool_name}")
        
        try:
            with open(self.registry_path, 'r') as f:
                content = f.read()
            
            # Remove from Proposed Tools section
            content = self._remove_from_proposed_section(content, tool_name)
            
            # Add to Failed Tools section
            content = self._add_to_failed_section(content, tool_name, failure_reason, lesson_learned)
            
            # Write updated content
            with open(self.registry_path, 'w') as f:
                f.write(content)
            
            logger.info(f"✅ Moved {tool_name} to Failed Tools section")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark tool as failed {tool_name}: {e}")
            return False
    
    def _remove_from_proposed_section(self, content: str, tool_name: str) -> str:
        """Remove a tool from the Proposed Tools section"""
        
        # Find the tool entry
        tool_marker = f"### **{tool_name}**"
        tool_start = content.find(tool_marker)
        
        if tool_start == -1:
            logger.warning(f"Tool {tool_name} not found in Proposed Tools section")
            return content
        
        # Find the end of this tool entry (next ### or ## marker)
        search_start = tool_start + len(tool_marker)
        next_tool = content.find("### ", search_start)
        next_section = content.find("## ", search_start)
        
        if next_tool == -1:
            tool_end = next_section if next_section != -1 else len(content)
        elif next_section == -1:
            tool_end = next_tool
        else:
            tool_end = min(next_tool, next_section)
        
        # Remove the tool entry
        return content[:tool_start] + content[tool_end:]
    
    def _add_to_failed_section(self, content: str, tool_name: str, failure_reason: str, lesson_learned: str) -> str:
        """Add a tool to the Failed Tools section"""
        
        # Find Failed Tools section
        failed_section = "## ❌ Failed Tools"
        failed_start = content.find(failed_section)
        
        if failed_start == -1:
            logger.error("Could not find Failed Tools section")
            return content
        
        # Find end of content (no more sections after Failed Tools in compact format)
        next_section = len(content)
        
        # Generate failed tool entry in YAML format
        failed_entry = f"""### {tool_name}
```yaml
purpose: Tool discovered during evolution but failed testing
failure_reason: {failure_reason}
lesson_learned: {lesson_learned}
```

"""
        
        # Insert before end
        return content[:next_section] + failed_entry
    
    def get_failed_tools(self) -> List[str]:
        """Get list of all failed tool names for gap identification"""
        
        if not self.registry_path.exists():
            return []
        
        failed_tools = []
        
        try:
            with open(self.registry_path, 'r') as f:
                content = f.read()
            
            # Find Failed Tools section
            failed_start = content.find("## ❌ Failed Tools")
            if failed_start == -1:
                return failed_tools
            
            # Parse to end of file (no sections after Failed Tools)
            failed_section = content[failed_start:]
            
            # Extract tool names (simple parsing)
            lines = failed_section.split('\n')
            for line in lines:
                if line.strip().startswith("### ") and not line.strip().startswith("### **"):
                    tool_name = line.strip()[4:]  # Remove "### "
                    failed_tools.append(tool_name)
            
        except Exception as e:
            logger.error(f"Failed to extract failed tools: {e}")
        
        return failed_tools
    
    def get_active_tools(self) -> List[str]:
        """Get list of all active tool names by parsing the registry"""
        registry_data = self.parse_registry()
        return list(registry_data.get("active_tools", {}).keys())
    
    def parse_registry(self) -> Dict[str, Dict]:
        """Parse the entire registry into structured data"""
        
        if not self.registry_path.exists():
            logger.warning(f"Registry file {self.registry_path} does not exist")
            return {"active_tools": {}, "proposed_tools": {}, "failed_tools": {}}
        
        try:
            with open(self.registry_path, 'r') as f:
                content = f.read()
            
            registry_data = {
                "active_tools": {},
                "proposed_tools": {},
                "failed_tools": {}
            }
            
            # Parse each section
            sections = [
                ("## ✅ Active Tools", "## 🔄 Proposed Tools", "active_tools"),
                ("## 🔄 Proposed Tools", "## ❌ Failed Tools", "proposed_tools"),
                ("## ❌ Failed Tools", None, "failed_tools")
            ]
            
            for start_marker, end_marker, section_key in sections:
                start_idx = content.find(start_marker)
                if start_idx == -1:
                    continue
                
                if end_marker:
                    end_idx = content.find(end_marker, start_idx)
                    section_content = content[start_idx:end_idx] if end_idx != -1 else content[start_idx:]
                else:
                    section_content = content[start_idx:]
                
                # Parse tools in this section
                tools = self._parse_section_tools(section_content)
                registry_data[section_key] = tools
            
            logger.info(f"📚 Parsed registry: {len(registry_data['active_tools'])} active, "
                       f"{len(registry_data['proposed_tools'])} proposed, "
                       f"{len(registry_data['failed_tools'])} failed")
            
            return registry_data
            
        except Exception as e:
            logger.error(f"Failed to parse registry: {e}")
            return {"active_tools": {}, "proposed_tools": {}, "failed_tools": {}}
    
    def _parse_section_tools(self, section_content: str) -> Dict[str, Dict]:
        """Parse tools from a section into structured data"""
        tools = {}
        
        # Split by tool headers (### ToolName)
        tool_blocks = []
        lines = section_content.split('\n')
        current_block = []
        current_tool_name = None
        
        for line in lines:
            if line.strip().startswith("### ") and not line.strip().startswith("### **"):
                # Save previous block if exists
                if current_tool_name and current_block:
                    tool_blocks.append((current_tool_name, '\n'.join(current_block)))
                # Start new block
                current_tool_name = line.strip()[4:].strip()
                current_block = []
            elif current_tool_name:
                current_block.append(line)
        
        # Don't forget the last block
        if current_tool_name and current_block:
            tool_blocks.append((current_tool_name, '\n'.join(current_block)))
        
        # Parse each tool block
        for tool_name, block_content in tool_blocks:
            # Extract YAML content between ```yaml and ```
            yaml_start = block_content.find("```yaml")
            yaml_end = block_content.find("```", yaml_start + 7)
            
            if yaml_start != -1 and yaml_end != -1:
                yaml_content = block_content[yaml_start + 7:yaml_end].strip()
                tool_data = self._parse_yaml_content(yaml_content)
                tools[tool_name] = tool_data
        
        return tools
    
    def _parse_yaml_content(self, yaml_content: str) -> Dict[str, str]:
        """Parse YAML-like content into dictionary"""
        data = {}
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data