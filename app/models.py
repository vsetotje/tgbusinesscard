from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class VisitCard(Base):
    __tablename__ = "visit_cards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    company_name = Column(String)
    position = Column(String)
    phone = Column(String)
    email = Column(String)
    work_email = Column(String)
    socials = Column(JSON)  # Список соцсетей
    logo_url = Column(String)  # Ссылка на логотип
    custom_fields = Column(JSON)  # Пользовательские поля

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, index=True)
    visit_card_id = Column(Integer, ForeignKey("visit_cards.id"))
    viewed_at = Column(DateTime, default=datetime.utcnow)