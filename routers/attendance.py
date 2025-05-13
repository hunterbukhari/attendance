from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime
import math

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# إعداد مركز الموقع المسموح ونصف القطر بالمتر
ALLOWED_LAT = 24.7136
ALLOWED_LNG = 46.6753
MAX_DISTANCE_METERS = 1000

def distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@router.post("/check-in")
def check_in(
    latitude: float,
    longitude: float,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # تحقق من الموقع
    if distance(latitude, longitude, ALLOWED_LAT, ALLOWED_LNG) > MAX_DISTANCE_METERS:
        raise HTTPException(400, "أنت خارج نطاق الموقع المسموح به")

    # تحقق من عدم التسجيل المكرر اليوم
    today = datetime.utcnow().date()
    exists = db.execute(
        "SELECT 1 FROM attendance WHERE user_id=:uid AND timestamp::date=:d AND type='in'",
        {"uid": user_id, "d": today}
    ).fetchone()
    if exists:
        raise HTTPException(400, "تم تسجيل الحضور مسبقاً اليوم")

    # تسجيل الحضور
    db.execute(
        """
        INSERT INTO attendance
          (user_id, type, device_info, latitude, longitude)
        VALUES
          (:uid, 'in', 'web', :lat, :lng)
        """,
        {"uid": user_id, "lat": latitude, "lng": longitude}
    )
    db.commit()
    return {"message": "تم تسجيل الحضور"}

@router.post("/check-out")
def check_out(
    latitude: float,
    longitude: float,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.utcnow().date()
    # تأكد من وجود حضور
    has_in = db.execute(
        "SELECT 1 FROM attendance WHERE user_id=:uid AND timestamp::date=:d AND type='in'",
        {"uid": user_id, "d": today}
    ).fetchone()
    if not has_in:
        raise HTTPException(400, "لم تسجل حضور اليوم")

    # تأكد من عدم الانصراف مسبقاً
    has_out = db.execute(
        "SELECT 1 FROM attendance WHERE user_id=:uid AND timestamp::date=:d AND type='out'",
        {"uid": user_id, "d": today}
    ).fetchone()
    if has_out:
        raise HTTPException(400, "تم تسجيل الانصراف مسبقاً اليوم")

    # تحقق من الموقع
    if distance(latitude, longitude, ALLOWED_LAT, ALLOWED_LNG) > MAX_DISTANCE_METERS:
        raise HTTPException(400, "أنت خارج نطاق الموقع المسموح به")

    # تسجيل الانصراف
    db.execute(
        """
        INSERT INTO attendance
          (user_id, type, device_info, latitude, longitude)
        VALUES
          (:uid, 'out', 'web', :lat, :lng)
        """,
        {"uid": user_id, "lat": latitude, "lng": longitude}
    )
    db.commit()
    return {"message": "تم تسجيل الانصراف"}
