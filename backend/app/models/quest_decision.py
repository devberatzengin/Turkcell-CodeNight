from sqlalchemy import Column, String, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class QuestDecision(Base):
    __tablename__ = "quest_decisions"

    decision_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    selected_reward_points = Column(Integer)
    reason = Column(Text)
    timestamp = Column(DateTime)

    user = relationship("User")
