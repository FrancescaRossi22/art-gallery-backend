from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from database import get_connection, IS_POSTGRES

router = APIRouter()

class Feedback(BaseModel):
    name: str
    surname: str
    email: str | None = None
    rating: int
    comment: str


@router.get("/feedback")
def get_feedback():
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT id, name, surname, rating, comment, date FROM feedback ORDER BY id DESC"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        formatted = []

        for r in rows:
            date_value = r[5]

            # Se arriva da Postgres come datetime, lo marchiamo esplicitamente come UTC
            if isinstance(date_value, datetime):
                if IS_POSTGRES:
                    # lo considero UTC e lo trasformo in stringa con timezone (+00:00)
                    date_value = date_value.replace(tzinfo=timezone.utc).isoformat()
                else:
                    date_value = date_value.isoformat()

            formatted.append({
                "id": r[0],
                "name": r[1],
                "surname": r[2],
                "rating": r[3],
                "comment": r[4],
                "date": date_value,
            })

        return formatted

    except Exception as e:
        print("❌ ERROR GET FEEDBACK:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
def add_feedback(item: Feedback):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Salviamo sempre in UTC
        now_utc = datetime.now(timezone.utc)

        if IS_POSTGRES:
            query = """
                INSERT INTO feedback (name, surname, email, rating, comment, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (item.name, item.surname, item.email, item.rating, item.comment, now_utc)
        else:
            query = """
                INSERT INTO feedback (name, surname, email, rating, comment, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                item.name,
                item.surname,
                item.email,
                item.rating,
                item.comment,
                now_utc.isoformat(),
            )

        cur.execute(query, params)
        conn.commit()
        conn.close()

        return {"message": "Feedback saved!"}

    except Exception as e:
        print("❌ ERROR POST FEEDBACK:", e)
        raise HTTPException(status_code=500, detail=str(e))
