#!/usr/bin/env python3
"""
Adversarial Attack Demonstration for OpenCanvas

This script demonstrates how to use adversarial attacks to test
the robustness of presentation evaluation systems.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from opencanvas.evaluation.adversarial_attacks import (
    PresentationAdversarialAttacks,
    apply_adversarial_attack,
    generate_all_attacks,
    find_test_presentations,
    load_existing_presentation
)

def demo_adversarial_attacks():
    """Demonstrate all adversarial attack types"""
    
    # Sample presentation HTML
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sustainable Energy Solutions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .slide { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
            h1, h2 { color: #2c3e50; }
            .highlight-box { background: #f39c12; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="slides">
            <!-- Slide 1: Title -->
            <div class="slide" data-id="1">
                <h1>Sustainable Energy Solutions for Developing Countries</h1>
                <p>A comprehensive analysis of renewable energy adoption</p>
            </div>
            
            <!-- Slide 2: Solar Power -->
            <div class="slide" data-id="2">
                <h2>Solar Power Revolution</h2>
                <ul>
                    <li>Photovoltaic (PV) technology converts sunlight directly into electricity</li>
                    <li>Cost decreased by 85% in Bangladesh over the past decade</li>
                    <li>Excellent solar resources in Ethiopia and Nepal</li>
                    <li>Low operational costs and long operational life</li>
                </ul>
                <div class="highlight-box">
                    Solar power is increasingly competitive with fossil fuels
                </div>
            </div>
            
            <!-- Slide 3: Wind Power -->
            <div class="slide" data-id="3">
                <h2>Wind Energy Potential</h2>
                <ul>
                    <li>Wind turbines convert energy of flowing air into electricity</li>
                    <li>Capacity increased by 120% in Sub-Saharan Africa</li>
                    <li>Wind farms can power inclusive development</li>
                    <li>Scalable technology with reliable performance</li>
                </ul>
            </div>
            
            <!-- Slide 4: Implementation -->
            <div class="slide" data-id="4">
                <h2>Implementation Challenges</h2>
                <ul>
                    <li>Grid integration requires technical expertise</li>
                    <li>Financing models need capacity building</li>
                    <li>Policy frameworks must accelerate implementation</li>
                    <li>Energy storage solutions are essential</li>
                </ul>
            </div>
            
            <!-- Slide 5: Conclusion -->
            <div class="slide" data-id="5">
                <h2>The Path Forward</h2>
                <p>Renewable energy offers a sustainable path to economic development</p>
                <p>Sustainable energy solutions make sense for developing countries</p>
                <div class="highlight-box">
                    Recommended: Accelerate renewable energy implementation
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("🚀 Adversarial Attack Demonstration")
    print("=" * 50)
    
    # Create attacker instance
    attacker = PresentationAdversarialAttacks(sample_html)
    
    # Demonstrate each attack type
    attack_descriptions = {
        1: "Beautiful Nonsense - Replace scientific content with surrealist art",
        2: "Fact Flip - Invert factual claims and numerical values", 
        3: "Logical Chaos - Randomly shuffle slide order",
        4: "Swiss Cheese - Randomly delete critical content",
        5: "Gradual Decay - Progressive quality degradation"
    }
    
    # Generate all attacks
    output_dir = "./demo_adversarial_attacks"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📁 Generating attacks in: {output_dir}")
    
    for attack_type in range(1, 6):
        print(f"\n🔥 Attack {attack_type}: {attack_descriptions[attack_type]}")
        
        # Apply attack
        modified_html = attacker.apply_attack(attack_type)
        
        # Save to file
        filename = f"attack_{attack_type}_{attack_descriptions[attack_type].split(' - ')[0].lower().replace(' ', '_')}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        print(f"   ✅ Generated: {filename}")
        print(f"   📊 Size: {len(modified_html):,} characters")
        print(f"   📈 Change: {abs(len(modified_html) - len(sample_html)):,} characters")
        
        # Show sample of changes for some attacks
        if attack_type == 1:  # Beautiful Nonsense
            if "surrealist dreamscapes" in modified_html:
                print("   🎨 Sample change: 'sustainable energy solutions' → 'surrealist dreamscapes'")
        elif attack_type == 2:  # Fact Flip  
            if "increased by 85%" in modified_html:
                print("   🔄 Sample change: 'decreased by 85%' → 'increased by 85%'")
    
    print(f"\n✅ All attacks generated successfully!")
    print(f"📁 Files saved in: {os.path.abspath(output_dir)}")
    
    # Show how to use with existing presentations
    print(f"\n🔍 Searching for existing presentations...")
    existing_presentations = find_test_presentations()
    
    if existing_presentations:
        print(f"📄 Found {len(existing_presentations)} existing presentations:")
        for i, pres in enumerate(existing_presentations[:3]):  # Show first 3
            print(f"   {i+1}. {pres}")
        
        if len(existing_presentations) > 3:
            print(f"   ... and {len(existing_presentations) - 3} more")
        
        print(f"\n💡 To test with existing presentations:")
        print(f"   python examples/adversarial_attack_demo.py {existing_presentations[0]}")
    else:
        print("   No existing presentations found in test_output/")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Open the generated HTML files in your browser")
    print(f"   2. Compare original vs attacked presentations")
    print(f"   3. Use these for evaluation robustness testing")
    print(f"   4. Run: python tests/test_adversarial_attacks.py")


def test_with_existing_presentation(presentation_file: str):
    """Test adversarial attacks with an existing presentation"""
    
    if not os.path.exists(presentation_file):
        print(f"❌ File not found: {presentation_file}")
        return
    
    print(f"🔍 Testing with: {presentation_file}")
    print("=" * 60)
    
    try:
        # Load the presentation
        html_content = load_existing_presentation(presentation_file)
        print(f"📄 Loaded presentation: {len(html_content):,} characters")
        
        # Generate all attacks
        output_dir = f"./adversarial_test_{Path(presentation_file).stem}"
        attack_files = generate_all_attacks(html_content, output_dir)
        
        print(f"\n✅ Generated {len(attack_files)} attack variants:")
        for attack_type, filepath in attack_files.items():
            attack_name = Path(filepath).stem.replace('presentation_', '')
            print(f"   {attack_type}. {attack_name} → {filepath}")
        
        print(f"\n📁 All files saved in: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test with specific presentation file
        test_with_existing_presentation(sys.argv[1])
    else:
        # Run demonstration
        demo_adversarial_attacks() 