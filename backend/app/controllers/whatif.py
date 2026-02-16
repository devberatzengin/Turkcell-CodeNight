from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict
from ..services.whatif import simulate_metrics

router = APIRouter()


class MetricDelta(BaseModel):
    """Request body for what-if simulation."""
    user_id: str
    deltas: Dict[str, int]  # e.g., {"pvp_wins_today": 2, "login_count_today": 1}


@router.post("/simulate", summary="What-if quest simulator")
def simulate_quest_for_user(request: MetricDelta):
    """
    Simulate what quest a user would get if their metrics changed.

    Example request:
    {
      "user_id": "U1",
      "deltas": {"pvp_wins_today": 2, "login_count_today": 1}
    }

    Returns analysis comparing current vs simulated quest selection.
    """
    result = simulate_metrics(request.user_id, request.deltas)
    return result


@router.post("/simulate_raw", summary="What-if quest simulator (query params)")
def simulate_quest_for_user_raw(user_id: str = Query(...), pvp_wins_delta: int = Query(0), login_delta: int = Query(0), play_minutes_delta: int = Query(0)):
    """
    Simulate what quest a user would get if their metrics changed (URL-encoded).

    Query params:
    - user_id (required): User ID
    - pvp_wins_delta: Change to pvp_wins_today
    - login_delta: Change to login_count_today
    - play_minutes_delta: Change to play_minutes_today

    Example: /whatif/simulate_raw?user_id=U1&pvp_wins_delta=2&login_delta=1
    """
    deltas = {}
    if pvp_wins_delta != 0:
        deltas['pvp_wins_today'] = pvp_wins_delta
    if login_delta != 0:
        deltas['login_count_today'] = login_delta
    if play_minutes_delta != 0:
        deltas['play_minutes_today'] = play_minutes_delta

    result = simulate_metrics(user_id, deltas)
    return result
