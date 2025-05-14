# main.py

from fastapi import FastAPI
from database import init_db
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

# 1) إنشاء التطبيق
app = FastAPI()

# 2) توليد الجداول عند بدء التطبيق
init_db()

# 3) تضمين الراوترات
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
app.include_router(export_router, prefix="/export", tags=["export"])
