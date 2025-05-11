from fastapi import APIRouter, HTTPException, Depends, Cookie
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from database import SessionLocal
from datetime import datetime, timedelta
import uuid

router = APIRouter()

# تسجيل مستخدم جديد
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

# تسجيل الدخول
@router.post("/login")
def login(national_id: str, password: str):
    db: Session = SessionLocal()
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE national_id = :nid",
        {"nid": national_id}
    ).fetchone()

    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(401, "بيانات الدخول غير صحيحة")

    session_id = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(minutes=15)

    db.execute(
        "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (:sid, :uid, :exp)",
        {"sid": session_id, "uid": user.id, "exp": expiry}
    )
    db.commit()

    return {"session_id": session_id}
