#!/usr/bin/env python3
"""Verify database state after pipeline execution."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text

engine = db.engine
with engine.connect() as conn:
    print("=" * 60)
    print("DATABASE STATE VERIFICATION")
    print("=" * 60)
    
    # Activity events
    ae_count = conn.execute(text("SELECT COUNT(*) FROM activity_events")).scalar()
    print(f"\n✓ activity_events: {ae_count} rows")
    ae_dates = conn.execute(text("SELECT DISTINCT date FROM activity_events ORDER BY date")).fetchall()
    print(f"  Dates: {[d[0] for d in ae_dates]}")
    
    # User state
    states = conn.execute(text("""
        SELECT user_id, login_count_today, play_minutes_today, 
               pvp_wins_today, login_streak_days FROM user_state ORDER BY user_id
    """)).fetchall()
    print(f"\n✓ user_state: {len(states)} rows")
    for s in states[:3]:
        print(f"  {s}")
    
    # Quest awards
    qa = conn.execute(text("""
        SELECT award_id, user_id, as_of_date, selected_quest, reward_points 
        FROM quest_awards ORDER BY user_id LIMIT 5
    """)).fetchall()
    qa_count = conn.execute(text("SELECT COUNT(*) FROM quest_awards")).scalar()
    print(f"\n✓ quest_awards: {qa_count} rows")
    for q in qa:
        print(f"  {q}")
    
    # Badge awards
    ba_count = conn.execute(text("SELECT COUNT(*) FROM badge_awards")).scalar()
    ba = conn.execute(text("""
        SELECT user_id, badge_id, awarded_at FROM badge_awards ORDER BY user_id LIMIT 5
    """)).fetchall()
    print(f"\n✓ badge_awards: {ba_count} rows")
    for b in ba:
        print(f"  {b}")
    
    # Leaderboard
    lb = conn.execute(text("""
        SELECT rank, user_id, total_points FROM leaderboard_view ORDER BY rank
    """)).fetchall()
    print(f"\n✓ leaderboard_view: {len(lb)} rows")
    for l in lb:
        print(f"  {l}")
    
    # Points ledger
    ledger = conn.execute(text("""
        SELECT user_id, points_delta, source, source_ref FROM points_ledger 
        ORDER BY user_id, created_at LIMIT 10
    """)).fetchall()
    ledger_count = conn.execute(text("SELECT COUNT(*) FROM points_ledger")).scalar()
    print(f"\n✓ points_ledger: {ledger_count} rows")
    for l in ledger[:3]:
        print(f"  {l}")

print("\n" + "=" * 60)
