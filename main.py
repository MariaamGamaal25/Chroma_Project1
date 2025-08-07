from fastapi import FastAPI
from routers.home_router import router as home_router
from routers.chroma_router import router as chroma_router
from chroma_functionalities import initialize_collection
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize the FastAPI application
app = FastAPI()

# Include routers
app.include_router(home_router)
app.include_router(chroma_router)

# --- Main entry point for running the server ---
if __name__ == "__main__":
    import uvicorn
    
    # Initialize the ChromaDB collection
    initialize_collection()
    
    # Run the FastAPI application with Uvicorn
    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)