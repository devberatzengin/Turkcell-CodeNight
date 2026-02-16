#!/usr/bin/env python3
"""Setup script: Ingest CSVs and update dates for current testing."""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.services.ingest import run_ingest
from sqlalchemy import text

print("=" * 60)
print("STEP 1: INGEST CSVs")
print("=" * 60)

# Get absolute path to datasets
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
datasets_dir = os.path.join(workspace_root, 'datasets')
print(f"Datasets path: {datasets_dir}")
print(f"Datasets exist: {os.path.exists(datasets_dir)}")

ingest_result = run_ingest(dataset_dir=datasets_dir)
print(f"\nIngest result: {ingest_result}\n")

print("=" * 60)
print("STEP 2: UPDATE DATES (Mar → Feb)")
print("=" * 60)

engine = db.engine
with engine.begin() as conn:
    # Shift dates: 2026-03-08 to 2026-03-12 → 2026-02-17 to 2026-02-21 (19 days back)
    result = conn.execute(text("""
        UPDATE activity_events 
        SET date = date - 19
        WHERE date >= '2026-03-08' AND date <= '2026-03-12'
    """))
    print(f"✓ Updated {result.rowcount} activity_events rows (date - 19 days)")
    
    # Verify
    count = conn.execute(text("SELECT COUNT(*) FROM activity_events WHERE date >= '2026-02-17' AND date <= '2026-02-21'")).scalar()
    print(f"✓ Verified: {count} events now in Feb 17-21 range")
    
    # Show sample
    sample = conn.execute(text("SELECT event_id, user_id, date FROM activity_events LIMIT 5")).fetchall()
    print(f"✓ Sample events:")
    for ev in sample:
        print(f"  {ev}")

print("\n" + "=" * 60)
print("READY FOR PIPELINE EXECUTION")
print("=" * 60)
print("\nNow run: curl -X POST 'http://localhost:8000/pipeline/run?sync=true'")
print()
