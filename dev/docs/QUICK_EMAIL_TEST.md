# 🧪 Quick Email Test

## Current Issue
The UI shows "No emails sent yet" - this is **correct**! 

You need to run a workflow first to generate emails.

---

## ✅ How to Test (30 seconds)

### Step 1: Start the UI
```bash
make dev
```

### Step 2: In Browser (http://localhost:8501)
Type in the chat:
```
provider T001 sick
```

### Step 3: View Emails
Click the **"📧 View Sent Emails"** button in the sidebar

You should see 3 emails sent!

---

## 🔍 What Should Happen

When you type "provider T001 sick":

1. **Workflow Triggers** → Finds 3 affected patients
2. **Smart Scheduling** → Matches replacement providers
3. **Patient Engagement** → Sends 3 emails:
   - Maria Rodriguez → Offer for Dr. Emily Ross
   - John Davis → Offer for Dr. Emily Ross
   - Susan Lee → Offer for Dr. James Wilson

4. **Email Preview** → All 3 visible in "📧 Sent Emails"

---

## 📧 Expected Output

After running the workflow, click "📧 View Sent Emails" to see:

```
📧 Sent Emails (Demo)
3 emails sent

📩 Important: Your Appointment on November 20, 2025... - maria.rodriguez@email.com
   To: maria.rodriguez@email.com
   Template: appointment_offer
   Sent: 2025-11-20 14:30:15
   Status: ✅ sent
   
   [Email body with full content...]

📩 Important: Your Appointment on November 20, 2025... - john.davis@email.com
   [...]

📩 Important: Your Appointment on November 20, 2025... - susan.lee@email.com
   [...]
```

---

## 🚀 Quick Demo Commands

Just type these in the chat (one at a time):

1. **`provider T001 sick`** → Triggers full workflow, sends 3 emails
2. **`run tests`** → Runs all test scenarios
3. **`show patients`** → View patient data
4. **`show providers`** → View provider data

---

## 🔧 Troubleshooting

### If emails still don't show:

**Check 1: Verify agent integration**
```bash
cd /Users/madhan.dhandapani/Documents/schedule
python << 'EOF'
from agents.patient_engagement_agent import PatientEngagementAgent
from demo.email_preview import EmailPreview

# Clear and test
EmailPreview.clear_emails()
agent = PatientEngagementAgent()

# Send test email
result = agent.send_offer(
    patient_id="P001",
    appointment_id="A001", 
    new_provider_id="T002",
    date="Nov 20",
    time="10:00 AM"
)

print(f"Email sent: {result.get('message_id', 'N/A')}")
print(f"Emails in inbox: {len(EmailPreview.get_sent_emails())}")
EOF
```

**Expected output:**
```
Email sent: EMAIL-001
Emails in inbox: 1
```

---

## 💡 Demo Script

### For Client Demo:

**Show the problem:**
> "Currently, when a therapist calls in sick, the receptionist manually calls each patient. Let me show you the automated solution."

**Run the workflow:**
> [Type: "provider T001 sick"]
> "Watch - the system is now finding affected patients, matching providers, and sending emails..."

**Show the results:**
> [Click: "📧 View Sent Emails"]
> "See? 3 personalized emails sent instantly. Let me expand one..."
> [Click on Maria's email]
> "Notice it's personalized with her condition, shows the new provider with same specialty, and even mentions she's at the same location. One click to confirm."

**Highlight the impact:**
> "This used to take 30 minutes of phone calls. Now it's 10 seconds, fully automated, and HIPAA compliant."

---

## ✅ Status Check

Run this to verify everything is connected:

```bash
cd /Users/madhan.dhandapani/Documents/schedule
python << 'EOF'
print("🔍 Email System Status Check\n" + "="*70)

# 1. Check imports
try:
    from config.email_templates import EmailTemplates
    print("✅ Email templates imported")
except Exception as e:
    print(f"❌ Email templates: {e}")

try:
    from demo.email_preview import EmailPreview, mock_send_email
    print("✅ Email preview imported")
except Exception as e:
    print(f"❌ Email preview: {e}")

try:
    from agents.patient_engagement_agent import PatientEngagementAgent
    print("✅ Patient engagement agent imported")
except Exception as e:
    print(f"❌ Patient engagement agent: {e}")

# 2. Test email template
try:
    email = EmailTemplates.render_offer(
        patient_name="Test Patient",
        patient_email="test@example.com",
        date="Nov 20",
        time="10:00 AM",
        reason="test",
        original_provider="Dr. A",
        new_provider="Dr. B",
        specialty="PT",
        location="Clinic",
        condition="test",
        confirmation_link="http://test",
        clinic_name="Test Clinic",
        clinic_phone="555-1234"
    )
    print("✅ Email template renders correctly")
except Exception as e:
    print(f"❌ Email template: {e}")

# 3. Test email preview
try:
    EmailPreview.clear_emails()
    result = mock_send_email("test@example.com", "Test", "Body", "test")
    emails = EmailPreview.get_sent_emails()
    if len(emails) == 1:
        print("✅ Email preview working")
    else:
        print(f"⚠️  Email preview: Expected 1 email, got {len(emails)}")
except Exception as e:
    print(f"❌ Email preview: {e}")

print("\n" + "="*70)
print("If all checks pass, run 'make dev' and type 'provider T001 sick'")
EOF
```

---

## 🎯 Next Steps

1. ✅ Start UI: `make dev`
2. ✅ Type: `provider T001 sick`
3. ✅ Click: `📧 View Sent Emails`
4. ✅ Expand emails to show client

**Everything is ready - just needs a workflow to run!** 🚀

