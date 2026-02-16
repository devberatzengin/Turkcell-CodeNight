#!/usr/bin/env python3
"""Verify database state: badge diversity and quest variety."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text

engine = db.engine
with engine.connect() as conn:
    print("=" * 70)
    print("DATABASE VERIFICATION - BADGE DIVERSITY")
    print("=" * 70)
    
    # Leaderboard with badges
    lb = conn.execute(text("""
        SELECT lv.rank, lv.user_id, lv.total_points,
               array_agg(DISTINCT ba.badge_id) as badges
        FROM leaderboard_view lv
        LEFT JOIN badge_awards ba ON lv.user_id = ba.user_id
        GROUP BY lv.rank, lv.user_id, lv.total_points
        ORDER BY lv.rank
    """)).fetchall()
    
    print("\nLEADERBOARD WITH BADGES:")
    print(f"{'Rank':<6} {'User':<8} {'Points':<10} {'Badges':<20}")
    print("-" * 70)
    for rank, uid, points, badges in lb:
        badge_list = [b for b in (badges or []) if b is not None]
        badge_str = ", ".join(badge_list) if badge_list else "None"
        print(f"{rank:<6} {uid:<8} {points:<10} {badge_str:<20}")
    
    # Badge distribution
    print("\n" + "=" * 70)
    print("BADGE DISTRIBUTION")
    print("=" * 70)
    
    badges_info = conn.execute(text("""
        SELECT b.badge_id, b.badge_name, b.level, COUNT(ba.user_id) as awarded_count
        FROM badges b
        LEFT JOIN badge_awards ba ON b.badge_id = ba.badge_id
        GROUP BY b.badge_id, b.badge_name, b.level
        ORDER BY b.level DESC
    """)).fetchall()
    
    for bid, bname, level, count in badges_info:
        print(f"{bid} - {bname} (Level {level}): {count} users")
    
    # Quest awards variety
    print("\n" + "=" * 70)
    print("QUEST AWARDS BY USER")
    print("=" * 70)
    
    qa_stats = conn.execute(text("""
        SELECT user_id, COUNT(*) as quest_count, SUM(reward_points) as total_points,
               array_agg(DISTINCT selected_quest) as quests
        FROM quest_awards
        GROUP BY user_id
        ORDER BY total_points DESC
    """)).fetchall()
    
    for uid, qcount, tpoints, quests in qa_stats:
        quest_list = [q for q in (quests or []) if q is not None]
        quest_str = ", ".join(quest_list) if quest_list else "None"
        print(f"{uid}: {qcount} quests, {tpoints} total pts → Quests: {quest_str}")
    
    # User state metrics
    print("\n" + "=" * 70)
    print("USER STATE METRICS (FOR TODAY)")
    print("=" * 70)
    
    states = conn.execute(text("""
        SELECT user_id, login_count_today, pvp_wins_today, coop_minutes_today,
               play_minutes_today, topup_try_today, login_streak_days
        FROM user_state
        ORDER BY user_id
    """)).fetchall()
    
    for s in states:
        print(f"{s[0]}: Logins={s[1]}, PvP={s[2]}, Coop={s[3]}min, Play={s[4]}min, TopUp={s[5]}, Streak={s[6]}")

print("\n" + "=" * 70)
