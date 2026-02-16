from sqlalchemy import Column, String, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class QuestAward(Base):
    __tablename__ = "quest_awards"

    award_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    triggered_quests = Column(Text)
    selected_quest = Column(String(10))
    reward_points = Column(Integer)
    suppressed_quests = Column(Text)
    timestamp = Column(DateTime)

    user = relationship("User")
