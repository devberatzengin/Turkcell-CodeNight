"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.db import Base


@pytest.fixture(scope="session")
def test_db():
    """Create an in-memory test database."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_db):
    """Create a test session for each test."""
    SessionLocal = sessionmaker(bind=test_db, future=True)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_csv_dir(tmp_path):
    """Create temporary CSV files for testing."""
    import pandas as pd

    # Users CSV
    users_df = pd.DataFrame({
        'user_id': ['U1', 'U2'],
        'name': ['Test1', 'Test2'],
        'city': ['City1', 'City2'],
        'segment': ['STUDENT', 'YOUNG_PRO'],
    })
    users_df.to_csv(tmp_path / 'users.csv', index=False)

    # Games CSV
    games_df = pd.DataFrame({
        'game_id': ['G1', 'G2'],
        'game_name': ['Game1', 'Game2'],
        'genre': ['PVP', 'CASUAL'],
    })
    games_df.to_csv(tmp_path / 'games.csv', index=False)

    # Badges CSV
    badges_df = pd.DataFrame({
        'badge_id': ['B1'],
        'badge_name': ['Test Badge'],
        'condition': ['total_points >= 100'],
        'level': [1],
    })
    badges_df.to_csv(tmp_path / 'badges.csv', index=False)

    # Quests CSV
    quests_df = pd.DataFrame({
        'quest_id': ['Q1', 'Q2'],
        'quest_name': ['Quest1', 'Quest2'],
        'quest_type': ['DAILY', 'WEEKLY'],
        'condition': ['login_count_today >= 1', 'play_minutes_7d >= 100'],
        'reward_points': [50, 100],
        'priority': [5, 4],
        'is_active': [True, True],
    })
    quests_df.to_csv(tmp_path / 'quests.csv', index=False)

    # Activity Events CSV
    activity_df = pd.DataFrame({
        'event_id': ['E1', 'E2', 'E3'],
        'user_id': ['U1', 'U1', 'U2'],
        'date': ['2026-03-12', '2026-03-11', '2026-03-12'],
        'game_id': ['G1', 'G2', 'G1'],
        'login_count': [1, 1, 1],
        'play_minutes': [100, 50, 150],
        'pvp_wins': [2, 1, 0],
        'coop_minutes': [30, 20, 40],
        'topup_try': [0, 50, 100],
    })
    activity_df.to_csv(tmp_path / 'activity_events.csv', index=False)

    return str(tmp_path)
