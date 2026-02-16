from sqlalchemy import Column, String, Integer, Date, Boolean, Text
from ..db import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100))
    segment = Column(String(50))


class ActivityEvent(Base):
    __tablename__ = 'activity_events'
    event_id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(10), nullable=False, index=True)
    date = Column(Date)
    game_id = Column(String(10))
    login_count = Column(Integer, default=0)
    play_minutes = Column(Integer, default=0)
    pvp_wins = Column(Integer, default=0)
    coop_minutes = Column(Integer, default=0)
    topup_try = Column(Integer, default=0)
