from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

# 1) إنشاء التطبيق
app = FastAPI()

# 2) إضافة Middleware لـ CORS
#    هنا نسمح لأي موقع (origin) بإرسال طلبات إلى ה־API.  
#    إذا أردت تشديد الأمان لاحقًا، استبدل ["*"] بقائمة النطاقات المسموح بها.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # أو ['https://hunterbukhari.github.io'] لتحديد منشأ واحد
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) توليد الجداول عند بدء التطبيق
init_db()

# 4) تضمين الراوترات
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
app.include_router(export_router, prefix="/export", tags=["export"])
