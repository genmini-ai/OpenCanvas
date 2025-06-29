#!/usr/bin/env python3
"""
Configuration validation script for OpenCanvas
Run this to test your .env setup
"""

import os
import sys
from pathlib import Path

def main():
    print("🔍 OpenCanvas Configuration Validator")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run: cp .env.example .env")
        return 1
    
    print("✅ .env file found")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed")
        print("💡 Run: pip install python-dotenv")
        return 1
    
    # Check required API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key or anthropic_key == 'your_anthropic_api_key_here':
        print("❌ ANTHROPIC_API_KEY not set or using placeholder")
        print("💡 Get your key from: https://console.anthropic.com/")
        return 1
    
    print("✅ ANTHROPIC_API_KEY configured")
    
    # Check optional keys
    brave_key = os.getenv('BRAVE_API_KEY')
    if brave_key and brave_key != 'your_brave_api_key_here':
        print("✅ BRAVE_API_KEY configured (web research enabled)")
    else:
        print("⚠️  BRAVE_API_KEY not configured (web research disabled)")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OPENAI_API_KEY configured (GPT evaluation enabled)")
    else:
        print("⚠️  OPENAI_API_KEY not configured (GPT evaluation disabled)")
    
    # Check evaluation settings
    eval_provider = os.getenv('EVALUATION_PROVIDER', 'claude')
    eval_model = os.getenv('EVALUATION_MODEL', 'claude-3-5-sonnet-20241022')
    
    print(f"📊 Evaluation Provider: {eval_provider}")
    print(f"🤖 Evaluation Model: {eval_model}")
    
    # Validate model/provider match
    if eval_provider == 'claude':
        if eval_model.startswith('gpt-'):
            print("❌ Provider/model mismatch: Claude provider with GPT model")
            print("💡 Fix: Set EVALUATION_MODEL=claude-3-5-sonnet-20241022")
            return 1
        if not anthropic_key:
            print("❌ Claude provider selected but ANTHROPIC_API_KEY missing")
            return 1
    elif eval_provider == 'gpt':
        if eval_model.startswith('claude-'):
            print("❌ Provider/model mismatch: GPT provider with Claude model")
            print("💡 Fix: Set EVALUATION_MODEL=gpt-4o-mini")
            return 1
        if not openai_key:
            print("❌ GPT provider selected but OPENAI_API_KEY missing")
            return 1
    
    print("✅ Evaluation configuration valid")
    
    # Test import
    try:
        from opencanvas.config import Config
        Config.validate()
        print("✅ OpenCanvas configuration valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    print("\n🎉 All checks passed! Your configuration is ready.")
    print("\n💡 Next steps:")
    print("   opencanvas generate 'your topic' --purpose 'presentation type'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 