# routers/auth.py

from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from datetime import datetime, timedelta
import uuid
from database import SessionLocal
from pydantic import BaseModel

router = APIRouter()
SESSION_DURATION = timedelta(minutes=15)  # مدة الجلسة

# نموذج بيانات دخول (يتوقع JSON)
class LoginRequest(BaseModel):
    national_id: str
    password: str

# Dependency لإنشاء جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------
# 1) تسجيل مستخدم جديد (يستخدمه الأدمن لاحقًا)
# ----------------------------------------
@router.post("/register")
def register(national_id: str, password: str, db: Session = Depends(get_db)):
    password_hash = bcrypt.hash(password)
    try:
        db.execute(
            """
            INSERT INTO users (national_id, password_hash, role)
            VALUES (:nid, :ph, 'user')
            """,
            {"nid": national_id, "ph": password_hash}
        )
        db.commit()
    except:
        raise HTTPException(status_code=400, detail="رقم الهوية مستخدم بالفعل")
    return {"message": "تم إنشاء الحساب بنجاح"}

# ----------------------------------------
# 2) تسجيل الدخول (ينشئ session ويضعه في كوكي)
# ----------------------------------------
@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    nid = req.national_id
    pwd = req.password
    
    row = db.execute(
        "SELECT id, password_hash, role FROM users WHERE national_id = :nid",
        {"nid": req.national_id}
    ).fetchone()
    if not row or not bcrypt.verify(req.password, row.password_hash):
        raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة")

    # إنشاء session_id وتعيين صلاحية 15 دقيقة
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + SESSION_DURATION

    db.execute(
        """
        INSERT INTO sessions (session_id, user_id, expires_at)
        VALUES (:sid, :uid, :exp)
        """,
        {"sid": session_id, "uid": row.id, "exp": expires_at}
    )
    db.commit()

    # وضع الكوكي في المتصفح
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,      # لا يمكن الوصول إليه من جافاسكربت
        samesite="strict",  # لمنع الإرسال من مواقع أخرى
        secure=False,       # ضع True إن كنت تستخدم HTTPS
        expires=int(expires_at.timestamp())
    )

    return {"message": "تم تسجيل الدخول بنجاح", "role": row.role}

# ----------------------------------------
# 3) استخراج user_id من الكوكي والتحقق من الجلسة
# ----------------------------------------
def get_current_user(
    session_id: str = Cookie(None),
    db: Session = Depends(get_db)
) -> int:
    if not session_id:
        raise HTTPException(status_code=401, detail="لم يتم تسجيل الدخول")
    row = db.execute(
        "SELECT user_id, expires_at FROM sessions WHERE session_id = :sid",
        {"sid": session_id}
    ).fetchone()
    if not row or row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="الجلسة منتهية أو غير صالحة")
    return row.user_id

# ----------------------------------------
# 4) للتحقق من صلاحيات الأدمن (يمكن استخدامه لاحقًا)
# ----------------------------------------
def get_current_admin(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> int:
    role_row = db.execute(
        "SELECT role FROM users WHERE id = :uid",
        {"uid": user_id}
    ).fetchone()
    if not role_row or role_row.role != "admin":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحيات المدير")
    return user_id
