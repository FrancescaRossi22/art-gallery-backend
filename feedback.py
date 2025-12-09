from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import get_connection

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

        cur.execute("""
            SELECT id, name, surname, rating, comment, date
            FROM feedback
            ORDER BY id DESC
        """)

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": r[0],
                "name": r[1],
                "surname": r[2],
                "rating": r[3],
                "comment": r[4],
                "date": r[5].isoformat() if r[5] else None
            }
            for r in rows
        ]

    except Exception as e:
        print("❌ GET FEEDBACK ERROR:", e)
        raise HTTPException(status_code=500, detail="Error loading reviews")


@router.post("/feedback")
def add_feedback(item: Feedback):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO feedback (name, surname, email, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            item.name,
            item.surname,
            item.email,
            item.rating,
            item.comment
        ))

        conn.commit()
        conn.close()

        return {"message": "Feedback saved!"}

    except Exception as e:
        print("❌ POST FEEDBACK ERROR:", e)
        raise HTTPException(status_code=500, detail="Error saving review")
