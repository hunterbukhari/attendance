from fastapi import FastAPI
from routers import auth, attendance, export_excel
from database import init_db
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

app = FastAPI()

init_db()

app.include_router(auth.router, prefix="/auth")
app.include_router(attendance.router, prefix="/attendance")
app.include_router(export_excel.router, prefix="/export")
