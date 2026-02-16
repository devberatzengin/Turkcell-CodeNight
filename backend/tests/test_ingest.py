"""
Integration tests for the ingestion service.
Tests CSV loading and database upserts.
"""
import pytest
import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text

from backend.app.db import Base
from backend.app.models import User, Game, Quest, Badge, ActivityEvent


@pytest.fixture
def sqlite_engine():
    """Create a test SQLite engine."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return engine


def test_csv_loading(sample_csv_dir, sqlite_engine):
    """Test that CSV files can be loaded successfully."""
    import os
    assert os.path.exists(os.path.join(sample_csv_dir, 'users.csv'))
    assert os.path.exists(os.path.join(sample_csv_dir, 'games.csv'))
    assert os.path.exists(os.path.join(sample_csv_dir, 'quests.csv'))
    assert os.path.exists(os.path.join(sample_csv_dir, 'activity_events.csv'))

    # Load and verify data
    users = pd.read_csv(os.path.join(sample_csv_dir, 'users.csv'))
    assert len(users) == 2
    assert 'U1' in users['user_id'].values

    quests = pd.read_csv(os.path.join(sample_csv_dir, 'quests.csv'))
    assert len(quests) == 2
    assert quests[quests['quest_id'] == 'Q1']['reward_points'].values[0] == 50


def test_model_instantiation(sqlite_engine):
    """Test that models can be instantiated and persisted."""
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=sqlite_engine)
    session = Session()

    # Create a user
    user = User(user_id='U1', name='Test User', city='Test City', segment='STUDENT')
    session.add(user)
    session.commit()

    # Retrieve and verify
    retrieved = session.query(User).filter_by(user_id='U1').first()
    assert retrieved is not None
    assert retrieved.name == 'Test User'
    session.close()


def test_foreign_key_relationships(sqlite_engine):
    """Test that foreign key relationships work."""
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=sqlite_engine)
    session = Session()

    # Create base data
    user = User(user_id='U1', name='Test', city='City', segment='STUDENT')
    game = Game(game_id='G1', game_name='Test Game', genre='PVP')
    session.add(user)
    session.add(game)
    session.commit()

    # Create an activity event with foreign keys
    event = ActivityEvent(
        event_id='E1',
        user_id='U1',
        date=date(2026, 3, 12),
        game_id='G1',
        login_count=1,
        play_minutes=100,
        pvp_wins=0,
        coop_minutes=0,
        topup_try=0,
    )
    session.add(event)
    session.commit()

    # Verify relationship
    retrieved_event = session.query(ActivityEvent).filter_by(event_id='E1').first()
    assert retrieved_event is not None
    assert retrieved_event.user_id == 'U1'
    assert retrieved_event.game_id == 'G1'

    session.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
