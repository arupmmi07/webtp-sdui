"""Emails Page - Embedded HTML Email Viewer"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Page config
st.set_page_config(
    page_title="📧 Emails",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Patient Emails")

# Read the HTML file
html_file = Path(__file__).parent.parent.parent / "static" / "emails.html"

if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Embed the HTML
    components.html(html_content, height=800, scrolling=True)
else:
    st.error("Emails HTML file not found. Please ensure static/emails.html exists.")
    st.info("Expected location: static/emails.html")
