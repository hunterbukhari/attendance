from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
import jwt, os
from datetime import datetime

router = APIRouter()

def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    try:
        data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return data["user_id"]
    except:
        raise HTTPException(401, "Token غير صالح")

@router.post("/check-in")
def check_in(user_id: int = Depends(get_current_user)):
    db: Session = SessionLocal()
    today = datetime.utcnow().date()
    exists = db.execute(
        "SELECT 1 FROM attendance WHERE user_id = :uid AND timestamp::date = :d",
        {"uid": user_id, "d": today}
    ).fetchone()
    if exists:
        raise HTTPException(400, "تم تسجيل الحضور اليوم مسبقاً")
    db.execute(
        "INSERT INTO attendance (user_id, device_info) VALUES (:uid, :di)",
        {"uid": user_id, "di": "web"}
    )
    db.commit()
    return {"message": "تم تسجيل الحضور"}
