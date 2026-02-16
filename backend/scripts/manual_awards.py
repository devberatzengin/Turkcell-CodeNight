#!/usr/bin/env python3
"""Manually insert diverse quest awards and generate badges."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text
from datetime import datetime, date
import uuid

engine = db.engine

with engine.begin() as conn:
    print("=" * 70)
    print("INSERTING DIVERSE QUEST AWARDS")
    print("=" * 70)
    
    # Design points distribution:
    # U1: 150+50+50 = 250 (Bronz if >= 300? No → 어라?)
    # U2: 180+150+250 = 580 (Bronz)
    # U3: 180+200+250 = 630 (Bronz)
    # U4: 180+200+250+200 = 830 (Gümüş)
    # U5: 500+500+500 = 1500 (Altín!)
    
    awards = [
        # U1: Low (250 pts)
        ('QA-U1-A', 'U1', date(2026, 2, 13), 'Q-02', 150),  # Streak
        ('QA-U1-B', 'U1', date(2026, 2, 14), 'Q-01', 50),   # Login
        ('QA-U1-C', 'U1', date(2026, 2, 15), 'Q-01', 50),   # Login
        
        # U2: Medium-Low (580 pts)
        ('QA-U2-A', 'U2', date(2026, 2, 13), 'Q-04', 180),  # Coop
        ('QA-U2-B', 'U2', date(2026, 2, 14), 'Q-02', 150),  # Streak
        ('QA-U2-C', 'U2', date(2026, 2, 15), 'Q-06', 250),  # Spending
        
        # U3: Medium (630 pts)
        ('QA-U3-A', 'U3', date(2026, 2, 13), 'Q-04', 180),  # Coop
        ('QA-U3-B', 'U3', date(2026, 2, 14), 'Q-03', 200),  # PvP
        ('QA-U3-C', 'U3', date(2026, 2, 15), 'Q-06', 250),  # Spending
        
        # U4: High (830 pts) → Gümüş
        ('QA-U4-A', 'U4', date(2026, 2, 13), 'Q-04', 180),  # Coop
        ('QA-U4-B', 'U4', date(2026, 2, 14), 'Q-03', 200),  # PvP
        ('QA-U4-C', 'U4', date(2026, 2, 15), 'Q-06', 250),  # Spending
        ('QA-U4-D', 'U4', date(2026, 2, 16), 'Q-03', 200),  # PvP again
        
        # U5: Maximum (1500 pts) → Altín
        ('QA-U5-A', 'U5', date(2026, 2, 13), 'Q-05', 500),  # Marathon
        ('QA-U5-B', 'U5', date(2026, 2, 14), 'Q-05', 500),  # Marathon
        ('QA-U5-C', 'U5', date(2026, 2, 15), 'Q-05', 500),  # Marathon
    ]
    
    ts = datetime.utcnow()
    
    for award_id, user_id, as_date, quest_id, points in awards:
        conn.execute(text("""
            INSERT INTO quest_awards (award_id, user_id, as_of_date, selected_quest, reward_points, timestamp)
            VALUES (:a, :u, :d, :q, :p, :ts)
        """), {'a': award_id, 'u': user_id, 'd': as_date, 'q': quest_id, 'p': points, 'ts': ts})
    
    print(f"✓ Inserted {len(awards)} quest awards")
    
    # Verify leaderboard points
    print("\nLEADERBOARD (FROM LEDGER):")
    lb = conn.execute(text("""
        SELECT user_id, SUM(points_delta) as total
        FROM points_ledger
        GROUP BY user_id
        ORDER BY total DESC
    """)).fetchall()
    
    for uid, tot in lb:
        print(f"  {uid}: {tot} pts")

print("\n" + "=" * 70)
print("System ready for dashboard testing!")
print("=" * 70)
