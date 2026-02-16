from fastapi import APIRouter, Query
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/", summary="Get leaderboard")
def get_leaderboard(limit: int = Query(10, ge=1, le=100)):
    with db.engine.connect() as conn:
        rows = conn.execute(text('SELECT rank, user_id, total_points FROM leaderboard ORDER BY rank ASC LIMIT :lim'), {'lim': limit}).fetchall()
    return [dict(r) for r in rows]


@router.get("/top", summary="Get top N leaderboard")
def get_top(n: int = Query(10, ge=1, le=100)):
    return get_leaderboard(limit=n)
