# app.py

import os
import gradio as gr
import cohere
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from pdfminer.high_level import extract_text
import docx
from io import BytesIO

# Read API keys securely from Environment Variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Function to extract text from resume
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
        return "⚠️ Error: API keys not loaded properly!"

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

        # Generate resume analysis
        response = co.generate(
            model="command",
            prompt=f"""You are an expert resume reviewer.
Analyze this resume for a {job_title} role:

Resume Excerpt: {resume_text[:2000]}

Job Description: {job_desc[:1000]}

Provide in the output:
1. Overall Match Score (0-100%)
2. Top 3 Missing Important Keywords
3. Two Improvement Tips
4. Pros of the Resume (at least 2 points)
5. Cons of the Resume (at least 2 points)

Make your response clear, use headings for each section.""",
            max_tokens=500
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
            <h3>Upload Your Resume & Instantly Get AI Insights!</h3>
        </div>
        """
    )

    resume_file = gr.File(label="Upload Resume (PDF or DOCX)", file_types=[".pdf", ".docx"])
    job_title = gr.Textbox(label="Job Title (e.g., Data Scientist)")
    analyze_btn = gr.Button("🔍 Analyze Resume")
    output_text = gr.Textbox(label="Resume Analysis", lines=20)

    analyze_btn.click(fn=analyze_resume, inputs=[resume_file, job_title], outputs=output_text)

# Special server settings for Render
demo.launch(server_name="0.0.0.0", server_port=8080)
