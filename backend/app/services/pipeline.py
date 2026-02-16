from typing import Dict, List
from datetime import datetime, timedelta, date
import uuid
import pandas as pd
import ast
from sqlalchemy import text
from .. import db
from . import ingest


def _safe_eval(expr: str, ctx: dict) -> bool:
    """Evaluate simple boolean expressions safely using AST.

    Supports comparisons and boolean and/or, names mapped from ctx.
    """
    tree = ast.parse(expr, mode='eval')

    allowed_nodes = (
        ast.Expression,
        ast.BoolOp,
        ast.BinOp,
        ast.UnaryOp,
        ast.Compare,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.And,
        ast.Or,
        ast.Gt,
        ast.Lt,
        ast.GtE,
        ast.LtE,
        ast.Eq,
        ast.NotEq,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Disallowed expression element: {type(node)}")

    code = compile(tree, '<string>', 'eval')
    return bool(eval(code, {}, ctx))


def _compute_user_state_from_events(df_events: pd.DataFrame, as_of_date: date) -> pd.DataFrame:
    # df_events expected columns: user_id, date, login_count, play_minutes, pvp_wins, coop_minutes, topup_try
    if df_events.empty:
        return pd.DataFrame()

    df_events['date'] = pd.to_datetime(df_events['date']).dt.date

    # today metrics
    today = as_of_date
    df_today = df_events[df_events['date'] == today].groupby('user_id').agg({
        'login_count': 'sum',
        'play_minutes': 'sum',
        'pvp_wins': 'sum',
        'coop_minutes': 'sum',
        'topup_try': 'sum',
    }).rename(columns={
        'login_count': 'login_count_today',
        'play_minutes': 'play_minutes_today',
        'pvp_wins': 'pvp_wins_today',
        'coop_minutes': 'coop_minutes_today',
        'topup_try': 'topup_try_today',
    })

    # last 7 days (as_of_date inclusive)
    start_7 = today - timedelta(days=6)
    df_7 = df_events[(df_events['date'] >= start_7) & (df_events['date'] <= today)]
    df_7agg = df_7.groupby('user_id').agg({
        'play_minutes': 'sum',
        'topup_try': 'sum',
        'login_count': 'sum',
    }).rename(columns={
        'play_minutes': 'play_minutes_7d',
        'topup_try': 'topup_try_7d',
        'login_count': 'logins_7d',
    })

    # login streak: count consecutive days back from as_of_date where login_count >=1
    streaks = {}
    grouped = df_events.groupby('user_id')
    for user, g in grouped:
        dates = set(g[g['login_count'] >= 1]['date'])
        streak = 0
        cur = today
        while cur in dates:
            streak += 1
            cur = cur - timedelta(days=1)
        streaks[user] = streak

    df_streak = pd.DataFrame.from_dict(streaks, orient='index', columns=['login_streak_days'])

    # merge
    out = pd.concat([df_today, df_7agg, df_streak], axis=1).fillna(0).reset_index()
    # ensure 'user_id' column name after reset_index (pandas version safety)
    if 'index' in out.columns and 'user_id' not in out.columns:
        out = out.rename(columns={'index': 'user_id'})
    # ensure integer types
    int_cols = ['login_count_today', 'play_minutes_today', 'pvp_wins_today', 'coop_minutes_today', 'topup_try_today', 'play_minutes_7d', 'topup_try_7d', 'logins_7d', 'login_streak_days']
    for c in int_cols:
        if c in out.columns:
            out[c] = out[c].astype(int)

    return out


def run_pipeline(as_of_date: str = None) -> Dict:
    """Run ingestion + compute user_state + evaluate quests and award points.

    After DB schema v2/v3 migrations:
    - Ledger insert is automatic (trg_quest_award_to_ledger trigger)
    - Badge award is automatic (trg_ledger_to_badge trigger)
    - quest_decisions table dropped
    - leaderboard is a VIEW (leaderboard_view)
    - user_state.total_points column dropped
    - triggered/suppressed quests stored in quest_award_quests junction table
    """
    engine = db.engine
    if as_of_date is None:
        as_of_date = datetime.utcnow().date()
    else:
        as_of_date = pd.to_datetime(as_of_date).date()

    # 1) ingest
    ingest_summary = ingest.run_ingest()

    # 2) load recent events into pandas
    start_date = as_of_date - timedelta(days=29)
    q = text("SELECT user_id, date, login_count, play_minutes, pvp_wins, coop_minutes, topup_try FROM activity_events WHERE date BETWEEN :start AND :end")
    df_events = pd.read_sql(q, engine, params={"start": start_date, "end": as_of_date})

    df_state = _compute_user_state_from_events(df_events, as_of_date)

    if df_state.empty:
        return {"status": "ok", "processed_users": 0, "ingest_summary": ingest_summary}

    processed = 0
    with engine.begin() as conn:
        # upsert user_state rows (no total_points, name, city, segment — those are derived)
        for _, row in df_state.iterrows():
            user_id = row['user_id']
            vals = {
                'user_id': user_id,
                'login_count_today': int(row.get('login_count_today', 0)),
                'play_minutes_today': int(row.get('play_minutes_today', 0)),
                'pvp_wins_today': int(row.get('pvp_wins_today', 0)),
                'coop_minutes_today': int(row.get('coop_minutes_today', 0)),
                'topup_try_today': int(row.get('topup_try_today', 0)),
                'play_minutes_7d': int(row.get('play_minutes_7d', 0)),
                'topup_try_7d': int(row.get('topup_try_7d', 0)),
                'logins_7d': int(row.get('logins_7d', 0)),
                'login_streak_days': int(row.get('login_streak_days', 0)),
            }
            cols = ','.join(vals.keys())
            params = ','.join([f":{k}" for k in vals.keys()])
            updates = ','.join([f"{k}=EXCLUDED.{k}" for k in vals.keys() if k != 'user_id'])
            sql = text(f"INSERT INTO user_state ({cols}) VALUES ({params}) ON CONFLICT (user_id) DO UPDATE SET {updates}")
            conn.execute(sql, vals)
            processed += 1

        # 3) evaluate quests
        quests = pd.read_sql(text('SELECT * FROM quests WHERE is_active = true'), conn)

        # load current total_points from leaderboard_view for quest condition context
        total_points_df = pd.read_sql(text('SELECT user_id, total_points FROM leaderboard_view'), conn)
        total_map = dict(zip(total_points_df['user_id'], total_points_df['total_points']))

        for _, s in df_state.iterrows():
            user_id = s['user_id']
            ctx = {k: int(s.get(k, 0)) for k in s.index if k != 'user_id'}
            ctx['total_points'] = int(total_map.get(user_id, 0))

            triggered = []
            for _, qrow in quests.iterrows():
                cond = qrow['condition']
                try:
                    ok = False
                    if cond and isinstance(cond, str) and cond.strip():
                        ok = _safe_eval(cond, ctx)
                    if ok:
                        triggered.append((qrow['quest_id'], int(qrow['priority']), int(qrow['reward_points'] or 0)))
                except Exception:
                    continue

            if not triggered:
                continue

            # idempotency: skip if quest_award already exists for this user+date
            existing = conn.execute(text(
                'SELECT 1 FROM quest_awards WHERE user_id = :u AND as_of_date = :d LIMIT 1'
            ), {'u': user_id, 'd': as_of_date}).fetchone()
            if existing:
                continue

            # select quest with minimum priority value
            triggered.sort(key=lambda x: x[1])
            selected = triggered[0]
            selected_qid, selected_priority, selected_points = selected

            ts = datetime.utcnow()
            award_id = f"QA-{uuid.uuid4().hex[:8]}-{user_id}"

            # insert quest_award (triggers auto ledger + auto badge via DB triggers)
            conn.execute(text(
                "INSERT INTO quest_awards (award_id, user_id, as_of_date, selected_quest, reward_points, timestamp) "
                "VALUES (:award_id, :user_id, :as_of_date, :selected, :points, :ts)"
            ), {
                'award_id': award_id,
                'user_id': user_id,
                'as_of_date': as_of_date,
                'selected': selected_qid,
                'points': selected_points,
                'ts': ts,
            })

            # insert triggered/suppressed into junction table
            for t in triggered:
                status = 'TRIGGERED' if t[0] == selected_qid else 'SUPPRESSED'
                conn.execute(text(
                    "INSERT INTO quest_award_quests (award_id, quest_id, status) VALUES (:a, :q, :s)"
                ), {'a': award_id, 'q': t[0], 's': status})

            # insert notification
            notif_id = f"N-{uuid.uuid4().hex[:8]}-{user_id}"
            conn.execute(text(
                "INSERT INTO notifications (notification_id, user_id, channel, message, sent_at) "
                "VALUES (:n, :u, :ch, :m, :ts)"
            ), {
                'n': notif_id,
                'u': user_id,
                'ch': 'BiP',
                'm': f"Kazanım: {selected_qid} görevi tamamlandı. +{selected_points} puan.",
                'ts': ts,
            })

        # Leaderboard is now a VIEW (leaderboard_view) — no manual rebuild needed
        # Badge awards are handled by DB trigger (trg_ledger_to_badge) — no manual evaluation needed

    return {"status": "ok", "processed_users": processed, "ingest_summary": ingest_summary}

