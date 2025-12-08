"""Test if Streamlit can find the pages."""
import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print()

# Check from demo directory
demo_dir = "demo"
if os.path.exists(demo_dir):
    print(f"✓ {demo_dir}/ exists")
    pages_dir = os.path.join(demo_dir, "pages")
    if os.path.exists(pages_dir):
        print(f"✓ {pages_dir}/ exists")
        files = os.listdir(pages_dir)
        print(f"  Files in pages/: {files}")
        
        # Check specific files
        sent_emails = os.path.join(pages_dir, "sent_emails.py")
        appointment_schedule = os.path.join(pages_dir, "appointment_schedule.py")
        
        if os.path.exists(sent_emails):
            print(f"✓ {sent_emails} exists")
            print(f"  Size: {os.path.getsize(sent_emails)} bytes")
        else:
            print(f"✗ {sent_emails} NOT FOUND")
            
        if os.path.exists(appointment_schedule):
            print(f"✓ {appointment_schedule} exists")
            print(f"  Size: {os.path.getsize(appointment_schedule)} bytes")
        else:
            print(f"✗ {appointment_schedule} NOT FOUND")
    else:
        print(f"✗ {pages_dir}/ NOT FOUND")
else:
    print(f"✗ {demo_dir}/ NOT FOUND")

print()
print("Testing Streamlit page detection...")
print("Expected path from chat_ui.py: 'pages/sent_emails.py'")
print()

# Try to import streamlit
try:
    import streamlit as st
    print(f"✓ Streamlit imported successfully")
    print(f"  Version: {st.__version__}")
except ImportError as e:
    print(f"✗ Could not import streamlit: {e}")

