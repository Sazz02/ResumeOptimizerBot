# app.py

import gradio as gr
import cohere
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from pdfminer.high_level import extract_text
import docx
from io import BytesIO

# Globals to store API keys
COHERE_API_KEY = None
ADZUNA_APP_ID = None
ADZUNA_APP_KEY = None
co = None

# Function to set API keys
def set_api_keys(cohere_key, adzuna_id, adzuna_key):
    global COHERE_API_KEY, ADZUNA_APP_ID, ADZUNA_APP_KEY, co
    COHERE_API_KEY = cohere_key.strip()
    ADZUNA_APP_ID = adzuna_id.strip()
    ADZUNA_APP_KEY = adzuna_key.strip()

    try:
        co = cohere.Client(COHERE_API_KEY)
        
        # Test Cohere API by making a small call
        test_response = co.generate(
            model="command",
            prompt="Say hello",
            max_tokens=5
        )
        if test_response:
            return "✅ API keys set successfully! Now proceed to Step 2.", gr.update(visible=True)
    except Exception as e:
        return f"❌ Error validating API keys: {str(e)}", gr.update(visible=False)

# Function to extract resume text
def extract_resume_text(file):
    if file.name.endswith('.docx'):
        doc = docx.Document(file)
        text = " ".join([para.text for para in doc.paragraphs])
    else:
        text = extract_text(file)
    return text

# Function to analyze resume
def analyze_resume(file, job_title):
    if not co:
        return "⚠️ Please enter and validate your API keys first!"

    try:
        if not file:
            return "⚠️ Please upload a resume first!"

        resume_text = extract_resume_text(file)

        # Fetch job description
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&what={job_title}"
            response = requests.get(url)
            job_desc = response.json()["results"][0]["description"]
        except Exception as e:
            job_desc = f"⚠️ Failed to fetch job description: {str(e)}"

        # AI analysis
        response = co.generate(
            model="command",
            prompt=f"""Analyze this resume for a {job_title} role:

            Resume Excerpt: {resume_text[:2000]}

            Job Description: {job_desc[:1000]}

            Provide:
            1. Match score (0-100%)
            2. Top 3 missing keywords
            3. Two improvement tips""",
            max_tokens=300
        )

        return f"📋 Resume Analysis:\n\n{response.generations[0].text}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio UI
with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="blue")) as demo:
    gr.Markdown(
        """
        <div style='text-align: center;'>
            <img src='https://cdn-icons-png.flaticon.com/512/4712/4712027.png' width='120px'/>
            <h1>🤖 Resume Robot</h1>
            <h3>Securely Upload Your Resume & Get AI Insights!</h3>
        </div>
        """
    )

    with gr.Tab("🔐 Step 1: Enter API Keys"):
        with gr.Row():
            cohere_key = gr.Textbox(label="Cohere API Key", type="password", placeholder="Paste your Cohere API key here")
            adzuna_id = gr.Textbox(label="Adzuna App ID", type="password", placeholder="Paste your Adzuna App ID here")
            adzuna_key = gr.Textbox(label="Adzuna App Key", type="password", placeholder="Paste your Adzuna App Key here")
        
        submit_keys = gr.Button("✅ Save API Keys and Validate")
        keys_output = gr.Textbox(label="Status", interactive=False)

        resume_section = gr.Column(visible=False)

        submit_keys.click(set_api_keys, inputs=[cohere_key, adzuna_id, adzuna_key], outputs=[keys_output, resume_section])

    with gr.Tab("📄 Step 2: Upload Resume and Analyze"):
        with resume_section:
            resume_file = gr.File(label="Upload Resume (PDF or DOCX)", file_types=[".pdf", ".docx"])
            job_title = gr.Textbox(label="Job Title (e.g., Data Scientist)")
            analyze_btn = gr.Button("🔍 Analyze Resume")
            output_text = gr.Textbox(label="Resume Analysis", lines=15)

            analyze_btn.click(fn=analyze_resume, inputs=[resume_file, job_title], outputs=output_text)

# 👉 Special Render.com server settings
demo.launch(server_name="0.0.0.0", server_port=8080)
