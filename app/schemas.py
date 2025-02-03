from pydantic import BaseModel
from typing import List, Optional, Dict

class VisitCardBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    company_name: str
    position: str
    phone: str
    email: str
    work_email: Optional[str] = None
    socials: List[str] = []
    custom_fields: Optional[Dict[str, str]] = {}

class VisitCardCreate(VisitCardBase):
    pass

class VisitCard(VisitCardBase):
    id: int
    user_id: int
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True  # Заменяет orm_mode в Pydantic v2