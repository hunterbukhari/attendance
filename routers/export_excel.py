from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal
import io, pandas as pd
from datetime import datetime

router = APIRouter()

@router.get("/excel")
def export_excel(
    start_date: str = Query(...),
    end_date: str = Query(...),
):
    db: Session = SessionLocal()
    rows = db.execute("""
        SELECT u.national_id, a.timestamp
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.timestamp::date BETWEEN :s AND :e
        ORDER BY a.timestamp
    """, {"s": start_date, "e": end_date}).fetchall()

    df = pd.DataFrame(rows, columns=["رقم الهوية", "وقت الحضور"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    buf.seek(0)
    filename = f"attendance_{start_date}_to_{end_date}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
