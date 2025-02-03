from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def create_visit_card(db: Session, visit_card: schemas.VisitCardCreate, user_id: int):
    db_visit_card = models.VisitCard(**visit_card.model_dump(), user_id=user_id)
    db.add(db_visit_card)
    db.commit()
    db.refresh(db_visit_card)
    return db_visit_card

def get_visit_card(db: Session, user_id: int):
    return db.query(models.VisitCard).filter(models.VisitCard.user_id == user_id).first()

def create_visit(db: Session, visit_card_id: int):
    db_visit = models.Visit(visit_card_id=visit_card_id, viewed_at=datetime.utcnow())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

def get_visit_count(db: Session, visit_card_id: int):
    return db.query(models.Visit).filter(models.Visit.visit_card_id == visit_card_id).count()