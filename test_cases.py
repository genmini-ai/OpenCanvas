import os
from slide_generator import SlideGenerator

# Get API keys from environment or replace with your actual keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

def run_test_cases():
    generator = SlideGenerator(api_key=ANTHROPIC_API_KEY, brave_api_key=BRAVE_API_KEY)
    
    test_cases = [
        # Test Case 1: Startup Pitch Deck
        {
            "name": "Startup Pitch Deck",
            "user_text": "AI-powered fitness app that creates personalized workout plans using computer vision to analyze form and provide real-time feedback",
            "purpose": "pitch deck",
            "theme": "bold high contrast"
        },
        
        # Test Case 2: Corporate Training
        {
            "name": "Corporate Training",
            "user_text": "Cybersecurity best practices for remote workers including password management, phishing detection, and secure file sharing protocols",
            "purpose": "educational presentation",
            "theme": "cool professional"
        },
        
        # Test Case 3: Academic Conference
        {
            "name": "Academic Research Presentation",
            "user_text": "Climate change impacts on coral reef ecosystems: a longitudinal study of bleaching events in the Great Barrier Reef from 2010-2024",
            "purpose": "academic presentation",
            "theme": "clean minimalist"
        },
        
        # Test Case 4: Marketing Campaign
        {
            "name": "Product Marketing Launch",
            "user_text": "New sustainable packaging initiative that reduces plastic waste by 70% while maintaining product freshness and brand appeal",
            "purpose": "marketing presentation",
            "theme": "natural earth"
        },
        
        # Test Case 5: Quarterly Business Report
        {
            "name": "Q4 Business Report",
            "user_text": "Q4 2024 financial performance showing 25% revenue growth, expansion into three new markets, and strategic acquisition of competitor",
            "purpose": "analytical report",
            "theme": "cool professional"
        },
        
        # Test Case 6: Creative Portfolio
        {
            "name": "Design Portfolio Showcase",
            "user_text": "Brand identity redesign projects for tech startups including logo development, color psychology, and user experience improvements",
            "purpose": "creative showcase",
            "theme": "muted morandi tones"
        },
        
        # Test Case 7: Conference Keynote
        {
            "name": "Industry Keynote",
            "user_text": "The future of artificial intelligence in healthcare: from diagnostic imaging to personalized medicine and ethical considerations",
            "purpose": "general presentation",
            "theme": "modern contemporary"
        },
        
        # Test Case 8: Educational Workshop
        {
            "name": "Personal Finance Workshop",
            "user_text": "Building wealth through smart investing: understanding compound interest, diversification strategies, and retirement planning for millennials",
            "purpose": "educational presentation",
            "theme": "warm earth tones"
        },
        
        # Test Case 9: Team Update Meeting
        {
            "name": "Project Status Update",
            "user_text": "Mobile app development progress: completed user authentication, in-progress payment integration, upcoming beta testing phase with timeline",
            "purpose": "business presentation",
            "theme": "clean minimalist"
        },
        
        # Test Case 10: Personal Storytelling
        {
            "name": "Personal Journey Presentation",
            "user_text": "My career transition from software engineering to sustainable agriculture: lessons learned, challenges faced, and advice for career changers",
            "purpose": "personal storytelling",
            "theme": "soft pastels"
        }
    ]
    
    # Run all test cases
    results = {}
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Running Test Case {i}: {test_case['name']} ===")
        print(f"Topic: {test_case['user_text'][:80]}...")
        print(f"Purpose: {test_case['purpose']} | Theme: {test_case['theme']}")
        
        try:
            result = generator.generate_complete_presentation(
                user_text=test_case['user_text'],
                purpose=test_case['purpose'],
                theme=test_case['theme']
            )
            
            # Count slides by a simple estimation method
            slide_count = None
            if result and 'html_content' in result:
                # Rough estimation by counting slide div elements
                slide_count = result['html_content'].count('<div class="slide"')
                if slide_count == 0:
                    # Try alternative pattern
                    slide_count = result['html_content'].count('<section class="slide"')
            
            results[test_case['name']] = {
                'status': 'success',
                'slides_count': slide_count or 0,
                'result': result
            }
            print(f"✓ Success: Generated {results[test_case['name']]['slides_count']} slides")
            
        except Exception as e:
            results[test_case['name']] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ Error: {e}")
    
    return results

# Run the tests
if __name__ == "__main__":
    test_results = run_test_cases()
    
    # Summary report
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    successful = sum(1 for r in test_results.values() if r['status'] == 'success')
    total = len(test_results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    for name, result in test_results.items():
        status_icon = "✓" if result['status'] == 'success' else "✗"
        if result['status'] == 'success':
            print(f"{status_icon} {name}: {result['slides_count']} slides")
        else:
            print(f"{status_icon} {name}: {result['error']}")
