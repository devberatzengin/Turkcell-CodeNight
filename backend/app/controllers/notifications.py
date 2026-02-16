from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_notifications(limit: int = Query(100, ge=1, le=1000)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT notification_id, user_id, channel, message, sent_at FROM notifications ORDER BY sent_at DESC LIMIT :lim'), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/user/{user_id}")
def notifications_for_user(user_id: str, limit: int = Query(50, ge=1, le=500)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT notification_id, channel, message, sent_at FROM notifications WHERE user_id = :u ORDER BY sent_at DESC LIMIT :lim'), {'u': user_id, 'lim': limit}).fetchall()
    return [dict(r) for r in rows]
