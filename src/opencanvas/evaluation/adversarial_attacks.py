"""
Adversarial Attacks for Presentation Evaluation Testing

This module implements various adversarial attacks to test the robustness
of presentation evaluation systems. It helps identify weaknesses in evaluation
prompts and scoring mechanisms.
"""

import re
import random
import os
from typing import List, Tuple, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PresentationAdversarialAttacks:
    """Implements 5 adversarial attacks to test presentation evaluation robustness"""
    
    def __init__(self, html_content: str):
        self.original_html = html_content
        self.slides = self._extract_slides()
    
    def _extract_slides(self) -> List[str]:
        """Extract individual slides with their comments"""
        # Pattern to match slide sections including their comment
        pattern = r'(<!-- Slide \d+:.*?-->.*?)(?=<!-- Slide \d+:|$)'
        slides = re.findall(pattern, self.original_html, re.DOTALL)
        return slides
    
    def _reconstruct_html(self, slides: List[str]) -> str:
        """Reconstruct HTML from modified slides"""
        # Find the slides container
        slides_start = self.original_html.find('<div class="slides">')
        if slides_start == -1:
            # Try alternative patterns
            slides_start = self.original_html.find('<div id="slides">')
            if slides_start == -1:
                slides_start = self.original_html.find('<main')
                if slides_start == -1:
                    # Fallback: just replace the entire body content
                    body_start = self.original_html.find('<body')
                    body_end = self.original_html.find('</body>')
                    if body_start != -1 and body_end != -1:
                        before_body = self.original_html[:body_start]
                        after_body = self.original_html[body_end:]
                        new_body = f'<body>\n<div class="slides">\n{"".join(slides)}\n</div>\n'
                        return before_body + new_body + after_body
        
        slides_end = self.original_html.find('</div>', slides_start)
        if slides_end == -1:
            slides_end = len(self.original_html)
        else:
            slides_end += 6
        
        # Get content before and after slides
        before_slides = self.original_html[:slides_start]
        after_slides = self.original_html[slides_end:]
        
        # Reconstruct with new slides
        new_slides_html = '<div class="slides">\n' + '\n'.join(slides) + '\n        </div>'
        
        return before_slides + new_slides_html + after_slides
    
    def attack_1_beautiful_nonsense(self) -> str:
        """Replace scientific content with surrealist art references"""
        nonsense_replacements = [
            (r'sustainable energy solutions?', 'surrealist dreamscapes'),
            (r'renewable energy', 'melting clock installations'),
            (r'solar panels?', "Dalí's elephant sculptures"),
            (r'photovoltaic \(PV\) technology', 'metamorphosis of Narcissus technique'),
            (r'wind turbines?', "Magritte's floating bowler hats"),
            (r'wind power', 'pipe dream manifestations'),
            (r'hydroelectric power', "Escher's infinite waterfalls"),
            (r'energy access', 'subconscious liberation'),
            (r'electricity', 'liquid persistence'),
            (r'fossil fuels', 'solid reality constraints'),
            (r'climate change', 'temporal distortion'),
            (r'cost decreased by ~?\d+%', 'surrealism increased by 42%'),
            (r'\d+ million people', '∞ dream inhabitants'),
            (r'Bangladesh', 'The Republic of Unconscious'),
            (r'Ethiopia', 'The Floating Islands of Magritte'),
            (r'Nepal', 'The Escherian Principality'),
            (r'converts? sunlight directly into electricity', 'transforms reality into impossible geometries'),
            (r'converts? energy of flowing water', 'channels the flow of liquid time'),
            (r'wind farm', 'bowler hat plantation'),
            (r'micro-hydro plants?', 'miniature paradox generators'),
            (r'sustainable development', 'perpetual impossibility cultivation'),
            (r'capacity building', 'dream architecture construction'),
            (r'technical expertise', 'surrealist interpretation skills'),
            (r'implementation challenges?', 'reality distortion difficulties'),
            (r'[Gg]rid integration', 'consciousness synchronization'),
            (r'energy storage', 'memory liquefaction'),
            (r'financing models?', 'imagination monetization schemes'),
            (r'The Path Forward', 'The Staircase to Nowhere'),
            (r'policy frameworks?', 'absurdity regulations'),
            (r'economic development', 'metaphysical expansion'),
            (r'\\$[\d,]+', '₹∞'),  # Replace dollar amounts with infinity symbol
            (r'\d+\s*[MG]W', '∞ Dalís'),  # Replace power units
            (r'per kWh', 'per dream'),
            # Generic content replacements
            (r'artificial intelligence', 'mechanical consciousness'),
            (r'machine learning', 'algorithmic dreaming'),
            (r'data analysis', 'information metamorphosis'),
            (r'quantum computing', 'probability sculpture'),
            (r'blockchain', 'cryptographic poetry'),
            (r'healthcare', 'wellness surrealism'),
            (r'diagnosis', 'symptom interpretation'),
            (r'treatment', 'healing abstraction'),
        ]
        
        modified_html = self.original_html
        
        # Apply replacements with case-insensitive matching
        for pattern, replacement in nonsense_replacements:
            modified_html = re.sub(pattern, replacement, modified_html, flags=re.IGNORECASE)
        
        return modified_html
    
    def attack_2_fact_flip(self) -> str:
        """Multiple types of factual corruptions"""
        fact_flips = [
            # Numerical inversions
            (r'decreased by (~?\d+%)', r'increased by \1'),
            (r'increased by (~?\d+%)', r'decreased by \1'),
            (r'Cost decreased', 'Cost increased'),
            (r'improved by', 'worsened by'),
            (r'reduced by', 'increased by'),
            
            # Wrong conclusions
            (r'offers a sustainable path', 'proves an unsustainable path'),
            (r'increasingly competitive', 'increasingly uncompetitive'),
            (r'can power inclusive development', 'will hinder inclusive development'),
            (r'shows promise', 'shows failure'),
            (r'effective', 'ineffective'),
            (r'successful', 'unsuccessful'),
            (r'beneficial', 'harmful'),
            (r'positive', 'negative'),
            
            # Unit changes (making numbers 1000x wrong) - handled separately
            (r'(\d+)\s*MW', 'REPLACE_MW'),
            (r'(\d+)\s*GW', 'REPLACE_GW'),
            (r'(\d+)\s*%', 'REPLACE_PERCENT'),
            
            # Price inversions
            (r'\$0\.0(\d)', r'$\1.0'),
            (r'below national average', 'above national average'),
            (r'affordable', 'expensive'),
            (r'cost-effective', 'cost-prohibitive'),
            
            # Country/location swaps
            (r'Bangladesh', 'Belgium'),
            (r'Sub-Saharan Africa', 'Northern Europe'),
            (r'Ethiopia', 'Estonia'),
            (r'Nepal', 'Netherlands'),
            (r'developing countries', 'developed countries'),
            (r'rural areas', 'urban areas'),
            
            # Technology effectiveness inversions
            (r'excellent solar resources', 'poor solar resources'),
            (r'Low operational costs', 'High operational costs'),
            (r'Long operational life', 'Short operational life'),
            (r'high efficiency', 'low efficiency'),
            (r'reliable', 'unreliable'),
            (r'scalable', 'non-scalable'),
            
            # Complete opposite statements
            (r'renewable energy makes sense', 'renewable energy makes no sense'),
            (r'accelerate implementation', 'halt implementation'),
            (r'recommended', 'not recommended'),
            (r'should', 'should not'),
            (r'will', 'will not'),
        ]
        
        modified_html = self.original_html
        
        # Handle special numeric transformations first
        # MW transformations (multiply by 1000)
        def replace_mw(match):
            return f'{int(match.group(1))*1000} MW'
        modified_html = re.sub(r'(\d+)\s*MW', replace_mw, modified_html, flags=re.IGNORECASE)
        
        # GW transformations (divide by 1000 or add decimal)
        def replace_gw(match):
            num = int(match.group(1))
            if num > 1000:
                return f'{num//1000} GW'
            else:
                return f'0.{num} GW'
        modified_html = re.sub(r'(\d+)\s*GW', replace_gw, modified_html, flags=re.IGNORECASE)
        
        # Percentage transformations (invert)
        def replace_percent(match):
            num = int(match.group(1))
            if num <= 100:
                return f'{100-num}%'
            else:
                return f'{num//10}%'
        modified_html = re.sub(r'(\d+)\s*%', replace_percent, modified_html, flags=re.IGNORECASE)
        
        # Apply regular string replacements
        for pattern, replacement in fact_flips:
            if replacement not in ['REPLACE_MW', 'REPLACE_GW', 'REPLACE_PERCENT']:
                modified_html = re.sub(pattern, replacement, modified_html, flags=re.IGNORECASE)
        
        return modified_html
    
    def attack_3_logical_chaos(self) -> str:
        """Randomly shuffle slide order"""
        slides = self.slides.copy()
        
        # Keep first (title) and last (conclusion) slides in place
        if len(slides) > 2:
            first_slide = slides[0]
            last_slide = slides[-1]
            middle_slides = slides[1:-1]
            
            # Shuffle middle slides
            random.shuffle(middle_slides)
            
            # Reconstruct with shuffled order
            shuffled_slides = [first_slide] + middle_slides + [last_slide]
        else:
            shuffled_slides = slides
        
        # Update slide numbers in comments to reflect new order
        updated_slides = []
        for i, slide in enumerate(shuffled_slides, 1):
            # Update the slide number in the comment
            updated_slide = re.sub(
                r'<!-- Slide \d+:',
                f'<!-- Slide {i}:',
                slide
            )
            # Update data-id attribute
            updated_slide = re.sub(
                r'data-id="\d+"',
                f'data-id="{i}"',
                updated_slide
            )
            updated_slides.append(updated_slide)
        
        return self._reconstruct_html(updated_slides)
    
    def attack_4_swiss_cheese(self) -> str:
        """Randomly delete critical content"""
        slides = self.slides.copy()
        
        # Delete 2-3 entire slides (not first or last)
        if len(slides) > 5:
            slides_to_delete = random.sample(range(1, len(slides)-1), min(3, len(slides)-2))
            slides_to_delete.sort(reverse=True)
            for idx in slides_to_delete:
                del slides[idx]
        
        # Delete content from remaining slides
        modified_slides = []
        for slide in slides:
            # Skip title and conclusion slides
            if 'Slide 1:' in slide or 'Path Forward' in slide or 'Conclusion' in slide:
                modified_slides.append(slide)
                continue
            
            modified_slide = slide
            
            # Delete random bullet points (30% chance per bullet)
            bullet_pattern = r'<li>.*?</li>'
            bullets = re.findall(bullet_pattern, modified_slide, re.DOTALL)
            for bullet in bullets:
                if random.random() < 0.3:
                    modified_slide = modified_slide.replace(bullet, '')
            
            # Delete highlight boxes (40% chance)
            if random.random() < 0.4:
                modified_slide = re.sub(
                    r'<div class="highlight-box">.*?</div>',
                    '',
                    modified_slide,
                    flags=re.DOTALL
                )
            
            # Delete entire content boxes (20% chance)
            if random.random() < 0.2:
                modified_slide = re.sub(
                    r'<div class="content-box">.*?</div>',
                    '<div class="content-box"><p>Content unavailable</p></div>',
                    modified_slide,
                    flags=re.DOTALL
                )
            
            # Delete headings (15% chance)
            if random.random() < 0.15:
                modified_slide = re.sub(r'<h[1-6]>.*?</h[1-6]>', '', modified_slide)
            
            modified_slides.append(modified_slide)
        
        return self._reconstruct_html(modified_slides)
    
    def attack_5_gradual_decay(self) -> str:
        """Progressive quality degradation with exponential probability"""
        slides = self.slides.copy()
        modified_slides = []
        
        for i, slide in enumerate(slides):
            # Calculate deletion probability based on position
            # Early: 10%, Middle: 30%, Late: 70%
            position_ratio = i / len(slides) if len(slides) > 1 else 0
            if position_ratio < 0.3:
                deletion_prob = 0.1
            elif position_ratio < 0.7:
                deletion_prob = 0.3
            else:
                deletion_prob = 0.7
            
            modified_slide = slide
            
            # Progressive degradation
            if random.random() < deletion_prob:
                degradation_level = random.choice(['minor', 'moderate', 'major'])
                
                if degradation_level == 'minor':
                    # Delete 1-2 bullet points
                    bullets = re.findall(r'<li>.*?</li>', modified_slide, re.DOTALL)
                    if bullets:
                        num_to_delete = min(2, len(bullets))
                        for bullet in random.sample(bullets, num_to_delete):
                            modified_slide = modified_slide.replace(bullet, '')
                
                elif degradation_level == 'moderate':
                    # Delete entire sections (h3 and following content)
                    sections = re.findall(r'<h3>.*?(?=<h3>|</div>)', modified_slide, re.DOTALL)
                    if sections and len(sections) > 1:
                        section_to_delete = random.choice(sections)
                        modified_slide = modified_slide.replace(section_to_delete, '')
                
                else:  # major
                    # Replace entire content with placeholder
                    modified_slide = re.sub(
                        r'<div class="content-box">.*?</div>',
                        '<div class="content-box"><p style="color: #ff6b6b; font-size: 2em;">CONTENT CORRUPTED</p></div>',
                        modified_slide,
                        flags=re.DOTALL
                    )
            
            modified_slides.append(modified_slide)
        
        return self._reconstruct_html(modified_slides)
    
    def apply_attack(self, attack_type: int) -> str:
        """Apply specified attack type (1-5)"""
        attacks = {
            1: self.attack_1_beautiful_nonsense,
            2: self.attack_2_fact_flip,
            3: self.attack_3_logical_chaos,
            4: self.attack_4_swiss_cheese,
            5: self.attack_5_gradual_decay
        }
        
        if attack_type not in attacks:
            raise ValueError(f"Attack type must be 1-5, got {attack_type}")
        
        logger.info(f"Applying adversarial attack type {attack_type}")
        return attacks[attack_type]()
    
    def get_attack_description(self, attack_type: int) -> str:
        """Get human-readable description of attack type"""
        descriptions = {
            1: "Beautiful Nonsense: Replace scientific content with surrealist art references",
            2: "Fact Flip: Invert factual claims and numerical values",
            3: "Logical Chaos: Randomly shuffle slide order",
            4: "Swiss Cheese: Randomly delete critical content",
            5: "Gradual Decay: Progressive quality degradation"
        }
        return descriptions.get(attack_type, "Unknown attack type")


def apply_adversarial_attack(html_content: str, attack_type: int) -> str:
    """
    Apply adversarial attack to presentation HTML
    
    Args:
        html_content: Original HTML presentation
        attack_type: 1-5 corresponding to:
            1: Beautiful Nonsense (surrealism)
            2: Fact Flip (multiple error types)
            3: Logical Chaos (shuffled slides)
            4: Swiss Cheese (random deletions)
            5: Gradual Decay (progressive degradation)
    
    Returns:
        Modified HTML with attack applied
    """
    attacker = PresentationAdversarialAttacks(html_content)
    return attacker.apply_attack(attack_type)


def generate_all_attacks(html_content: str, output_dir: str = "./adversarial_presentations") -> Dict[int, str]:
    """
    Generate all 5 attack variants for testing
    
    Args:
        html_content: Original HTML presentation
        output_dir: Directory to save attacked presentations
    
    Returns:
        Dictionary mapping attack_type to output file path
    """
    os.makedirs(output_dir, exist_ok=True)
    
    attack_names = {
        1: "beautiful_nonsense",
        2: "fact_flip", 
        3: "logical_chaos",
        4: "swiss_cheese",
        5: "gradual_decay"
    }
    
    output_files = {}
    attacker = PresentationAdversarialAttacks(html_content)
    
    for attack_num, attack_name in attack_names.items():
        try:
            modified_html = attacker.apply_attack(attack_num)
            
            output_path = os.path.join(output_dir, f"presentation_{attack_name}.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_html)
            
            output_files[attack_num] = output_path
            logger.info(f"Generated {attack_name} attack: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate {attack_name} attack: {e}")
    
    return output_files


def load_existing_presentation(file_path: str) -> str:
    """
    Load HTML content from existing presentation file
    
    Args:
        file_path: Path to HTML presentation file
        
    Returns:
        HTML content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load presentation from {file_path}: {e}")
        raise


def find_test_presentations(base_dir: str = "test_output") -> List[str]:
    """
    Find existing presentation HTML files for testing
    
    Args:
        base_dir: Base directory to search for presentations
        
    Returns:
        List of paths to HTML presentation files
    """
    html_files = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        logger.warning(f"Base directory {base_dir} does not exist")
        return html_files
    
    # Search for presentation.html files in the organized structure
    for html_file in base_path.rglob("presentation.html"):
        html_files.append(str(html_file))
    
    # Also search for any other HTML files
    for html_file in base_path.rglob("*.html"):
        if html_file.name != "presentation.html":
            html_files.append(str(html_file))
    
    logger.info(f"Found {len(html_files)} presentation files")
    return html_files 