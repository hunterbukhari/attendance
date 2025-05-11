from sqlalchemy import (
    create_engine, Column, BigInteger, Text,
    DateTime, Float, String, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id            = Column(BigInteger, primary_key=True, index=True)
    national_id   = Column(Text, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    attendances   = relationship("Attendance", back_populates="user")
    sessions      = relationship("Session", back_populates="user")

class Attendance(Base):
    __tablename__ = "attendance"
    id           = Column(BigInteger, primary_key=True, index=True)
    user_id      = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    timestamp    = Column(DateTime(timezone=False), server_default="now()", nullable=False)
    device_info  = Column(Text, nullable=False)
    type         = Column(String(10), nullable=False)
    latitude     = Column(Float, nullable=False)
    longitude    = Column(Float, nullable=False)
    user         = relationship("User", back_populates="attendances")
    __table_args__ = (Index("idx_attendance_date", timestamp),)

class Session(Base):
    __tablename__ = "sessions"
    id          = Column(BigInteger, primary_key=True, index=True)
    user_id     = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    session_id  = Column(Text, unique=True, nullable=False)
    expires_at  = Column(DateTime(timezone=False), nullable=False)
    user        = relationship("User", back_populates="sessions")
