from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import uuid
from datetime import datetime, timedelta
from database import SessionLocal

router = APIRouter()

# إنشاء اتصال بقاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# تسجيل مستخدم جديد (اختياري للإدارة)
@router.post("/register")
def register(national_id: str, password: str, db: Session = Depends(get_db)):
    password_hash = bcrypt.hash(password)
    try:
        db.execute(
            "INSERT INTO users (national_id, password_hash) VALUES (:nid, :ph)",
            {"nid": national_id, "ph": password_hash}
        )
        db.commit()
    except:
        raise HTTPException(400, "رقم الهوية مستخدم بالفعل")
    return {"message": "تم إنشاء الحساب بنجاح"}

# تسجيل الدخول - ينشئ جلسة ويرسل كوكي HttpOnly
@router.post("/login")
def login(national_id: str, password: str, response: Response, db: Session = Depends(get_db)):
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE national_id = :nid",
        {"nid": national_id}
    ).fetchone()

    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(401, "بيانات الدخول غير صحيحة")

    # إنشاء جلسة جديدة
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    db.execute(
        "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (:sid, :uid, :exp)",
        {"sid": session_id, "uid": user.id, "exp": expires_at}
    )
    db.commit()

    # إرسال الكوكي للمتصفح
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="strict",
        secure=True,  # اجعلها False للتجربة المحلية بدون HTTPS
        expires=int(expires_at.timestamp())
    )

    return {"message": "تم تسجيل الدخول بنجاح"}

# استخراج المستخدم من الكوكي
@router.get("/me")
def get_me(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(401, "لم يتم تسجيل الدخول")
    row = db.execute(
        "SELECT user_id, expires_at FROM sessions WHERE session_id = :sid",
        {"sid": session_id}
    ).fetchone()
    if not row or row.expires_at < datetime.utcnow():
        raise HTTPException(401, "الجلسة منتهية أو غير صالحة")
    return {"user_id": row.user_id}

# تغيير كلمة المرور
@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    session_id: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not session_id:
        raise HTTPException(401, "غير مسجل دخول")
    session = db.execute(
        "SELECT user_id FROM sessions WHERE session_id = :sid",
        {"sid": session_id}
    ).fetchone()
    if not session:
        raise HTTPException(401, "جلسة غير صالحة")

    user = db.execute(
        "SELECT password_hash FROM users WHERE id = :uid",
        {"uid": session.user_id}
    ).fetchone()

    if not user or not bcrypt.verify(old_password, user.password_hash):
        raise HTTPException(403, "كلمة المرور القديمة غير صحيحة")

    new_hash = bcrypt.hash(new_password)
    db.execute(
        "UPDATE users SET password_hash = :ph WHERE id = :uid",
        {"ph": new_hash, "uid": session.user_id}
    )
    db.commit()
    return {"message": "تم تغيير كلمة المرور بنجاح"}
