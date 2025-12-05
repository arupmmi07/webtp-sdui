"""Email Preview Component for Streamlit.

Display emails in the UI for demo purposes.
No external service needed - perfect for client demos!
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime


class EmailPreview:
    """Render emails in Streamlit UI for demo purposes."""
    
    # In-memory store for demo (use st.session_state in production)
    _sent_emails: List[Dict[str, Any]] = []
    
    @classmethod
    def send_email(cls, email_data: Dict[str, str]) -> Dict[str, Any]:
        """Mock sending an email - stores it for preview instead.
        
        Args:
            email_data: Dict with 'to', 'subject', 'body', 'template'
        
        Returns:
            Dict with email_id, status, sent_at
        """
        email_record = {
            "email_id": f"EMAIL-{len(cls._sent_emails) + 1:03d}",
            "to": email_data.get("to", ""),
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "template": email_data.get("template", ""),
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "sent"
        }
        
        cls._sent_emails.append(email_record)
        
        return {
            "email_id": email_record["email_id"],
            "status": "sent",
            "sent_at": email_record["sent_at"]
        }
    
    @classmethod
    def get_sent_emails(cls) -> List[Dict[str, Any]]:
        """Get all sent emails."""
        return cls._sent_emails
    
    @classmethod
    def clear_emails(cls):
        """Clear all sent emails."""
        cls._sent_emails.clear()
    
    @classmethod
    def render_email_inbox(cls):
        """Render all sent emails in Streamlit UI."""
        st.markdown("### 📧 Sent Emails (Demo)")
        
        if not cls._sent_emails:
            st.info("No emails sent yet. Run a workflow to see emails!")
            return
        
        st.markdown(f"**{len(cls._sent_emails)} emails sent**")
        
        # Show most recent first
        for email in reversed(cls._sent_emails):
            cls._render_single_email(email)
    
    @classmethod
    def _render_single_email(cls, email: Dict[str, Any]):
        """Render a single email as a card."""
        with st.expander(f"📩 {email['subject'][:60]}... - {email['to']}", expanded=False):
            # Email metadata
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**To:** {email['to']}")
                st.markdown(f"**Template:** `{email['template']}`")
            with col2:
                st.markdown(f"**Sent:** {email['sent_at']}")
                st.markdown(f"**Status:** ✅ {email['status']}")
            
            st.markdown("---")
            
            # Email subject
            st.markdown(f"**Subject:** {email['subject']}")
            
            st.markdown("---")
            
            # Email body with styling
            st.markdown(f"""
            <div style='padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; color: #000;'>
                <pre style='white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: #000; margin: 0;'>{email['body']}</pre>
            </div>
            """, unsafe_allow_html=True)
    
    @classmethod
    def render_email_summary(cls):
        """Render a compact summary of sent emails."""
        if not cls._sent_emails:
            return
        
        st.markdown(f"**📧 {len(cls._sent_emails)} emails sent** | [View all](#sent-emails-demo)")
        
        # Show just the most recent 2
        for email in list(reversed(cls._sent_emails))[:2]:
            st.markdown(f"  • _{email['to']}_ - {email['subject'][:50]}...")


# Convenience function for use in workflow
def mock_send_email(to: str, subject: str, body: str, template: str = "") -> Dict[str, Any]:
    """Mock email sending - use in agents instead of real SMTP.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        template: Template name used
    
    Returns:
        Dict with email_id, status, sent_at
    """
    return EmailPreview.send_email({
        "to": to,
        "subject": subject,
        "body": body,
        "template": template
    })


if __name__ == "__main__":
    # Test the preview
    from config.email_templates import EmailTemplates
    
    # Send test emails
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
    
    EmailPreview.send_email(offer)
    
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
    
    EmailPreview.send_email(confirmation)
    
    print("✅ Test emails added!")
    print(f"Total emails: {len(EmailPreview.get_sent_emails())}")

