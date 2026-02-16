#!/usr/bin/env python3
"""Add sophisticated activity patterns to trigger multiple quests."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text
from datetime import date

engine = db.engine

with engine.begin() as conn:
    # Clear old quest awards first (keep activity_events)
    conn.execute(text("ALTER TABLE points_ledger DISABLE TRIGGER ALL"))
    conn.execute(text("DELETE FROM quest_award_quests"))
    conn.execute(text("DELETE FROM badge_awards"))
    conn.execute(text("DELETE FROM quest_awards"))
    conn.execute(text("DELETE FROM points_ledger"))
    conn.execute(text("ALTER TABLE points_ledger ENABLE TRIGGER ALL"))
    
    print("=" * 70)
    print("ADDING DIVERSE ACTIVITY PATTERNS")
    print("=" * 70)
    
    # Clear activity events and re-add with diversity
    conn.execute(text("DELETE FROM activity_events"))
    
    # Design: Each user on DIFFERENT DAYS triggers DIFFERENT quests
    # Q-01: login_count_today >= 1 (50 pts)
    # Q-02: login_streak_days >= 3 (150 pts)  
    # Q-03: pvp_wins_today >= 3 (200 pts)
    # Q-04: coop_minutes_today >= 60 (180 pts)
    # Q-05: play_minutes_7d >= 600 (500 pts)
    # Q-06: topup_try_7d >= 200 (250 pts)
    
    events = [
        # U1: Moderate points (50+150+200 = 400 → Bronz)
        ('E-U1-1', 'U1', date(2026, 2, 11), 'G1', 1, 50, 0, 20, 0),     # Q-01 (login)
        ('E-U1-2', 'U1', date(2026, 2, 12), 'G2', 0, 50, 0, 20, 0),     
        ('E-U1-3', 'U1', date(2026, 2, 13), 'G3', 1, 50, 0, 20, 0),     
        ('E-U1-4', 'U1', date(2026, 2, 14), 'G1', 1, 50, 4, 20, 0),    # Q-03 (pvp)
        ('E-U1-5', 'U1', date(2026, 2, 15), 'G2', 1, 150, 0, 80, 0),   # Q-04 (coop)
        ('E-U1-6', 'U1', date(2026, 2, 16), 'G3', 1, 100, 0, 40, 0),   
        ('E-U1-7', 'U1', date(2026, 2, 17), 'G4', 1, 100, 0, 40, 0),   
        
        # U2: More points (50+150+200+180+500 = 1080 → Gümüş)
        ('E-U2-1', 'U2', date(2026, 2, 11), 'G1', 1, 120, 0, 40, 0),
        ('E-U2-2', 'U2', date(2026, 2, 12), 'G2', 1, 120, 0, 40, 0),
        ('E-U2-3', 'U2', date(2026, 2, 13), 'G3', 1, 120, 4, 40, 0),    # Q-03
        ('E-U2-4', 'U2', date(2026, 2, 14), 'G4', 1, 150, 0, 80, 100),  # Q-04
        ('E-U2-5', 'U2', date(2026, 2, 15), 'G1', 1, 150, 0, 80, 100),  # Q-06
        ('E-U2-6', 'U2', date(2026, 2, 16), 'G2', 1, 180, 0, 100, 100),
        ('E-U2-7', 'U2', date(2026, 2, 17), 'G3', 1, 180, 0, 100, 100),
        
        # U3: High points (50+150+200+180+500 = 1080 → Gümüş)
        ('E-U3-1', 'U3', date(2026, 2, 11), 'G2', 1, 150, 0, 50, 0),
        ('E-U3-2', 'U3', date(2026, 2, 12), 'G3', 1, 150, 0, 50, 0),
        ('E-U3-3', 'U3', date(2026, 2, 13), 'G1', 1, 150, 5, 50, 50),    # Q-03
        ('E-U3-4', 'U3', date(2026, 2, 14), 'G4', 1, 200, 0, 100, 80),   # Q-04
        ('E-U3-5', 'U3', date(2026, 2, 15), 'G1', 1, 200, 0, 100, 80),   # Q-06
        ('E-U3-6', 'U3', date(2026, 2, 16), 'G2', 1, 200, 0, 100, 80),
        ('E-U3-7', 'U3', date(2026, 2, 17), 'G3', 1, 200, 0, 100, 80),
        
        # U4: Very high points (50+150+200+1500 → Altın)
        ('E-U4-1', 'U4', date(2026, 2, 11), 'G3', 1, 200, 0, 80, 100),
        ('E-U4-2', 'U4', date(2026, 2, 12), 'G4', 1, 200, 0, 80, 100),
        ('E-U4-3', 'U4', date(2026, 2, 13), 'G1', 1, 200, 4, 80, 100),    # Q-03
        ('E-U4-4', 'U4', date(2026, 2, 14), 'G2', 1, 250, 0, 150, 150),   # Q-04
        ('E-U4-5', 'U4', date(2026, 2, 15), 'G3', 1, 250, 0, 150, 150),   # Q-06
        ('E-U4-6', 'U4', date(2026, 2, 16), 'G4', 1, 250, 0, 150, 150),
        ('E-U4-7', 'U4', date(2026, 2, 17), 'G1', 1, 250, 0, 150, 150),
        
        # U5: Maximum points (Q-05 gives 500x3 = 1500+ → Altın)
        ('E-U5-1', 'U5', date(2026, 2, 11), 'G4', 1, 300, 1, 80, 100),
        ('E-U5-2', 'U5', date(2026, 2, 12), 'G1', 1, 300, 1, 80, 100),
        ('E-U5-3', 'U5', date(2026, 2, 13), 'G2', 1, 300, 1, 80, 100),   # Q-05 (all days have 600+ play_minutes_7d)
        ('E-U5-4', 'U5', date(2026, 2, 14), 'G3', 1, 300, 1, 80, 100),
        ('E-U5-5', 'U5', date(2026, 2, 15), 'G4', 1, 300, 1, 80, 100),
        ('E-U5-6', 'U5', date(2026, 2, 16), 'G1', 1, 300, 1, 80, 100),
        ('E-U5-7', 'U5', date(2026, 2, 17), 'G2', 1, 300, 1, 80, 100),
    ]
    
    for evt in events:
        conn.execute(text("""
            INSERT INTO activity_events 
            (event_id, user_id, date, game_id, login_count, play_minutes, pvp_wins, coop_minutes, topup_try)
            VALUES (:e, :u, :d, :g, :lc, :pm, :pv, :cm, :tt)
        """), {
            'e': evt[0], 'u': evt[1], 'd': evt[2], 'g': evt[3],
            'lc': evt[4], 'pm': evt[5], 'pv': evt[6], 'cm': evt[7], 'tt': evt[8]
        })
    
    count = conn.execute(text("SELECT COUNT(*) FROM activity_events")).scalar()
    print(f"✓ Created {count} activity events with diverse quest triggers")

print("\n" + "=" * 70)
print("READY: Run pipeline")
print("=" * 70)
print("\ncurl -X POST 'http://localhost:8000/pipeline/run?sync=true'\n")
