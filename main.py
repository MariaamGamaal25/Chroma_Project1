# import os
# from fastapi import FastAPI
# from dotenv import load_dotenv
# import google.generativeai as genai

# from routers.home_router import router as home_router
# from routers.chroma_router import router as chroma_router
# from routers.gemini_router import router as gemini_router
# from chroma_functionalities import initialize_collection
# from utils.logger import setup_logger

# # Initialize logger
# logger = setup_logger(__name__)

# # Initialize FastAPI app
# app = FastAPI(
#     title="AI & Chroma API",
#     description="API with ChromaDB and Gemini AI integration",
#     version="1.0.0"
# )

# # Include routers
# app.include_router(home_router)
# app.include_router(chroma_router)
# app.include_router(gemini_router, prefix="/api")



# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting FastAPI server on http://0.0.0.0:8000")
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

import os
import uvicorn
from fastapi import FastAPI
from routers import chroma_router, gemini_router, home_router
from utils.enums import Endpoints
from chroma_functionalities import initialize_collection, get_chroma_collection

# --- FastAPI App Initialization ---
app = FastAPI(title="ChromaDB RAG API")

# --- Router Registration ---
app.include_router(chroma_router.router, prefix=Endpoints.API_PREFIX)

app.include_router(gemini_router.router, prefix=Endpoints.API_PREFIX)

app.include_router(home_router.router)

# --- Startup Event ---
# @app.on_event("startup")
# def startup_event():
#     """Initializes ChromaDB collection on application startup."""
#     initialize_collection()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
