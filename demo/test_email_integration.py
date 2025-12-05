"""Quick test to verify email preview integration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo.email_preview import EmailPreview, mock_send_email
from config.email_templates import EmailTemplates

print("🧪 Testing Email Integration...")
print("=" * 70)

# Test 1: Send appointment offer
print("\n1. Sending appointment offer...")
offer = EmailTemplates.render_offer(
    patient_name="Maria Rodriguez",
    patient_email="maria.rodriguez@email.com",
    date="November 20, 2025",
    time="10:00 AM",
    reason="Dr. Johnson called in sick",
    original_provider="Dr. Sarah Johnson",
    new_provider="Dr. Emily Ross",
    specialty="Post-surgical knee rehabilitation",
    location="Downtown Clinic",
    condition="post-surgical knee recovery",
    confirmation_link="https://clinic.com/confirm?token=abc123",
    clinic_name="Metro Physical Therapy",
    clinic_phone="(555) 123-4567"
)
result = mock_send_email(offer["to"], offer["subject"], offer["body"], offer["template"])
print(f"   ✅ Email sent: {result['email_id']}")

# Test 2: Send confirmation
print("\n2. Sending confirmation...")
confirmation = EmailTemplates.render_confirmation(
    patient_name="John Davis",
    patient_email="john.davis@email.com",
    provider_name="Dr. Emily Ross",
    date="November 20, 2025",
    time="2:00 PM",
    location="Downtown Clinic",
    address="123 Main St, Suite 100",
    clinic_phone="(555) 123-4567",
    calendar_link="https://clinic.com/calendar/add",
    clinic_name="Metro Physical Therapy",
    confirmation_number="CONF-A002-P002"
)
result = mock_send_email(confirmation["to"], confirmation["subject"], confirmation["body"], confirmation["template"])
print(f"   ✅ Email sent: {result['email_id']}")

# Test 3: Check inbox
print("\n3. Checking inbox...")
emails = EmailPreview.get_sent_emails()
print(f"   ✅ Total emails in inbox: {len(emails)}")

# Test 4: Display details
print("\n4. Email details:")
for email in emails:
    print(f"   📧 {email['email_id']}")
    print(f"      To: {email['to']}")
    print(f"      Subject: {email['subject'][:50]}...")
    print(f"      Template: {email['template']}")
    print(f"      Sent: {email['sent_at']}")
    print()

print("=" * 70)
print("✅ Email integration test passed!")
print("\n💡 Next step: Run 'make dev' and click '📧 View Sent Emails' in UI")
