# 🤖 Gemini FAQ Chatbot

AI-powered FAQ chatbot built using **FastAPI** and **Azure OpenAI**.  
The system answers questions using structured FAQ data and falls back to intelligent web search when needed.

---

## 🚀 Overview

This project demonstrates an enterprise-style chatbot workflow:

- FAQ-based response generation
- Azure OpenAI integration
- Fallback search using DuckDuckGo
- FastAPI REST backend
- Static web interface

The goal is to provide accurate answers while maintaining secure, environment-based configuration.

---

## 🧱 Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Azure OpenAI
- **Frontend:** HTML, CSS, JavaScript
- **Search Integration:** DuckDuckGo
- **Configuration:** dotenv (.env)

---

## 📁 Project Structure
├── main.py
├── utils.py
├── faq_data.py
├── static/
├── requirements.txt
└── Dockerfile


---

## ⚙️ Setup

### 1. Clone Repository
git clone https://github.com/Nancy2107/gemini-faq-chatbot.git
cd gemini-faq-chatbot


### 2. Create `.env` File
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2023-12-01-preview


### 3. Install Dependencies

pip install -r requirements.txt


### 4. Run Server

python -m uvicorn main:app --reload


## 👩‍💻 Author

Nancy Sheth  
Full Stack Developer