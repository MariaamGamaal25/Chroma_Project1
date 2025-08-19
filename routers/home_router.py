from fastapi import APIRouter
from utils.enums import Messages, Endpoints

router = APIRouter()

@router.get(Endpoints.ROOT, tags=["Home"])
def read_root():
    """
    A simple root endpoint to check if the server is running.
    """
    return {"message": Messages.APP_RUNNING}
