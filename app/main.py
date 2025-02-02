from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import qrcode
from weasyprint import HTML
import os
from telegram import Bot

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Загрузка логотипа
@app.post("/upload-logo/{user_id}")
async def upload_logo(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = f"static/logos/{user_id}.png"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    db_visit_card = crud.get_visit_card(db, user_id)
    if db_visit_card:
        db_visit_card.logo_url = file_path
        db.commit()
        db.refresh(db_visit_card)
    return {"logo_url": file_path}

# Предпросмотр визитки
@app.get("/preview/{user_id}", response_class=HTMLResponse)
async def preview_visit_card(user_id: int, db: Session = Depends(get_db)):
    db_visit_card = crud.get_visit_card(db, user_id)
    if not db_visit_card:
        raise HTTPException(status_code=404, detail="Visit card not found")
    with open("templates/preview_visit_card.html", "r") as file:
        return HTMLResponse(content=file.read())

# Остальные эндпоинты (создание, редактирование, QR-код, PDF) остаются без изменений