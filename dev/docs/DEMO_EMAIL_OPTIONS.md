# 📧 Email Demo Options for Client Presentation

## Quick Comparison

| Option | Setup Time | Cost | Realism | Best For |
|--------|-----------|------|---------|----------|
| **UI Preview** | 0 min | Free | ⭐⭐⭐ | Quick demos, offline |
| **MailHog** | 5 min | Free | ⭐⭐⭐⭐ | Realistic inbox, Docker |
| **Mailtrap** | 2 min | Free* | ⭐⭐⭐⭐⭐ | Professional demos |
| **Ethereal** | 1 min | Free | ⭐⭐⭐⭐ | No signup needed |

*Mailtrap: 100 emails/month free, 500/month on paid plan ($10/mo)

---

## ✅ Option 1: UI Preview (Recommended for Quick Demos)

**What it is:** Emails shown directly in Streamlit UI

**Pros:**
- ✅ Zero setup - works immediately
- ✅ No external dependencies
- ✅ Works offline
- ✅ Perfect for client demos
- ✅ Shows exactly what patients receive

**Cons:**
- ❌ Not a real inbox
- ❌ Can't test email clients

**Implementation:**
```python
# Already created: demo/email_preview.py
from demo.email_preview import mock_send_email, EmailPreview

# In your agent:
email = EmailTemplates.render_offer(...)
mock_send_email(
    to=email["to"],
    subject=email["subject"],
    body=email["body"],
    template=email["template"]
)

# In UI:
EmailPreview.render_email_inbox()  # Shows all sent emails
```

**Demo Flow:**
1. Receptionist types: "provider T001 sick"
2. System runs workflow
3. Click "📩 View Sent Emails" in sidebar
4. See all 3 emails with full content
5. Expand each to see patient name, subject, body

**Perfect for:**
- Quick client demos
- Showing email content
- No internet needed
- No setup complexity

---

## ✅ Option 2: MailHog (Recommended for Docker Demos)

**What it is:** Local SMTP server with web UI

**Pros:**
- ✅ Realistic email inbox
- ✅ Test actual SMTP sending
- ✅ Free, open source
- ✅ Works offline
- ✅ No signup needed
- ✅ Integrates with Docker Compose

**Cons:**
- ❌ Requires Docker
- ❌ Extra service to run

**Setup:**

### 1. Add to `docker-compose.yml`:
```yaml
  mailhog:
    image: mailhog/mailhog:latest
    container_name: schedule-mailhog
    ports:
      - "8025:8025"  # Web UI
      - "1025:1025"  # SMTP server
    networks:
      - schedule-network
```

### 2. Update `.env`:
```bash
# Email Settings (MailHog)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@metrophysicaltherapy.com
```

### 3. Create email sender (`utils/email_sender.py`):
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_FROM')
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
        server.send_message(msg)
```

### 4. Use in your agents:
```python
from utils.email_sender import send_email
from config.email_templates import EmailTemplates

email = EmailTemplates.render_offer(...)
send_email(email["to"], email["subject"], email["body"])
```

### 5. Demo:
```bash
make docker-up
# Open: http://localhost:8025
# Run workflow, see emails in MailHog UI!
```

**Perfect for:**
- Docker-based demos
- Testing real SMTP
- Multiple team members viewing emails
- More "production-like" feel

---

## ✅ Option 3: Mailtrap (Best for Professional Demos)

**What it is:** Cloud email testing service

**Pros:**
- ✅ Most realistic
- ✅ Beautiful UI
- ✅ Shows rendering in Gmail/Outlook
- ✅ Email analytics
- ✅ Multiple inboxes (dev/staging/demo)
- ✅ Can share with client

**Cons:**
- ❌ Requires signup
- ❌ 100 emails/month free limit
- ❌ Needs internet

**Setup:**

### 1. Sign up at https://mailtrap.io (free)

### 2. Create "Demo" inbox

### 3. Get SMTP credentials:
```
Host: sandbox.smtp.mailtrap.io
Port: 2525
Username: <your_username>
Password: <your_password>
```

### 4. Update `.env`:
```bash
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_username
SMTP_PASSWORD=your_password
SMTP_FROM=noreply@metrophysicaltherapy.com
```

### 5. Use same email sender as MailHog

**Perfect for:**
- Polished client presentations
- Testing email rendering
- Sharing inbox with stakeholders
- Professional demos

---

## ✅ Option 4: Ethereal Email (Fastest Temporary Solution)

**What it is:** nodemailer's test service

**Pros:**
- ✅ No signup needed
- ✅ Instant temporary inbox
- ✅ Shareable link

**Cons:**
- ❌ Expires after inactivity
- ❌ Less polished UI

**Setup:**

### 1. Get credentials via API:
```python
import requests
response = requests.post('https://api.nodemailer.com/user')
creds = response.json()
# Use creds['smtp'] credentials
```

### 2. View at provided web URL

**Perfect for:**
- One-off testing
- No commitment
- Quick validation

---

## 🎯 Recommendation for Your Demo

**Use Option 1 (UI Preview) + Option 2 (MailHog)**

### Why Both?

1. **UI Preview** - For quick in-person demos
   - No setup needed
   - Works offline
   - Client sees exactly what patients get
   - Perfect for "show me what happens" moments

2. **MailHog** - For "production-like" demos
   - Shows realistic email workflow
   - Clients can explore inbox themselves
   - Demonstrates integration capability
   - Easy Docker setup you already have

### Implementation Plan:

```python
# Create hybrid approach
USE_REAL_EMAIL = os.getenv("USE_REAL_EMAIL", "false") == "true"

def send_patient_email(to, subject, body, template):
    if USE_REAL_EMAIL:
        # Use MailHog/SMTP
        send_email(to, subject, body)
    else:
        # Use UI preview
        mock_send_email(to, subject, body, template)
```

### Demo Script:

**Phase 1: Quick Demo (UI Preview)**
```
1. "Let me show you what happens when a therapist calls in sick..."
2. Type: "provider T001 sick"
3. Click: "📩 View Sent Emails"
4. Show: "See? 3 emails sent instantly to affected patients"
5. Expand: "Here's exactly what Maria receives..."
```

**Phase 2: Realistic Demo (MailHog)**
```
1. "Now let me show you in a real email inbox..."
2. Open: http://localhost:8025
3. Run same workflow
4. Show: "These emails actually went through SMTP"
5. Click email: "You can see headers, formatting, everything"
```

---

## 📊 Feature Comparison

| Feature | UI Preview | MailHog | Mailtrap | Ethereal |
|---------|-----------|---------|----------|----------|
| View email body | ✅ | ✅ | ✅ | ✅ |
| Real SMTP | ❌ | ✅ | ✅ | ✅ |
| Works offline | ✅ | ✅ | ❌ | ❌ |
| No signup | ✅ | ✅ | ❌ | ✅ |
| Share with client | ❌ | ❌* | ✅ | ✅ |
| Email analytics | ❌ | ❌ | ✅ | ❌ |
| Docker integration | ✅ | ✅ | ❌ | ❌ |
| Professional UI | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

*MailHog can be shared if deployed, but typically local only

---

## 🚀 Quick Start Commands

### Option 1 (UI Preview):
```bash
# No setup needed!
make dev
# Click "📩 View Sent Emails" in UI
```

### Option 2 (MailHog):
```bash
# Add to docker-compose.yml (I can do this)
make docker-up
# Open http://localhost:8025
```

### Option 3 (Mailtrap):
```bash
# Sign up at mailtrap.io
# Add credentials to .env
make dev
# Check Mailtrap inbox
```

---

## 💡 My Recommendation

**Start with UI Preview (Option 1)** - I've already created the code!

It's:
- ✅ Instant (no setup)
- ✅ Perfect for demos
- ✅ Shows exact email content
- ✅ Works offline

**Then add MailHog (Option 2)** if client wants to see "real" emails.

Would you like me to:
1. ✅ Add email preview to the Streamlit UI? (5 min)
2. ⏳ Add MailHog to Docker Compose? (5 min)
3. ⏳ Create hybrid email sender? (3 min)

Let me know which approach you prefer! 🎯

