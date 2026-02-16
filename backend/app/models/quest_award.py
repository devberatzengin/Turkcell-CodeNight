from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class QuestAward(Base):
    __tablename__ = "quest_awards"

    award_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    selected_quest = Column(String(10), ForeignKey("quests.quest_id"))
    reward_points = Column(Integer)
    timestamp = Column(DateTime)

    user = relationship("User")
    quest = relationship("Quest")
    # triggered/suppressed quests are in quest_award_quests junction table
    award_quests = relationship("QuestAwardQuest", back_populates="award")
