#!/usr/bin/env python3
"""
Demo script for the AssistModeStyleEditor

This shows how to use the two-step assist mode for presentation style editing.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from opencanvas.editing import AssistModeStyleEditor

def demo_assist_mode_editing():
    """Demonstrate the two-step assist mode editing process"""
    
    # Sample presentation HTML (simplified for demo)
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI in Animal Care</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .slide { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
            h1, h2 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <div class="slides">
            <div class="slide">
                <h1>AI in Animal Care</h1>
                <p>Transforming veterinary medicine, pet care, and wildlife conservation</p>
            </div>
            <div class="slide">
                <h2>Veterinary Diagnostics</h2>
                <ul>
                    <li>AI-powered image analysis for faster diagnosis</li>
                    <li>Machine learning algorithms for pattern recognition</li>
                    <li>90%+ accuracy in radiology interpretation</li>
                </ul>
            </div>
            <div class="slide">
                <h2>Wildlife Conservation</h2>
                <ul>
                    <li>Automated species identification from camera traps</li>
                    <li>Population monitoring and tracking</li>
                    <li>Anti-poaching surveillance systems</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("🎨 AssistModeStyleEditor Demo")
    print("=" * 50)
    
    try:
        # Initialize the style editor
        editor = AssistModeStyleEditor()
        
        print("\n📊 Step 1: Getting style recommendations...")
        
        # Get style recommendations
        content_analysis, recommendations = editor.get_style_recommendations(
            html_content=sample_html,
            topic="AI in animal care",
            purpose="educational presentation",
            audience="veterinary professionals and researchers"
        )
        
        print(f"✅ Content Analysis:")
        print(f"  - Primary themes: {content_analysis.get('primary_themes', [])}")
        print(f"  - Emotional tone: {content_analysis.get('emotional_tone', 'N/A')}")
        print(f"  - Complexity: {content_analysis.get('complexity_level', 'N/A')}")
        
        print(f"\n🎨 Generated {len(recommendations)} style recommendations:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec.style_name} ({rec.style_category})")
            print(f"     Colors: {rec.color_palette}")
            print(f"     Animation: {rec.animation_philosophy}")
            print(f"     Typography: {rec.typography_approach}")
            print(f"     Best for: {rec.best_suited_for}")
            print(f"     Mood: {', '.join(rec.mood_keywords)}")
        
        # For demo, automatically choose the first recommendation
        if recommendations:
            chosen_style = recommendations[0]
            print(f"\n🎯 Choosing style: {chosen_style.style_name}")
            
            print("\n🛠️ Step 2: Implementing chosen style...")
            
            # Implement the chosen style
            modified_html, implementation_summary = editor.implement_chosen_style(
                original_html=sample_html,
                chosen_style=chosen_style
            )
            
            print("✅ Style implementation completed!")
            print(f"\n📝 Implementation Summary:")
            print(implementation_summary)
            
            # Save the results
            output_dir = Path("demo_output")
            output_dir.mkdir(exist_ok=True)
            
            # Save original
            with open(output_dir / "original_presentation.html", "w", encoding="utf-8") as f:
                f.write(sample_html)
            
            # Save styled version
            with open(output_dir / "styled_presentation.html", "w", encoding="utf-8") as f:
                f.write(modified_html)
            
            print(f"\n📁 Files saved to: {output_dir.absolute()}")
            print(f"  - original_presentation.html")
            print(f"  - styled_presentation.html")
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"Open the HTML files in your browser to see the difference.")
            
        else:
            print("❌ No recommendations generated")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_assist_mode_editing() 