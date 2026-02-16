from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class BadgeAward(Base):
    __tablename__ = "badge_awards"

    award_id = Column(Integer, primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    badge_id = Column(String(10), ForeignKey("badges.badge_id"), nullable=False)
    awarded_at = Column(DateTime)

    user = relationship("User")
    badge = relationship("Badge")
