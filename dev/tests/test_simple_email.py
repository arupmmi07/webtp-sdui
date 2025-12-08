"""Simple email test without full workflow."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.patient_engagement_agent import PatientEngagementAgent
from demo.email_preview import EmailPreview

print("🧪 Testing Email Integration in Agent")
print("=" * 70)

# Clear inbox
EmailPreview.clear_emails()

# Initialize agent
print("\n1. Initializing Patient Engagement Agent...")
agent = PatientEngagementAgent()
print("   ✅ Agent initialized")

# Send offer
print("\n2. Sending appointment offer...")
offer_result = agent.send_offer(
    patient_id="P001",
    appointment_id="A001",
    new_provider_id="T002",
    date="November 20, 2025",
    time="10:00 AM"
)
print(f"   ✅ Offer sent: {offer_result['message_id']}")
print(f"      Subject: {offer_result.get('email_subject', 'N/A')[:60]}...")

# Send confirmation
print("\n3. Sending confirmation...")
conf_result = agent.send_confirmation(
    patient_id="P002",
    appointment_id="A002",
    provider_id="T002",
    date="November 20, 2025",
    time="2:00 PM"
)
print(f"   ✅ Confirmation sent: {conf_result['message_id']}")
print(f"      Subject: {conf_result.get('email_subject', 'N/A')[:60]}...")

# Check inbox
print("\n4. Checking email inbox...")
emails = EmailPreview.get_sent_emails()
print(f"   ✅ Total emails: {len(emails)}")

for i, email in enumerate(emails, 1):
    print(f"\n   📧 Email #{i}:")
    print(f"      ID: {email['email_id']}")
    print(f"      To: {email['to']}")
    print(f"      Subject: {email['subject']}")
    print(f"      Template: {email['template']}")

print("\n" + "=" * 70)
print("✅ Email integration test passed!")
print("\n💡 Next: Run 'make dev' and click '📧 View Sent Emails' in UI!")
