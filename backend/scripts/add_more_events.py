#!/usr/bin/env python3
"""Add more activity events to database to generate badge-qualifying points."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text
from datetime import datetime, date, timedelta
import random

engine = db.engine

# Generate more activity events (adding to Feb 8-16 range)
events_to_add = [
    # Feb 8-12
    ('E-26', 'U1', date(2026, 2, 8), 'G1', 1, 150, 5, 50, 150),
    ('E-27', 'U1', date(2026, 2, 9), 'G2', 1, 200, 3, 80, 200),
    ('E-28', 'U1', date(2026, 2, 10), 'G3', 1, 250, 2, 100, 250),
    ('E-29', 'U2', date(2026, 2, 8), 'G2', 1, 180, 4, 60, 180),
    ('E-30', 'U2', date(2026, 2, 9), 'G1', 1, 220, 2, 90, 200),
    ('E-31', 'U2', date(2026, 2, 10), 'G3', 1, 260, 1, 110, 220),
    ('E-32', 'U3', date(2026, 2, 8), 'G4', 1, 190, 3, 75, 190),
    ('E-33', 'U3', date(2026, 2, 9), 'G1', 1, 210, 4, 85, 210),
    ('E-34', 'U3', date(2026, 2, 10), 'G2', 1, 240, 2, 95, 230),
    ('E-35', 'U4', date(2026, 2, 8), 'G1', 1, 170, 2, 70, 170),
    ('E-36', 'U4', date(2026, 2, 9), 'G3', 1, 200, 3, 80, 200),
    ('E-37', 'U4', date(2026, 2, 10), 'G4', 1, 230, 1, 100, 230),
    ('E-38', 'U5', date(2026, 2, 8), 'G2', 1, 210, 4, 85, 210),
    ('E-39', 'U5', date(2026, 2, 9), 'G3', 1, 250, 3, 110, 250),
    ('E-40', 'U5', date(2026, 2, 10), 'G1', 1, 280, 2, 130, 280),
    # Feb 11-16 (more recent, closer to today)
    ('E-41', 'U1', date(2026, 2, 11), 'G4', 1, 260, 4, 120, 250),
    ('E-42', 'U1', date(2026, 2, 12), 'G1', 1, 290, 3, 140, 280),
    ('E-43', 'U2', date(2026, 2, 11), 'G2', 1, 240, 3, 105, 240),
    ('E-44', 'U2', date(2026, 2, 12), 'G4', 1, 270, 2, 125, 260),
    ('E-45', 'U3', date(2026, 2, 11), 'G3', 1, 250, 4, 110, 250),
    ('E-46', 'U3', date(2026, 2, 12), 'G1', 1, 280, 3, 130, 270),
    ('E-47', 'U4', date(2026, 2, 11), 'G2', 1, 220, 2, 95, 220),
    ('E-48', 'U4', date(2026, 2, 12), 'G3', 1, 250, 3, 115, 250),
    ('E-49', 'U5', date(2026, 2, 11), 'G4', 1, 300, 4, 150, 300),
    ('E-50', 'U5', date(2026, 2, 12), 'G2', 1, 320, 3, 160, 320),
]

with engine.begin() as conn:
    print("=" * 60)
    print("ADDING MORE ACTIVITY EVENTS")
    print("=" * 60)
    
    for event_data in events_to_add:
        conn.execute(text("""
            INSERT INTO activity_events 
            (event_id, user_id, date, game_id, login_count, play_minutes, pvp_wins, coop_minutes, topup_try)
            VALUES (:e, :u, :d, :g, :lc, :pm, :pv, :cm, :tt)
        """), {
            'e': event_data[0], 'u': event_data[1], 'd': event_data[2], 'g': event_data[3],
            'lc': event_data[4], 'pm': event_data[5], 'pv': event_data[6], 'cm': event_data[7], 'tt': event_data[8]
        })
    
    ae_count = conn.execute(text("SELECT COUNT(*) FROM activity_events")).scalar()
    print(f"✓ Added {len(events_to_add)} events")
    print(f"✓ Total activity_events: {ae_count}")
    
    # Show date range
    dates = conn.execute(text("SELECT MIN(date), MAX(date) FROM activity_events")).fetchone()
    print(f"✓ Date range: {dates[0]} to {dates[1]}")

print("\n" + "=" * 60)
print("NOW RUN PIPELINE AGAIN")
print("=" * 60)
print("curl -X POST 'http://localhost:8000/pipeline/run?sync=true'\n")
