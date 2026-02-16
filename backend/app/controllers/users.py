from fastapi import APIRouter, HTTPException, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_users(limit: int = Query(100, ge=1, le=1000)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT user_id, name, city, segment FROM users ORDER BY user_id LIMIT :lim'), {'lim': limit}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{user_id}")
def get_user_detail(user_id: str):
    with db.engine.connect() as conn:
        u = conn.execute(text('SELECT user_id, name, city, segment FROM users WHERE user_id = :u'), {'u': user_id}).fetchone()
        if not u:
            raise HTTPException(status_code=404, detail='user not found')
        state = conn.execute(text('''
            SELECT us.*, COALESCE(lv.total_points, 0) AS total_points
            FROM user_state us
            LEFT JOIN leaderboard_view lv ON us.user_id = lv.user_id
            WHERE us.user_id = :u
        '''), {'u': user_id}).fetchone()
        awards = conn.execute(text('''
            SELECT qa.award_id, qa.user_id, qa.as_of_date, qa.selected_quest,
                   qa.reward_points, qa.timestamp
            FROM quest_awards qa
            WHERE qa.user_id = :u ORDER BY qa.timestamp DESC LIMIT 10
        '''), {'u': user_id}).fetchall()
        badges = conn.execute(text('SELECT b.badge_id, b.badge_name, ba.awarded_at FROM badge_awards ba JOIN badges b ON ba.badge_id = b.badge_id WHERE ba.user_id = :u ORDER BY ba.awarded_at DESC'), {'u': user_id}).fetchall()
        notifs = conn.execute(text('SELECT * FROM notifications WHERE user_id = :u ORDER BY sent_at DESC LIMIT 20'), {'u': user_id}).fetchall()

    return {
        'user': dict(u._mapping),
        'state': dict(state._mapping) if state else None,
        'recent_awards': [dict(r._mapping) for r in awards],
        'badges': [dict(b._mapping) for b in badges],
        'notifications': [dict(n._mapping) for n in notifs],
    }
