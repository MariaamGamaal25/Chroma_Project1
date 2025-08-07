from pydantic import BaseModel
from typing import Dict

# Pydantic Model for API Response
# This model defines the structure of the data returned from the API.
class Document(BaseModel):
    id: str
    text: str
    metadata: Dict