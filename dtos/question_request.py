from pydantic import BaseModel
from typing import Dict



class QuestionRequest(BaseModel):
    question: str
