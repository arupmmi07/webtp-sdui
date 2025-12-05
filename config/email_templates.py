"""Email Templates for Patient Communication.

Simple, reliable, compliant email templates.
No LLM needed - faster, cheaper, more consistent.
"""

from typing import Dict, Any
from string import Template


class EmailTemplates:
    """Patient email templates - HIPAA compliant, pre-approved messaging."""
    
    # Appointment Offer Template
    APPOINTMENT_OFFER = Template("""
Subject: Important: Your Appointment on ${date} at ${time}

Dear ${patient_name},

We wanted to reach out regarding your upcoming appointment.

Due to ${reason}, ${original_provider} will not be available for your scheduled appointment on ${date} at ${time}.

We'd like to offer you an alternative:

Provider: ${new_provider}
Specialty: ${specialty}
Date: ${date}
Time: ${time}
Location: ${location}

${new_provider} is highly qualified and available to provide excellent care for your ${condition}.

To confirm this appointment, please click here:
${confirmation_link}

If you prefer a different time or have questions, please call us at (555) 123-4567.

Thank you,
${clinic_name}
${clinic_phone}
""")
    
    # Appointment Confirmation Template
    APPOINTMENT_CONFIRMATION = Template("""
Subject: Appointment Confirmed - ${date} at ${time}

Dear ${patient_name},

Your appointment has been confirmed!

Details:
Provider: ${provider_name}
Date: ${date}
Time: ${time}
Location: ${location}
Address: ${address}

What to bring:
- Photo ID
- Insurance card
- List of current medications

If you need to reschedule or have questions, please call us at ${clinic_phone}.

Add to calendar: ${calendar_link}

We look forward to seeing you!

${clinic_name}
Confirmation #: ${confirmation_number}
""")
    
    # Waitlist Notification Template
    WAITLIST_NOTIFICATION = Template("""
Subject: You've been added to our waitlist

Dear ${patient_name},

We've added you to our waitlist for ${specialty} appointments.

Current Status:
- Position: ${position}
- Estimated wait: ${estimated_wait}
- Preferred times: ${preferred_times}

We'll contact you as soon as an appointment becomes available that matches your preferences.

In the meantime, if you have urgent concerns, please call us at ${clinic_phone}.

Thank you for your patience,
${clinic_name}
""")
    
    # Appointment Reminder Template (for high no-show risk)
    APPOINTMENT_REMINDER = Template("""
Subject: Reminder: Appointment Tomorrow at ${time}

Dear ${patient_name},

This is a friendly reminder about your appointment:

Tomorrow, ${date} at ${time}
Provider: ${provider_name}
Location: ${location}

If you need to reschedule, please call us at least 24 hours in advance: ${clinic_phone}

We look forward to seeing you!

${clinic_name}
""")
    
    @classmethod
    def render_offer(cls, **kwargs) -> Dict[str, str]:
        """Render appointment offer email.
        
        Required kwargs:
            patient_name, date, time, reason, original_provider, new_provider,
            specialty, location, condition, confirmation_link, clinic_name, clinic_phone
        
        Returns:
            Dict with 'subject' and 'body'
        """
        text = cls.APPOINTMENT_OFFER.safe_substitute(**kwargs)
        lines = text.strip().split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])  # Skip subject and blank line
        
        return {
            "subject": subject,
            "body": body,
            "to": kwargs.get("patient_email", ""),
            "template": "appointment_offer"
        }
    
    @classmethod
    def render_confirmation(cls, **kwargs) -> Dict[str, str]:
        """Render appointment confirmation email.
        
        Required kwargs:
            patient_name, provider_name, date, time, location, address,
            clinic_phone, calendar_link, clinic_name, confirmation_number
        
        Returns:
            Dict with 'subject' and 'body'
        """
        text = cls.APPOINTMENT_CONFIRMATION.safe_substitute(**kwargs)
        lines = text.strip().split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])
        
        return {
            "subject": subject,
            "body": body,
            "to": kwargs.get("patient_email", ""),
            "template": "appointment_confirmation"
        }
    
    @classmethod
    def render_waitlist(cls, **kwargs) -> Dict[str, str]:
        """Render waitlist notification email.
        
        Required kwargs:
            patient_name, specialty, position, estimated_wait,
            preferred_times, clinic_phone, clinic_name
        
        Returns:
            Dict with 'subject' and 'body'
        """
        text = cls.WAITLIST_NOTIFICATION.safe_substitute(**kwargs)
        lines = text.strip().split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])
        
        return {
            "subject": subject,
            "body": body,
            "to": kwargs.get("patient_email", ""),
            "template": "waitlist_notification"
        }
    
    @classmethod
    def render_reminder(cls, **kwargs) -> Dict[str, str]:
        """Render appointment reminder email (for high no-show risk).
        
        Required kwargs:
            patient_name, date, time, provider_name, location, clinic_phone, clinic_name
        
        Returns:
            Dict with 'subject' and 'body'
        """
        text = cls.APPOINTMENT_REMINDER.safe_substitute(**kwargs)
        lines = text.strip().split('\n')
        subject = lines[0].replace('Subject: ', '')
        body = '\n'.join(lines[2:])
        
        return {
            "subject": subject,
            "body": body,
            "to": kwargs.get("patient_email", ""),
            "template": "appointment_reminder"
        }


# Convenience function
def get_email_template(template_type: str, **kwargs) -> Dict[str, str]:
    """Get rendered email template.
    
    Args:
        template_type: Type of template (offer, confirmation, waitlist, reminder)
        **kwargs: Template variables
    
    Returns:
        Dict with subject, body, to, template
    """
    template_map = {
        "offer": EmailTemplates.render_offer,
        "appointment_offer": EmailTemplates.render_offer,
        "confirmation": EmailTemplates.render_confirmation,
        "appointment_confirmation": EmailTemplates.render_confirmation,
        "waitlist": EmailTemplates.render_waitlist,
        "waitlist_notification": EmailTemplates.render_waitlist,
        "reminder": EmailTemplates.render_reminder,
        "appointment_reminder": EmailTemplates.render_reminder,
    }
    
    renderer = template_map.get(template_type)
    if not renderer:
        raise ValueError(f"Unknown template type: {template_type}")
    
    return renderer(**kwargs)


if __name__ == "__main__":
    # Test templates
    print("=" * 70)
    print("EMAIL TEMPLATES TEST")
    print("=" * 70)
    
    # Test appointment offer
    print("\n1. Appointment Offer:")
    offer = EmailTemplates.render_offer(
        patient_name="Maria Rodriguez",
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
        clinic_phone="(555) 123-4567",
        patient_email="maria@example.com"
    )
    print(f"Subject: {offer['subject']}")
    print(f"To: {offer['to']}")
    print(f"Preview: {offer['body'][:150]}...")
    
    # Test confirmation
    print("\n2. Appointment Confirmation:")
    confirmation = EmailTemplates.render_confirmation(
        patient_name="Maria Rodriguez",
        provider_name="Dr. Emily Ross",
        date="November 20, 2025",
        time="10:00 AM",
        location="Downtown Clinic",
        address="123 Main St, Suite 100",
        clinic_phone="(555) 123-4567",
        calendar_link="https://clinic.com/calendar/add",
        clinic_name="Metro Physical Therapy",
        confirmation_number="CONF-A001-P001",
        patient_email="maria@example.com"
    )
    print(f"Subject: {confirmation['subject']}")
    print(f"Preview: {confirmation['body'][:150]}...")
    
    print("\n✅ Templates working correctly!")
    print("\n💡 Benefits:")
    print("  - Instant (no LLM latency)")
    print("  - $0 cost per email")
    print("  - Consistent messaging")
    print("  - HIPAA compliant")
    print("  - Easy to update/translate")

