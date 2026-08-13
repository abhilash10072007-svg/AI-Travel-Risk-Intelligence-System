"""
Maps to the `risk_assessments` table created by Dhanasri in Supabase.
NOT used yet - reserved for Nikhil's risk/scoring engine.
"""
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey

from app.db.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True)
    route_segment_id = Column(BigInteger, ForeignKey("route_segments.id"), nullable=True)
    disruption_score = Column(Integer, nullable=True)
    risk_badge = Column(Text, nullable=True)
    confidence_badge = Column(Text, nullable=True)
    calculated_at = Column(DateTime(timezone=True), nullable=True)