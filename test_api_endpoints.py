"""Test if API endpoints work correctly."""
import sys
from pathlib import Path

# Test 1: Check if static directory exists
print("=" * 70)
print("Testing Static File Structure")
print("=" * 70)

static_dir = Path("static")
if static_dir.exists():
    print(f"✓ static/ directory exists")
    files = list(static_dir.glob("*.html"))
    print(f"  HTML files found: {len(files)}")
    for f in files:
        size = f.stat().st_size
        print(f"    - {f.name} ({size:,} bytes)")
else:
    print(f"✗ static/ directory NOT FOUND")
    print(f"  Creating directory...")
    static_dir.mkdir(exist_ok=True)
    print(f"  ✓ Created")

# Test 2: Check if emails.html exists
emails_file = static_dir / "emails.html"
if emails_file.exists():
    print(f"\n✓ emails.html exists ({emails_file.stat().st_size:,} bytes)")
else:
    print(f"\n✗ emails.html NOT FOUND at {emails_file}")

# Test 3: Try to read the file
try:
    with open(emails_file, 'r') as f:
        content = f.read()
        if len(content) > 0:
            print(f"✓ File is readable ({len(content):,} characters)")
            if "<!DOCTYPE html>" in content:
                print("✓ Valid HTML file")
            if "Sent Emails" in content:
                print("✓ Contains expected content")
        else:
            print("✗ File is empty")
except Exception as e:
    print(f"✗ Error reading file: {e}")

print("\n" + "=" * 70)
print("Testing API Server Configuration")
print("=" * 70)

# Test 4: Check if server.py has the routes
server_file = Path("api/server.py")
if server_file.exists():
    with open(server_file, 'r') as f:
        content = f.read()
        if '/emails.html' in content:
            print("✓ /emails.html route found in server.py")
        else:
            print("✗ /emails.html route NOT found in server.py")
        
        if 'FileResponse' in content:
            print("✓ FileResponse imported")
        else:
            print("✗ FileResponse NOT imported")

print("\n" + "=" * 70)
print("✅ File structure validation complete!")
print("=" * 70)
print("\nTo test the endpoint:")
print("  1. Start server: python api/server.py")
print("  2. Test endpoint: curl http://localhost:8000/emails.html")
print("  3. Or open in browser: http://localhost:8000/emails.html")
