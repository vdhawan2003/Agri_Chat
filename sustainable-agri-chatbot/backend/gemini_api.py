import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def generate_gemini_response(prompt, context=""):
    """Uses Gemini 2.5 Flash model for text generation."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        full_prompt = f"Context:\n{context}\n\nUser Query:\n{prompt}\n\nAnswer clearly and helpfully."
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Error] {str(e)}"
