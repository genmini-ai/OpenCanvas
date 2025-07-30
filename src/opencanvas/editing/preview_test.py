#!/usr/bin/env python3
"""
Preview Test Script - Generate style previews for comparison

This script demonstrates the new preview functionality:
1. Analyzes the presentation and gets 3 style recommendations
2. Generates preview HTML for each style (first slide only)
3. Saves all previews for easy browser comparison
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from opencanvas.editing import AssistModeStyleEditor

def test_preview_generation():
    """Test the preview generation feature"""
    
    # Path to the existing presentation
    presentation_path = Path("test_output/20250727_231244/slides/presentation.html")
    
    if not presentation_path.exists():
        print(f"❌ Presentation not found at: {presentation_path}")
        print("Please run this script from the project root directory")
        return
    
    print("🎨 Testing Style Preview Generation")
    print("=" * 50)
    
    try:
        # Load the existing presentation
        print(f"📂 Loading presentation...")
        with open(presentation_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"✅ Loaded {len(html_content):,} characters")
        
        # Initialize the style editor
        editor = AssistModeStyleEditor()
        
        print(f"\n🎯 Step 1: Getting style recommendations...")
        
        # Get style recommendations
        content_analysis, recommendations = editor.get_style_recommendations(
            html_content=html_content,
            topic="AI in animal care",
            purpose="educational presentation",
            audience="veterinary professionals and researchers"
        )
        
        if not recommendations:
            print("❌ No recommendations generated")
            return
        
        print(f"✅ Generated {len(recommendations)} style recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec.style_name} ({rec.style_category})")
        
        print(f"\n🖼️ Step 2: Generating style previews...")
        print("⏳ This will take 30-60 seconds to generate all previews...")
        
        # Generate previews for all recommendations
        previews = editor.generate_style_previews(
            original_html=html_content,
            recommendations=recommendations
        )
        
        print(f"✅ Generated {len(previews)} style previews!")
        
        # Create output directory
        output_dir = Path("test_output/style_previews")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save all previews
        preview_files = []
        for i, (style_name, preview_html) in enumerate(previews.items(), 1):
            # Create safe filename
            safe_name = style_name.lower().replace(' ', '_').replace('/', '_')
            filename = f"preview_{i}_{safe_name}.html"
            filepath = output_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(preview_html)
            
            preview_files.append(filepath)
            print(f"  💾 Saved: {filename}")
        
        # Also save the original first slide for comparison
        original_preview = create_original_first_slide_preview(html_content)
        original_file = output_dir / "00_original_first_slide.html"
        with open(original_file, "w", encoding="utf-8") as f:
            f.write(original_preview)
        preview_files.insert(0, original_file)
        
        print(f"\n📁 All previews saved to: {output_dir.absolute()}")
        print(f"📄 Files created:")
        for filepath in preview_files:
            print(f"  - {filepath.name}")
        
        print(f"\n🌐 Next Steps:")
        print(f"  1. Open all HTML files in your browser (use separate tabs)")
        print(f"  2. Compare the different visual styles side by side")
        print(f"  3. Choose your favorite style for full implementation")
        
        print(f"\n💡 Pro Tips:")
        print(f"  - Open in browser tabs and switch between them quickly")
        print(f"  - Each preview shows how the first slide would look")
        print(f"  - The styling would be applied to the entire presentation")
        print(f"  - Preview generation is much faster than full implementation")
        
        # Generate browser-friendly comparison page
        create_comparison_page(output_dir, preview_files, recommendations)
        
        print(f"\n🎯 Bonus: Created comparison.html for easy side-by-side viewing!")
        
    except Exception as e:
        print(f"❌ Preview test failed: {e}")
        import traceback
        traceback.print_exc()


def create_original_first_slide_preview(html_content: str) -> str:
    """Extract and create a preview of the original first slide"""
    # Simple extraction of the first slide for comparison
    # This is a basic version - in practice, you'd want more sophisticated parsing
    
    # Find the first slide
    slide_start = html_content.find('<div class="slide')
    if slide_start == -1:
        slide_start = html_content.find('<div class="slide-content')
    
    if slide_start != -1:
        # Find the end of the first slide
        slide_count = 0
        pos = slide_start
        while pos < len(html_content):
            if html_content[pos:pos+17] == '<div class="slide':
                slide_count += 1
                if slide_count == 2:  # Found start of second slide
                    slide_end = pos
                    break
            pos += 1
        else:
            slide_end = html_content.find('</div>\n<div class="navigation">')
            if slide_end == -1:
                slide_end = len(html_content) - 100
        
        # Extract the first slide content
        first_slide = html_content[slide_start:slide_end]
        
        # Create a minimal HTML wrapper
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Original Style - First Slide</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .preview-header {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .slide-container {{ background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; }}
        /* Copy relevant styles from original */
        {extract_css_from_html(html_content)}
    </style>
</head>
<body>
    <div class="preview-header">
        <h2>Original Style</h2>
        <p>This is how the first slide currently looks</p>
    </div>
    <div class="slide-container">
        {first_slide}
    </div>
    <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 5px; font-size: 0.9em; color: #666;">
        <strong>Note:</strong> This is the original first slide for comparison with the styled previews.
    </div>
</body>
</html>"""
    
    return f"""<!DOCTYPE html>
<html>
<head><title>Original Preview</title></head>
<body>
    <h2>Original Style Preview</h2>
    <p>Could not extract first slide for preview.</p>
</body>
</html>"""


def extract_css_from_html(html_content: str) -> str:
    """Extract CSS styles from the HTML content"""
    css_start = html_content.find('<style>')
    css_end = html_content.find('</style>')
    
    if css_start != -1 and css_end != -1:
        return html_content[css_start+7:css_end]
    return ""


def create_comparison_page(output_dir: Path, preview_files: list, recommendations: list) -> None:
    """Create a comparison page with all previews in iframes"""
    
    comparison_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Style Preview Comparison</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .preview-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .preview-card {{ background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; }}
        .preview-header {{ padding: 15px; background: #2196F3; color: white; }}
        .preview-frame {{ width: 100%; height: 400px; border: none; }}
        .instructions {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Style Preview Comparison</h1>
        <p>Compare different visual styles for your AI in Animal Care presentation</p>
    </div>
    
    <div class="instructions">
        <h3>📋 How to Use:</h3>
        <ul>
            <li><strong>Compare Styles:</strong> All previews show the same content with different visual treatments</li>
            <li><strong>Click to Expand:</strong> Click on any preview to open it in full size</li>
            <li><strong>Choose Your Favorite:</strong> Once you decide, use the full implementation script</li>
        </ul>
    </div>
    
    <div class="preview-grid">
"""
    
    # Add original preview
    comparison_html += f"""
        <div class="preview-card">
            <div class="preview-header">
                <h3>Original Style</h3>
                <p>Current presentation style</p>
            </div>
            <iframe src="{preview_files[0].name}" class="preview-frame"></iframe>
        </div>
"""
    
    # Add styled previews
    for i, (filepath, rec) in enumerate(zip(preview_files[1:], recommendations), 1):
        comparison_html += f"""
        <div class="preview-card">
            <div class="preview-header">
                <h3>{rec.style_name}</h3>
                <p>{rec.style_category.title()} • {', '.join(rec.mood_keywords[:2])}</p>
            </div>
            <iframe src="{filepath.name}" class="preview-frame"></iframe>
        </div>
"""
    
    comparison_html += """
    </div>
    
    <div style="margin-top: 40px; text-align: center; padding: 20px; background: white; border-radius: 10px;">
        <h3>Ready to Choose?</h3>
        <p>Once you've decided on a style, use the full implementation script to apply it to your entire presentation!</p>
    </div>
</body>
</html>"""
    
    comparison_file = output_dir / "comparison.html"
    with open(comparison_file, "w", encoding="utf-8") as f:
        f.write(comparison_html)


if __name__ == "__main__":
    test_preview_generation() 