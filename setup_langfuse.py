#!/usr/bin/env python3
"""
Setup script to configure Langfuse environment variables for tracing.

This script helps you set up Langfuse tracing for the scheduling system.
"""

import os
from pathlib import Path

def setup_langfuse():
    """Setup Langfuse environment variables."""
    
    print("🔧 Langfuse Setup for Scheduling System")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(__file__).parent / '.env'
    
    print(f"\n📁 Environment file: {env_file}")
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Read existing .env
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check for existing Langfuse variables
        has_langfuse = any(line.startswith('LANGFUSE_') for line in content.split('\n'))
        
        if has_langfuse:
            print("✅ Langfuse variables already configured in .env")
            print("\n🔍 Current Langfuse configuration:")
            for line in content.split('\n'):
                if line.startswith('LANGFUSE_'):
                    key = line.split('=')[0]
                    print(f"   {key}: {'✅ Set' if '=' in line and line.split('=')[1].strip() else '❌ Empty'}")
        else:
            print("⚠️  No Langfuse variables found in .env")
            print("\n📝 Add these variables to your .env file:")
            print_langfuse_template()
    else:
        print("❌ .env file not found")
        print("\n📝 Create a .env file with these variables:")
        print_langfuse_template()
    
    print("\n🌐 How to get Langfuse credentials:")
    print("1. Go to https://cloud.langfuse.com (or https://us.cloud.langfuse.com for US)")
    print("2. Create an account or log in")
    print("3. Create a new project")
    print("4. Go to Settings → API Keys")
    print("5. Create new API credentials")
    print("6. Copy the Public Key and Secret Key to your .env file")
    
    print("\n🚀 After setup:")
    print("1. Restart your web server")
    print("2. Test provider unavailable (3+ days)")
    print("3. Check Langfuse dashboard for traces")

def print_langfuse_template():
    """Print Langfuse environment variable template."""
    template = """
# Langfuse Configuration for LLM Tracing
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
# LANGFUSE_HOST=https://us.cloud.langfuse.com  # Uncomment for US region
"""
    print(template)

def check_current_env():
    """Check current environment variables."""
    print("\n🔍 Current Environment Variables:")
    langfuse_vars = ['LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_HOST']
    
    for var in langfuse_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var:
                display_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            else:
                display_value = value
            print(f"   {var}: ✅ {display_value}")
        else:
            print(f"   {var}: ❌ Not set")

if __name__ == "__main__":
    setup_langfuse()
    check_current_env()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("💡 Tip: Set environment variables in .env file for persistence")
