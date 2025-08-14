import os
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai

from routers.home_router import router as home_router
from routers.chroma_router import router as chroma_router
from routers.gemini_router import router as gemini_router
from chroma_functionalities import initialize_collection
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Load environment variables early
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI & Chroma API",
    description="API with ChromaDB and Gemini AI integration",
    version="1.0.0"
)

# Include routers
app.include_router(home_router)
app.include_router(chroma_router)
app.include_router(gemini_router, prefix="/api")

# Configure Gemini API (only if key exists)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.error("❌ GEMINI_API_KEY is missing in .env file")
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=API_KEY)


# --- Main entry point ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
