from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.orm import Session
from database import SessionLocal
import jwt, os
from datetime import datetime
from pydantic import BaseModel, confloat

# نموذج بيانات الموقع
class Location(BaseModel):
    latitude:  confloat(ge=-90,  le=90)
    longitude: confloat(ge=-180, le=180)

# يرث حقول latitude و longitude
class AttendRequest(Location):
    pass

router = APIRouter()

# استخراج user_id من الـ JWT
def get_current_user(authorization: str = Header(...)) -> int:
    try:
        token = authorization.split(" ")[1]
        data = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return data["user_id"]
    except Exception:
        raise HTTPException(401, "Token غير صالح")

@router.post("/check-in")
def check_in(
    loc: AttendRequest = Body(...),
    user_id: int = Depends(get_current_user)
):
    db: Session = SessionLocal()
    today = datetime.utcnow().date()
    exists = db.execute(
        """
        SELECT 1
        FROM attendance
        WHERE user_id = :uid
          AND timestamp::date = :d
          AND type = 'in'
        """,
        {"uid": user_id, "d": today}
    ).fetchone()
    if exists:
        raise HTTPException(400, "تم تسجيل الحضور اليوم مسبقاً")

    db.execute(
        """
        INSERT INTO attendance (user_id, device_info, type, latitude, longitude)
        VALUES (:uid, :di, 'in', :lat, :lng)
        """,
        {
          "uid": user_id,
          "di": "web",
          "lat": loc.latitude,
          "lng": loc.longitude
        }
    )
    db.commit()
    return {"message": "تم تسجيل الحضور", "location": loc.dict()}

@router.post("/check-out")
def check_out(
    loc: AttendRequest = Body(...),
    user_id: int = Depends(get_current_user)
):
    db: Session = SessionLocal()
    today = datetime.utcnow().date()

    # تأكد من وجود حضور 'in' اليوم
    has_in = db.execute(
        """
        SELECT 1
        FROM attendance
        WHERE user_id = :uid
          AND timestamp::date = :d
          AND type = 'in'
        """,
        {"uid": user_id, "d": today}
    ).fetchone()
    if not has_in:
        raise HTTPException(400, "لم تسجل حضور اليوم")

    # تأكد من عدم وجود انصراف 'out' مسبقاً
    has_out = db.execute(
        """
        SELECT 1
        FROM attendance
        WHERE user_id = :uid
          AND timestamp::date = :d
          AND type = 'out'
        """,
        {"uid": user_id, "d": today}
    ).fetchone()
    if has_out:
        raise HTTPException(400, "تم تسجيل انصراف اليوم مسبقاً")

    db.execute(
        """
        INSERT INTO attendance (user_id, device_info, type, latitude, longitude)
        VALUES (:uid, :di, 'out', :lat, :lng)
        """,
        {
          "uid": user_id,
          "di": "web",
          "lat": loc.latitude,
          "lng": loc.longitude
        }
    )
    db.commit()
    return {"message": "تم تسجيل الانصراف", "location": loc.dict()}
