from sqlalchemy import Column, String, Integer, Boolean
from ..db import Base


class Quest(Base):
    __tablename__ = "quests"

    quest_id = Column(String(10), primary_key=True)
    quest_name = Column(String(100), nullable=False)
    quest_type = Column(String(50))
    condition = Column(String(255))
    reward_points = Column(Integer)
    priority = Column(Integer)
    is_active = Column(Boolean)
