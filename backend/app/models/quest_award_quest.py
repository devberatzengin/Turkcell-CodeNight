from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class QuestAwardQuest(Base):
    """Junction table: which quests were triggered/suppressed per award."""
    __tablename__ = "quest_award_quests"

    award_id = Column(String(50), ForeignKey("quest_awards.award_id", ondelete="CASCADE"), primary_key=True)
    quest_id = Column(String(10), ForeignKey("quests.quest_id", ondelete="CASCADE"), primary_key=True)
    status = Column(String(20), nullable=False)  # 'TRIGGERED' or 'SUPPRESSED'

    award = relationship("QuestAward", back_populates="award_quests")
    quest = relationship("Quest")
