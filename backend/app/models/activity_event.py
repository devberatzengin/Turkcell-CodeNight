from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    event_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    date = Column(Date, nullable=False)
    game_id = Column(String(10), ForeignKey("games.game_id"))
    login_count = Column(Integer, default=0)
    play_minutes = Column(Integer, default=0)
    pvp_wins = Column(Integer, default=0)
    coop_minutes = Column(Integer, default=0)
    topup_try = Column(Integer, default=0)

    user = relationship("User")
    game = relationship("Game")
