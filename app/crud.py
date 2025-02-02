from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def create_visit(db: Session, visit_card_id: int):
    db_visit = models.Visit(visit_card_id=visit_card_id, viewed_at=datetime.utcnow())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

def get_visit_count(db: Session, visit_card_id: int):
    return db.query(models.Visit).filter(models.Visit.visit_card_id == visit_card_id).count()