# 📧 Email Personalization Setup

## 🎯 Overview

The system now supports two modes for email personalization:

1. **LangFuse Prompt** (Default) - Uses LLM-powered personalization via LangFuse
2. **Template** - Uses simple template-based messages

---

## 🔧 Configuration

### Environment Variable

Add to your `.env` file:

```bash
# Email Personalization
USE_LANGFUSE_EMAIL_PROMPT=true   # Set to 'false' to use template instead
```

### LangFuse Setup

1. **Create Prompt in LangFuse:**
   - Name: `patient-engagement-message`
   - Label: `production`
   - Type: `Chat` or `Text`

2. **Enhanced Prompt Template:**

See `langfuse_email_prompt_template.txt` for the complete enhanced prompt.

**Key Features:**
- Comprehensive patient context (condition, preferences)
- Detailed provider information (specialty, experience, availability)
- Clear tone & style guidelines with examples
- Step-by-step message structure
- Explicit constraints (no links, proper length, personalization)

**Quick Copy:** Use the content from `langfuse_email_prompt_template.txt` - it's ready to paste into LangFuse!

3. **Available Variables:**
   - `{{message_type}}` - "APPOINTMENT_OFFER", "APPOINTMENT_CONFIRMATION", etc.
   - `{{patient_name}}` - Patient's name
   - `{{original_provider}}` - Name of original provider
   - `{{new_provider}}` - Name of new provider
   - `{{appointment_date}}` - Appointment date
   - `{{appointment_time}}` - Appointment time
   - `{{location}}` - Provider location
   - `{{channel}}` - Communication channel (email, sms, etc.)

---

## 🔄 Switching Modes

### Use LangFuse Prompt (Default):
```bash
USE_LANGFUSE_EMAIL_PROMPT=true
```

### Use Template:
```bash
USE_LANGFUSE_EMAIL_PROMPT=false
```

---

## 📝 Example Outputs

### LangFuse Prompt (Personalized):
```
Hi Maria,

I hope this message finds you well. I wanted to personally reach out regarding 
your upcoming appointment.

Unfortunately, Dr. Sarah Johnson has an unexpected absence and won't be able 
to see you on November 24, 2025 at 9:00 AM. However, I have great news - we've 
found an excellent alternative provider who matches your preferences perfectly.

I'd like to offer you an appointment with:

👨‍⚕️ Dr. Emily Ross
📋 Sports Physical Therapy
📅 November 24, 2025 at 9:00 AM
🏥 Metro PT Main Clinic

Dr. Emily Ross specializes in post-surgical knee rehabilitation and has extensive 
experience with cases like yours. She's available at your preferred time and 
location, and I believe she'll provide you with the same high-quality care 
you've come to expect.

Please let us know if this works for you by clicking the link below.

Thank you for your understanding!
Metro Physical Therapy
```

### Template (Simple):
```
Hi Maria,

Your therapist has an unexpected absence. We'd like to reassign your appointment to:

👨‍⚕️ Dr. Emily Ross
📋 Sports Physical Therapy
📅 November 24, 2025 at 9:00 AM

This provider is available and matches your needs based on your preferences.

Please confirm or decline:
(Links will be provided in the email)

Thank you!
Metro Physical Therapy
```

---

## 🚀 Testing

1. **Set the flag:**
   ```bash
   USE_LANGFUSE_EMAIL_PROMPT=true
   ```

2. **Restart the system:**
   ```bash
   make restart
   ```

3. **Trigger a workflow:**
   ```bash
   curl -X POST http://localhost:8000/api/trigger-workflow \
     -H "Content-Type: application/json" \
     -d '{
       "trigger_type": "provider_unavailable",
       "provider_id": "T001",
       "start_date": "2025-11-24",
       "end_date": "2025-11-24"
     }'
   ```

4. **Check emails:**
   - View at: http://localhost:8000/emails.html
   - Check logs for: `[EMAIL] ✅ Using LangFuse prompt for personalization`

---

## 🐛 Troubleshooting

### LangFuse prompt not being used:
- Check `.env` file has `USE_LANGFUSE_EMAIL_PROMPT=true`
- Verify LangFuse credentials are set
- Check logs for: `[AGENT] Email Personalization: LangFuse Prompt`
- Ensure prompt exists in LangFuse with name `patient-engagement-message` and label `production`

### Falling back to template:
- Check logs for: `[EMAIL] Warning: LangFuse prompt failed: ...`
- Verify LangFuse API keys are correct
- Ensure prompt is published with label `production`

### Template being used:
- If `USE_LANGFUSE_EMAIL_PROMPT=false`, template will be used
- Check logs for: `[AGENT] Email Personalization: Template`

---

## 💡 Benefits

**LangFuse Prompt:**
- ✅ Personalized messages tailored to each patient
- ✅ Context-aware (considers patient preferences, condition, etc.)
- ✅ More natural, empathetic tone
- ✅ Can adapt to different communication channels

**Template:**
- ✅ Faster (no LLM call)
- ✅ Consistent messaging
- ✅ Lower cost
- ✅ More predictable output

---

**Status**: ✅ **Email Personalization Ready!**

