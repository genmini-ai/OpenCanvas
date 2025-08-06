"""
Prompt Evolution Management - Simplified prompt versioning and management
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Simplified prompt evolution manager with versioning capabilities
    """
    
    def __init__(self, evolution_dir: str = "evolution_prompts"):
        """Initialize prompt manager"""
        self.evolution_dir = Path(evolution_dir)
        self.evolution_dir.mkdir(exist_ok=True)
        self.current_iteration = self._get_latest_iteration()
        
        # Standard prompt categories
        self.prompt_categories = [
            "topic_generation",
            "pdf_generation",
            "visual_enhancement", 
            "content_validation",
            "quality_control"
        ]
    
    def create_iteration(self, iteration_number: int, improvements: List[Dict[str, Any]], 
                        baseline_scores: Dict[str, float]) -> str:
        """Create new iteration with evolved prompts"""
        
        iteration_dir = self.evolution_dir / f"iteration_{iteration_number:03d}"
        iteration_dir.mkdir(exist_ok=True)
        
        logger.info(f"🧬 Creating prompt evolution iteration {iteration_number}")
        
        # Copy baseline prompts or previous iteration
        if iteration_number == 1:
            self._create_baseline_prompts(iteration_dir)
        else:
            self._copy_previous_iteration(iteration_dir, iteration_number - 1)
        
        # Apply improvements to prompts
        evolved_prompts = self._evolve_prompts(improvements, baseline_scores)
        self._save_evolved_prompts(iteration_dir, evolved_prompts)
        
        # Create metadata
        self._create_metadata(iteration_dir, iteration_number, improvements, baseline_scores)
        
        self.current_iteration = iteration_number
        
        logger.info(f"✅ Iteration {iteration_number} created: {iteration_dir}")
        return str(iteration_dir)
    
    def get_prompts(self, iteration: Optional[int] = None) -> Dict[str, str]:
        """Get prompts for specific iteration"""
        
        if iteration is None:
            iteration = self.current_iteration
        
        iteration_dir = self.evolution_dir / f"iteration_{iteration:03d}"
        if not iteration_dir.exists():
            logger.warning(f"Iteration {iteration} not found, using baseline")
            return self._get_baseline_prompts()
        
        prompts = {}
        for category in self.prompt_categories:
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts[category] = f.read()
        
        return prompts
    
    def _get_latest_iteration(self) -> int:
        """Get the latest iteration number"""
        
        iteration_dirs = [d for d in self.evolution_dir.iterdir() 
                         if d.is_dir() and d.name.startswith("iteration_")]
        
        if not iteration_dirs:
            return 0
        
        iteration_numbers = []
        for dir_path in iteration_dirs:
            try:
                num = int(dir_path.name.split("_")[1])
                iteration_numbers.append(num)
            except (IndexError, ValueError):
                continue
        
        return max(iteration_numbers) if iteration_numbers else 0
    
    def _create_baseline_prompts(self, iteration_dir: Path):
        """Create baseline prompts for iteration 1"""
        
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
        
        for category, prompt in baseline_prompts.items():
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
        
        logger.info(f"✅ Created baseline prompts")
    
    def _copy_previous_iteration(self, iteration_dir: Path, previous_iteration: int):
        """Copy prompts from previous iteration"""
        
        previous_dir = self.evolution_dir / f"iteration_{previous_iteration:03d}"
        if not previous_dir.exists():
            logger.error(f"Previous iteration {previous_iteration} not found")
            return
        
        for category in self.prompt_categories:
            previous_file = previous_dir / f"{category}_prompt.txt"
            if previous_file.exists():
                new_file = iteration_dir / f"{category}_prompt.txt"
                shutil.copy2(previous_file, new_file)
        
        logger.info(f"📋 Copied prompts from iteration {previous_iteration}")
    
    def _evolve_prompts(self, improvements: List[Dict[str, Any]], 
                       baseline_scores: Dict[str, float]) -> Dict[str, str]:
        """Generate evolved prompts based on improvements"""
        
        evolved_prompts = {}
        
        # Group improvements by category
        improvements_by_category = self._group_improvements(improvements)
        
        for category, category_improvements in improvements_by_category.items():
            if category_improvements:
                evolved_prompt = self._evolve_category_prompt(category, category_improvements, baseline_scores)
                evolved_prompts[category] = evolved_prompt
        
        return evolved_prompts
    
    def _group_improvements(self, improvements: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group improvements by prompt category"""
        
        grouped = {category: [] for category in self.prompt_categories}
        
        for improvement in improvements:
            solution_type = improvement.get('solution_type', 'prompt_enhancement')
            target_weakness = improvement.get('target_weakness', '')
            
            # Map improvements to prompt categories
            if 'visual' in target_weakness.lower():
                grouped['visual_enhancement'].append(improvement) 
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            elif 'content' in target_weakness.lower():
                grouped['content_validation'].append(improvement)
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            elif 'accuracy' in target_weakness.lower():
                grouped['quality_control'].append(improvement)
                grouped['pdf_generation'].append(improvement)
            else:
                # Default to main generation prompts
                grouped['topic_generation'].append(improvement)
                grouped['pdf_generation'].append(improvement)
        
        return grouped
    
    def _evolve_category_prompt(self, category: str, improvements: List[Dict[str, Any]], 
                               baseline_scores: Dict[str, float]) -> str:
        """Evolve a specific prompt category"""
        
        if category == "topic_generation":
            return self._evolve_topic_prompt(improvements, baseline_scores)
        elif category == "pdf_generation":
            return self._evolve_pdf_prompt(improvements, baseline_scores)
        elif category == "visual_enhancement":
            return self._evolve_visual_prompt(improvements)
        elif category == "content_validation":
            return self._evolve_content_prompt(improvements)
        elif category == "quality_control":
            return self._evolve_quality_prompt(improvements)
        else:
            return ""
    
    def _evolve_topic_prompt(self, improvements: List[Dict[str, Any]], 
                            baseline_scores: Dict[str, float]) -> str:
        """Evolve topic generation prompt"""
        
        base_prompt = """You are an expert presentation generator with enhanced quality standards. Create a comprehensive HTML presentation based on the given topic.

TOPIC: {topic}
PURPOSE: {purpose}
THEME: {theme}"""
        
        # Add enhancement sections based on improvements
        enhancements = []
        
        for improvement in improvements:
            description = improvement.get('description', '')
            if 'visual' in description.lower():
                enhancements.append("""
ENHANCED VISUAL REQUIREMENTS:
- All charts MUST have clearly labeled axes with readable font sizes (minimum 14pt)
- No visual elements should be cropped or incomplete
- Every visual element must directly support the content
- Maintain consistent color scheme and professional design""")
            
            if 'accuracy' in description.lower() or 'citation' in description.lower():
                enhancements.append("""
ENHANCED ACCURACY REQUIREMENTS:
- NEVER create fake author names or fabricated citations
- Use generic attributions like "Recent research shows..." instead of specific fake names
- Only create data visualizations using plausible, realistic data
- Ensure all claims are reasonable and fact-checkable""")
            
            if 'completeness' in description.lower():
                enhancements.append("""
ENHANCED COMPLETENESS REQUIREMENTS:
- Include comprehensive coverage of the topic
- Address both benefits AND limitations/challenges
- Provide sufficient context and background information
- Ensure logical flow from introduction to conclusion""")
        
        final_prompt = base_prompt
        for enhancement in enhancements:
            final_prompt += enhancement
        
        final_prompt += """

CORE REQUIREMENTS:
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Ensure excellent visual hierarchy and readability
- Make content engaging, accurate, and comprehensive
- Apply all enhanced quality requirements above

Generate complete HTML presentation that meets these evolved standards."""
        
        return final_prompt
    
    def _evolve_pdf_prompt(self, improvements: List[Dict[str, Any]], 
                          baseline_scores: Dict[str, float]) -> str:
        """Evolve PDF generation prompt"""
        
        base_prompt = """You are an expert presentation generator with enhanced fidelity standards. Create a comprehensive HTML presentation based on the provided PDF content.

PDF CONTENT: {pdf_content}
PURPOSE: {purpose}
THEME: {theme}"""
        
        # Add PDF-specific enhancements
        enhancements = []
        
        for improvement in improvements:
            if 'accuracy' in improvement.get('description', '').lower():
                enhancements.append("""
ENHANCED SOURCE FIDELITY REQUIREMENTS:
- Maintain STRICT accuracy to the source PDF content
- Only create visualizations using data explicitly provided in the source
- NEVER add unsupported statistics or claims not in the source
- Preserve all numerical values, percentages, and technical specifications exactly""")
        
        final_prompt = base_prompt
        for enhancement in enhancements:
            final_prompt += enhancement
        
        final_prompt += """

CORE REQUIREMENTS:
- Extract and organize key information maintaining complete accuracy
- Create 6-8 slides with clear titles and content
- Use proper HTML structure with div class="slide"
- Ensure all content is faithful to the source material
- Apply enhanced visual and accuracy standards

Generate complete HTML presentation with perfect source fidelity."""
        
        return final_prompt
    
    def _evolve_visual_prompt(self, improvements: List[Dict[str, Any]]) -> str:
        """Evolve visual enhancement prompt"""
        
        enhancements = []
        for improvement in improvements:
            description = improvement.get('description', '')
            if 'chart' in description.lower():
                enhancements.append("- Ensure all charts have complete, readable axes with proper scaling")
            if 'readability' in description.lower():
                enhancements.append("- Optimize font sizes for presentation viewing (minimum 14pt)")
            if 'consistency' in description.lower():
                enhancements.append("- Maintain consistent professional design throughout")
        
        return f"""Enhanced visual quality standards based on identified improvements:

{chr(10).join(enhancements)}

Apply these enhancements to ensure presentations meet elevated visual standards."""
    
    def _evolve_content_prompt(self, improvements: List[Dict[str, Any]]) -> str:
        """Evolve content validation prompt"""
        
        validations = []
        for improvement in improvements:
            description = improvement.get('description', '')
            if 'accuracy' in description.lower():
                validations.append("- Verify all factual claims for plausibility and consistency")
            if 'completeness' in description.lower():
                validations.append("- Ensure comprehensive coverage of essential information")
        
        return f"""Enhanced content validation standards:

{chr(10).join(validations)}

Apply these validation criteria to ensure content meets elevated quality standards."""
    
    def _evolve_quality_prompt(self, improvements: List[Dict[str, Any]]) -> str:
        """Evolve quality control prompt"""
        
        controls = []
        for improvement in improvements:
            controls.append(f"- {improvement.get('description', 'Quality improvement')}")
        
        return f"""Enhanced quality control checklist based on identified improvements:

{chr(10).join(controls)}

Ensure all presentations meet these enhanced quality standards before finalization."""
    
    def _save_evolved_prompts(self, iteration_dir: Path, evolved_prompts: Dict[str, str]):
        """Save evolved prompts to iteration directory"""
        
        for category, prompt in evolved_prompts.items():
            prompt_file = iteration_dir / f"{category}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
        
        logger.info(f"💾 Saved {len(evolved_prompts)} evolved prompts")
    
    def _create_metadata(self, iteration_dir: Path, iteration_number: int,
                        improvements: List[Dict[str, Any]], baseline_scores: Dict[str, float]):
        """Create metadata for the iteration"""
        
        metadata = {
            "iteration_number": iteration_number,
            "created_timestamp": datetime.now().isoformat(),
            "baseline_scores": baseline_scores,
            "improvements_applied": [
                {
                    "name": imp.get('name', 'Unnamed'),
                    "description": imp.get('description', ''),
                    "expected_impact": imp.get('expected_impact', {}),
                    "priority": imp.get('priority', 'medium')
                }
                for imp in improvements
            ],
            "prompt_categories": self.prompt_categories,
            "total_improvements": len(improvements)
        }
        
        metadata_file = iteration_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_baseline_prompts(self) -> Dict[str, str]:
        """Get baseline prompts as fallback"""
        
        # Simple baseline prompts
        return {
            "topic_generation": "Create a presentation about {topic} for {purpose} with {theme} theme.",
            "pdf_generation": "Create a presentation from the PDF content: {pdf_content}",
            "visual_enhancement": "Enhance visual quality",
            "content_validation": "Validate content quality",
            "quality_control": "Apply quality control checks"
        }
    
    def get_evolution_history(self) -> Dict[str, Any]:
        """Get complete evolution history"""
        
        history = {
            "total_iterations": self.current_iteration,
            "evolution_dir": str(self.evolution_dir),
            "iterations": []
        }
        
        for i in range(1, self.current_iteration + 1):
            iteration_dir = self.evolution_dir / f"iteration_{i:03d}"
            metadata_file = iteration_dir / "metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    iteration_metadata = json.load(f)
                    history["iterations"].append(iteration_metadata)
        
        return history