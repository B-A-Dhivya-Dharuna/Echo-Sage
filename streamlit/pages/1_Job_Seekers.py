import streamlit as st
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from docx import Document
import fitz  # PyMuPDF
import os
import requests
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# -------------------- Helper Functions --------------------

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyMuPDF."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file."""
    doc = Document(docx_file)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_missing_skills(feedback_text):
    """Parse missing skills section from feedback."""
    match = re.search(r"### Missing Skills or Keywords(.*?)(?=###|$)", feedback_text, re.DOTALL)
    if not match:
        return {}
    section = match.group(1)
    skill_impact = defaultdict(int)
    for line in section.strip().split('\n'):
        line = line.strip()
        if not line or (not line.startswith(('-', '*'))) or ':' not in line:
            continue
        try:
            skill, importance = map(str.strip, line.split(':', 1))
            skill = skill.lstrip("*- ")
            importance = importance.lower()
            impact = 5 if 'critical' in importance else 4 if 'important' in importance else 3
            skill_impact[skill] = impact
        except:
            continue
    return dict(skill_impact)

def analyze_formatting(resume_text):
    """Analyze resume formatting by checking standard sections"""
    sections = ["experience", "education", "skills", "projects"]
    found = sum(1 for section in sections if re.search(fr"\b{section}\b", resume_text, re.I))
    return min(100, int((found / len(sections)) * 100 + 20))  # Bonus for basic structure

def generate_ats_scorecard(resume_text, job_desc):
    """Generate a dynamic ATS scorecard based on text matching"""
    resume_text = resume_text.lower()
    job_desc = job_desc.lower()

    # Extract keyword-like terms (simple version)
    keywords = set(re.findall(r'\b\w+\b', job_desc))
    resume_words = set(re.findall(r'\b\w+\b', resume_text))

    # Keyword Matching Score
    matched_keywords = keywords.intersection(resume_words)
    keyword_score = int((len(matched_keywords) / len(keywords)) * 100) if keywords else 0

    # Experience Relevance (basic heuristic based on job role mention)
    role_keywords = ["experience", "developed", "worked", "managed", "projects"]
    experience_matches = sum(1 for word in role_keywords if word in resume_text)
    experience_score = min(100, experience_matches * 20)

    # Education Alignment
    education_keywords = ["bachelor", "master", "degree", "university", "college", "b.tech", "m.tech"]
    education_matches = sum(1 for word in education_keywords if word in resume_text)
    education_score = min(100, education_matches * 20)

    # Skills Coverage: look for common tech skills from JD in resume
    skills = re.findall(r'\b(python|java|sql|machine learning|data analysis|aws|azure|cloud|docker|react|node)\b', job_desc)
    skills = set(skills)
    matched_skills = [skill for skill in skills if skill in resume_text]
    skill_score = int((len(matched_skills) / len(skills)) * 100) if skills else 0

    # Formatting: basic check for key section headings
    formatting_score = analyze_formatting(resume_text)

    scores = {
        "Keyword Matching": keyword_score,
        "Experience Relevance": experience_score,
        "Education Alignment": education_score,
        "Skills Coverage": skill_score,
        "Formatting": formatting_score
    }

    explanations = {
        "Keyword Matching": f"{keyword_score}% of keywords from the job description were found in the resume.",
        "Experience Relevance": f"{experience_score}% relevance based on key experience indicators in your resume.",
        "Education Alignment": f"{education_score}% alignment with common educational qualifications.",
        "Skills Coverage": f"{skill_score}% of the technical skills from the job description are present in your resume.",
        "Formatting": f"{formatting_score}% score based on use of standard sections like Experience, Education, Skills, Projects."
    }

    overall_score = sum(scores.values()) // len(scores)
    hiring_probability = min(100, overall_score + 15)

    return {
        "scores": scores,
        "explanations": explanations,
        "overall_score": overall_score,
        "hiring_probability": hiring_probability
    }

def show_ats_scorecard(ats_data):
    """Display the ATS scorecard with visualizations"""
    st.subheader(f"Overall ATS Score: {ats_data['overall_score']}/100")
    st.progress(ats_data['overall_score']/100)
    
    st.subheader(f"Hiring Probability: {ats_data['hiring_probability']}%")
    st.markdown("""
    * 80-100%: Excellent match - Strong candidate for interview
    * 60-79%: Good match - Worth considering
    * Below 60%: Needs improvement
    """)
    
    st.markdown("---")
    st.subheader("Detailed Breakdown")
    
    for category, score in ats_data['scores'].items():
        with st.expander(f"{category} - {score}/100"):
            st.write(ats_data['explanations'][category])
            fig, ax = plt.subplots(figsize=(6, 1))
            ax.barh([category], [score], color='#4CC9F0')
            ax.set_xlim(0, 100)
            ax.set_xticks([])
            st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("Recommendations to Improve ATS Score")
    st.write("""
    1. Add more keywords from the job description naturally throughout your resume
    2. Quantify achievements with metrics and numbers
    3. Highlight relevant skills at the top of your resume
    4. Use standard section headings like 'Work Experience', 'Education', 'Skills'
    5. Avoid graphics and tables that ATS systems can't read
    """)

from fpdf import FPDF
import re
from datetime import datetime

def generate_pdf_report(feedback: str, ats_scorecard: dict, extracted_skills: list, recommendations=None) -> bytes:
    """Generate a PDF report with all analysis sections"""

    pdf = FPDF()
    pdf.add_page()
    width = pdf.w - 2 * pdf.l_margin

    # Header Font
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(width, 10, txt="Resume Analysis Report", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(width, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
    pdf.ln(10)

    # Feedback Sections
    feedback_sections = {
        "Summary": r"### Resume Feedback Summary(.*?)(?=###|$)",
        "Analysis": r"### Detailed Analysis(.*?)(?=###|$)",
        "Missing": r"### Missing Skills or Keywords(.*?)(?=###|$)",
        "Suggestions": r"### Suggestions to Improve(.*?)(?=###|$)",
        "Additional": r"### Additional Recommendations(.*?)(?=###|$)"
    }

    feedback_clean = re.sub(r'[^\x00-\x7F]+', '', feedback)
    parsed_feedback = {
        name: (re.search(pattern, feedback_clean, re.DOTALL).group(1).strip() 
               if re.search(pattern, feedback_clean, re.DOTALL) 
               else "No input available for this section.")
        for name, pattern in feedback_sections.items()
    }

    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="Executive Summary", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=parsed_feedback["Summary"])
    pdf.ln(5)

    # Key Metrics
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="Key Metrics", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(width, 10, txt=f"ATS Score: {ats_scorecard.get('overall_score', 'N/A')}/100", ln=1)
    pdf.cell(width, 10, txt=f"Hiring Probability: {ats_scorecard.get('hiring_probability', 'N/A')}%", ln=1)
    pdf.cell(width, 10, txt=f"Missing Skills: {len(extracted_skills) if extracted_skills else 0}", ln=1)
    pdf.ln(10)

    # Detailed Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="Detailed Analysis", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=parsed_feedback["Analysis"])
    pdf.ln(5)

    # Missing Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="Missing Skills", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=parsed_feedback["Missing"])
    pdf.ln(5)

    # ATS Scorecard
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="ATS Scorecard", ln=1)
    pdf.set_font("Arial", size=12)

    score_items = ats_scorecard.get('scores', {})
    explanations = ats_scorecard.get('explanations', {})

    for category, score in score_items.items():
        pdf.cell(width, 10, txt=f"{category}: {score}/100", ln=1)
        explanation = explanations.get(category, "No explanation available.")
        pdf.multi_cell(0, 10, txt=explanation)
        pdf.ln(3)

    # Recommendations
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(width, 10, txt="Recommendations", ln=1)
    pdf.set_font("Arial", size=12)

    if recommendations is None:
        recommendations = [
            "1. Add more keywords from the job description.",
            "2. Quantify achievements with metrics.",
            "3. Highlight relevant skills at the top.",
            "4. Use standard section headings.",
            "5. Avoid graphics and tables."
        ]

    for rec in recommendations:
        pdf.cell(width, 10, txt=rec, ln=1)

    # Footer with page number
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')

    return pdf.output(dest='S').encode('latin1')

# -------------------- GROQ API Integration --------------------

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def analyze_with_groq(resume_text, job_desc):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a professional resume screening assistant. Provide detailed feedback on how well the resume matches the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_desc}

Provide feedback in this structured format:

### Resume Feedback Summary
[Overall assessment of match quality]

### Detailed Analysis
1. **Strengths**: 
   - [List 3-5 key strengths]
2. **Weaknesses**:
   - [List 3-5 key weaknesses]

### Missing Skills or Keywords
[For each missing skill, specify importance level (Critical/Important/Nice-to-have)]
* Skill 1: Critical - [Explanation]
* Skill 2: Important - [Explanation]
* Skill 3: Nice-to-have - [Explanation]

### Suggestions to Improve
1. [Suggestion 1]
2. [Suggestion 2]
3. [Suggestion 3]

### Additional Recommendations
[Any other advice for the candidate]
"""

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

# -------------------- Streamlit App --------------------

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

with st.sidebar:
    st.title("Resume Analyzer")
    st.markdown("""
    **How to use:**
    1. Upload your resume (PDF/DOCX)
    2. Paste the job description
    3. Click "Run Analysis"
    """)
    st.markdown("---")
    st.markdown("""
    **Features:**
    - ATS score analysis
    - Hiring probability estimate
    - Personalized improvement suggestions
    """)

st.title("Resume Analysis Tool")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Your Resume (PDF or DOCX)", type=["pdf", "docx"])
with col2:
    job_desc = st.text_area("Paste Job Description", height=200)

if st.button("Run Comprehensive Analysis", use_container_width=True):
    if not resume_file:
        st.warning("Please upload a resume file first.")
        st.stop()

    with st.spinner("Analyzing your resume with AI..."):
        try:
            ext = resume_file.name.split('.')[-1].lower()
            if ext == 'pdf':
                resume_text = extract_text_from_pdf(resume_file)
            elif ext == 'docx':
                resume_text = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file type. Please upload a PDF or DOCX file.")
                st.stop()

            jd = job_desc.strip() or "Software Engineer position"
            feedback = analyze_with_groq(resume_text, jd)
            extracted_skills = extract_missing_skills(feedback)
            ats_scorecard = generate_ats_scorecard(resume_text, jd)

            st.session_state.update({
                "feedback": feedback,
                "extracted_skills": extracted_skills,
                "ats_scorecard": ats_scorecard,
                "analysis_done": True
            })
        except Exception as e:
            st.error(f"Analysis failed: {e}")

if st.session_state.analysis_done:
    st.markdown("---")
    st.header("Analysis Results")

    feedback_sections = {
        "Summary": r"### Resume Feedback Summary(.*?)(?=###|$)",
        "Analysis": r"### Detailed Analysis(.*?)(?=###|$)",
        "Missing": r"### Missing Skills or Keywords(.*?)(?=###|$)",
        "Suggestions": r"### Suggestions to Improve(.*?)(?=###|$)",
        "Additional": r"### Additional Recommendations(.*?)(?=###|$)"
    }

    parsed_feedback = {}
    for name, pattern in feedback_sections.items():
        match = re.search(pattern, st.session_state.feedback, re.DOTALL)
        parsed_feedback[name] = match.group(1).strip() if match else "Not available"

    with st.expander("Executive Summary", expanded=True):
        st.write(parsed_feedback["Summary"])
        m1, m2, m3 = st.columns(3)
        with m1:
            total_missing = len(st.session_state.extracted_skills)
            st.metric("Total Missing Skills", total_missing)
        with m2:
            st.metric("ATS Score", f"{st.session_state.ats_scorecard['overall_score']}/100")
        with m3:
            st.metric("Hiring Probability", f"{st.session_state.ats_scorecard['hiring_probability']}%")

    tab1, tab2, tab3 = st.tabs(["Detailed Analysis", "Missing Skills", "ATS Scorecard"])

    with tab1:
        st.write(parsed_feedback["Analysis"])

    with tab2:
        st.write(parsed_feedback["Missing"])
        st.write(parsed_feedback["Suggestions"])
        st.write(parsed_feedback["Additional"])

    with tab3:
        show_ats_scorecard(st.session_state.ats_scorecard)

    # Generate and download PDF report
    pdf_bytes = generate_pdf_report(
        st.session_state.feedback,
        st.session_state.ats_scorecard,
        st.session_state.extracted_skills
    )
    
    st.download_button(
        label="Download Full Analysis Report (PDF)",
        data=pdf_bytes,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )