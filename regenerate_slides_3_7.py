#!/usr/bin/env python3
"""
Regenerate slides 3 and 7 with extracted figures for comparison
Uses existing blueprints and extracts figures from PDF
"""
import sys
import os
sys.path.insert(0, 'src')

import logging
import json
from pathlib import Path
from opencanvas.generators.pdf_generator import PDFGenerator
from opencanvas.generators.image_generator import ImageSlideGenerator

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main():
    print("🧪 Regenerating Slides 3 & 7 with Figures")
    print("="*60)
    
    # Use existing folder
    base_folder = Path('test_output/241206769_20251212_160235')
    sources_folder = base_folder / 'sources'
    slides_folder = base_folder / 'slides'
    
    # Step 1: Extract figures from PDF
    print("\n📥 Step 1: Extracting figures from PDF...")
    pdf_gen = PDFGenerator(os.getenv('ANTHROPIC_API_KEY'))
    pdf_data, error = pdf_gen.encode_pdf_from_url('https://arxiv.org/pdf/2412.06769')
    
    if error:
        print(f"❌ Failed: {error}")
        return 1
    
    image_captions, extracted_images_dir, plots = pdf_gen._extract_images_and_captions(
        pdf_data, base_folder
    )
    
    if not plots:
        print(f"❌ No plots extracted")
        return 1
    
    print(f"✅ Extracted {len(plots)} figures")
    print(f"📁 Saved to: {extracted_images_dir}")
    
    # Step 2: Load blueprints with figure assignments (from the other folder)
    print(f"\n📋 Step 2: Loading blueprints with figure assignments...")
    blueprint_file = Path('test_output/241206769_20251212_152245/sources/slide_blueprints.json')
    
    with open(blueprint_file) as f:
        blueprints = json.load(f)
    
    slide_3 = [bp for bp in blueprints if bp['slide_number'] == 3][0]
    slide_7 = [bp for bp in blueprints if bp['slide_number'] == 7][0]
    
    print(f"   Slide 3: '{slide_3['title']}'")
    print(f"            Figure {slide_3.get('figure_id')} ({slide_3.get('figure_usage')})")
    print(f"   Slide 7: '{slide_7['title']}'")
    print(f"            Figure {slide_7.get('figure_id')} ({slide_7.get('figure_usage')})")
    
    # Step 3: Load existing style settings
    print(f"\n🎨 Step 3: Loading style settings...")
    style_file = sources_folder / 'style_settings.txt'
    with open(style_file) as f:
        style_settings = f.read()
    
    # Step 4: Initialize slide generator
    print(f"\n🖼️  Step 4: Generating slides...")
    slide_gen = ImageSlideGenerator(
        anthropic_key=os.getenv('ANTHROPIC_API_KEY'),
        gemini_key=os.getenv('GEMINI_API_KEY')
    )
    
    # Create comparison folder
    comparison_folder = base_folder / 'comparison'
    comparison_folder.mkdir(exist_ok=True)
    
    # Generate Slide 3 WITH figure
    print(f"\n   Generating Slide 3 WITH figure (Figure {slide_3.get('figure_id')})...")
    slide_3_with_fig = slide_gen._generate_slide_image(
        blueprint=slide_3,
        style_settings=style_settings,
        style_ref=None,
        extracted_figures=plots
    )
    path_3_with = comparison_folder / 'slide_003_WITH_FIGURE.png'
    with open(path_3_with, 'wb') as f:
        f.write(slide_3_with_fig)
    print(f"   ✅ Saved: {path_3_with}")
    
    # Generate Slide 7 WITH figure
    print(f"\n   Generating Slide 7 WITH figure (Figure {slide_7.get('figure_id')})...")
    slide_7_with_fig = slide_gen._generate_slide_image(
        blueprint=slide_7,
        style_settings=style_settings,
        style_ref=None,
        extracted_figures=plots
    )
    path_7_with = comparison_folder / 'slide_007_WITH_FIGURE.png'
    with open(path_7_with, 'wb') as f:
        f.write(slide_7_with_fig)
    print(f"   ✅ Saved: {path_7_with}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Slides regenerated with figures")
    print(f"{'='*60}")
    print(f"\n📁 Comparison files:")
    print(f"   {comparison_folder}/")
    print(f"\n🎯 Compare:")
    print(f"   Original Slide 3: {slides_folder}/slide_003.png")
    print(f"   With Figure:      {path_3_with}")
    print(f"")
    print(f"   Original Slide 7: {slides_folder}/slide_007.png")
    print(f"   With Figure:      {path_7_with}")
    print(f"\n💡 The WITH_FIGURE versions should include the actual paper figures!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
