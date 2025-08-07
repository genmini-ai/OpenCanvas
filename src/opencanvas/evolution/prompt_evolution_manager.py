"""
Prompt Evolution Manager - Manages evolution of generation prompts across iterations
"""

import json
from opencanvas.evolution.prompts.evolution_prompts import EvolutionPrompts
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class PromptEvolutionManager:
    """
    Manages evolution of generation prompts with versioning and rollback capabilities
    Similar to training checkpoints - each iteration gets its own folder
    """
    
    def __init__(self, evolution_base_dir: str = "evolution_prompts"):
        """Initialize prompt evolution manager"""
        self.evolution_base_dir = Path(evolution_base_dir)
        self.evolution_base_dir.mkdir(exist_ok=True)
        
        # Current active iteration
        self.current_iteration = self._get_latest_iteration()
        
        # Prompt categories that can evolve
        self.prompt_categories = [
            "topic_generation",
            "pdf_generation", 
            "visual_enhancement",
            "content_validation",
            "quality_control"
        ]
    
    def create_evolution_iteration(self, iteration_number: int, 
                                 improvements: List[Dict[str, Any]], 
                                 baseline_scores: Dict[str, float]) -> str:
        """
        Create a new evolution iteration with enhanced prompts
        
        Args:
            iteration_number: Iteration number (e.g., 1, 2, 3...)
            improvements: List of improvements to implement
            baseline_scores: Current performance baseline
            
        Returns:
            Path to the created iteration directory
        """
        
        iteration_dir = self.evolution_base_dir / f"iteration_{iteration_number:03d}"
        iteration_dir.mkdir(exist_ok=True)
        
        logger.info(f"🚀 Creating evolution iteration {iteration_number}")
        logger.info(f"📁 Directory: {iteration_dir}")
        
        # Copy baseline prompts from previous iteration or original
        if iteration_number == 1:
            self._initialize_baseline_prompts(iteration_dir)
        else:
            self._copy_from_previous_iteration(iteration_dir, iteration_number - 1)
        
        # Generate evolved prompts based on improvements
        evolved_prompts = self._generate_evolved_prompts(improvements, baseline_scores)
        
        # Save evolved prompts to iteration directory
        self._save_evolved_prompts(iteration_dir, evolved_prompts)
        
        # Create iteration metadata
        self._create_iteration_metadata(iteration_dir, iteration_number, improvements, baseline_scores)
        
        # Create prompt comparison report
        self._create_prompt_comparison_report(iteration_dir, iteration_number)
        
        self.current_iteration = iteration_number
        
        logger.info(f"✅ Evolution iteration {iteration_number} created successfully")
        
        return str(iteration_dir)
    
    def get_current_prompts(self, iteration: Optional[int] = None) -> Dict[str, str]:
        """
        Get prompts for a specific iteration (or current if not specified)
        
        Args:
            iteration: Specific iteration number, or None for current
            
        Returns:
            Dictionary of prompt category -> prompt text
        """
        
        if iteration is None:
            iteration = self.current_iteration
        
        iteration_dir = self.evolution_base_dir / f"iteration_{iteration:03d}"
        
        if not iteration_dir.exists():
            logger.error(f"Iteration {iteration} not found")
            return {}
        
        prompts = {}
        
        for category in self.prompt_categories:
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts[category] = f.read()
        
        return prompts
    
    def _get_latest_iteration(self) -> int:
        """Get the latest iteration number"""
        
        iteration_dirs = [d for d in self.evolution_base_dir.iterdir() 
                         if d.is_dir() and d.name.startswith("iteration_")]
        
        if not iteration_dirs:
            return 0
        
        # Extract iteration numbers and find max
        iteration_numbers = []
        for dir_name in iteration_dirs:
            try:
                num = int(dir_name.name.split("_")[1])
                iteration_numbers.append(num)
            except (IndexError, ValueError):
                continue
        
        return max(iteration_numbers) if iteration_numbers else 0
    
    def _initialize_baseline_prompts(self, iteration_dir: Path):
        """Initialize baseline prompts for iteration 1"""
        
        logger.info("📝 Initializing baseline prompts...")
        
        # Define baseline prompts (simplified versions of current system)
        baseline_prompts = {
            "topic_generation": """You are an expert presentation generator. Create a comprehensive HTML presentation based on the given topic.

TOPIC: {topic}
PURPOSE: {purpose}
THEME: {theme}

Requirements:
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Include relevant information and examples
- Ensure good visual hierarchy
- Make content engaging and informative

Generate complete HTML presentation.""",

            "pdf_generation": """You are an expert presentation generator. Create a comprehensive HTML presentation based on the provided PDF content.

PDF CONTENT: {pdf_content}
PURPOSE: {purpose}
THEME: {theme}

Requirements:
- Extract key information from the PDF content
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Maintain accuracy to source material
- Ensure good visual hierarchy
- Include all essential findings and methodology

Generate complete HTML presentation based on the PDF content.""",

            "visual_enhancement": """Enhance the visual quality of presentations by ensuring:
- Clear, readable fonts and proper sizing
- Consistent color scheme and design
- Good contrast for readability
- Proper spacing and alignment
- Professional appearance""",

            "content_validation": """Validate presentation content for:
- Factual accuracy and consistency
- Completeness of key information
- Logical flow and structure
- Appropriate depth for audience
- Clear and engaging narrative""",

            "quality_control": """Quality control checklist:
- All text is readable and properly sized
- Visual elements support the content
- No spelling or grammar errors
- Consistent formatting throughout
- Professional and polished appearance"""
        }
        
        # Save baseline prompts
        for category, prompt in baseline_prompts.items():
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
        
        logger.info(f"✅ Initialized {len(baseline_prompts)} baseline prompts")
    
    def _copy_from_previous_iteration(self, iteration_dir: Path, previous_iteration: int):
        """Copy prompts from previous iteration as starting point"""
        
        previous_dir = self.evolution_base_dir / f"iteration_{previous_iteration:03d}"
        
        if not previous_dir.exists():
            logger.error(f"Previous iteration {previous_iteration} not found")
            return
        
        logger.info(f"📋 Copying prompts from iteration {previous_iteration}")
        
        # Copy all prompt files
        for category in self.prompt_categories:
            previous_prompt_file = previous_dir / f"{category}_prompt.txt"
            if previous_prompt_file.exists():
                new_prompt_file = iteration_dir / f"{category}_prompt.txt"
                shutil.copy2(previous_prompt_file, new_prompt_file)
        
        logger.info("✅ Copied prompts from previous iteration")
    
    def _generate_evolved_prompts(self, improvements: List[Dict[str, Any]], 
                                baseline_scores: Dict[str, float]) -> Dict[str, str]:
        """Generate evolved prompts based on identified improvements"""
        
        logger.info(f"🧬 Generating evolved prompts for {len(improvements)} improvements...")
        
        evolved_prompts = {}
        
        # Group improvements by target category
        improvements_by_category = self._group_improvements_by_category(improvements)
        
        for category, category_improvements in improvements_by_category.items():
            if category_improvements:
                evolved_prompt = self._evolve_category_prompt(category, category_improvements, baseline_scores)
                evolved_prompts[category] = evolved_prompt
        
        return evolved_prompts
    
    def _group_improvements_by_category(self, improvements: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group improvements by prompt category they should affect"""
        
        grouped = {category: [] for category in self.prompt_categories}
        
        for improvement in improvements:
            # Determine which prompt categories this improvement should affect
            target_dimensions = improvement.get('target_dimensions', [])
            improvement_type = improvement.get('category', 'general')
            
            # Map improvement types to prompt categories
            if 'visual' in str(target_dimensions).lower() or improvement_type == 'visual':
                grouped['visual_enhancement'].append(improvement)
                # Visual improvements also affect main generation prompts
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            
            if 'content' in str(target_dimensions).lower() or improvement_type == 'content':
                grouped['content_validation'].append(improvement)
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            
            if 'accuracy' in str(target_dimensions).lower() or improvement_type == 'accuracy':
                grouped['quality_control'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            
            # If no specific mapping, apply to main generation prompts
            if not any(grouped.values()):
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
        
        return grouped
    
    def _evolve_category_prompt(self, category: str, improvements: List[Dict[str, Any]], 
                              baseline_scores: Dict[str, float]) -> str:
        """Evolve a specific prompt category based on improvements"""
        
        logger.info(f"  🔧 Evolving {category} prompt with {len(improvements)} improvements")
        
        if category == "topic_generation":
            return self._evolve_topic_generation_prompt(improvements, baseline_scores)
        elif category == "pdf_generation":
            return self._evolve_pdf_generation_prompt(improvements, baseline_scores)
        elif category == "visual_enhancement":
            return self._evolve_visual_enhancement_prompt(improvements, baseline_scores)
        elif category == "content_validation":
            return self._evolve_content_validation_prompt(improvements, baseline_scores)
        elif category == "quality_control":
            return self._evolve_quality_control_prompt(improvements, baseline_scores)
        else:
            logger.warning(f"Unknown prompt category: {category}")
            return ""
    
    def _evolve_topic_generation_prompt(self, improvements: List[Dict[str, Any]], 
                                      baseline_scores: Dict[str, float]) -> str:
        """Evolve the topic generation prompt"""
        
        # Base prompt structure
        base_prompt = EvolutionPrompts.get_prompt(
            'TOPIC_GENERATION_BASE',
            topic='{topic}',
            purpose='{purpose}',
            theme='{theme}'
        )
        
        # Add evolution improvements
        evolution_sections = []
        
        # Visual improvements
        visual_improvements = [imp for imp in improvements if 'visual' in str(imp.get('target_dimensions', [])).lower()]
        if visual_improvements:
            evolution_sections.append("""
ENHANCED VISUAL REQUIREMENTS:
- All charts MUST have clearly labeled axes with readable font sizes (minimum 14pt)
- No visual elements should be cropped or incomplete
- Every visual element must directly support the content
- Maintain consistent color scheme and professional design
- Ensure perfect readability for presentation viewing""")
        
        # Content accuracy improvements
        accuracy_improvements = [imp for imp in improvements if 'accuracy' in str(imp.get('target_dimensions', [])).lower()]
        if accuracy_improvements:
            evolution_sections.append("""
ENHANCED ACCURACY REQUIREMENTS:
- NEVER create fake author names or fabricated citations
- Use generic attributions like "Recent research shows..." instead of specific fake names
- Only create data visualizations using plausible, realistic data
- Ensure all claims are reasonable and fact-checkable
- Include appropriate disclaimers for uncertain information""")
        
        # Content completeness improvements
        coverage_improvements = [imp for imp in improvements if 'coverage' in str(imp.get('target_dimensions', [])).lower()]
        if coverage_improvements:
            evolution_sections.append("""
ENHANCED COMPLETENESS REQUIREMENTS:
- Include comprehensive coverage of the topic
- Address both benefits AND limitations/challenges
- Provide sufficient context and background information
- Ensure logical flow from introduction to conclusion
- Include practical examples and applications where relevant""")
        
        # Build final prompt
        final_prompt = base_prompt
        for section in evolution_sections:
            final_prompt += section
        
        final_prompt += """

CORE REQUIREMENTS:
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Ensure excellent visual hierarchy and readability
- Make content engaging, accurate, and comprehensive
- Apply all enhanced quality requirements above

Generate complete HTML presentation that meets these evolved standards."""
        
        return final_prompt
    
    def _evolve_pdf_generation_prompt(self, improvements: List[Dict[str, Any]], 
                                    baseline_scores: Dict[str, float]) -> str:
        """Evolve the PDF generation prompt"""
        
        base_prompt = EvolutionPrompts.get_prompt(
            'TOPIC_GENERATION_BASE',
            topic='{topic}',
            purpose='{purpose}',
            theme='{theme}'
        )
        
        # Add source fidelity enhancements
        evolution_sections = []
        
        accuracy_improvements = [imp for imp in improvements if 'accuracy' in str(imp.get('target_dimensions', [])).lower()]
        if accuracy_improvements:
            evolution_sections.append("""
ENHANCED SOURCE FIDELITY REQUIREMENTS:
- Maintain STRICT accuracy to the source PDF content
- Only create visualizations using data explicitly provided in the source
- NEVER add unsupported statistics or claims not in the source
- Preserve all numerical values, percentages, and technical specifications exactly
- Include all essential methodological details and findings from the source""")
        
        coverage_improvements = [imp for imp in improvements if 'coverage' in str(imp.get('target_dimensions', [])).lower()]
        if coverage_improvements:
            evolution_sections.append("""
ENHANCED COVERAGE REQUIREMENTS:
- Include ALL key findings and conclusions from the source
- Cover both main results AND limitations/challenges mentioned
- Preserve the original context and significance
- Include appropriate methodological background
- Maintain the balance of coverage as presented in the source""")
        
        final_prompt = base_prompt
        for section in evolution_sections:
            final_prompt += section
        
        final_prompt += """

CORE REQUIREMENTS:
- Extract and organize key information maintaining complete accuracy
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Ensure all content is faithful to the source material
- Apply enhanced visual and accuracy standards

Generate complete HTML presentation with perfect source fidelity."""
        
        return final_prompt
    
    def _evolve_visual_enhancement_prompt(self, improvements: List[Dict[str, Any]], 
                                        baseline_scores: Dict[str, float]) -> str:
        """Evolve the visual enhancement prompt"""
        
        enhancements = []
        
        for improvement in improvements:
            if 'chart' in improvement.get('description', '').lower():
                enhancements.append("- Ensure all charts have complete, readable axes with proper scaling")
            if 'readability' in improvement.get('description', '').lower():
                enhancements.append("- Optimize font sizes for presentation viewing (minimum 14pt)")
            if 'balance' in improvement.get('description', '').lower():
                enhancements.append("- Perfect integration between visual elements and text content")
            if 'design' in improvement.get('description', '').lower():
                enhancements.append("- Maintain consistent professional design throughout")
        
        return f"""Enhanced visual quality standards based on identified improvements:

{chr(10).join(enhancements)}

Apply these enhancements to ensure presentations meet elevated visual standards."""
    
    def _evolve_content_validation_prompt(self, improvements: List[Dict[str, Any]], 
                                        baseline_scores: Dict[str, float]) -> str:
        """Evolve the content validation prompt"""
        
        validations = []
        
        for improvement in improvements:
            if 'accuracy' in improvement.get('description', '').lower():
                validations.append("- Verify all factual claims for plausibility and consistency")
            if 'completeness' in improvement.get('description', '').lower():
                validations.append("- Ensure comprehensive coverage of essential information")
            if 'structure' in improvement.get('description', '').lower():
                validations.append("- Validate logical flow and narrative coherence")
        
        return f"""Enhanced content validation standards:

{chr(10).join(validations)}

Apply these validation criteria to ensure content meets elevated quality standards."""
    
    def _evolve_quality_control_prompt(self, improvements: List[Dict[str, Any]], 
                                     baseline_scores: Dict[str, float]) -> str:
        """Evolve the quality control prompt"""
        
        controls = []
        
        for improvement in improvements:
            controls.append(f"- {improvement.get('description', 'Quality improvement')}")
        
        return f"""Enhanced quality control checklist based on identified improvements:

{chr(10).join(controls)}

Ensure all presentations meet these enhanced quality standards before finalization."""
    
    def _save_evolved_prompts(self, iteration_dir: Path, evolved_prompts: Dict[str, str]):
        """Save evolved prompts to the iteration directory"""
        
        logger.info(f"💾 Saving {len(evolved_prompts)} evolved prompts...")
        
        for category, prompt in evolved_prompts.items():
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
        
        logger.info("✅ Evolved prompts saved")
    
    def _create_iteration_metadata(self, iteration_dir: Path, iteration_number: int,
                                 improvements: List[Dict[str, Any]], baseline_scores: Dict[str, float]):
        """Create metadata file for the iteration"""
        
        metadata = {
            "iteration_number": iteration_number,
            "created_timestamp": datetime.now().isoformat(),
            "baseline_scores": baseline_scores,
            "improvements_applied": [
                {
                    "name": imp.get('name', 'Unnamed'),
                    "description": imp.get('description', ''),
                    "target_dimensions": imp.get('target_dimensions', []),
                    "expected_impact": imp.get('expected_impact', ''),
                    "priority": imp.get('priority', 'medium')
                }
                for imp in improvements
            ],
            "prompt_categories_evolved": list(self.prompt_categories),
            "total_improvements": len(improvements)
        }
        
        metadata_file = iteration_dir / "iteration_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("📋 Iteration metadata created")
    
    def _create_prompt_comparison_report(self, iteration_dir: Path, iteration_number: int):
        """Create a report comparing prompts with previous iteration"""
        
        if iteration_number == 1:
            return  # No previous iteration to compare
        
        previous_dir = self.evolution_base_dir / f"iteration_{iteration_number-1:03d}"
        if not previous_dir.exists():
            return
        
        logger.info(f"📊 Creating prompt comparison report...")
        
        comparison_report = {
            "comparison_timestamp": datetime.now().isoformat(),
            "current_iteration": iteration_number,
            "previous_iteration": iteration_number - 1,
            "changes_by_category": {}
        }
        
        for category in self.prompt_categories:
            current_file = iteration_dir / f"{category}_prompt.txt"
            previous_file = previous_dir / f"{category}_prompt.txt"
            
            if current_file.exists() and previous_file.exists():
                with open(current_file, 'r', encoding='utf-8') as f:
                    current_prompt = f.read()
                with open(previous_file, 'r', encoding='utf-8') as f:
                    previous_prompt = f.read()
                
                # Simple change detection
                changed = current_prompt != previous_prompt
                size_change = len(current_prompt) - len(previous_prompt)
                
                comparison_report["changes_by_category"][category] = {
                    "changed": changed,
                    "size_change_chars": size_change,
                    "current_size": len(current_prompt),
                    "previous_size": len(previous_prompt)
                }
        
        comparison_file = iteration_dir / "prompt_comparison_report.json"
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, indent=2)
        
        logger.info("📊 Prompt comparison report created")
    
    def get_evolution_history(self) -> Dict[str, Any]:
        """Get complete evolution history"""
        
        history = {
            "total_iterations": self.current_iteration,
            "evolution_base_dir": str(self.evolution_base_dir),
            "iterations": []
        }
        
        for i in range(1, self.current_iteration + 1):
            iteration_dir = self.evolution_base_dir / f"iteration_{i:03d}"
            metadata_file = iteration_dir / "iteration_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    iteration_metadata = json.load(f)
                    history["iterations"].append(iteration_metadata)
        
        return history
    
    def rollback_to_iteration(self, iteration_number: int) -> bool:
        """Rollback to a specific iteration"""
        
        target_dir = self.evolution_base_dir / f"iteration_{iteration_number:03d}"
        
        if not target_dir.exists():
            logger.error(f"Cannot rollback to iteration {iteration_number} - not found")
            return False
        
        logger.info(f"🔄 Rolling back to iteration {iteration_number}")
        
        self.current_iteration = iteration_number
        
        logger.info(f"✅ Rolled back to iteration {iteration_number}")
        return True
    
    def create_prompt_usage_guide(self, iteration_dir: Path):
        """Create a guide for how to use the evolved prompts"""
        
        guide_content = f"""# Prompt Evolution Guide - Iteration {self.current_iteration}

## How to Use These Evolved Prompts

### Integration with Generation System

```python
from opencanvas.evolution.prompt_evolution_manager import PromptEvolutionManager

# Initialize manager
prompt_manager = PromptEvolutionManager()

# Get current evolved prompts
current_prompts = prompt_manager.get_current_prompts()

# Use in generation
topic_prompt = current_prompts['topic_generation']
enhanced_prompt = topic_prompt.format(
    topic="Your topic here",
    purpose="presentation purpose", 
    theme="visual theme"
)
```

### Prompt Categories Available

{chr(10).join(f"- **{category}**: {category.replace('_', ' ').title()} prompt" for category in self.prompt_categories)}

### Evolution History

This iteration includes improvements targeting:
- Visual quality enhancements
- Content accuracy improvements  
- Source fidelity requirements
- Completeness validation

### Testing and Validation

1. Generate presentations using these evolved prompts
2. Compare quality against previous iteration
3. Validate improvements with human evaluation
4. Rollback if quality decreases

### Next Steps

1. Deploy these prompts in the generation system
2. Run A/B tests against previous iteration
3. Collect user feedback on generated presentations
4. Plan next evolution iteration based on results
"""
        
        guide_file = iteration_dir / "USAGE_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        logger.info("📖 Prompt usage guide created")