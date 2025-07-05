#!/usr/bin/env python3
"""
E2E Test Runner - Wrapper for tests/test_e2e_pipeline.py

This script provides a convenient way to run E2E tests from the project root.
It supports various test modes and options.

Usage:
    python run_tests.py [test_type] [options]

Test Types:
    topic       - Run only topic-based tests
    pdf         - Run only PDF-based tests  
    full        - Run both topic and PDF tests (default)

Options:
    light       - Run light mode (1 test per type instead of 5)
    force       - Force regenerate all files from scratch
    convert     - Force conversion and evaluation (skip generation if exists)

Examples:
    python run_tests.py                    # Full suite
    python run_tests.py light              # Light mode (2 tests total)
    python run_tests.py topic              # Topic tests only
    python run_tests.py pdf light          # PDF tests only, light mode
    python run_tests.py force              # Force regenerate everything
    python run_tests.py convert            # Force conversion and evaluation
    python run_tests.py topic convert      # Topic tests with forced conversion
"""

import sys
import os
from pathlib import Path

# Add the tests directory to the path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

from test_e2e_pipeline import (
    run_topic_based_e2e_suite,
    run_pdf_based_e2e_suite, 
    run_full_e2e_suite
)

def main():
    """Main test runner function"""
    args = sys.argv[1:]
    
    # Parse arguments
    test_type = "full"  # default
    light_mode = False
    force_regenerate = False
    force_conversion = False
    
    for arg in args:
        if arg in ["topic", "pdf", "full"]:
            test_type = arg
        elif arg == "light":
            light_mode = True
        elif arg == "force":
            force_regenerate = True
        elif arg == "convert":
            force_conversion = True
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
            return 1
    
    # Show configuration
    print("🧪 E2E Test Configuration:")
    print(f"  Test Type: {test_type}")
    print(f"  Light Mode: {light_mode}")
    print(f"  Force Regenerate: {force_regenerate}")
    print(f"  Force Conversion: {force_conversion}")
    print()
    
    # Run appropriate test suite
    try:
        if test_type == "topic":
            results = run_topic_based_e2e_suite(light_mode, force_regenerate, force_conversion)
        elif test_type == "pdf":
            results = run_pdf_based_e2e_suite(light_mode, force_regenerate, force_conversion)
        else:  # full
            results = run_full_e2e_suite(light_mode, force_regenerate, force_conversion)
        
        # Save results
        import json
        from opencanvas.config import Config
        results_file = Config.OUTPUT_DIR / "e2e_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Return appropriate exit code
        if results.get("failed", 0) > 0:
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 