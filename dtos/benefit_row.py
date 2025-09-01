from pydantic import BaseModel

class BenefitRow(BaseModel):
    id: str
    service: str
    medright_2024: str
    seha_one_2025: str
    page: int
    filename: str
    section: str
    source: str
