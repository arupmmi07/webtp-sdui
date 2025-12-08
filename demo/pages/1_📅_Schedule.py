"""Schedule Page - Embedded HTML Calendar"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Page config
st.set_page_config(
    page_title="📅 Schedule",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Appointment Schedule")

# Read the HTML file
html_file = Path(__file__).parent.parent.parent / "static" / "schedule.html"

if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Embed the HTML
    components.html(html_content, height=800, scrolling=True)
else:
    st.error("Schedule HTML file not found. Please ensure static/schedule.html exists.")
    st.info("Expected location: static/schedule.html")
