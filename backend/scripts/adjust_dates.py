#!/usr/bin/env python3
"""Adjust activity events to recent dates for better metrics."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text
from datetime import date, timedelta

engine = db.engine

with engine.begin() as conn:
    print("=" * 70)
    print("STEP 1: ADJUSTING ACTIVITY EVENTS TO RECENT DATES")
    print("=" * 70)
    
    # Current dates are Feb 8-12, we need them Feb 11-17 (more recent, ending today)
    # Shift forward 3 days
    result = conn.execute(text("""
        UPDATE activity_events 
        SET date = date + 3
        WHERE date >= '2026-02-08' AND date <= '2026-02-21'
    """))
    print(f"✓ Shifted activity_events forward 3 days")
    
    dates = conn.execute(text("SELECT MIN(date), MAX(date) FROM activity_events")).fetchone()
    print(f"✓ New date range: {dates[0]} to {dates[1]}")
    
    # Count events per user to see distribution
    dist = conn.execute(text("""
        SELECT user_id, COUNT(*) as cnt FROM activity_events 
        GROUP BY user_id ORDER BY user_id
    """)).fetchall()
    
    print(f"\n✓ Activity events per user:")
    for uid, cnt in dist:
        print(f"  {uid}: {cnt} events")

print("\n" + "=" * 70)
print("READY: Run pipeline with updated data")
print("=" * 70)
print("\ncurl -X POST 'http://localhost:8000/pipeline/run?sync=true'\n")
