# app.py

import os
import gradio as gr
import cohere
import requests
from pdfminer.high_level import extract_text
import docx

# -------------------- ENV VARIABLES --------------------
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Initialize Cohere (NEW CLIENT)
co = cohere.ClientV2(COHERE_API_KEY)

# -------------------- RESUME TEXT EXTRACTION --------------------
def extract_resume_text(file):
    try:
        if file.name.endswith(".docx"):
            document = docx.Document(file.name)
            text = "\n".join([para.text for para in document.paragraphs])
        else:
            text = extract_text(file.name)
        return text
    except Exception as e:
        return f"Error reading file: {str(e)}"

# -------------------- MAIN ANALYSIS FUNCTION --------------------
def analyze_resume(file, job_title):

    if not COHERE_API_KEY:
        return "⚠️ Cohere API Key not found in Render Environment Variables."

    if file is None:
        return "⚠️ Please upload a resume first."

    try:
        resume_text = extract_resume_text(file)

        # ---------------- JOB DESCRIPTION FROM ADZUNA ----------------
        job_desc = "No job description available."
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&what={job_title}"
            res = requests.get(url, timeout=10)
            data = res.json()
            if "results" in data and len(data["results"]) > 0:
                job_desc = data["results"][0]["description"]
        except Exception:
            job_desc = "Could not fetch job description."

        # ---------------- PROMPT ----------------
        prompt = f"""
You are an expert ATS Resume Reviewer.

Analyze the following resume for a {job_title} role.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_desc[:1000]}

Provide:
1) Overall Match Score (0-100%)
2) Top 3 Missing Keywords
3) Two Improvement Tips
4) Resume Pros (at least 2 points)
5) Resume Cons (at least 2 points)

Format with proper headings.
"""

        # ---------------- COHERE CHAT API (FIXED PART) ----------------
        response = co.chat(
            model="command-r-plus",
            messages=[
                {"role": "system", "content": "You are a professional ATS resume optimization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=600
        )

        analysis = response.message.content[0].text

        return f"📋 Resume Analysis\n\n{analysis}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# -------------------- GRADIO UI --------------------
with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="blue")) as demo:

    gr.Markdown(
        """
        <div style='text-align:center'>
            <img src='https://cdn-icons-png.flaticon.com/512/4712/4712027.png' width='120'/>
            <h1>🤖 Resume Robot</h1>
            <h3>Upload Your Resume & Instantly Get AI Insights!</h3>
        </div>
        """
    )

    resume_file = gr.File(label="Upload Resume (PDF or DOCX)", file_types=[".pdf", ".docx"])
    job_title = gr.Textbox(label="Job Title (Example: Data Scientist)")

    analyze_btn = gr.Button("🔍 Analyze Resume")
    output_text = gr.Textbox(label="Resume Analysis", lines=20)

    analyze_btn.click(fn=analyze_resume, inputs=[resume_file, job_title], outputs=output_text)

# Render Server Launch
demo.launch(server_name="0.0.0.0", server_port=8080)
