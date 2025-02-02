from pydantic import BaseModel
from typing import List, Optional

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
    custom_fields: Optional[dict] = {}

class VisitCardCreate(VisitCardBase):
    pass

class VisitCard(VisitCardBase):
    id: int
    user_id: int
    logo_url: Optional[str] = None

    class Config:
        orm_mode = True