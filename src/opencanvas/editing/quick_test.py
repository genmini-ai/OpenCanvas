#!/usr/bin/env python3
"""
Quick test script - automatically applies first style recommendation

This script loads the AI in Animal Care presentation and automatically 
applies the first style recommendation for quick testing.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from opencanvas.editing import AssistModeStyleEditor

def quick_test():
    """Quick test - automatically apply first style recommendation"""
    
    # Path to the existing presentation
    presentation_path = Path("test_output/20250727_231244/slides/presentation.html")
    
    if not presentation_path.exists():
        print(f"❌ Presentation not found at: {presentation_path}")
        print("Please run this script from the project root directory")
        return
    
    print("⚡ Quick Test: AssistModeStyleEditor with AI in Animal Care")
    print("=" * 60)
    
    try:
        # Load the existing presentation
        print(f"📂 Loading presentation...")
        with open(presentation_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"✅ Loaded {len(html_content):,} characters")
        
        # Initialize the style editor
        editor = AssistModeStyleEditor()
        
        print(f"🎯 Step 1: Getting style recommendations...")
        
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
        
        # Automatically choose the first recommendation
        chosen_style = recommendations[0]
        
        print(f"✅ Content analyzed - {len(recommendations)} recommendations generated")
        print(f"🎨 Auto-selected: {chosen_style.style_name} ({chosen_style.style_category})")
        print(f"🎨 Colors: {chosen_style.color_palette.get('primary', 'N/A')} (primary)")
        print(f"🎬 Animation: {chosen_style.animation_philosophy}")
        
        print(f"\n🛠️ Step 2: Implementing style...")
        print("⏳ Processing...")
        
        # Implement the style
        modified_html, implementation_summary = editor.implement_chosen_style(
            original_html=html_content,
            chosen_style=chosen_style
        )
        
        # Create output directory
        output_dir = Path("test_output/quick_editing_test")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save results with simple names
        original_file = output_dir / "original.html"
        styled_file = output_dir / "styled.html"
        
        with open(original_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        with open(styled_file, "w", encoding="utf-8") as f:
            f.write(modified_html)
        
        print(f"✅ Style implementation complete!")
        print(f"\n📁 Results saved to: {output_dir.absolute()}")
        print(f"  📄 Original: {original_file.name}")
        print(f"  🎨 Styled: {styled_file.name}")
        
        print(f"\n📊 Results:")
        print(f"  Original: {len(html_content):,} characters")
        print(f"  Styled: {len(modified_html):,} characters")
        print(f"  Change: {len(modified_html) - len(html_content):+,} characters")
        
        print(f"\n🌐 Open both HTML files in your browser to see the transformation!")
        print(f"🎯 Style applied: {chosen_style.style_name}")
        
        # Show a brief summary
        print(f"\n📝 Brief Summary:")
        if "Color System:" in implementation_summary:
            color_section = implementation_summary.split("**Animation Features:**")[0]
            color_lines = [line.strip() for line in color_section.split('\n') if line.strip() and not line.startswith('#')]
            for line in color_lines[:3]:  # Show first 3 lines
                if line and not line.startswith('*'):
                    print(f"  {line}")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    quick_test() 