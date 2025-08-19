from pydantic import BaseModel
from typing import Dict


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3  # default top-k results  