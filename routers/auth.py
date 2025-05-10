from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from database import SessionLocal
import jwt, os

router = APIRouter()

@router.post("/register")
def register(national_id: str, password: str):
    db: Session = SessionLocal()
    pw_hash = bcrypt.hash(password)
    try:
        db.execute(
            "INSERT INTO users (national_id, password_hash) VALUES (:nid, :ph)",
            {"nid": national_id, "ph": pw_hash}
        )
        db.commit()
    except:
        raise HTTPException(400, "رقم الهوية موجود مسبقاً")
    return {"message": "تم التسجيل"}

@router.post("/login")
def login(national_id: str, password: str):
    db: Session = SessionLocal()
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE national_id = :nid",
        {"nid": national_id}
    ).fetchone()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(401, "بيانات الدخول غير صحيحة")
    token = jwt.encode({"user_id": user.id}, os.getenv("JWT_SECRET"), algorithm="HS256")
    return {"access_token": token}
