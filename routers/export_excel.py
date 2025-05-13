from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal
import io, pandas as pd
from datetime import date
from routers.auth import get_current_admin, get_db

router = APIRouter()

@router.get("/excel")
def export_excel(
    start_date: date = Query(..., description="تاريخ البداية (YYYY-MM-DD)"),
    end_date:   date = Query(..., description="تاريخ النهاية (YYYY-MM-DD)"),
    admin_id:   int  = Depends(get_current_admin),  # تحقّق صلاحية الأدمن
    db:         Session = Depends(get_db)           # يفتح ويغلق الجلسة تلقائيًا
):
    # 1) جلب البيانات من DB
    rows = db.execute("""
        SELECT u.national_id, a.timestamp
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.timestamp::date BETWEEN :s AND :e
        ORDER BY a.timestamp
    """, {"s": start_date, "e": end_date}).fetchall()

    # 2) بناء DataFrame
    df = pd.DataFrame(rows, columns=["رقم الهوية", "وقت الحضور"])

    # 3) تصدير إلى بايتس
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    buf.seek(0)

    # 4) إعداد الاستجابة
    filename = f"attendance_{start_date}_to_{end_date}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
