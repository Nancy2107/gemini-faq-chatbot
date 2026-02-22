
from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from fastapi.responses import FileResponse

from pydantic import BaseModel

from openai import AzureOpenAI

from dotenv import load_dotenv

import os

from utils import get_best_faq_answer

from utils import search_duckduckgo_for_answer, search_with_conversation_flow, search_duckduckgo_web_scraping

# Load your Azure OpenAI configuration

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

if not AZURE_OPENAI_API_KEY:

    raise ValueError("AZURE_OPENAI_API_KEY is missing from environment variables")

if not AZURE_OPENAI_ENDPOINT:

    raise ValueError("AZURE_OPENAI_ENDPOINT is missing from environment variables")

# Initialize Azure OpenAI client

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Initialize FastAPI app

app = FastAPI()

# CORS configuration

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],  # Or ["*"] to allow all (not recommended in prod)

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

# Mount static files (your chatbot folder)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Request models

class FAQRequest(BaseModel):

    question: str
 
class SearchConfirmRequest(BaseModel):

    question: str

    confirm: bool = True

# Root route

@app.get("/")

def home():

    return FileResponse('static/index.html')

# FAQ chatbot route with enhanced fallback sequence

@app.post("/api/faq")

def answer_faq(request: FAQRequest):

    try:

        question = request.question.strip()

        if not question:

            raise HTTPException(status_code=400, detail="No question provided.")

        print(f"Received question: {question}")  # Debug log

        # Check for confirmation keywords

        confirmation_keywords = ["yes", "go ahead", "sure", "ok", "okay", "proceed", "search"]

        if any(keyword in question.lower() for keyword in confirmation_keywords):

            # For confirmation, try to provide general guidance

            print("User confirmed - providing general guidance")

            from utils import generate_direct_answer

            guidance_answer = generate_direct_answer(question)

            return {"answer": guidance_answer, "needs_confirmation": False}

        # First try FAQ

        answer = get_best_faq_answer(question, client)

        print(f"Initial FAQ answer: {answer}")  # Debug log

        # Check if we need to search the web

        if "Sorry, I can only answer based on the official ACS FAQs" in answer:

            print("No FAQ match found, starting fallback sequence...")

            # Use the enhanced fallback sequence: Instant API → Web scraping → Direct answer

            fallback_answer = search_duckduckgo_for_answer(question)
            print("Final Answer Sent to Frontend:", fallback_answer)

            return {"answer": fallback_answer, "needs_confirmation": False}

        return {"answer": answer, "needs_confirmation": False}
        

    except Exception as e:

        print(f"Error in answer_faq: {str(e)}")  # Debug log

        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
 
 
# Enhanced endpoint for direct web search with fallback sequence

@app.post("/api/websearch")

def enhanced_web_search(request: SearchConfirmRequest):

    try:

        question = request.question.strip()

        if not question:

            raise HTTPException(status_code=400, detail="No question provided.")

        if request.confirm:

            print(f"Enhanced web search with fallback sequence for: {question}")

            # Use the complete fallback sequence

            result = search_duckduckgo_for_answer(question)

            return {"answer": result, "needs_confirmation": False}

        else:

            return {"answer": "Okay, I'll only search the ACS FAQs for your questions.", "needs_confirmation": False}

    except Exception as e:

        print(f"Error in enhanced_web_search: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Add this for testing DuckDuckGo search directly

@app.post("/api/search")

def search_web(request: FAQRequest):

    try:

        question = request.question.strip()

        if not question:

            raise HTTPException(status_code=400, detail="No question provided.")

        print(f"Direct web search for: {question}")

        result = search_duckduckgo_for_answer(question)

        return {"answer": result}

    except Exception as e:

        print(f"Error in search_web: {str(e)}")

        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Add this for testing

@app.get("/test")

def test():

    return {"message": "API is working!"}

# Health check endpoint

@app.get("/health")

def health_check():

    return {"status": "healthy"}
 