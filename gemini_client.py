import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is not configured in .env file")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Create a reusable model instance
_model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(question: str) -> str:
    """
    Sends a question to the Gemini API and returns the answer as plain text.
    """
    try:
        response = _model.generate_content(question)
        return response.text.strip()
    except Exception as e:
        return f"Error from Gemini API: {str(e)}"
    

    
