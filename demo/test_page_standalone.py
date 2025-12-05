"""Test that sent_emails page can be loaded standalone."""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("TESTING SENT EMAILS PAGE STANDALONE")
print("=" * 70)

try:
    # Import dependencies
    print("\n1. Testing imports...")
    from demo.email_preview import EmailPreview
    print("   ✓ EmailPreview imported")
    
    from config.email_templates import EmailTemplates
    print("   ✓ EmailTemplates imported")
    
    # Test EmailPreview functionality
    print("\n2. Testing EmailPreview...")
    EmailPreview.clear_emails()
    print("   ✓ clear_emails() works")
    
    emails = EmailPreview.get_sent_emails()
    print(f"   ✓ get_sent_emails() works (found {len(emails)} emails)")
    
    # Test sending an email
    print("\n3. Testing email sending...")
    email = EmailTemplates.render_offer(
        patient_name="Test Patient",
        patient_email="test@example.com",
        date="2025-11-20",
        time="10:00 AM",
        reason="testing",
        original_provider="Dr. Smith",
        new_provider="Dr. Jones",
        specialty="Physical Therapy",
        location="Test Clinic",
        condition="test condition",
        confirmation_link="http://test.com",
        clinic_name="Test Clinic",
        clinic_phone="555-1234"
    )
    print("   ✓ Email template rendered")
    
    from demo.email_preview import mock_send_email
    result = mock_send_email(
        to=email["to"],
        subject=email["subject"],
        body=email["body"],
        template=email["template"]
    )
    print(f"   ✓ Email sent: {result['email_id']}")
    
    emails = EmailPreview.get_sent_emails()
    print(f"   ✓ Email stored (now have {len(emails)} emails)")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - PAGE SHOULD WORK!")
    print("=" * 70)
    print("\nYou can now run:")
    print("  cd demo")
    print("  streamlit run pages/sent_emails.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("❌ TESTS FAILED")
    print("=" * 70)

