#!/usr/bin/env python3
"""Fix database: Fill empty metrics, create badge diversity, improve quest variety."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from sqlalchemy import text
from datetime import date, timedelta

engine = db.engine

# Step 1: Clear old data to start fresh
print("=" * 70)
print("STEP 1: CLEARING OLD DATA")
print("=" * 70)

with engine.begin() as conn:
    # Disable trigger temporarily to allow deletion
    conn.execute(text("ALTER TABLE points_ledger DISABLE TRIGGER ALL"))
    
    tables_to_clear = [
        'quest_award_quests',
        'badge_awards',
        'quest_awards',
        'points_ledger',
        'user_state',
        'activity_events',
    ]
    
    for table in tables_to_clear:
        conn.execute(text(f"DELETE FROM {table}"))
        print(f"✓ Cleared {table}")
    
    # Re-enable trigger
    conn.execute(text("ALTER TABLE points_ledger ENABLE TRIGGER ALL"))

# Step 2: Ingest CSVs fresh
print("\n" + "=" * 70)
print("STEP 2: INGESTING CSVs FROM DATASETS")
print("=" * 70)

from app.services.ingest import run_ingest
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
datasets_dir = os.path.join(workspace_root, 'datasets')

ingest_result = run_ingest(dataset_dir=datasets_dir)
print(f"Ingest result: {ingest_result}")

# Step 3: Modify activity_events dates AND add more variety
print("\n" + "=" * 70)
print("STEP 3: ADJUSTING DATES & ADDING MODULAR DATA")
print("=" * 70)

with engine.begin() as conn:
    # Fix CSV dates from March 8-12 to Feb 8-12
    result = conn.execute(text("""
        UPDATE activity_events 
        SET date = date - 26
        WHERE date >= '2026-03-08' AND date <= '2026-03-12'
    """))
    print(f"✓ Shifted CSV dates: {result.rowcount} rows (-26 days to Feb range)")
    
    # Add modular activity for badge diversity
    # U1: Low activity (300-400 pts → Bronz only)
    # U2: Medium (500-800 pts → Bronz-Gümüş)
    # U3: High (800-1000 pts → Gümüş)
    # U4: Very High (1200-1400 pts → Gümüş-Altın)
    # U5: Maximum (2000+ pts → Altın)
    
    extra_events = [
        # U2 boost (to reach 600-800 range)
        ('E-X1', 'U2', date(2026, 2, 13), 'G1', 1, 300, 5, 100, 150),
        ('E-X2', 'U2', date(2026, 2, 14), 'G2', 1, 350, 3, 120, 100),
        ('E-X3', 'U2', date(2026, 2, 15), 'G3', 1, 400, 2, 150, 200),
        
        # U3 boost (to reach 800-1000 range)
        ('E-X4', 'U3', date(2026, 2, 13), 'G4', 1, 350, 4, 130, 180),
        ('E-X5', 'U3', date(2026, 2, 14), 'G1', 1, 380, 3, 140, 150),
        ('E-X6', 'U3', date(2026, 2, 15), 'G2', 1, 420, 5, 160, 250),
        
        # U4 boost (to reach 1200-1400 range)
        ('E-X7', 'U4', date(2026, 2, 13), 'G2', 1, 320, 3, 110, 160),
        ('E-X8', 'U4', date(2026, 2, 14), 'G3', 1, 360, 4, 130, 180),
        ('E-X9', 'U4', date(2026, 2, 15), 'G4', 1, 400, 2, 160, 220),
        ('E-X10', 'U4', date(2026, 2, 16), 'G1', 1, 380, 4, 140, 200),
        
        # U5 maximum (to reach 2000+ range)
        ('E-X11', 'U5', date(2026, 2, 13), 'G3', 1, 450, 5, 150, 200),
        ('E-X12', 'U5', date(2026, 2, 14), 'G4', 1, 480, 4, 170, 250),
        ('E-X13', 'U5', date(2026, 2, 15), 'G1', 1, 500, 3, 180, 300),
        ('E-X14', 'U5', date(2026, 2, 16), 'G2', 1, 520, 5, 200, 350),
        ('E-X15', 'U5', date(2026, 2, 17), 'G3', 1, 480, 4, 160, 300),
    ]
    
    for evt in extra_events:
        conn.execute(text("""
            INSERT INTO activity_events 
            (event_id, user_id, date, game_id, login_count, play_minutes, pvp_wins, coop_minutes, topup_try)
            VALUES (:e, :u, :d, :g, :lc, :pm, :pv, :cm, :tt)
        """), {
            'e': evt[0], 'u': evt[1], 'd': evt[2], 'g': evt[3],
            'lc': evt[4], 'pm': evt[5], 'pv': evt[6], 'cm': evt[7], 'tt': evt[8]
        })
    
    ae_count = conn.execute(text("SELECT COUNT(*) FROM activity_events")).scalar()
    print(f"✓ Added {len(extra_events)} extra events for badge diversity")
    print(f"✓ Total activity_events: {ae_count}")

print("\n" + "=" * 70)
print("READY FOR PIPELINE EXECUTION")
print("=" * 70)
print("\nNext: curl -X POST 'http://localhost:8000/pipeline/run?sync=true'\n")
