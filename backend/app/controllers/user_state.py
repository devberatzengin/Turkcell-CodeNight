from fastapi import APIRouter, HTTPException, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_user_states(limit: int = Query(100, ge=1, le=1000)):
    """List user states for all users."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT user_id, login_count_today, play_minutes_today, pvp_wins_today, 
                   coop_minutes_today, topup_try_today, play_minutes_7d, topup_try_7d, 
                   logins_7d, login_streak_days, total_points 
            FROM user_state 
            ORDER BY total_points DESC LIMIT :lim
        '''), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/{user_id}")
def get_user_state(user_id: str):
    """Get user state for a specific user."""
    with db.engine.connect() as conn:
        row = conn.execute(text('''
            SELECT user_id, name, city, segment, login_count_today, play_minutes_today, pvp_wins_today, 
                   coop_minutes_today, topup_try_today, play_minutes_7d, topup_try_7d, 
                   logins_7d, login_streak_days, total_points 
            FROM user_state 
            WHERE user_id = :u
        '''), {'u': user_id}).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail='user state not found')
    return dict(row)
