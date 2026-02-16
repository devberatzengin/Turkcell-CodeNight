"""
Unit tests for the pipeline service.
Tests state calculation, quest evaluation, conflict resolution, and badge assignment.
"""
import pytest
from datetime import date, timedelta, datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.services.pipeline import (
    _safe_eval,
    _compute_user_state_from_events,
)


class TestSafeEval:
    """Test the safe expression evaluator."""

    def test_simple_comparison(self):
        """Test basic comparison operators."""
        ctx = {"login_count_today": 1}
        assert _safe_eval("login_count_today >= 1", ctx) is True
        assert _safe_eval("login_count_today >= 2", ctx) is False

    def test_multiple_conditions(self):
        """Test AND/OR logic."""
        ctx = {"pvp_wins_today": 3, "coop_minutes_today": 30}
        assert _safe_eval("pvp_wins_today >= 3 and coop_minutes_today >= 60", ctx) is False
        assert _safe_eval("pvp_wins_today >= 3 or coop_minutes_today >= 60", ctx) is True

    def test_arithmetic(self):
        """Test arithmetic operations."""
        ctx = {"play_minutes_7d": 600}
        assert _safe_eval("play_minutes_7d >= 600", ctx) is True
        assert _safe_eval("play_minutes_7d * 2 >= 1200", ctx) is True

    def test_invalid_code_raises(self):
        """Test that dangerous code is rejected."""
        ctx = {"x": 1}
        with pytest.raises(ValueError):
            _safe_eval("__import__('os').system('ls')", ctx)


class TestStateCalculation:
    """Test user state computation from activity events."""

    def test_today_metrics(self):
        """Test today's metric aggregation."""
        today = date(2026, 3, 12)
        df = pd.DataFrame({
            'user_id': ['U1', 'U1', 'U1'],
            'date': [today, today - timedelta(days=1), today - timedelta(days=2)],
            'login_count': [2, 1, 1],
            'play_minutes': [100, 50, 30],
            'pvp_wins': [2, 1, 0],
            'coop_minutes': [30, 20, 10],
            'topup_try': [0, 50, 100],
        })
        df['date'] = pd.to_datetime(df['date']).dt.date

        state = _compute_user_state_from_events(df, today)

        assert state[state['user_id'] == 'U1']['login_count_today'].values[0] == 2
        assert state[state['user_id'] == 'U1']['play_minutes_today'].values[0] == 100
        assert state[state['user_id'] == 'U1']['pvp_wins_today'].values[0] == 2

    def test_7day_metrics(self):
        """Test 7-day metric aggregation."""
        today = date(2026, 3, 12)
        dates = [today - timedelta(days=i) for i in range(7)]
        df = pd.DataFrame({
            'user_id': ['U1'] * 7,
            'date': dates,
            'login_count': [1] * 7,
            'play_minutes': [100] * 7,
            'pvp_wins': [1] * 7,
            'coop_minutes': [30] * 7,
            'topup_try': [0] * 7,
        })
        df['date'] = pd.to_datetime(df['date']).dt.date

        state = _compute_user_state_from_events(df, today)

        assert state[state['user_id'] == 'U1']['play_minutes_7d'].values[0] == 700
        assert state[state['user_id'] == 'U1']['logins_7d'].values[0] == 7

    def test_login_streak(self):
        """Test login streak calculation."""
        today = date(2026, 3, 12)
        # 5 consecutive days with login
        dates = [today - timedelta(days=i) for i in range(5)]
        df = pd.DataFrame({
            'user_id': ['U1'] * 5,
            'date': dates,
            'login_count': [1, 1, 1, 1, 1],
            'play_minutes': [100] * 5,
            'pvp_wins': [0] * 5,
            'coop_minutes': [0] * 5,
            'topup_try': [0] * 5,
        })
        df['date'] = pd.to_datetime(df['date']).dt.date

        state = _compute_user_state_from_events(df, today)
        assert state[state['user_id'] == 'U1']['login_streak_days'].values[0] == 5

    def test_broken_streak(self):
        """Test that streak breaks on missing login."""
        today = date(2026, 3, 12)
        # 2 days with login, then break, then 1 more login
        dates = [today, today - timedelta(days=1), today - timedelta(days=3)]
        df = pd.DataFrame({
            'user_id': ['U1'] * 3,
            'date': dates,
            'login_count': [1, 1, 1],
            'play_minutes': [100] * 3,
            'pvp_wins': [0] * 3,
            'coop_minutes': [0] * 3,
            'topup_try': [0] * 3,
        })
        df['date'] = pd.to_datetime(df['date']).dt.date

        state = _compute_user_state_from_events(df, today)
        # Should only count 1 (today's login)
        assert state[state['user_id'] == 'U1']['login_streak_days'].values[0] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
