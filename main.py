# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

app = FastAPI()

# ----------------------------------------
# 1) تفعيل CORS للسماح للواجهة الأمامية بإرسال الطلبات
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # في الإنتاج: ضع هنا رابط الواجهة فقط، مثال: ["https://example.com"]
    allow_credentials=True,      # لتمرير الكوكيز
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# 2) إنشاء الجداول في قاعدة البيانات (إن لم تكن موجودة)
# ----------------------------------------
init_db()

# ----------------------------------------
# 3) تسجيل الـ routers
# ----------------------------------------
app.include_router(auth_router,       prefix="/auth",       tags=["auth"])
app.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
app.include_router(export_router,     prefix="/export",     tags=["export"])
