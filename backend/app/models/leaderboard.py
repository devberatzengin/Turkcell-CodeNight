from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    rank = Column(Integer, primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    total_points = Column(Integer)

    user = relationship("User")
