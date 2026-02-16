from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_quest_awards(limit: int = Query(100, ge=1, le=1000)):
    """List quest awards with triggered/suppressed quests from junction table."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT qa.award_id, qa.user_id, qa.as_of_date, qa.selected_quest,
                   qa.reward_points, qa.timestamp,
                   STRING_AGG(CASE WHEN qaq.status = 'TRIGGERED' THEN qaq.quest_id END, '|') AS triggered_quests,
                   STRING_AGG(CASE WHEN qaq.status = 'SUPPRESSED' THEN qaq.quest_id END, '|') AS suppressed_quests
            FROM quest_awards qa
            LEFT JOIN quest_award_quests qaq ON qa.award_id = qaq.award_id
            GROUP BY qa.award_id, qa.user_id, qa.as_of_date, qa.selected_quest,
                     qa.reward_points, qa.timestamp
            ORDER BY qa.timestamp DESC
            LIMIT :lim
        '''), {'lim': limit}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/user/{user_id}")
def list_awards_for_user(user_id: str, limit: int = Query(50, ge=1, le=500)):
    """List quest awards for a user with triggered/suppressed from junction table."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT qa.award_id, qa.as_of_date, qa.selected_quest,
                   qa.reward_points, qa.timestamp,
                   STRING_AGG(CASE WHEN qaq.status = 'TRIGGERED' THEN qaq.quest_id END, '|') AS triggered_quests,
                   STRING_AGG(CASE WHEN qaq.status = 'SUPPRESSED' THEN qaq.quest_id END, '|') AS suppressed_quests
            FROM quest_awards qa
            LEFT JOIN quest_award_quests qaq ON qa.award_id = qaq.award_id
            WHERE qa.user_id = :u
            GROUP BY qa.award_id, qa.as_of_date, qa.selected_quest,
                     qa.reward_points, qa.timestamp
            ORDER BY qa.timestamp DESC
            LIMIT :lim
        '''), {'u': user_id, 'lim': limit}).fetchall()
    return [dict(r._mapping) for r in rows]
