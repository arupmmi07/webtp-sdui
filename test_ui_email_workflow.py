"""Test full workflow with UI email preview."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import create_workflow_orchestrator
from demo.email_preview import EmailPreview
import json

print("🧪 Testing Full Workflow with Email Preview")
print("=" * 70)

# Clear any previous emails
EmailPreview.clear_emails()
print("✅ Email inbox cleared")

# Initialize orchestrator
print("\n1. Initializing LangGraph workflow...")
orchestrator = create_workflow_orchestrator(engine="langgraph")
print("   ✅ Orchestrator initialized")

# Run workflow
print("\n2. Triggering workflow: 'provider T001 sick'...")
result = orchestrator.run("provider T001 sick")
print(f"   ✅ Workflow completed: {result.get('final_status')}")

# Check emails sent
print("\n3. Checking sent emails...")
emails = EmailPreview.get_sent_emails()
print(f"   ✅ Total emails sent: {len(emails)}")

# Display email summary
print("\n4. Email Summary:")
print("-" * 70)
for i, email in enumerate(emails, 1):
    print(f"\n📧 Email #{i}")
    print(f"   ID: {email['email_id']}")
    print(f"   To: {email['to']}")
    print(f"   Subject: {email['subject']}")
    print(f"   Template: {email['template']}")
    print(f"   Sent: {email['sent_at']}")
    print(f"   Preview: {email['body'][:100]}...")

print("\n" + "=" * 70)
print("✅ Workflow test completed!")
print(f"\n📊 Summary:")
print(f"   • Workflow Status: {result.get('final_status')}")
print(f"   • Emails Sent: {len(emails)}")
print(f"   • Affected Appointments: {result.get('trigger_result', {}).get('affected_count', 0)}")
print("\n💡 Next: Run 'make dev' and click '📧 View Sent Emails' to see in UI!")
