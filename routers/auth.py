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

# التحقق من الجلسة واستخراج المستخدم
def get_current_user(session_id: str = Cookie(...)):
    db: Session = SessionLocal()
    session = db.execute(
        "SELECT user_id, expires_at FROM sessions WHERE session_id = :sid",
        {"sid": session_id}
    ).fetchone()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(401, "انتهت صلاحية الجلسة أو غير موجودة")
    return session.user_id

# تسجيل حضور
@router.post("/attendance/check-in")
def check_in(user_id: int = Depends(get_current_user)):
    db: Session = SessionLocal()
    today = datetime.utcnow().date()

    already_checked = db.execute(
        "SELECT 1 FROM attendance WHERE user_id = :uid AND timestamp::date = :d AND type = 'in'",
        {"uid": user_id, "d": today}
    ).fetchone()

    if already_checked:
        raise HTTPException(400, "تم تسجيل الحضور مسبقاً")

    db.execute(
        "INSERT INTO attendance (user_id, type, device_info, latitude, longitude) VALUES (:uid, 'in', 'web', 0.0, 0.0)",
        {"uid": user_id}
    )
    db.commit()
    return {"message": "تم تسجيل الحضور"}

# تسجيل انصراف
@router.post("/attendance/check-out")
def check_out(user_id: int = Depends(get_current_user)):
    db: Session = SessionLocal()
    today = datetime.utcnow().date()

    already_checked = db.execute(
        "SELECT 1 FROM attendance WHERE user_id = :uid AND timestamp::date = :d AND type = 'out'",
        {"uid": user_id, "d": today}
    ).fetchone()

    if already_checked:
        raise HTTPException(400, "تم تسجيل الانصراف مسبقاً")

    db.execute(
        "INSERT INTO attendance (user_id, type, device_info, latitude, longitude) VALUES (:uid, 'out', 'web', 0.0, 0.0)",
        {"uid": user_id}
    )
    db.commit()
    return {"message": "تم تسجيل الانصراف"}
