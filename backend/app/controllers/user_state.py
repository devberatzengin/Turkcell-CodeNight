from fastapi import APIRouter, HTTPException, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_user_states(limit: int = Query(100, ge=1, le=1000)):
    """List user states joined with total_points from leaderboard_view."""
    with db.engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT us.user_id, us.login_count_today, us.play_minutes_today, us.pvp_wins_today,
                   us.coop_minutes_today, us.topup_try_today, us.play_minutes_7d, us.topup_try_7d,
                   us.logins_7d, us.login_streak_days,
                   COALESCE(lv.total_points, 0) AS total_points
            FROM user_state us
            LEFT JOIN leaderboard_view lv ON us.user_id = lv.user_id
            ORDER BY total_points DESC
            LIMIT :lim
        '''), {'lim': limit}).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{user_id}")
def get_user_state(user_id: str):
    """Get user state with total_points from leaderboard_view and name/city/segment from users."""
    with db.engine.connect() as conn:
        row = conn.execute(text('''
            SELECT us.user_id, u.name, u.city, u.segment,
                   us.login_count_today, us.play_minutes_today, us.pvp_wins_today,
                   us.coop_minutes_today, us.topup_try_today, us.play_minutes_7d, us.topup_try_7d,
                   us.logins_7d, us.login_streak_days,
                   COALESCE(lv.total_points, 0) AS total_points
            FROM user_state us
            JOIN users u ON us.user_id = u.user_id
            LEFT JOIN leaderboard_view lv ON us.user_id = lv.user_id
            WHERE us.user_id = :u
        '''), {'u': user_id}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='user state not found')
    return dict(row._mapping)
