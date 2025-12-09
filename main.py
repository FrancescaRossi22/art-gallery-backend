from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import resend
import os
import base64

load_dotenv()

app = FastAPI()

resend.api_key = os.getenv("RESEND_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://prismalab.pages.dev",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/send-email")
async def api_send_email(
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile | None = File(None),
):
    html_body = f"""
        <h2>Nuova richiesta preventivo</h2>
        <p><b>Nome:</b> {name}</p>
        <p><b>Cognome:</b> {surname}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Messaggio:</b><br>{message}</p>
    """

    attachments = []

    if file:
        encoded = base64.b64encode(await file.read()).decode("utf-8")
        attachments.append({
            "filename": file.filename,
            "content": encoded,
            "type": file.content_type or "application/octet-stream",
        })

    try:
        resend.Emails.send({
            "from": "PrismaLab <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": "Nuova richiesta preventivo",
            "html": html_body,
            "attachments": attachments,
        })
        return {"message": "Email inviata"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Errore invio email")
