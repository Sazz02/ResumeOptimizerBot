# 🤖 Resume Optimizer Bot

![Resume Robot Logo](https://cdn-icons-png.flaticon.com/512/4712/4712027.png)

### Live Demo 🚀
🌐 [Click here to use the app!](https://resumeoptimizerbot.onrender.com/)

---

## 📄 Project Description

**Resume Optimizer Bot** is a smart AI-powered chatbot that analyzes your resume against a specific job title and provides:

- ✅ Match Score (0-100%)
- ✅ Top 3 Missing Important Keywords
- ✅ Two Improvement Tips
- ✅ Pros of your Resume
- ✅ Cons of your Resume

This tool helps job seekers **improve their resumes** for better job matching and better visibility to recruiters!

---
  
## ⚙️ How It Works

- Upload your **Resume** (PDF or DOCX).
- Enter your **desired Job Title** (e.g., "Data Scientist", "Software Engineer").
- Get a detailed **AI-driven analysis** including Match Score, Keywords, Pros & Cons instantly!

Behind the scenes:
- Resume text is extracted using **PDFMiner** or **Python-Docx**.
- **Job description** is fetched live from **Adzuna Jobs API**.
- **Cohere AI API** generates the full professional analysis.

---
  
## 🛠 Tech Stack Used

| Technology | Purpose |
|:-----------|:--------|
| Gradio      | Frontend UI (upload, inputs, outputs) |
| Render.com  | Cloud Hosting (Free forever tier) |
| Cohere AI   | Resume analysis & text generation |
| Adzuna Jobs API | Job description fetching |
| Python      | Backend Logic |
| PDFMiner    | PDF Text Extraction |
| python-docx | DOCX Text Extraction |

---

## 📦 Installation Guide (for local run)

1. Clone the repository:

```bash
git clone https://github.com/Sazz02/ResumeOptimizerBot.git
cd ResumeOptimizerBot

