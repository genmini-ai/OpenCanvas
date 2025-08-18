"""
Prompt Evolution Analyzer

Core module for analyzing how prompts evolve over iterations, calculating
metrics, and identifying patterns in prompt optimization.
"""

import json
import re
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

@dataclass
class PromptVersion:
    """Represents a single version of an evolved prompt"""
    version: int
    iteration: int
    content: str
    file_path: Path
    word_count: int
    line_count: int
    instruction_count: int
    section_count: int
    
@dataclass
class PromptChange:
    """Represents a change between two prompt versions"""
    from_version: int
    to_version: int
    change_type: str  # 'addition', 'deletion', 'modification'
    section: str
    old_content: str
    new_content: str
    line_numbers: Tuple[int, int]
    
@dataclass
class EvolutionMetrics:
    """Metrics calculated for prompt evolution"""
    baseline_metrics: Dict[str, float]
    evolution_metrics: Dict[int, Dict[str, float]]
    score_improvements: Dict[int, Dict[str, float]]
    total_changes: int
    successful_changes: int
    failed_changes: int

class PromptEvolutionAnalyzer:
    """Analyzes prompt evolution patterns and generates insights"""
    
    def __init__(self, evolution_dir: Path):
        self.evolution_dir = Path(evolution_dir)
        self.prompt_versions: List[PromptVersion] = []
        self.prompt_changes: List[PromptChange] = []
        self.evaluation_data: Dict[int, Dict] = {}
        self.baseline_prompt: Optional[PromptVersion] = None
        
    def load_evolution_data(self) -> bool:
        """Load all evolution data from the evolution directory"""
        try:
            # Load prompt versions
            self._load_prompt_versions()
            
            # Load evaluation results for each iteration
            self._load_evaluation_data()
            
            # Calculate changes between versions
            self._calculate_prompt_changes()
            
            logger.info(f"Loaded {len(self.prompt_versions)} prompt versions")
            logger.info(f"Loaded evaluation data for {len(self.evaluation_data)} iterations")
            logger.info(f"Identified {len(self.prompt_changes)} changes")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load evolution data: {e}")
            return False
    
    def _load_prompt_versions(self):
        """Load all prompt versions from evolved_prompts directory"""
        prompts_dir = self.evolution_dir / "evolved_prompts"
        baseline_prompt_path = Path("src/opencanvas/prompts/baseline/generation_prompt.txt")
        
        # Load baseline prompt
        if baseline_prompt_path.exists():
            content = baseline_prompt_path.read_text(encoding='utf-8')
            self.baseline_prompt = PromptVersion(
                version=0,
                iteration=0,
                content=content,
                file_path=baseline_prompt_path,
                **self._calculate_prompt_metrics(content)
            )
        
        # Load evolved prompts
        if prompts_dir.exists():
            for prompt_file in sorted(prompts_dir.glob("generation_prompt_v*.txt")):
                version_match = re.search(r'v(\d+)', prompt_file.name)
                if version_match:
                    version = int(version_match.group(1))
                    content = prompt_file.read_text(encoding='utf-8')
                    
                    prompt_version = PromptVersion(
                        version=version,
                        iteration=version,
                        content=content,
                        file_path=prompt_file,
                        **self._calculate_prompt_metrics(content)
                    )
                    self.prompt_versions.append(prompt_version)
    
    def _load_evaluation_data(self):
        """Load evaluation results for each iteration"""
        evolution_results_path = self.evolution_dir / "evolution_results.json"
        
        if evolution_results_path.exists():
            with open(evolution_results_path, 'r') as f:
                evolution_data = json.load(f)
                
            # Extract evaluation data for each iteration
            for iteration_data in evolution_data.get('iterations', []):
                iteration = iteration_data['iteration']
                self.evaluation_data[iteration] = {
                    'scores': iteration_data.get('baseline_scores', {}),
                    'improvements': iteration_data.get('improvement_from_previous', {}),
                    'evaluation_data': iteration_data.get('evaluation_data', [])
                }
    
    def _calculate_prompt_metrics(self, content: str) -> Dict[str, int]:
        """Calculate basic metrics for a prompt"""
        lines = content.split('\n')
        words = content.split()
        
        # Count instructions (lines starting with -, numbers, or containing specific keywords)
        instruction_patterns = [
            r'^\s*-\s+',  # Bullet points
            r'^\s*\d+\.\s+',  # Numbered lists
            r'(must|should|ensure|create|use|include|add|implement)',  # Instruction keywords
        ]
        
        instruction_count = 0
        for line in lines:
            if any(re.search(pattern, line.lower()) for pattern in instruction_patterns):
                instruction_count += 1
        
        # Count sections (lines with XML-like tags or headers)
        section_count = len(re.findall(r'<[^>]+>|#+\s+', content))
        
        return {
            'word_count': len(words),
            'line_count': len(lines),
            'instruction_count': instruction_count,
            'section_count': section_count
        }
    
    def _calculate_prompt_changes(self):
        """Calculate changes between consecutive prompt versions"""
        all_prompts = []
        
        if self.baseline_prompt:
            all_prompts.append(self.baseline_prompt)
        
        all_prompts.extend(sorted(self.prompt_versions, key=lambda x: x.version))
        
        for i in range(1, len(all_prompts)):
            prev_prompt = all_prompts[i-1]
            curr_prompt = all_prompts[i]
            
            changes = self._diff_prompts(prev_prompt, curr_prompt)
            self.prompt_changes.extend(changes)
    
    def _diff_prompts(self, prev_prompt: PromptVersion, curr_prompt: PromptVersion) -> List[PromptChange]:
        """Calculate detailed differences between two prompts"""
        changes = []
        
        prev_lines = prev_prompt.content.split('\n')
        curr_lines = curr_prompt.content.split('\n')
        
        differ = difflib.unified_diff(
            prev_lines, 
            curr_lines,
            fromfile=f'v{prev_prompt.version}',
            tofile=f'v{curr_prompt.version}',
            lineterm=''
        )
        
        current_section = "unknown"
        
        for line in differ:
            if line.startswith('@@'):
                continue
            elif line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('-'):
                # Deletion
                old_content = line[1:].strip()
                section = self._identify_section(old_content)
                current_section = section if section != "unknown" else current_section
                
                changes.append(PromptChange(
                    from_version=prev_prompt.version,
                    to_version=curr_prompt.version,
                    change_type='deletion',
                    section=current_section,
                    old_content=old_content,
                    new_content='',
                    line_numbers=(0, 0)  # Could be improved with better line tracking
                ))
            elif line.startswith('+'):
                # Addition
                new_content = line[1:].strip()
                section = self._identify_section(new_content)
                current_section = section if section != "unknown" else current_section
                
                changes.append(PromptChange(
                    from_version=prev_prompt.version,
                    to_version=curr_prompt.version,
                    change_type='addition',
                    section=current_section,
                    old_content='',
                    new_content=new_content,
                    line_numbers=(0, 0)
                ))
        
        return changes
    
    def _identify_section(self, content: str) -> str:
        """Identify which section of the prompt a line belongs to"""
        content_lower = content.lower()
        
        # Check for XML-like section tags
        section_match = re.search(r'<([^>]+)>', content)
        if section_match:
            return section_match.group(1)
        
        # Check for common section keywords
        section_keywords = {
            'design_philosophy': ['philosophy', 'emotional impact', 'wow factor'],
            'visual_requirements': ['visual', 'requirement', 'create', 'implement'],
            'content_presentation': ['content', 'presentation', 'transform'],
            'content_enhancements': ['enhancement', 'data analysis', 'travel'],
            'technical_requirements': ['technical', 'html', 'css', 'javascript'],
            'navigation': ['navigation', 'slide', 'transition'],
            'accessibility': ['accessibility', 'contrast', 'wcag']
        }
        
        for section, keywords in section_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return section
        
        return "unknown"
    
    def get_evolution_metrics(self) -> EvolutionMetrics:
        """Calculate comprehensive evolution metrics"""
        baseline_metrics = {}
        evolution_metrics = {}
        score_improvements = {}
        
        # Calculate baseline metrics
        if self.baseline_prompt:
            baseline_metrics = {
                'word_count': self.baseline_prompt.word_count,
                'line_count': self.baseline_prompt.line_count,
                'instruction_count': self.baseline_prompt.instruction_count,
                'section_count': self.baseline_prompt.section_count
            }
        
        # Calculate metrics for each version
        for prompt_version in self.prompt_versions:
            evolution_metrics[prompt_version.version] = {
                'word_count': prompt_version.word_count,
                'line_count': prompt_version.line_count,
                'instruction_count': prompt_version.instruction_count,
                'section_count': prompt_version.section_count
            }
        
        # Get score improvements
        for iteration, eval_data in self.evaluation_data.items():
            score_improvements[iteration] = eval_data.get('improvements', {})
        
        # Count successful/failed changes
        successful_changes = 0
        failed_changes = 0
        
        for iteration, improvements in score_improvements.items():
            if improvements:
                overall_improvement = improvements.get('presentation_overall', 0)
                if overall_improvement > 0:
                    successful_changes += 1
                elif overall_improvement < 0:
                    failed_changes += 1
        
        return EvolutionMetrics(
            baseline_metrics=baseline_metrics,
            evolution_metrics=evolution_metrics,
            score_improvements=score_improvements,
            total_changes=len(self.prompt_changes),
            successful_changes=successful_changes,
            failed_changes=failed_changes
        )
    
    def get_change_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in prompt changes"""
        patterns = {
            'section_changes': defaultdict(int),
            'change_types': defaultdict(int),
            'common_additions': Counter(),
            'common_deletions': Counter(),
            'successful_change_types': defaultdict(list),
            'failed_change_types': defaultdict(list)
        }
        
        # Analyze change distribution
        for change in self.prompt_changes:
            patterns['section_changes'][change.section] += 1
            patterns['change_types'][change.change_type] += 1
            
            if change.change_type == 'addition' and change.new_content:
                # Extract key phrases from additions
                key_phrases = self._extract_key_phrases(change.new_content)
                patterns['common_additions'].update(key_phrases)
            
            if change.change_type == 'deletion' and change.old_content:
                key_phrases = self._extract_key_phrases(change.old_content)
                patterns['common_deletions'].update(key_phrases)
        
        # Correlate changes with success/failure
        for change in self.prompt_changes:
            iteration = change.to_version
            if iteration in self.evaluation_data:
                improvements = self.evaluation_data[iteration].get('improvements', {})
                overall_improvement = improvements.get('presentation_overall', 0)
                
                change_description = f"{change.section}:{change.change_type}"
                
                if overall_improvement > 0.1:  # Successful
                    patterns['successful_change_types'][change_description].append(overall_improvement)
                elif overall_improvement < -0.1:  # Failed
                    patterns['failed_change_types'][change_description].append(overall_improvement)
        
        return patterns
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text for pattern analysis"""
        # Simple phrase extraction - could be enhanced with NLP
        text_lower = text.lower()
        
        # Common meaningful phrases in prompt instructions
        key_patterns = [
            r'visual\s+\w+',
            r'create\s+\w+',
            r'use\s+\w+',
            r'implement\s+\w+',
            r'ensure\s+\w+',
            r'add\s+\w+',
            r'include\s+\w+',
            r'\w+\s+effect[s]?',
            r'\w+\s+animation[s]?',
            r'\w+\s+design',
            r'\w+\s+layout',
            r'\w+\s+hierarchy'
        ]
        
        phrases = []
        for pattern in key_patterns:
            matches = re.findall(pattern, text_lower)
            phrases.extend(matches)
        
        return phrases
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the evolution analysis"""
        metrics = self.get_evolution_metrics()
        patterns = self.get_change_patterns()
        
        summary = {
            'evolution_overview': {
                'total_iterations': len(self.prompt_versions),
                'total_changes': metrics.total_changes,
                'successful_iterations': metrics.successful_changes,
                'failed_iterations': metrics.failed_changes,
                'success_rate': metrics.successful_changes / len(self.prompt_versions) if self.prompt_versions else 0
            },
            'prompt_growth': {},
            'change_patterns': patterns,
            'score_progression': {},
            'key_insights': []
        }
        
        # Calculate prompt growth
        if self.baseline_prompt and self.prompt_versions:
            final_prompt = max(self.prompt_versions, key=lambda x: x.version)
            summary['prompt_growth'] = {
                'word_count_change': final_prompt.word_count - self.baseline_prompt.word_count,
                'instruction_count_change': final_prompt.instruction_count - self.baseline_prompt.instruction_count,
                'section_count_change': final_prompt.section_count - self.baseline_prompt.section_count,
                'relative_growth': (final_prompt.word_count / self.baseline_prompt.word_count - 1) * 100
            }
        
        # Score progression
        for iteration in sorted(self.evaluation_data.keys()):
            eval_data = self.evaluation_data[iteration]
            summary['score_progression'][iteration] = eval_data['scores']
        
        # Generate key insights
        summary['key_insights'] = self._generate_insights(metrics, patterns)
        
        return summary
    
    def _generate_insights(self, metrics: EvolutionMetrics, patterns: Dict[str, Any]) -> List[str]:
        """Generate key insights from the analysis"""
        insights = []
        
        # Success rate insights
        if metrics.successful_changes > metrics.failed_changes:
            insights.append(f"Evolution was generally successful with {metrics.successful_changes} positive iterations vs {metrics.failed_changes} negative")
        else:
            insights.append(f"Evolution showed mixed results with {metrics.failed_changes} negative iterations vs {metrics.successful_changes} positive")
        
        # Most changed sections
        top_sections = sorted(patterns['section_changes'].items(), key=lambda x: x[1], reverse=True)[:3]
        if top_sections:
            section_names = [section for section, count in top_sections]
            insights.append(f"Most frequently modified sections: {', '.join(section_names)}")
        
        # Change type patterns
        top_change_types = sorted(patterns['change_types'].items(), key=lambda x: x[1], reverse=True)
        if top_change_types:
            insights.append(f"Primary change type: {top_change_types[0][0]} ({top_change_types[0][1]} occurrences)")
        
        # Successful patterns
        if patterns['successful_change_types']:
            successful_patterns = sorted(patterns['successful_change_types'].items(), 
                                       key=lambda x: len(x[1]), reverse=True)[:2]
            pattern_names = [pattern for pattern, scores in successful_patterns]
            insights.append(f"Most successful change patterns: {', '.join(pattern_names)}")
        
        # Common additions that worked
        if patterns['common_additions']:
            top_additions = [phrase for phrase, count in patterns['common_additions'].most_common(3)]
            insights.append(f"Most common successful additions: {', '.join(top_additions)}")
        
        return insights