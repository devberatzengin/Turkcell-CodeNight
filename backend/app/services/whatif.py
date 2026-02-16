"""
What-if simulator service.
Allows simulating metric changes and predicting which quest would be selected.
"""
from typing import Dict, List, Tuple
from datetime import date
from sqlalchemy import text
from .. import db
from .pipeline import _safe_eval


def simulate_metrics(user_id: str, metric_deltas: Dict[str, int], as_of_date: date = None) -> Dict:
    """
    Simulate what would happen if a user's metrics were adjusted.

    Args:
        user_id: User ID to simulate
        metric_deltas: Dict of {metric_name: delta_value} to apply
                      e.g., {'pvp_wins_today': 2, 'login_count_today': 1}
        as_of_date: Date to simulate for (default: today)

    Returns:
        Dict with:
        - current_state: User's current state
        - simulated_state: State after applying deltas
        - triggered_quests: Quests that would trigger
        - selected_quest: Which quest would be selected (min priority)
        - analysis: Explanation of the result
    """
    from datetime import datetime

    if as_of_date is None:
        as_of_date = datetime.utcnow().date()

    engine = db.engine
    with engine.connect() as conn:
        # Get current user state
        state_row = conn.execute(text('SELECT * FROM user_state WHERE user_id = :u'), {'u': user_id}).fetchone()
        if not state_row:
            return {"error": f"User {user_id} not found"}

        state_dict = dict(state_row)

        # Load all active quests
        quests = conn.execute(text('SELECT * FROM quests WHERE is_active = true')).fetchall()

    # Build current context
    current_ctx = {k: int(v) for k, v in state_dict.items() if k != 'user_id'}

    # Build simulated context (apply deltas)
    simulated_ctx = current_ctx.copy()
    for metric, delta in metric_deltas.items():
        if metric in simulated_ctx:
            simulated_ctx[metric] = simulated_ctx[metric] + delta
        else:
            simulated_ctx[metric] = delta

    # Evaluate current quests
    current_triggered = _evaluate_quests(quests, current_ctx)
    simulated_triggered = _evaluate_quests(quests, simulated_ctx)

    # Select best quest
    current_best = _select_best_quest(current_triggered)
    simulated_best = _select_best_quest(simulated_triggered)

    # Build response
    return {
        "user_id": user_id,
        "as_of_date": str(as_of_date),
        "metric_changes": metric_deltas,
        "current": {
            "state": {k: current_ctx[k] for k in sorted(current_ctx.keys())},
            "triggered_quests": [q[0] for q in current_triggered],
            "selected_quest": current_best[0] if current_best else None,
            "reward_points": current_best[2] if current_best else 0,
        },
        "simulated": {
            "state": {k: simulated_ctx[k] for k in sorted(simulated_ctx.keys())},
            "triggered_quests": [q[0] for q in simulated_triggered],
            "selected_quest": simulated_best[0] if simulated_best else None,
            "reward_points": simulated_best[2] if simulated_best else 0,
        },
        "analysis": _build_analysis(metric_deltas, current_best, simulated_best),
    }


def _evaluate_quests(quests: List, ctx: Dict) -> List[Tuple]:
    """Evaluate quests against a context. Returns list of (quest_id, priority, reward_points)."""
    triggered = []
    for q in quests:
        cond = q['condition']
        try:
            ok = False
            if cond and isinstance(cond, str) and cond.strip():
                ok = _safe_eval(cond, ctx)
            if ok:
                triggered.append((q['quest_id'], q['priority'], q['reward_points'] or 0))
        except Exception:
            continue
    return triggered


def _select_best_quest(triggered: List[Tuple]) -> Tuple or None:
    """Select the best quest from triggered list (min priority). Returns (quest_id, priority, reward_points)."""
    if not triggered:
        return None
    triggered.sort(key=lambda x: x[1])
    return triggered[0]


def _build_analysis(deltas: Dict[str, int], current: Tuple, simulated: Tuple) -> str:
    """Build a human-readable analysis of the what-if scenario."""
    lines = []
    lines.append("What-if Analysis:")
    
    delta_str = ", ".join([f"{k} +{v}" for k, v in deltas.items()])
    lines.append(f"  Scenario: {delta_str}")

    if current:
        lines.append(f"  Current: {current[0]} ({current[2]} points)")
    else:
        lines.append("  Current: No quest triggered")

    if simulated:
        lines.append(f"  Simulated: {simulated[0]} ({simulated[2]} points)")
    else:
        lines.append("  Simulated: No quest triggered")

    if current and simulated:
        if current[0] == simulated[0]:
            lines.append("  Outcome: Same quest selected")
        else:
            delta_pts = simulated[2] - current[2]
            lines.append(f"  Outcome: Different quest! (+{delta_pts} points)")
    elif not current and simulated:
        lines.append(f"  Outcome: Quest now triggered! (+{simulated[2]} points)")
    elif current and not simulated:
        lines.append("  Outcome: Quest no longer triggered")

    return "\n".join(lines)
