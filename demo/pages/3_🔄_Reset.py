"""Reset Page - Embedded HTML Reset Control"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Page config
st.set_page_config(
    page_title="🔄 Reset",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Demo Reset Control")

# Read the HTML file
html_file = Path(__file__).parent.parent.parent / "static" / "reset.html"

if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Embed the HTML
    components.html(html_content, height=600, scrolling=True)
else:
    st.error("Reset HTML file not found. Please ensure static/reset.html exists.")
    st.info("Expected location: static/reset.html")
