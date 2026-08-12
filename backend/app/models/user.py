# → Dhanasri (table definitions)
"""
Maps to the `users` table already created by Dhanasri in Supabase.
Columns match exactly what's in the schema visualizer - do not add
or rename columns here without updating the table in Supabase too.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    firebase_uid = Column(String, unique=True, nullable=True, index=True)