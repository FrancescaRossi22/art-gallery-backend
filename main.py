from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

from database import init_db
from feedback import router as feedback_router

load_dotenv()

app = FastAPI()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# CORS per Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← in produzione metti il dominio Netlify
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inizializza DB e router
init_db()
app.include_router(feedback_router)


async def send_email_with_optional_file(
    name: str,
    surname: str,
    email: str,
    message: str,
    file: UploadFile | None,
) -> bool:

    msg = EmailMessage()
    msg["Subject"] = "Nuova richiesta preventivo"
    msg["From"] = SMTP_USERNAME
    msg["To"] = RECIPIENT_EMAIL

    msg.set_content(f"""
Hai ricevuto una nuova richiesta di preventivo:

Nome: {name}
Cognome: {surname}
Email: {email}

Messaggio:
{message}

---
Inviato automaticamente dal sito PrismaLab
""")

    if file:
        file_content = await file.read()
        msg.add_attachment(
            file_content,
            maintype="application",
            subtype="octet-stream",
            filename=file.filename,
        )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True

    except Exception as e:
        print("❌ Errore email:", e)
        return False


@app.post("/send-email")
async def api_send_email(
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile | None = File(None),
):
    ok = await send_email_with_optional_file(name, surname, email, message, file)
    if not ok:
        raise HTTPException(status_code=500, detail="Errore invio email")
    return {"message": "Email inviata!"}
