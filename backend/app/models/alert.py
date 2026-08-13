"""
Maps to the `alerts` table created by Dhanasri in Supabase.
NOT used yet - reserved for the Journey Guardian module.
"""
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey

from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"), nullable=True)
    alert_type = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)