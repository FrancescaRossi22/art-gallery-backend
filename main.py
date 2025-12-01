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

# 🌍 CORS — aggiungi qui il dominio Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://prismalab.netlify.app",   # ← SOSTITUISCI con il tuo dominio
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🗄 Inizializza database
init_db()

# 📌 Router recensioni
app.include_router(feedback_router)


# 📧 Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


async def send_email_with_optional_file(name, surname, email, message, file):
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

    if file is not None:
        try:
            content = await file.read()
            filename = file.filename or "attachment"
            msg.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)
        except:
            pass

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Errore invio email:", e)
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
        raise HTTPException(status_code=500, detail="Impossibile inviare l'email.")
    return {"message": "Email inviata con successo"}
