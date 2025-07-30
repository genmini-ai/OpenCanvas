#!/usr/bin/env python3
"""
Complete Style Editing Workflow

This script provides the full editing experience:
1. Analyzes presentation and gets 3 style recommendations
2. Generates previews for all 3 styles (first slide only) 
3. Shows user the previews for comparison
4. Allows user to choose their favorite
5. Implements the chosen style on the full presentation

This is the recommended way to use the editing system.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from opencanvas.editing import AssistModeStyleEditor

def complete_editing_workflow():
    """Complete workflow: analyze → preview → choose → implement"""
    
    # Path to the existing presentation
    presentation_path = Path("test_output/20250727_231244/slides/presentation.html")
    
    if not presentation_path.exists():
        print(f"❌ Presentation not found at: {presentation_path}")
        print("Please run this script from the project root directory")
        return
    
    print("🎨 Complete Style Editing Workflow")
    print("=" * 50)
    
    try:
        # Load the existing presentation
        print(f"📂 Loading presentation...")
        with open(presentation_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"✅ Loaded {len(html_content):,} characters")
        
        # Initialize the style editor
        editor = AssistModeStyleEditor()
        
        print(f"\n🎯 Step 1: Analyzing presentation content...")
        
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
        
        print(f"✅ Content Analysis Complete:")
        print(f"  🎯 Key themes: {', '.join(content_analysis.get('primary_themes', [])[:3])}")
        print(f"  😊 Tone: {content_analysis.get('emotional_tone', 'N/A')}")
        
        print(f"\n🎨 Generated {len(recommendations)} style recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec.style_name} ({rec.style_category}) - {', '.join(rec.mood_keywords[:2])}")
        
        print(f"\n🖼️ Step 2: Generating style previews...")
        print("⏳ Generating previews for all 3 styles (30-60 seconds)...")
        
        # Generate previews for all recommendations
        previews = editor.generate_style_previews(
            original_html=html_content,
            recommendations=recommendations
        )
        
        print(f"✅ Generated {len(previews)} previews!")
        
        # Create output directory for previews
        preview_dir = Path("test_output/style_previews")
        preview_dir.mkdir(exist_ok=True, parents=True)
        
        # Save all previews
        preview_files = []
        for i, (style_name, preview_html) in enumerate(previews.items(), 1):
            safe_name = style_name.lower().replace(' ', '_').replace('/', '_')
            filename = f"preview_{i}_{safe_name}.html"
            filepath = preview_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(preview_html)
            
            preview_files.append(filepath)
        
        # Create comparison page
        create_simple_comparison_page(preview_dir, preview_files, recommendations)
        comparison_path = preview_dir / "comparison.html"
        
        print(f"\n🌐 Step 3: Review style previews...")
        print(f"📁 Previews saved to: {preview_dir.absolute()}")
        
        # Try to open comparison page in browser
        try:
            webbrowser.open(f"file://{comparison_path.absolute()}")
            print(f"🌐 Opened comparison page in your browser!")
        except:
            print(f"💡 Manually open: {comparison_path}")
        
        print(f"\n⏸️ PAUSE: Review the style previews before continuing")
        print(f"   - Check the browser window that just opened")
        print(f"   - Compare all 3 style options side by side")
        print(f"   - Each preview shows how the first slide would look")
        
        input(f"\n⌨️  Press Enter when you're ready to choose a style...")
        
        print(f"\n🤔 Step 4: Choose your preferred style")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}) {rec.style_name} ({rec.style_category})")
            print(f"     🎨 Colors: {rec.color_palette.get('primary', 'N/A')} primary")
            print(f"     🎬 Animation: {rec.animation_philosophy}")
            print(f"     👥 Best for: {rec.best_suited_for}")
            print()
        
        while True:
            try:
                choice = input(f"Enter your choice (1-{len(recommendations)}): ")
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(recommendations):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(recommendations)}")
            except ValueError:
                print("Please enter a valid number")
        
        chosen_style = recommendations[choice_idx]
        print(f"\n🎯 You chose: {chosen_style.style_name}")
        
        print(f"\n🛠️ Step 5: Implementing full presentation styling...")
        print("⏳ This will take 15-30 seconds to style the entire presentation...")
        
        # Implement the chosen style
        modified_html, implementation_summary = editor.implement_chosen_style(
            original_html=html_content,
            chosen_style=chosen_style
        )
        
        # Create output directory for final results
        final_dir = Path("test_output/final_styled_presentation")
        final_dir.mkdir(exist_ok=True, parents=True)
        
        # Save final results
        original_file = final_dir / "original_presentation.html"
        styled_file = final_dir / f"styled_{chosen_style.style_name.lower().replace(' ', '_')}.html"
        summary_file = final_dir / "implementation_summary.txt"
        
        with open(original_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        with open(styled_file, "w", encoding="utf-8") as f:
            f.write(modified_html)
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Style Implementation Summary\n")
            f.write(f"===========================\n\n")
            f.write(f"Chosen Style: {chosen_style.style_name} ({chosen_style.style_category})\n")
            f.write(f"Target Audience: {chosen_style.best_suited_for}\n")
            f.write(f"Mood Keywords: {', '.join(chosen_style.mood_keywords)}\n\n")
            f.write(f"Implementation Details:\n")
            f.write(f"{implementation_summary}\n")
        
        print(f"✅ Complete styling implementation finished!")
        
        print(f"\n📁 Final Results:")
        print(f"  📄 Original: {original_file.name}")
        print(f"  🎨 Styled: {styled_file.name}")
        print(f"  📝 Summary: {summary_file.name}")
        print(f"  📂 Location: {final_dir.absolute()}")
        
        print(f"\n📊 Transformation Stats:")
        print(f"  Original size: {len(html_content):,} characters")
        print(f"  Styled size: {len(modified_html):,} characters")
        print(f"  Size change: {len(modified_html) - len(html_content):+,} characters")
        
        # Try to open the final styled presentation
        try:
            webbrowser.open(f"file://{styled_file.absolute()}")
            print(f"\n🌐 Opened your styled presentation in browser!")
        except:
            print(f"\n💡 Manually open: {styled_file}")
        
        print(f"\n🎉 Workflow Complete!")
        print(f"✨ Your presentation has been transformed with the {chosen_style.style_name} style")
        print(f"📊 Compare the original and styled versions to see the transformation")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()


def create_simple_comparison_page(output_dir: Path, preview_files: list, recommendations: list) -> None:
    """Create a simple comparison page for the workflow"""
    
    comparison_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Choose Your Style - AI in Animal Care</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        .preview-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; }}
        .preview-card {{ background: rgba(255,255,255,0.95); border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); transition: transform 0.3s ease; }}
        .preview-card:hover {{ transform: translateY(-5px); }}
        .preview-header {{ padding: 20px; background: linear-gradient(45deg, #2196F3, #21CBF3); color: white; }}
        .preview-header h3 {{ margin: 0 0 5px 0; font-size: 1.4rem; }}
        .preview-header p {{ margin: 0; opacity: 0.9; }}
        .preview-frame {{ width: 100%; height: 400px; border: none; background: white; }}
        .instructions {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin-bottom: 30px; backdrop-filter: blur(10px); }}
        .instructions h3 {{ margin-top: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Choose Your Presentation Style</h1>
            <p>Compare these 3 style options for your "AI in Animal Care" presentation</p>
        </div>
        
        <div class="instructions">
            <h3>📋 Next Steps:</h3>
            <ol>
                <li><strong>Compare the styles below</strong> - Each shows how your first slide would look</li>
                <li><strong>Note your favorite</strong> - Remember the style name you prefer</li>
                <li><strong>Return to the terminal</strong> - Choose your preferred style for full implementation</li>
            </ol>
        </div>
        
        <div class="preview-grid">
"""
    
    # Add styled previews
    for i, (filepath, rec) in enumerate(zip(preview_files, recommendations), 1):
        comparison_html += f"""
        <div class="preview-card">
            <div class="preview-header">
                <h3>{rec.style_name}</h3>
                <p>{rec.style_category.title()} Style • {', '.join(rec.mood_keywords[:2])}</p>
            </div>
            <iframe src="{filepath.name}" class="preview-frame"></iframe>
        </div>
"""
    
    comparison_html += """
        </div>
        
        <div style="margin-top: 50px; text-align: center; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px);">
            <h3>⌨️ Ready to Decide?</h3>
            <p>Return to your terminal window to select your preferred style and apply it to the full presentation!</p>
        </div>
    </div>
</body>
</html>"""
    
    comparison_file = output_dir / "comparison.html"
    with open(comparison_file, "w", encoding="utf-8") as f:
        f.write(comparison_html)


if __name__ == "__main__":
    complete_editing_workflow() 