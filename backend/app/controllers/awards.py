from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text
from datetime import datetime, date
import uuid

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


@router.post("/earn")
def earn_quest_award(user_id: str = Query(...), quest_id: str = Query(...)):
    """Allow a user to manually earn a quest award (dashboard Earn button)."""
    try:
        with db.engine.begin() as conn:
            # 1. Get quest details
            quest = conn.execute(text("""
                SELECT quest_id, quest_name, reward_points FROM quests WHERE quest_id = :q
            """), {'q': quest_id}).fetchone()
            
            if not quest:
                return {"status": "error", "message": f"Quest {quest_id} not found"}
            
            quest_id_result, quest_name, reward_points = quest
            
            # 2. Create award
            award_id = f"QA-{uuid.uuid4().hex[:8]}-{user_id}"
            ts = datetime.utcnow()
            today = date.today()
            
            # 3. Insert quest award
            conn.execute(text("""
                INSERT INTO quest_awards (award_id, user_id, as_of_date, selected_quest, reward_points, timestamp)
                VALUES (:a, :u, :d, :q, :p, :ts)
            """), {
                'a': award_id,
                'u': user_id,
                'd': today,
                'q': quest_id,
                'p': reward_points or 0,
                'ts': ts
            })
            
            # 4. Insert junction entry (mark as triggered)
            conn.execute(text("""
                INSERT INTO quest_award_quests (award_id, quest_id, status)
                VALUES (:a, :q, 'TRIGGERED')
            """), {'a': award_id, 'q': quest_id})
            
            # 5. Create notification
            notif_id = f"N-{uuid.uuid4().hex[:8]}-{user_id}"
            conn.execute(text("""
                INSERT INTO notifications (notification_id, user_id, channel, message, sent_at)
                VALUES (:n, :u, :ch, :m, :ts)
            """), {
                'n': notif_id,
                'u': user_id,
                'ch': 'BiP',
                'm': f"🎉 Başarılı! '{quest_name}' görevi tamamlandı. +{reward_points} puan!",
                'ts': ts
            })
            
            # Get updated total points
            total_pts = conn.execute(text("""
                SELECT COALESCE(SUM(points_delta), 0) FROM points_ledger WHERE user_id = :u
            """), {'u': user_id}).scalar()
            
            return {
                "status": "success",
                "message": f"Quest '{quest_name}' earned! +{reward_points} pts",
                "award_id": award_id,
                "reward_points": reward_points,
                "total_points": total_pts,
                "notification_id": notif_id
            }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
