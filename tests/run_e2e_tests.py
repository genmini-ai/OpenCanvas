#!/usr/bin/env python3
"""
Standalone E2E Test Runner for OpenCanvas
Run this script to test the complete pipeline with both topic-based and PDF-based generation
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_e2e_pipeline import run_full_e2e_suite, run_topic_based_e2e_suite, run_pdf_based_e2e_suite
from dotenv import load_dotenv

def print_usage():
    """Print usage information"""
    print("\n📖 Usage:")
    print("  python run_e2e_tests.py [TEST_TYPE] [MODE] [OPTIONS]")
    print("\n🎯 Test Types:")
    print("  topic  - Run only topic-based generation tests")
    print("  pdf    - Run only PDF-based generation tests") 
    print("  full   - Run both topic and PDF tests (default)")
    print("\n⚡ Modes:")
    print("  light  - Run 1 test per type (fast, ~5 minutes)")
    print("  (none) - Run all tests (thorough, ~30 minutes)")
    print("\n🔧 Options:")
    print("  force  - Force regeneration even if slides exist")
    print("  help   - Show this help message")
    print("\n💡 Examples:")
    print("  python run_e2e_tests.py                    # Full suite, all tests")
    print("  python run_e2e_tests.py light              # Full suite, light mode")
    print("  python run_e2e_tests.py topic              # Topic tests only, all tests")
    print("  python run_e2e_tests.py topic light        # Topic tests only, light mode")
    print("  python run_e2e_tests.py pdf light          # PDF tests only, light mode")
    print("  python run_e2e_tests.py light force        # Full suite, light mode, force regenerate")
    print("  python run_e2e_tests.py topic force        # Topic tests only, force regenerate")

def main():
    """Main test runner"""
    print("🧪 OpenCanvas E2E Test Runner")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("💡 Please set ANTHROPIC_API_KEY in your .env file")
        return 1
    
    # Parse arguments
    test_type = "full"  # default
    light_mode = False
    force_regenerate = False
    
    for arg in sys.argv[1:]:
        arg_lower = arg.lower()
        if arg_lower in ["topic", "pdf", "full"]:
            test_type = arg_lower
        elif arg_lower in ["light", "--light", "-l"]:
            light_mode = True
        elif arg_lower in ["force", "--force", "-f"]:
            force_regenerate = True
        elif arg_lower in ["help", "--help", "-h"]:
            print_usage()
            return 0
    
    # Show mode information
    mode_info = "Light Mode (1 test per type)" if light_mode else "Full Mode (5 tests per type)"
    force_info = " - FORCE REGENERATE" if force_regenerate else ""
    print(f"🎯 Mode: {mode_info}{force_info}")
    
    if test_type == "topic":
        print("🎯 Running Topic-Based E2E Tests Only")
        results = run_topic_based_e2e_suite(light_mode, force_regenerate)
    elif test_type == "pdf":
        print("🎯 Running PDF-Based E2E Tests Only")
        results = run_pdf_based_e2e_suite(light_mode, force_regenerate)
    elif test_type == "full":
        print("🎯 Running Complete E2E Test Suite")
        results = run_full_e2e_suite(light_mode, force_regenerate)
    else:
        print("❌ Invalid test type. Use: topic, pdf, or full")
        print_usage()
        return 1
    
    # Save results to output directory
    import json
    from pathlib import Path
    from opencanvas.config import Config
    
    output_dir = Config.OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    results_file = output_dir / "e2e_test_results.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return appropriate exit code
    if "summary" in results:
        total_tests = results["summary"]["total_tests"]
        total_passed = results["summary"]["total_passed"]
        if total_passed == total_tests:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {total_tests - total_passed} tests failed")
            return 1
    else:
        # Single suite results
        if results.get("passed", 0) == results.get("total_tests", 0):
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {results.get('failed', 0)} tests failed")
            return 1

if __name__ == "__main__":
    exit(main()) 