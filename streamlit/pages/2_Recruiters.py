import streamlit as st
import os
import json
import requests
import re
import time
from docx import Document
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# ----------------------------------
# Config & constants
# ----------------------------------
st.set_page_config(page_title="📄 Resume Analyzer Pro", layout="wide")

# 🔐 GROQ API Config
# Prefer: st.secrets["GROQ_API_KEY"]
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "PUT_YOUR_KEY_IN_st.secrets_PLEASE")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------------------
# Sidebar (procedure + sorting help + features)
# ----------------------------------
st.sidebar.title("ℹ️ How this tool works")
st.sidebar.markdown("""
**Procedure**
1. Paste a **Job Description (JD)**.
2. Upload one or more **resumes** (`.pdf`/`.docx`).
3. Click **Analyze**.
4. Use the **Sort Order** switch to reorder the results.

**Sorting**
- **Ascending** = *Least to Best* (lowest score first)
- **Descending** = *Best to Least* (highest score first)

**Features**
- AI-based JD ↔ Resume matching
- Score (0–100), matched & missing skills
- One-line reason for the score
- Downloadable **PDF report** per resume
""")

sort_order = st.sidebar.radio(
    "Sort Order",
    ["Descending (Best → Least)", "Ascending (Least → Best)"],
    index=0
)

# ----------------------------------
# Helpers
# ----------------------------------
def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_json(content: str):
    """Try to coerce any 'extra-text + JSON' response into a clean JSON."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {"error": "Failed to parse extracted JSON", "raw_response": match.group()}
        return {"error": "No valid JSON found in response", "raw_response": content}

def get_resume_analysis(job_description, resume_text):
    prompt = f"""
You are a smart AI HR assistant. Compare the following resume with the job description and return the result as STRICT JSON ONLY with keys: score (0-100), matched_skills (list), missing_skills (list), and reason (string).

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

IMPORTANT: Return ONLY the JSON object, without any additional text or explanation before or after it.
"""

    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that returns only strict JSON, without any additional text or explanation."},
            {"role": "user", "content": prompt}
        ],
        # Some providers honor this, some ignore; we keep our regex fallback anyway.
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return extract_json(content)
    except requests.exceptions.HTTPError as e:
        # 429 / 400 etc.
        return {"error": f"HTTPError: {e}", "raw_response": response.text if 'response' in locals() else None}
    except Exception as e:
        return {"error": str(e)}

def generate_pdf_report(file_name, score, matched_skills, missing_skills, reason):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Resume Analysis Report — {file_name}")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Score: {score}%")
    y -= 25

    c.drawString(50, y, "Matched Skills:")
    y -= 20
    for skill in matched_skills:
        c.drawString(70, y, f"• {skill}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

    y -= 10
    c.drawString(50, y, "Missing Skills:")
    y -= 20
    for skill in missing_skills:
        c.drawString(70, y, f"• {skill}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

    y -= 10
    c.drawString(50, y, "Reason:")
    y -= 20
    for line in reason.split('. '):
        c.drawString(70, y, line.strip())
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

    c.save()
    buffer.seek(0)
    return buffer

# ----------------------------------
# Main UI
# ----------------------------------
st.title("📄 Resume Analyzer Pro")
st.write("Upload multiple resumes and get an AI-based match against the JD, with ranking and PDF export.")

job_description = st.text_area("📌 Paste Job Description Here", height=200)
uploaded_files = st.file_uploader("📁 Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# Maintain results between reruns (so you can re-sort without paying API again)
if "results" not in st.session_state:
    st.session_state.results = None

if st.button("🔍 Analyze"):
    if not job_description:
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        results = []
        st.subheader("📊 Analysis Results")

        for idx, file in enumerate(uploaded_files):
            try:
                if file.name.endswith('.docx'):
                    file_text = extract_text_from_docx(file)
                else:
                    file_text = extract_text_from_pdf(file)

                if not file_text.strip():
                    st.error(f"❌ {file.name}: Empty or unreadable content.")
                    continue

                with st.spinner(f"Analyzing {file.name}..."):
                    analysis = get_resume_analysis(job_description, file_text)

                if "error" in analysis:
                    st.error(f"❌ Error processing {file.name}: {analysis['error']}")
                    if "raw_response" in analysis and analysis["raw_response"]:
                        with st.expander(f"Raw response from API for {file.name}"):
                            st.code(analysis["raw_response"])
                else:
                    # Ensure minimal fields exist to avoid KeyErrors
                    analysis.setdefault("score", 0)
                    analysis.setdefault("matched_skills", [])
                    analysis.setdefault("missing_skills", [])
                    analysis.setdefault("reason", "No reason provided.")
                    results.append((file.name, analysis))

                # Simple throttle to avoid 429s (tune as needed)
                time.sleep(1.1)

            except Exception as e:
                st.error(f"❌ Failed to process {file.name}: {e}")

        # Save to session state for re-sorting later
        st.session_state.results = results

# ----------------------------------
# Show results (if we have any), sorted by chosen order
# ----------------------------------
if st.session_state.results:
    results = st.session_state.results

    reverse_sort = (sort_order.startswith("Descending"))
    results_sorted = sorted(results, key=lambda x: x[1]["score"], reverse=reverse_sort)

    st.subheader("📊 Ranked Resumes")
    for rank, (name, data) in enumerate(results_sorted, 1):
        st.markdown(f"### #{rank}. **{name}** — Score: **{data['score']}%**")
        st.success(f"✅ **Matched Skills:** {', '.join(data['matched_skills']) or 'None'}")
        st.error(f"❌ **Missing Skills:** {', '.join(data['missing_skills']) or 'None'}")
        st.info(f"📌 **Reason:** {data['reason']}")

        # PDF Report Download
        pdf = generate_pdf_report(name, data['score'], data['matched_skills'], data['missing_skills'], data['reason'])
        st.download_button(
            label="📥 Download Recruiter Report PDF",
            data=pdf,
            file_name=f"Report_{name}.pdf",
            mime="application/pdf",
            key=f"download_{name}"
        )
