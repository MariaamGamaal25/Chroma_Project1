# from fastapi import APIRouter
# from utils.enums import Messages, Endpoints

# router = APIRouter()

# @router.get(Endpoints.ROOT, tags=["Home"])
# def read_root():
#     """
#     A simple root endpoint to check if the server is running.
#     """
#     return {"message": Messages.APP_RUNNING}
import os
from fastapi import APIRouter
from utils.enums import Endpoints, Messages
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get(Endpoints.ROOT, tags=["Home"])
def read_root():
    """Returns a simple message confirming the API is running."""
    logger.info("Root endpoint called.")
    return {"message": Messages.APP_RUNNING}

@router.get(Endpoints.API_PREFIX, tags=["Home"])
def api_root():
    """Returns a simple message for the API root."""
    logger.info("API root endpoint called.")
    return {"message": "Welcome to the ChromaDB RAG API! Use /docs to view the API documentation."}

