from sqlalchemy import Column, Integer, String
from ..db import Base


class Leaderboard(Base):
    """Read-only model mapped to leaderboard_view (derived VIEW, not a table)."""
    __tablename__ = "leaderboard_view"

    user_id = Column(String(10), primary_key=True)
    total_points = Column(Integer)
    rank = Column(Integer)
