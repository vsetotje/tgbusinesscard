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

# Создание таблиц в базе данных
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

# Генерация QR-кода
@app.get("/qr/{user_id}")
def generate_qr(user_id: int, db: Session = Depends(get_db)):
    db_visit_card = crud.get_visit_card(db, user_id)
    if not db_visit_card:
        raise HTTPException(status_code=404, detail="Visit card not found")
    
    # Формируем vCard
    vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{db_visit_card.first_name} {db_visit_card.last_name}
ORG:{db_visit_card.company_name}
TITLE:{db_visit_card.position}
TEL:{db_visit_card.phone}
EMAIL:{db_visit_card.email}
URL:{db_visit_card.socials[0] if db_visit_card.socials else ''}
END:VCARD
    """
    
    # Генерируем QR-код
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f"static/qr_{user_id}.png")
    
    return {"qr_url": f"/static/qr_{user_id}.png"}

# Генерация PDF
@app.get("/pdf/{user_id}")
def generate_pdf(user_id: int, background_color: str = "#ffffff", db: Session = Depends(get_db)):
    db_visit_card = crud.get_visit_card(db, user_id)
    if not db_visit_card:
        raise HTTPException(status_code=404, detail="Visit card not found")
    html = HTML(string=render_template("visit_card.html", visit_card=db_visit_card, background_color=background_color))
    pdf_path = f"static/visit_{user_id}.pdf"
    html.write_pdf(pdf_path)
    return {"pdf_url": f"/static/visit_{user_id}.pdf"}

# Уведомления через Telegram Bot API
async def send_notification(user_id: int, message: str):
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    await bot.send_message(chat_id=user_id, text=message)

# Просмотр визитки
@app.get("/visit/{user_id}")
async def view_visit_card(user_id: int, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    db_visit_card = crud.get_visit_card(db, user_id)
    if not db_visit_card:
        raise HTTPException(status_code=404, detail="Visit card not found")
    
    # Записываем просмотр
    crud.create_visit(db, db_visit_card.id)
    
    # Отправляем уведомление
    if background_tasks:
        background_tasks.add_task(send_notification, db_visit_card.user_id, "Вашу визитку просмотрели!")
    
    return db_visit_card