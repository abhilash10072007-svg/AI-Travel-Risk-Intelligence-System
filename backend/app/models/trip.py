"""
Maps to the `trips` table created by Dhanasri in Supabase.
Columns match exactly what's in the schema visualizer - do not add
or rename columns here without updating the table in Supabase too.
"""
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True)
    # users.id is int4 (Integer) in Supabase, not int8 - must match for the FK to be valid
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    origin = Column(Text, nullable=True)
    destination = Column(Text, nullable=True)
    departure_time = Column(DateTime(timezone=True), nullable=True)
    travel_mode = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())