#!/usr/bin/env python3
"""
Basic Usage Examples for Presentation Toolkit

This file demonstrates the most common use cases and workflows.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from opencanvas.generators.router import GenerationRouter
from opencanvas.conversion.html_to_pdf import PresentationConverter
from opencanvas.evaluation.evaluator import PresentationEvaluator
from opencanvas.config import Config

def example_1_topic_generation():
    """Example 1: Generate presentation from a topic"""
    print("=== Example 1: Topic-based Generation ===")
    
    # Initialize the router (auto-detects input type)
    router = GenerationRouter(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    # Generate presentation
    result = router.generate(
        input_source="The benefits of renewable energy for businesses",
        purpose="corporate presentation",
        theme="natural earth"
    )
    
    if result:
        print(f"✅ Generated: {result['html_file']}")
        print(f"🔍 Research performed: {result.get('research_performed', False)}")
        return result['html_file']
    else:
        print("❌ Generation failed")
        return None

def example_2_pdf_generation():
    """Example 2: Generate presentation from PDF"""
    print("\n=== Example 2: PDF-based Generation ===")
    
    # Initialize the router
    router = GenerationRouter(api_key=Config.ANTHROPIC_API_KEY)
    
    # Generate from arXiv paper
    result = router.generate(
        input_source="https://arxiv.org/pdf/2505.20286",
        purpose="academic seminar",
        theme="academic"
    )
    
    if result:
        print(f"✅ Generated: {result['html_file']}")
        return result['html_file']
    else:
        print("❌ Generation failed")
        return None

def example_3_html_to_pdf_conversion():
    """Example 3: Convert HTML to PDF"""
    print("\n=== Example 3: HTML to PDF Conversion ===")
    
    # First generate a presentation
    router = GenerationRouter(api_key=Config.ANTHROPIC_API_KEY)
    result = router.generate(
        input_source="Introduction to machine learning",
        purpose="educational workshop",
        theme="clean minimalist"
    )
    
    if not result:
        print("❌ Could not generate presentation for conversion")
        return None
    
    html_file = result['html_file']
    
    # Convert to PDF
    converter = PresentationConverter(
        html_file=html_file,
        method="selenium",  # or "playwright"
        zoom_factor=1.3
    )
    
    try:
        pdf_path = converter.convert("example_presentation.pdf")
        print(f"✅ Converted to PDF: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return None

def example_4_presentation_evaluation():
    """Example 4: Evaluate presentation quality"""
    print("\n=== Example 4: Presentation Evaluation ===")
    
    # For this example, we need a folder with presentation.pdf
    # and optionally paper.pdf for reference comparison
    
    # Create evaluation folder structure (you would do this manually)
    eval_folder = "evaluation_example"
    
    print(f"📁 To run evaluation, create folder: {eval_folder}/")
    print("   └── presentation.pdf  (required)")
    print("   └── paper.pdf         (optional, for reference-required evaluation)")
    
    # Example evaluation code (commented out since folder might not exist)
    """
    evaluator = PresentationEvaluator(api_key=Config.ANTHROPIC_API_KEY)
    
    try:
        result = evaluator.evaluate_presentation(eval_folder)
        evaluator.print_results(result)
        
        # Save results
        evaluator.save_results(result, f"{eval_folder}_results.json")
        print(f"✅ Evaluation completed, results saved")
        
    except FileNotFoundError as e:
        print(f"❌ Evaluation folder not found: {e}")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
    """
    
    print("💡 Run this after creating the evaluation folder structure")

def example_5_complete_pipeline():
    """Example 5: Complete pipeline - Generate, Convert, Evaluate"""
    print("\n=== Example 5: Complete Pipeline ===")
    
    topic = "Sustainable urban transportation solutions"
    purpose = "city council presentation"
    theme = "natural earth"
    
    # Step 1: Generate presentation
    print("🎯 Step 1: Generating presentation...")
    router = GenerationRouter(
        api_key=Config.ANTHROPIC_API_KEY,
        brave_api_key=Config.BRAVE_API_KEY
    )
    
    gen_result = router.generate(
        input_source=topic,
        purpose=purpose,
        theme=theme
    )
    
    if not gen_result:
        print("❌ Generation failed")
        return
    
    html_file = gen_result['html_file']
    print(f"✅ Generated: {html_file}")
    
    # Step 2: Convert to PDF
    print("\n🔄 Step 2: Converting to PDF...")
    try:
        converter = PresentationConverter(
            html_file=html_file,
            zoom_factor=1.4
        )
        pdf_path = converter.convert("pipeline_presentation.pdf")
        print(f"✅ Converted: {pdf_path}")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return
    
    # Step 3: Evaluation (would require manual setup)
    print("\n📊 Step 3: Evaluation...")
    print("💡 To complete evaluation:")
    print(f"   1. Create folder: evaluation_pipeline/")
    print(f"   2. Copy {pdf_path} to evaluation_pipeline/presentation.pdf")
    print(f"   3. Optionally add evaluation_pipeline/paper.pdf for reference")
    print(f"   4. Run: python -m src.main evaluate evaluation_pipeline/")

def example_6_custom_themes():
    """Example 6: Using different themes"""
    print("\n=== Example 6: Theme Variations ===")
    
    from shared.themes import ThemeManager
    
    # List available themes
    theme_manager = ThemeManager()
    themes = theme_manager.list_themes()
    
    print("🎨 Available themes:")
    for theme in themes:
        description = theme_manager.get_theme_description(theme)
        print(f"   • {theme}: {description}")
    
    # Generate with different themes
    router = GenerationRouter(api_key=Config.ANTHROPIC_API_KEY)
    
    test_cases = [
        ("bold high contrast", "startup pitch"),
        ("soft pastels", "creative showcase"),
        ("academic", "research presentation")
    ]
    
    print(f"\n🎯 Generating presentations with different themes:")
    for theme, purpose in test_cases:
        print(f"   Generating with '{theme}' theme...")
        result = router.generate(
            input_source=f"Sample presentation for {purpose}",
            purpose=purpose,
            theme=theme
        )
        if result:
            print(f"   ✅ Created: {result['html_file']}")
        else:
            print(f"   ❌ Failed")

def example_7_error_handling():
    """Example 7: Error handling and validation"""
    print("\n=== Example 7: Error Handling ===")
    
    router = GenerationRouter(api_key=Config.ANTHROPIC_API_KEY)
    
    # Test invalid inputs
    test_cases = [
        ("", "Empty input"),
        ("https://invalid-url.com/nonexistent.pdf", "Invalid PDF URL"),
        ("/nonexistent/file.pdf", "Non-existent PDF file")
    ]
    
    for input_source, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        try:
            result = router.generate(
                input_source=input_source,
                purpose="test presentation",
                theme="professional blue"
            )
            if result:
                print(f"   ✅ Unexpectedly succeeded")
            else:
                print(f"   ✅ Properly handled failure")
        except Exception as e:
            print(f"   ✅ Caught exception: {type(e).__name__}")

def main():
    """Run all examples"""
    print("🚀 Presentation Toolkit - Basic Usage Examples")
    print("=" * 60)
    
    # Check configuration
    try:
        Config.validate()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure to set ANTHROPIC_API_KEY in your .env file")
        return
    
    # Run examples
    examples = [
        example_1_topic_generation,
        example_2_pdf_generation,
        example_3_html_to_pdf_conversion,
        example_4_presentation_evaluation,
        example_5_complete_pipeline,
        example_6_custom_themes,
        example_7_error_handling
    ]
    
    for example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n👋 Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            continue
    
    print("\n🎉 Examples completed!")
    print("\n💡 Next steps:")
    print("   • Try the CLI: python -m src.main --help")
    print("   • Run tests: python tests/test_topics.py")
    print("   • Check out advanced_workflow.py for more complex examples")

if __name__ == "__main__":
    main()