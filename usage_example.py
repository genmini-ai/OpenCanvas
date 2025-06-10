import os
from slide_generator import SlideGenerator

def main():
    # Get API key from environment variable
    api_key = os.getenv('ANTHROPIC_API_KEY')
    brave_api_key = os.getenv('BRAVE_API_KEY')  # Optional
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key as an environment variable:")
        print("export ANTHROPIC_API_KEY=your_api_key_here")
        return
    
    # Initialize the slide generator
    generator = SlideGenerator(api_key=api_key, brave_api_key=brave_api_key)
    
    # Example topic
    topic = "Sustainable urban farming technologies and their impact on local food systems"
    purpose = "educational presentation"
    theme = "natural earth"
    
    print("=" * 50)
    print("OpenCanvas - AI-Powered Presentation Generator")
    print("=" * 50)
    print(f"Topic: {topic}")
    print(f"Purpose: {purpose}")
    print(f"Theme: {theme}")
    print("-" * 50)
    
    # Generate the presentation
    result = generator.generate_complete_presentation(
        user_text=topic,
        purpose=purpose,
        theme=theme
    )
    
    if result:
        print("\n✅ Presentation generated successfully!")
        print(f"📊 Knowledge assessment: {result['knowledge_assessment']}")
        if result['research_performed']:
            print("🔍 Additional research was performed to enhance content quality")
        print(f"📂 HTML file saved as: {result['html_file']}")
        print(f"🌐 Presentation should be open in your default browser")
    else:
        print("\n❌ Failed to generate presentation")

if __name__ == "__main__":
    main()
