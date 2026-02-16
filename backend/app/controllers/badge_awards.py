from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_badge_awards(limit: int = Query(100, ge=1, le=1000)):
    """List all badge awards."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT ba.award_id, ba.user_id, ba.badge_id, b.badge_name, b.level, ba.awarded_at 
            FROM badge_awards ba 
            JOIN badges b ON ba.badge_id = b.badge_id 
            ORDER BY ba.awarded_at DESC LIMIT :lim
        '''), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/user/{user_id}")
def badges_for_user(user_id: str):
    """Get all badges awarded to a user."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT ba.award_id, ba.badge_id, b.badge_name, b.level, ba.awarded_at 
            FROM badge_awards ba 
            JOIN badges b ON ba.badge_id = b.badge_id 
            WHERE ba.user_id = :u 
            ORDER BY ba.awarded_at DESC
        '''), {'u': user_id}).fetchall()
    return [dict(r) for r in rows]
