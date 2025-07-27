import streamlit as st
from PIL import Image
import base64

st.set_page_config(page_title="Interview Prep | Echo Sage", page_icon="🧠")

# Centered Coming Soon Message
st.markdown(
    """
    <div style='text-align: center; margin-top: 50px;'>
        <h1 style='font-size: 60px;'>🛠️ Coming Soon</h1>
        <p style='font-size: 20px;'>Our <strong>Interview Preparation</strong> tools are on their way!</p>
        <p style='font-size: 16px; color: gray;'>Mock Interviews • Curated Questions • AI-Powered Feedback</p>
        <img src='https://cdn.dribbble.com/users/15687/screenshots/15585399/media/eb8590f2b1c2fd1c2fa0dbd0aeb0ed8c.gif' width='500' />
        <p style='font-size: 16px; margin-top: 20px;'>Stay tuned – we’re building something amazing just for you!</p>
    </div>
    """,
    unsafe_allow_html=True
)
