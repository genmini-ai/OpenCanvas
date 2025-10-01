#!/usr/bin/env python3
"""
Visual Adversarial Attack Generator

Generates adversarial versions of presentations using Claude
to test visual evaluation prompt robustness.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from opencanvas.config import Config
from opencanvas.conversion.html_to_pdf import PresentationConverter
from visual_adversarial_prompts import VISUAL_ATTACK_PROMPTS, get_all_attack_types

# Import Claude client
try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualAdversarialGenerator:
    """Generates visual adversarial attacks using Claude"""
    
    def __init__(self, source_evolution_dir: str, output_dir: str = "test_output/visual_adversarial_testing"):
        """
        Initialize the generator
        
        Args:
            source_evolution_dir: Path to evolution run directory with HTML slides
            output_dir: Where to save adversarial versions
        """
        self.source_dir = Path(source_evolution_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize Claude client
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        # Create output structure
        self._setup_output_dirs()
        
    def _setup_output_dirs(self):
        """Create output directory structure"""
        dirs = [
            self.output_dir / "original_slides",
            self.output_dir / "adversarial_attacks",
            self.output_dir / "pdf_conversions" / "original",
            self.output_dir / "pdf_conversions" / "adversarial",
            self.output_dir / "evaluation_results",
            self.output_dir / "logs"
        ]
        
        # Create adversarial attack subdirs
        for attack_type in get_all_attack_types():
            dirs.append(self.output_dir / "adversarial_attacks" / attack_type)
            dirs.append(self.output_dir / "pdf_conversions" / "adversarial" / attack_type)
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def find_source_slides(self) -> List[Tuple[str, Path]]:
        """
        Find all HTML slides in the source evolution directory
        
        Returns:
            List of (identifier, path) tuples
        """
        slides = []
        
        # Look for iteration_5 first (most evolved), then others
        iteration_dirs = sorted([d for d in self.source_dir.glob("evolution/iteration_*") if d.is_dir()], reverse=True)
        
        if not iteration_dirs:
            logger.warning(f"No iteration directories found in {self.source_dir}")
            return slides
            
        # Use the latest iteration
        latest_iteration = iteration_dirs[0]
        logger.info(f"Using slides from {latest_iteration.name}")
        
        # Find all HTML files
        for html_file in latest_iteration.rglob("*.html"):
            # Skip non-slide files
            if "index" in html_file.name.lower():
                continue
                
            # Create identifier from path
            relative_path = html_file.relative_to(latest_iteration)
            identifier = str(relative_path).replace("/", "_").replace("\\", "_").replace(".html", "")
            
            slides.append((identifier, html_file))
            
        logger.info(f"Found {len(slides)} HTML slides")
        return slides
        
    def copy_original_slides(self, slides: List[Tuple[str, Path]]) -> Dict[str, Path]:
        """
        Copy original slides to output directory
        
        Returns:
            Mapping of identifier to copied path
        """
        copied = {}
        
        for identifier, source_path in slides:
            dest_path = self.output_dir / "original_slides" / f"{identifier}.html"
            shutil.copy2(source_path, dest_path)
            copied[identifier] = dest_path
            logger.info(f"Copied {identifier} to original_slides/")
            
        return copied
        
    def apply_claude_attack(self, html_content: str, attack_type: str) -> str:
        """
        Use Claude to apply an adversarial attack to HTML
        
        Args:
            html_content: Original HTML content
            attack_type: Type of attack to apply
            
        Returns:
            Modified HTML content
        """
        attack_info = VISUAL_ATTACK_PROMPTS[attack_type]
        
        logger.info(f"Applying {attack_info['name']} using Claude...")
        logger.info(f"📡 Using streaming for {attack_info['name']}...")
        
        try:
            stream = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=50000,  # Match original generators for complete HTML
                temperature=0.3,
                stream=True,  # Enable streaming for large responses
                system="You are an expert at modifying HTML presentations for testing purposes. Follow the instructions exactly to create adversarial examples.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{attack_info['prompt']}\n\nHere is the HTML to modify:\n\n{html_content}"
                    }
                ]
            )
            
            # Collect the streamed response
            modified_html = ""
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    modified_html += chunk.delta.text
                    # Log progress every 1000 characters
                    if len(modified_html) % 1000 == 0:
                        logger.info(f"  📝 Generated {len(modified_html)} characters...")
            
            logger.info(f"  ✅ Completed {attack_type}: {len(modified_html)} characters")
            
            # Basic validation that we got HTML back
            if "<html" not in modified_html.lower() or "<body" not in modified_html.lower():
                logger.error(f"Claude response doesn't appear to be valid HTML for {attack_type}")
                return html_content  # Return original if attack failed
                
            return modified_html
            
        except Exception as e:
            logger.error(f"Error applying {attack_type} attack: {e}")
            return html_content  # Return original if attack failed
            
    def generate_all_attacks(self, slides: Dict[str, Path]) -> Dict[str, Dict[str, Path]]:
        """
        Generate all attack types for all slides
        
        Returns:
            Nested dict: {attack_type: {slide_id: path}}
        """
        results = {}
        
        for attack_type in get_all_attack_types():
            logger.info(f"\nGenerating {attack_type} attacks...")
            results[attack_type] = {}
            
            for slide_id, original_path in slides.items():
                # Read original HTML
                with open(original_path, 'r', encoding='utf-8') as f:
                    original_html = f.read()
                    
                # Apply attack
                attacked_html = self.apply_claude_attack(original_html, attack_type)
                
                # Save attacked version
                output_path = self.output_dir / "adversarial_attacks" / attack_type / f"{slide_id}.html"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(attacked_html)
                    
                results[attack_type][slide_id] = output_path
                logger.info(f"  Generated {attack_type} attack for {slide_id}")
                
        return results
        
    def convert_to_pdfs(self, original_slides: Dict[str, Path], 
                       attacked_slides: Dict[str, Dict[str, Path]]) -> Dict[str, Dict[str, Path]]:
        """
        Convert all HTML files to PDFs for evaluation
        
        Returns:
            Nested dict of PDF paths
        """
        pdf_paths = {"original": {}}
        
        # Convert original slides
        logger.info("\nConverting original slides to PDF...")
        for slide_id, html_path in original_slides.items():
            pdf_path = self.output_dir / "pdf_conversions" / "original" / f"{slide_id}.pdf"
            try:
                converter = PresentationConverter(
                    html_file=str(html_path),
                    output_dir=str(pdf_path.parent),
                    zoom_factor=1.0  # No zoom to preserve original sizing
                )
                converter.convert(output_filename=pdf_path.name)
                pdf_paths["original"][slide_id] = pdf_path
                logger.info(f"  Converted {slide_id} to PDF")
            except Exception as e:
                logger.error(f"  Failed to convert {slide_id}: {e}")
                
        # Convert attacked slides
        for attack_type, slides in attacked_slides.items():
            logger.info(f"\nConverting {attack_type} attacks to PDF...")
            pdf_paths[attack_type] = {}
            
            for slide_id, html_path in slides.items():
                pdf_path = self.output_dir / "pdf_conversions" / "adversarial" / attack_type / f"{slide_id}.pdf"
                try:
                    converter = PresentationConverter(
                        html_file=str(html_path),
                        output_dir=str(pdf_path.parent),
                        zoom_factor=1.0  # No zoom to preserve original sizing
                    )
                    converter.convert(output_filename=pdf_path.name)
                    pdf_paths[attack_type][slide_id] = pdf_path
                    logger.info(f"  Converted {slide_id} to PDF")
                except Exception as e:
                    logger.error(f"  Failed to convert {slide_id}: {e}")
                    
        return pdf_paths
        
    def save_metadata(self, original_slides: Dict[str, Path], 
                     attacked_slides: Dict[str, Dict[str, Path]],
                     pdf_paths: Dict[str, Dict[str, Path]]):
        """Save metadata about the generation run"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "output_directory": str(self.output_dir),
            "original_slides": {k: str(v) for k, v in original_slides.items()},
            "attacked_slides": {
                attack: {k: str(v) for k, v in slides.items()}
                for attack, slides in attacked_slides.items()
            },
            "pdf_paths": {
                category: {k: str(v) for k, v in paths.items()}
                for category, paths in pdf_paths.items()
            },
            "attack_types": get_all_attack_types()
        }
        
        metadata_path = self.output_dir / "generation_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"\nSaved metadata to {metadata_path}")
        
    def run(self):
        """Execute the full generation pipeline"""
        logger.info("="*60)
        logger.info("Visual Adversarial Attack Generation")
        logger.info("="*60)
        
        # Find source slides
        source_slides = self.find_source_slides()
        if not source_slides:
            logger.error("No source slides found!")
            return
            
        # Copy originals
        logger.info("\nCopying original slides...")
        original_slides = self.copy_original_slides(source_slides)
        
        # Generate attacks
        logger.info("\nGenerating adversarial attacks...")
        attacked_slides = self.generate_all_attacks(original_slides)
        
        # Convert to PDFs
        logger.info("\nConverting to PDFs for evaluation...")
        pdf_paths = self.convert_to_pdfs(original_slides, attacked_slides)
        
        # Save metadata
        self.save_metadata(original_slides, attacked_slides, pdf_paths)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("Generation Complete!")
        logger.info(f"Original slides: {len(original_slides)}")
        logger.info(f"Attack types: {len(attacked_slides)}")
        logger.info(f"Total adversarial slides: {sum(len(s) for s in attacked_slides.values())}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*60)
        

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate visual adversarial attacks for presentations")
    parser.add_argument(
        "--source",
        default="/Users/christineh./Downloads/slidebee/OpenCanvas/evolution_runs/pdf_tracked_evolution_20250826_102641",
        help="Path to evolution run directory with source slides"
    )
    parser.add_argument(
        "--output",
        default="test_output/visual_adversarial_testing",
        help="Output directory for adversarial attacks"
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF conversion (faster for testing)"
    )
    
    args = parser.parse_args()
    
    # Create and run generator
    generator = VisualAdversarialGenerator(args.source, args.output)
    generator.run()
    

if __name__ == "__main__":
    main()