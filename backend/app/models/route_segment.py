"""
Maps to the `route_segments` table created by Dhanasri in Supabase.
NOT used yet - reserved for the route segmentation module.
"""
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey

from app.db.database import Base


class RouteSegment(Base):
    __tablename__ = "route_segments"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True)
    trip_id = Column(BigInteger, ForeignKey("trips.id"), nullable=True)
    zone_name = Column(Text, nullable=True)
    rainfall_band = Column(Integer, nullable=True)
    terrain_band = Column(Integer, nullable=True)
    flood_history_band = Column(Integer, nullable=True)
    transport_status = Column(Text, nullable=True)
    eta = Column(DateTime(timezone=True), nullable=True)