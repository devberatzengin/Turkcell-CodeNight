"""Activity tracking controller - logs user activities like logins."""

from fastapi import APIRouter, Query, Body
from typing import Optional
from pydantic import BaseModel
from .. import db
from sqlalchemy import text
from datetime import datetime, date
import uuid

router = APIRouter()


class LoginRequest(BaseModel):
    user_id: str


@router.post("/record-login")
def record_login_activity(req: Optional[LoginRequest] = Body(None), user_id: str = Query(None)):
    """Record a login activity for the user - create activity event and notification."""
    # Handle both POST body and query parameter for backward compatibility
    uid = req.user_id if req else user_id
    if not uid:
        return {"status": "error", "message": "user_id required"}
    
    user_id = uid
    try:
        with db.engine.begin() as conn:
            # 1. Check if user exists
            user = conn.execute(text("""
                SELECT user_id, name FROM users WHERE user_id = :u
            """), {'u': user_id}).fetchone()
            
            if not user:
                return {"status": "error", "message": f"User {user_id} not found"}
            
            user_name = user[1]
            today = date.today()
            
            # 2. Check if already logged in today
            existing_event = conn.execute(text("""
                SELECT event_id FROM activity_events 
                WHERE user_id = :u AND date = :d
                LIMIT 1
            """), {'u': user_id, 'd': today}).fetchone()
            
            if existing_event:
                # 3a. Increment login count if already logged in today
                conn.execute(text("""
                    UPDATE activity_events
                    SET login_count = login_count + 1
                    WHERE event_id = :e
                """), {'e': existing_event[0]})
            else:
                # 3b. Create login activity event for first login of the day
                event_id = f"LOGIN-{uuid.uuid4().hex[:8]}-{user_id}"
                conn.execute(text("""
                    INSERT INTO activity_events 
                    (event_id, user_id, date, game_id, login_count, play_minutes, pvp_wins, coop_minutes, topup_try)
                    VALUES (:e, :u, :d, :g, 1, 0, 0, 0, 0)
                """), {'e': event_id, 'u': user_id, 'd': today, 'g': 'G1'})
            
            # 4. Get current streak from user_state and total points from leaderboard_view
            state = conn.execute(text("""
                SELECT login_streak_days FROM user_state WHERE user_id = :u
            """), {'u': user_id}).fetchone()
            
            streak = state[0] if state else 0
            
            # Get total points from leaderboard_view
            lb = conn.execute(text("""
                SELECT total_points FROM leaderboard_view WHERE user_id = :u
            """), {'u': user_id}).fetchone()
            
            total_pts = lb[0] if lb else 0
            
            # 5. Create notification
            notif_id = f"N-{uuid.uuid4().hex[:8]}-{user_id}"
            ts = datetime.utcnow()
            
            message = f"🎮 Hoş geldin, {user_name}! Streak: {streak} gün (Total Puan: {total_pts})"
            
            conn.execute(text("""
                INSERT INTO notifications (notification_id, user_id, channel, message, sent_at)
                VALUES (:n, :u, :ch, :m, :ts)
            """), {
                'n': notif_id,
                'u': user_id,
                'ch': 'BiP',
                'm': message,
                'ts': ts
            })
            
            return {
                "status": "success",
                "message": message,
                "user_id": user_id,
                "user_name": user_name,
                "streak": streak,
                "total_points": total_pts,
                "notification_id": notif_id
            }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
