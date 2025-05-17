# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers.auth import router as auth_router
from routers.attendance import router as attendance_router
from routers.export_excel import router as export_router

app = FastAPI()

# ⬇️ Allow your front-end origin (or "*" for all during testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hunterbukhari.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(attendance_router, prefix="/attendance", tags=["attendance"])
app.include_router(export_router, prefix="/export", tags=["export"])
