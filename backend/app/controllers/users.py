from fastapi import APIRouter, HTTPException, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_users(limit: int = Query(100, ge=1, le=1000)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT user_id, name, city, segment FROM users ORDER BY user_id LIMIT :lim'), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/{user_id}")
def get_user_detail(user_id: str):
    with db.engine.connect() as conn:
        u = conn.execute(text('SELECT user_id, name, city, segment FROM users WHERE user_id = :u'), {'u': user_id}).fetchone()
        if not u:
            raise HTTPException(status_code=404, detail='user not found')
        state = conn.execute(text('SELECT * FROM user_state WHERE user_id = :u'), {'u': user_id}).fetchone()
        awards = conn.execute(text('SELECT * FROM quest_awards WHERE user_id = :u ORDER BY timestamp DESC LIMIT 10'), {'u': user_id}).fetchall()
        badges = conn.execute(text('SELECT b.badge_id, b.badge_name, ba.awarded_at FROM badge_awards ba JOIN badges b ON ba.badge_id = b.badge_id WHERE ba.user_id = :u ORDER BY ba.awarded_at DESC'), {'u': user_id}).fetchall()
        notifs = conn.execute(text('SELECT * FROM notifications WHERE user_id = :u ORDER BY sent_at DESC LIMIT 20'), {'u': user_id}).fetchall()

    return {
        'user': dict(u),
        'state': dict(state) if state else None,
        'recent_awards': [dict(r) for r in awards],
        'badges': [dict(b) for b in badges],
        'notifications': [dict(n) for n in notifs],
    }
