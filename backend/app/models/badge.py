from sqlalchemy import Column, String, Integer
from ..db import Base


class Badge(Base):
    __tablename__ = "badges"

    badge_id = Column(String(10), primary_key=True)
    badge_name = Column(String(100), nullable=False)
    condition = Column(String(255))
    level = Column(Integer)
    threshold_points = Column(Integer)

