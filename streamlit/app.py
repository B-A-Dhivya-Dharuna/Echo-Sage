import streamlit as st
import base64
from streamlit_extras.switch_page_button import switch_page

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# Set background image
def set_bg():
    with open(r"C:\Users\B A DHIVYA DHARUNA\Downloads\Echo Sage AI\streamlit\Background pic.jpg", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}

        .main-container {{
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 3rem;
            margin: 2rem auto;
            max-width: 800px;
            color: white;
        }}

        .glass-panel {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 2rem;
            margin-top: 2rem;
            color: white;
        }}

        .try-btn {{
            background: violet;
            color: black;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 30px;
            font-weight: bold;
            margin-top: 2rem;
            cursor: pointer;
            display: block;
            margin-left: auto;
            margin-right: auto;
            transition: all 0.3s;
        }}

        .try-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            background: white;
            color: black;
        }}

        .button-row {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .feature-btn {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            color: white;
        }}

        .feature-btn:hover {{
            background: rgba(238,130,238,0.6);
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.2);
            color: white;
            outline: 2px solid white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# Header section
st.markdown("""
<div class="main-container">
    <h1 style="text-align: center">EchoSage</h1>
    <h3 style="text-align: center">Subtle brilliance, clear results.</h3>
    <p style="text-align: center">
        EchoSage listens between the lines. Whether you're a jobseeker crafting your narrative,
        a recruiter seeking quiet brilliance, or a curious mind prepping for the questions that matter — 
        EchoSage offers soft guidance with sharp insight. Not loud. Just wise.
    </p>
</div>
""", unsafe_allow_html=True)

# Role options
options = ["Job Seekers", "Recruiters", "Interview Prep"]

cols = st.columns(3)
for i, option in enumerate(options):
    with cols[i]:
        if st.button(option, key=f"option_{i}"):
            st.session_state.selected_option = option

# Handle selection
selected_option = st.session_state.selected_option
selected_content = ""

if selected_option == "Job Seekers":
    selected_content = """
    <div class="glass-content">
        <h3>🎯 Echo Sage for Job Seekers</h3>
        <p>Echo Sage is your AI-powered career companion designed to help you stand out in a competitive job market. Whether you're a fresher or a professional aiming for your dream role, Echo Sage gives you a personalized edge.</p>
        <h4>🔍 Key Features:</h4>
        <ul>
            <li>📄 Resume & JD Matching: Instantly analyze your resume against any job description.</li>
            <li>📊 ATS Scorecard: Understand how recruiters and Applicant Tracking Systems (ATS) view your resume.</li>
            <li>📌 Matched & Missing Skills: Learn what you're doing right and what to improve.</li>
            <li>📈 Ranked Resume Insights: See how you compare to other applicants.</li>
            <li>🎤 Mock Interview AI (Coming Soon): Practice with camera-enabled, real-time body language and speech feedback.</li>
        </ul>
    </div>
    """
elif selected_option == "Recruiters":
    selected_content = """
    <div class="glass-content">
        <h3>🧑‍💼 Echo Sage for Recruiters</h3>
        <p>Echo Sage is an AI-driven recruitment assistant designed to streamline the hiring process, ensuring you find the most relevant candidates faster and more effectively.</p>
        <h4>🚀 Key Features:</h4>
        <ul>
            <li>🧠 Intelligent Resume Screening: Quickly match resumes to job descriptions using advanced semantic analysis.</li>
            <li>📊 ATS Compatibility Scorecard: Instantly evaluate how well a candidate aligns with the role and industry expectations.</li>
            <li>📌 Skill Matching Engine: View matched and missing skills for each applicant to assess suitability at a glance.</li>
            <li>🏅 Resume Ranking: Automatically sort candidates by relevance — no more manual sifting.</li>
            <li>🎤 Interview Readiness Insights (Coming Soon): Get behavioral and communication analytics via camera-based AI.</li>
        </ul>
    </div>
    """
elif selected_option == "Interview Prep":
    selected_content = """
    <div class="glass-content">
        <h3>🔹 Interview Prep</h3>
        <p>COMING SOON!</p>
    </div>
    """

# Show feature content if selected
if selected_content:
    st.markdown(f"""
    <div class="glass-panel">
        {selected_content}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Use a regular button with custom styling
    if st.button("✨ Try Me", key="try_me_button"):
       # Replace the switch_page import and usage with:
        if st.session_state.selected_option == "Job Seekers":
            st.switch_page("./pages/1_Job_Seekers.py")
        elif st.session_state.selected_option == "Recruiters":
            st.switch_page("./pages/2_Recruiters.py")
        elif st.session_state.selected_option == "Interview Prep":
            st.switch_page("./pages/3_Interview_Prep.py")
