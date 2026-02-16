from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class UserState(Base):
    __tablename__ = "user_state"

    user_id = Column(String(10), ForeignKey("users.user_id"), primary_key=True)
    login_count_today = Column(Integer, default=0)
    play_minutes_today = Column(Integer, default=0)
    pvp_wins_today = Column(Integer, default=0)
    coop_minutes_today = Column(Integer, default=0)
    topup_try_today = Column(Integer, default=0)
    play_minutes_7d = Column(Integer, default=0)
    topup_try_7d = Column(Integer, default=0)
    logins_7d = Column(Integer, default=0)
    login_streak_days = Column(Integer, default=0)

    user = relationship("User")
