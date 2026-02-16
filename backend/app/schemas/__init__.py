from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    name: Optional[str] = None
    city: Optional[str] = None
    segment: Optional[str] = None


class UserState(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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



class Quest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quest_id: str
    quest_name: str
    quest_type: Optional[str] = None
    condition: Optional[str] = None
    reward_points: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class QuestAward(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    award_id: str
    user_id: str
    as_of_date: date
    selected_quest: Optional[str] = None
    reward_points: Optional[int] = None
    timestamp: Optional[datetime] = None
    triggered_quests: Optional[str] = None  # derived from junction table
    suppressed_quests: Optional[str] = None  # derived from junction table


class PointsLedgerEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ledger_id: str
    user_id: str
    points_delta: int
    source: Optional[str] = None
    source_ref: Optional[str] = None
    created_at: Optional[datetime] = None


class BadgeAward(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    award_id: Optional[int] = None
    user_id: str
    badge_id: str
    awarded_at: Optional[datetime] = None


class Notification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: str
    user_id: str
    channel: Optional[str] = None
    message: Optional[str] = None
    sent_at: Optional[datetime] = None


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    user_id: str
    total_points: int


class PipelineRunResponse(BaseModel):
    status: str
    processed_users: int
    message: Optional[str] = None
