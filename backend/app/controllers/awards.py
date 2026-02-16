from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_quest_awards(limit: int = Query(100, ge=1, le=1000)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT award_id, user_id, as_of_date, triggered_quests, selected_quest, reward_points, suppressed_quests, timestamp FROM quest_awards ORDER BY timestamp DESC LIMIT :lim'), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/user/{user_id}")
def list_awards_for_user(user_id: str, limit: int = Query(50, ge=1, le=500)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT award_id, as_of_date, triggered_quests, selected_quest, reward_points, suppressed_quests, timestamp FROM quest_awards WHERE user_id = :u ORDER BY timestamp DESC LIMIT :lim'), {'u': user_id, 'lim': limit}).fetchall()
    return [dict(r) for r in rows]
