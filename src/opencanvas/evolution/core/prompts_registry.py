"""
Prompts Registry Manager - Long-term memory for prompt evolution
Tracks successful and failed prompt modifications with lessons learned
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptsRegistryManager:
    """
    Manages the PROMPTS_REGISTRY.md file for tracking prompt evolution
    Similar to RegistryInitializer but specifically for prompts
    """
    
    def __init__(self, registry_file: str = "PROMPTS_REGISTRY.md"):
        """Initialize prompts registry manager"""
        self.registry_file = Path(registry_file)
        self.registry_data = None
        
        # Create registry if it doesn't exist
        if not self.registry_file.exists():
            self._create_initial_registry()
        
        # Parse existing registry
        self.registry_data = self.parse_registry()
        logger.info(f"📚 PromptsRegistryManager initialized with {registry_file}")
    
    def parse_registry(self) -> Dict[str, Any]:
        """Parse the PROMPTS_REGISTRY.md file"""
        
        if not self.registry_file.exists():
            return self._get_empty_registry()
        
        content = self.registry_file.read_text()
        
        registry = {
            "active_prompts": {},
            "proposed_edits": {},
            "failed_edits": {},
            "successful_patterns": {},
            "failed_patterns": {},
            "statistics": {},
            "lessons_learned": []
        }
        
        # Parse sections using regex
        sections = {
            "active_prompts": r"## ✅ Active Prompts(.*?)(?=##|$)",
            "proposed_edits": r"## 🔄 Proposed Prompt Edits(.*?)(?=##|$)",
            "failed_edits": r"## ❌ Failed Prompt Edits(.*?)(?=##|$)",
            "successful_patterns": r"## 📊 Successful Prompt Patterns(.*?)(?=##|$)",
            "failed_patterns": r"## ❌ Failed Prompt Patterns(.*?)(?=##|$)"
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_content = match.group(1)
                registry[key] = self._parse_section(section_content, key)
        
        # Parse statistics
        stats_match = re.search(r"## 📈 Evolution Metrics(.*?)(?=##|$)", content, re.DOTALL)
        if stats_match:
            registry["statistics"] = self._parse_statistics(stats_match.group(1))
        
        # Parse lessons learned
        lessons_match = re.search(r"## 💡 Lessons Learned(.*?)(?=##|---)", content, re.DOTALL)
        if lessons_match:
            registry["lessons_learned"] = self._parse_lessons(lessons_match.group(1))
        
        return registry
    
    def add_active_prompt(self, prompt_data: Dict[str, Any], test_results: Dict[str, Any]) -> bool:
        """Add a successful prompt to the active prompts section"""
        
        try:
            prompt_name = prompt_data.get("name", f"Prompt_v{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            version = prompt_data.get("version", "1.0")
            
            active_prompt = {
                "version": version,
                "type": prompt_data.get("type", "generation_prompt"),
                "baseline_score": test_results.get("baseline_avg", 0),
                "current_score": test_results.get("edited_avg", 0),
                "improvement": test_results.get("improvement", 0),
                "key_changes": prompt_data.get("changes", []),
                "deployed_date": datetime.now().strftime("%Y-%m-%d"),
                "iterations_stable": 0,
                "evaluation_dimensions": test_results.get("dimension_scores", {}),
                "statistical_significance": test_results.get("statistical_significance", "unknown")
            }
            
            # Update registry
            self.registry_data["active_prompts"][prompt_name] = active_prompt
            
            # Update statistics
            self._update_statistics("success", active_prompt)
            
            # Write to file
            self._update_registry_file()
            
            logger.info(f"✅ Added active prompt: {prompt_name} with +{active_prompt['improvement']:.3f} improvement")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add active prompt: {e}")
            return False
    
    def add_failed_prompt(self, prompt_data: Dict[str, Any], test_results: Dict[str, Any]) -> bool:
        """Add a failed prompt edit to the registry with lessons learned"""
        
        try:
            prompt_name = prompt_data.get("name", f"Failed_Prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            failed_edit = {
                "version": prompt_data.get("version", "unknown"),
                "failure_reason": test_results.get("failure_reason", "Did not improve scores"),
                "baseline_score": test_results.get("baseline_avg", 0),
                "attempted_score": test_results.get("edited_avg", 0),
                "degradation": test_results.get("improvement", 0),  # Will be negative
                "attempted_changes": prompt_data.get("changes", []),
                "tested_date": datetime.now().strftime("%Y-%m-%d"),
                "lesson_learned": self._extract_lesson(prompt_data, test_results)
            }
            
            # Update registry
            self.registry_data["failed_edits"][prompt_name] = failed_edit
            
            # Update failed patterns
            self._update_failed_patterns(prompt_data, test_results)
            
            # Update statistics
            self._update_statistics("failure", failed_edit)
            
            # Write to file
            self._update_registry_file()
            
            logger.info(f"❌ Documented failed prompt: {prompt_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add failed prompt: {e}")
            return False
    
    def get_successful_patterns(self) -> List[Dict[str, Any]]:
        """Get successful prompt patterns for agent context"""
        
        patterns = []
        
        for pattern_name, pattern_data in self.registry_data.get("successful_patterns", {}).items():
            patterns.append({
                "name": pattern_name,
                "description": pattern_data.get("description", ""),
                "success_rate": pattern_data.get("success_rate", 0),
                "average_improvement": pattern_data.get("average_improvement", 0),
                "example_changes": pattern_data.get("example_changes", []),
                "applies_to": pattern_data.get("applies_to", [])
            })
        
        return sorted(patterns, key=lambda x: x["success_rate"], reverse=True)
    
    def get_failed_patterns(self) -> List[Dict[str, Any]]:
        """Get failed prompt patterns to avoid"""
        
        patterns = []
        
        for pattern_name, pattern_data in self.registry_data.get("failed_patterns", {}).items():
            patterns.append({
                "name": pattern_name,
                "description": pattern_data.get("description", ""),
                "failure_rate": pattern_data.get("failure_rate", 0),
                "average_degradation": pattern_data.get("average_degradation", 0),
                "example_failures": pattern_data.get("example_failures", []),
                "lesson_learned": pattern_data.get("lesson_learned", "")
            })
        
        return sorted(patterns, key=lambda x: x["failure_rate"], reverse=True)
    
    def check_similar_edits(self, proposed_changes: List[str]) -> Dict[str, Any]:
        """Check if similar edits have been tried before"""
        
        similar_attempts = {
            "exact_matches": [],
            "partial_matches": [],
            "pattern_warnings": []
        }
        
        # Check against failed edits
        for edit_name, edit_data in self.registry_data.get("failed_edits", {}).items():
            attempted_changes = edit_data.get("attempted_changes", [])
            
            # Check for exact matches
            for change in proposed_changes:
                if change in attempted_changes:
                    similar_attempts["exact_matches"].append({
                        "edit_name": edit_name,
                        "change": change,
                        "degradation": edit_data.get("degradation", 0),
                        "lesson": edit_data.get("lesson_learned", "")
                    })
                
                # Check for partial matches (similar keywords)
                change_keywords = set(change.lower().split())
                for attempted in attempted_changes:
                    attempted_keywords = set(attempted.lower().split())
                    overlap = len(change_keywords & attempted_keywords) / max(len(change_keywords), 1)
                    
                    if overlap > 0.6:  # 60% keyword overlap
                        similar_attempts["partial_matches"].append({
                            "edit_name": edit_name,
                            "proposed": change,
                            "previous": attempted,
                            "similarity": overlap,
                            "result": edit_data.get("degradation", 0)
                        })
        
        # Check against failed patterns
        for pattern_name, pattern_data in self.registry_data.get("failed_patterns", {}).items():
            pattern_keywords = pattern_data.get("description", "").lower().split()
            
            for change in proposed_changes:
                if any(keyword in change.lower() for keyword in pattern_keywords):
                    similar_attempts["pattern_warnings"].append({
                        "pattern": pattern_name,
                        "warning": pattern_data.get("lesson_learned", ""),
                        "failure_rate": pattern_data.get("failure_rate", 0)
                    })
        
        return similar_attempts
    
    def get_context_for_agents(self) -> str:
        """Get registry context for improvement agents - just return the whole file content"""
        
        if not self.registry_file.exists():
            return "No prompt evolution history available."
        
        try:
            registry_content = self.registry_file.read_text()
            
            # Add a header to make it clear this is context
            context = "PROMPT EVOLUTION HISTORY AND LESSONS LEARNED:\n\n"
            context += registry_content
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to read registry file: {e}")
            return "Error loading prompt evolution history."
    
    def _parse_section(self, content: str, section_type: str) -> Dict[str, Any]:
        """Parse a section of the registry"""
        
        items = {}
        
        # Find all YAML blocks in the section (we'll parse them as key-value pairs)
        yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        
        for block in yaml_blocks:
            try:
                # Simple YAML-like parsing for our structured data
                data = {}
                current_key = None
                current_list = None
                
                for line in block.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle key: value pairs
                    if ':' in line and not line.startswith('-'):
                        parts = line.split(':', 1)
                        key = parts[0].strip()
                        value = parts[1].strip() if len(parts) > 1 else ''
                        
                        # Clean up quotes
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Try to convert to appropriate type
                        if value.lower() in ['true', 'false']:
                            value = value.lower() == 'true'
                        elif value.replace('.', '').replace('-', '').isdigit():
                            try:
                                value = float(value) if '.' in value else int(value)
                            except:
                                pass
                        
                        data[key] = value
                        current_key = key
                        current_list = None
                    
                    # Handle list items
                    elif line.startswith('-'):
                        item = line[1:].strip()
                        if item.startswith('"') and item.endswith('"'):
                            item = item[1:-1]
                        
                        if current_key:
                            if not isinstance(data.get(current_key), list):
                                data[current_key] = []
                            data[current_key].append(item)
                
                if data:
                    # Extract name from the data or generate one
                    name = data.get('name') or data.get('pattern_name') or data.get('version') or f"{section_type}_{len(items)}"
                    items[name] = data
            except Exception as e:
                logger.debug(f"Failed to parse YAML block: {e}")
                continue
        
        return items
    
    def _parse_statistics(self, content: str) -> Dict[str, Any]:
        """Parse statistics section"""
        
        stats = {}
        
        yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        
        for block in yaml_blocks:
            try:
                # Simple parsing for statistics
                for line in block.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if ':' in line:
                        parts = line.split(':', 1)
                        key = parts[0].strip()
                        value = parts[1].strip() if len(parts) > 1 else ''
                        
                        # Try to convert to number
                        if value.replace('.', '').replace('-', '').isdigit():
                            try:
                                value = float(value) if '.' in value else int(value)
                            except:
                                pass
                        elif value == 'N/A':
                            value = None
                        
                        stats[key] = value
            except Exception as e:
                logger.debug(f"Failed to parse statistics block: {e}")
                continue
        
        return stats
    
    def _parse_lessons(self, content: str) -> List[str]:
        """Parse lessons learned section"""
        
        lessons = []
        
        # Extract numbered lessons
        lesson_matches = re.findall(r'\d+\.\s+\*\*(.*?)\*\*:\s+(.*?)(?=\n\d+\.|\n##|$)', content, re.DOTALL)
        
        for title, description in lesson_matches:
            lessons.append(f"{title}: {description.strip()}")
        
        return lessons
    
    def _extract_lesson(self, prompt_data: Dict[str, Any], test_results: Dict[str, Any]) -> str:
        """Extract lesson learned from failed prompt attempt"""
        
        degradation = test_results.get("improvement", 0)
        changes = prompt_data.get("changes", [])
        
        if degradation < -0.5:
            lesson = "Severe degradation - avoid this type of change entirely"
        elif degradation < -0.2:
            lesson = "Moderate degradation - approach needs refinement"
        else:
            lesson = "Minimal impact - changes too conservative or off-target"
        
        # Add specific insights based on changes
        if any("restrict" in str(c).lower() or "must" in str(c).lower() for c in changes):
            lesson += ". Over-restriction likely caused issues"
        if any("vague" in str(c).lower() or "better" in str(c).lower() for c in changes):
            lesson += ". Instructions too vague to be effective"
        
        return lesson
    
    def _update_failed_patterns(self, prompt_data: Dict[str, Any], test_results: Dict[str, Any]):
        """Update failed patterns based on new failure"""
        
        # Identify pattern type from changes
        changes = prompt_data.get("changes", [])
        
        pattern_type = None
        if any("restrict" in str(c).lower() or "never" in str(c).lower() or "must" in str(c).lower() for c in changes):
            pattern_type = "over_restriction"
        elif any("better" in str(c).lower() or "improve" in str(c).lower() for c in changes):
            pattern_type = "vague_instructions"
        
        if pattern_type and pattern_type in self.registry_data.get("failed_patterns", {}):
            pattern = self.registry_data["failed_patterns"][pattern_type]
            
            # Update failure rate
            current_rate = pattern.get("failure_rate", 0)
            pattern["failure_rate"] = (current_rate + 1.0) / 2  # Moving average
            
            # Add to example failures
            if "example_failures" not in pattern:
                pattern["example_failures"] = []
            pattern["example_failures"].extend(changes[:2])  # Add up to 2 examples
    
    def _update_statistics(self, result_type: str, prompt_data: Dict[str, Any]):
        """Update overall statistics"""
        
        if "statistics" not in self.registry_data:
            self.registry_data["statistics"] = {}
        
        stats = self.registry_data["statistics"]
        
        # Update counts
        if result_type == "success":
            stats["successful_edits"] = stats.get("successful_edits", 0) + 1
            improvement = prompt_data.get("improvement", 0)
            
            # Update average improvement
            current_avg = stats.get("avg_improvement_successful", 0)
            count = stats["successful_edits"]
            stats["avg_improvement_successful"] = ((current_avg * (count - 1)) + improvement) / count
            
        else:  # failure
            stats["failed_edits"] = stats.get("failed_edits", 0) + 1
            degradation = prompt_data.get("degradation", 0)
            
            # Update average degradation
            current_avg = stats.get("avg_degradation_failed", 0)
            count = stats["failed_edits"]
            stats["avg_degradation_failed"] = ((current_avg * (count - 1)) + degradation) / count
        
        # Update success rate
        total = stats.get("successful_edits", 0) + stats.get("failed_edits", 0)
        if total > 0:
            stats["success_rate"] = stats.get("successful_edits", 0) / total
        
        stats["total_prompt_edits_tested"] = total
    
    def _update_registry_file(self):
        """Actually write updated registry to file"""
        
        try:
            from datetime import datetime
            
            # Build new registry content
            stats = self.registry_data.get("statistics", {})
            total_runs = stats.get("total_prompt_edits_tested", 0)
            
            lines = [
                "# Prompts Registry",
                f"Updated: {datetime.now().strftime('%Y-%m-%d')} | Total Runs: {total_runs}",
                "",
                "**Long-term memory for prompt evolution. Tracks successful and failed prompt modifications across evolution runs.**",
                ""
            ]
            
            # Find current best prompt
            best_prompt = None
            best_score = 0
            best_improvement = 0
            
            for name, data in self.registry_data.get("active_prompts", {}).items():
                score = data.get("current_score", 0)
                improvement = data.get("improvement", 0)
                if score > best_score:
                    best_score = score
                    best_improvement = improvement
                    best_prompt = {
                        "name": name,
                        "path": data.get("location", f"evolution_runs/evolved_prompts/{name.lower().replace(' ', '_')}.txt"),
                        "score": score,
                        "improvement": improvement
                    }
            
            # Default to baseline if no better prompts
            if not best_prompt:
                best_prompt = {
                    "name": "baseline",
                    "path": "src/opencanvas/prompts/baseline/generation_prompt.txt",
                    "score": 3.2,
                    "improvement": 0.0
                }
            
            # Current Best section
            lines.extend([
                "## Current Best",
                f"path: {best_prompt['path']}",
                f"score: {best_prompt['score']:.1f}",
                f"improvement: {best_prompt['improvement']:+.1f}",
                ""
            ])
            
            # Accepted prompts section
            lines.append("## Accepted (>0.1 improvement)")
            
            accepted_found = False
            for name, data in self.registry_data.get("active_prompts", {}).items():
                improvement = data.get("improvement", 0)
                if improvement >= 0.1:
                    accepted_found = True
                    path = data.get("location", f"evolution_runs/evolved_prompts/{name.lower().replace(' ', '_')}.txt")
                    key_changes = data.get("key_changes", ["unknown"])
                    key_change = key_changes[0] if key_changes else "unknown"
                    lines.append(f"{name.lower().replace(' ', '_')}: {path} | {improvement:+.1f} | {key_change}")
            
            # Add baseline if no accepted prompts
            if not accepted_found:
                lines.append("baseline: src/opencanvas/prompts/baseline/generation_prompt.txt | +0.0 | baseline_prompt")
            
            lines.extend(["", "## Failed (>0.2 degradation)"])
            
            # Failed prompts section
            failed_found = False
            for name, data in self.registry_data.get("failed_edits", {}).items():
                degradation = data.get("degradation", 0)
                if abs(degradation) >= 0.2:
                    failed_found = True
                    path = data.get("location", f"evolution_runs/evolved_prompts/{name.lower().replace(' ', '_')}.txt")
                    reason = data.get("failure_reason", "unknown")
                    lines.append(f"{name.lower().replace(' ', '_')}: {path} | {degradation:.1f} | {reason}")
            
            if not failed_found:
                lines.append("*No failed prompts yet*")
            
            # Write to file
            content = "\n".join(lines)
            self.registry_file.write_text(content)
            
            logger.info(f"📝 Updated {self.registry_file} with {len(self.registry_data.get('active_prompts', {}))} active prompts")
            
        except Exception as e:
            logger.error(f"Failed to update registry file: {e}")
    
    def _create_initial_registry(self):
        """Create initial PROMPTS_REGISTRY.md if it doesn't exist"""
        
        # Use the template we already created
        logger.info(f"📝 Creating initial prompts registry: {self.registry_file}")
    
    def _get_empty_registry(self) -> Dict[str, Any]:
        """Get empty registry structure"""
        
        return {
            "active_prompts": {},
            "proposed_edits": {},
            "failed_edits": {},
            "successful_patterns": {
                "source_adherence": {
                    "pattern_name": "source_adherence",
                    "description": "Adding explicit instructions to follow source material exactly",
                    "success_rate": 0.75,
                    "average_improvement": 0.8,
                    "example_changes": [
                        "You MUST use only information from the source material",
                        "Do not add any information not explicitly stated in the source"
                    ],
                    "applies_to": ["accuracy", "completeness"]
                }
            },
            "failed_patterns": {
                "over_restriction": {
                    "pattern_name": "over_restriction",
                    "description": "Too many constraints that limit model creativity",
                    "failure_rate": 0.8,
                    "average_degradation": -0.6,
                    "example_failures": [
                        "NEVER use any words not in the source"
                    ],
                    "lesson_learned": "Balance accuracy requirements with creative freedom"
                }
            },
            "statistics": {
                "total_prompt_edits_tested": 0,
                "successful_edits": 0,
                "failed_edits": 0,
                "success_rate": 0,
                "avg_improvement_successful": 0,
                "avg_degradation_failed": 0
            },
            "lessons_learned": []
        }
    
    def get_prompt_version_history(self, prompt_type: str = "generation_prompt") -> List[Dict[str, Any]]:
        """Get version history for a specific prompt type"""
        
        versions = []
        
        for name, data in self.registry_data.get("active_prompts", {}).items():
            if data.get("type") == prompt_type:
                versions.append({
                    "name": name,
                    "version": data.get("version"),
                    "improvement": data.get("improvement", 0),
                    "date": data.get("deployed_date"),
                    "stable_iterations": data.get("iterations_stable", 0)
                })
        
        return sorted(versions, key=lambda x: x.get("version", "0"))