from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
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
        cur.execute("SELECT id, name, surname, rating, comment, date FROM feedback ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": r[0],
                "name": r[1],
                "surname": r[2],
                "rating": r[3],
                "comment": r[4],
                "date": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        print("❌ ERROR GET FEEDBACK:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def add_feedback(item: Feedback):
    try:
        conn = get_connection()
        cur = conn.cursor()

        now = datetime.now()

        if IS_POSTGRES:
            query = """
                INSERT INTO feedback (name, surname, email, rating, comment, date)
                VALUES ($1, $2, $3, $4, $5, $6)
            """
        else:
            query = """
                INSERT INTO feedback (name, surname, email, rating, comment, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """

        cur.execute(query, (item.name, item.surname, item.email, item.rating, item.comment, now))

        conn.commit()
        conn.close()
        return {"message": "Feedback saved!"}

    except Exception as e:
        print("❌ ERROR POST FEEDBACK:", e)
        raise HTTPException(status_code=500, detail=str(e))
