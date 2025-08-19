from pydantic import BaseModel
from typing import Dict



class AskRequest(BaseModel):
     query: str