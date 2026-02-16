from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    name: Optional[str]
    city: Optional[str]
    segment: Optional[str]

    class Config:
        orm_mode = True


class UserState(BaseModel):
    user_id: str
    login_count_today: int = 0
    play_minutes_today: int = 0
    pvp_wins_today: int = 0
    coop_minutes_today: int = 0
    topup_try_today: int = 0
    play_minutes_7d: int = 0
    topup_try_7d: int = 0
    logins_7d: int = 0
    login_streak_days: int = 0
    total_points: int = 0

    class Config:
        orm_mode = True


class Quest(BaseModel):
    quest_id: str
    quest_name: str
    quest_type: Optional[str]
    condition: Optional[str]
    reward_points: Optional[int]
    priority: Optional[int]
    is_active: Optional[bool]

    class Config:
        orm_mode = True


class QuestAward(BaseModel):
    award_id: str
    user_id: str
    as_of_date: date
    triggered_quests: Optional[str]
    selected_quest: Optional[str]
    reward_points: Optional[int]
    suppressed_quests: Optional[str]
    timestamp: Optional[datetime]

    class Config:
        orm_mode = True


class PointsLedgerEntry(BaseModel):
    ledger_id: str
    user_id: str
    points_delta: int
    source: Optional[str]
    source_ref: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class BadgeAward(BaseModel):
    award_id: Optional[int]
    user_id: str
    badge_id: str
    awarded_at: Optional[datetime]

    class Config:
        orm_mode = True


class Notification(BaseModel):
    notification_id: str
    user_id: str
    channel: Optional[str]
    message: Optional[str]
    sent_at: Optional[datetime]

    class Config:
        orm_mode = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    total_points: int

    class Config:
        orm_mode = True


class PipelineRunResponse(BaseModel):
    status: str
    processed_users: int
    message: Optional[str]
