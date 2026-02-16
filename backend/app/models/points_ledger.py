from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class PointsLedger(Base):
    __tablename__ = "points_ledger"

    ledger_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    points_delta = Column(Integer, nullable=False)
    source = Column(String(50))
    source_ref = Column(String(50))
    created_at = Column(DateTime)

    user = relationship("User")
