# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

app = FastAPI()

# 1) تمكين CORS لإتاحة الطلبات من GitHub Pages (او أي origin آخر)
#    أثناء التطوير ممكن ترك "*" لكن للإنتاج حدد origin الصالح فقط.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hunterbukhari.github.io/attendance"],            # أو ["https://hunterbukhari.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) إنشاء الجداول عند بدء تشغيل التطبيق
init_db()

# 3) تضمين الراوترات
app.include_router(auth_router,      prefix="/auth",       tags=["auth"])
app.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
app.include_router(export_router,    prefix="/export",     tags=["export"])
