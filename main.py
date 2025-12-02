from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import resend

from database import init_db
from feedback import router as feedback_router

load_dotenv()

app = FastAPI()

resend.api_key = os.getenv("RESEND_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://prismalab.pages.dev",
        "http://localhost:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend PrismaLab is running!"}

init_db()
app.include_router(feedback_router)


async def send_email_with_optional_file(
    name: str,
    surname: str,
    email: str,
    message: str,
    file: UploadFile | None,
):
    html_body = f"""
        <h2>Nuova richiesta preventivo</h2>
        <p><strong>Nome:</strong> {name}</p>
        <p><strong>Cognome:</strong> {surname}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Messaggio:</strong><br>{message}</p>
        <hr>
        <p>Inviato automaticamente dal sito PrismaLab</p>
    """

    attachment_data = None

    if file:
        attachment_data = [{
            "filename": file.filename,
            "content": (await file.read()).decode("latin-1"),
        }]

    try:
        resend.Emails.send({
            "from": "PrismaLab <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": "Nuova richiesta preventivo",
            "html": html_body,
            "attachments": attachment_data,
        })
        return True

    except Exception as e:
        print("❌ Errore RESEND:", e)
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
