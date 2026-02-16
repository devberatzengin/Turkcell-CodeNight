from typing import Dict, List
from datetime import datetime, timedelta, date
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
        ast.Num,
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
    # ensure integer types
    int_cols = ['login_count_today', 'play_minutes_today', 'pvp_wins_today', 'coop_minutes_today', 'topup_try_today', 'play_minutes_7d', 'topup_try_7d', 'logins_7d', 'login_streak_days']
    for c in int_cols:
        if c in out.columns:
            out[c] = out[c].astype(int)

    return out


def run_pipeline(as_of_date: str = None) -> Dict:
    """Run ingestion + compute user_state + evaluate quests and award points.

    This is a lightweight implementation that:
    - runs ingestion (CSV -> tables)
    - computes `user_state` from `activity_events`
    - evaluates quests (simple safe evaluator)
    - applies conflict rule (min priority)
    - inserts quest_awards, points_ledger, quest_decisions, notifications
    - updates user_state.total_points from points_ledger
    """
    engine = db.engine
    if as_of_date is None:
        as_of_date = datetime.utcnow().date()
    else:
        as_of_date = pd.to_datetime(as_of_date).date()

    # 1) ingest
    ingest_summary = ingest.run_ingest()

    # 2) load recent events into pandas
    # load last 30 days of events
    start_date = as_of_date - timedelta(days=29)
    q = text(f"SELECT user_id, date, login_count, play_minutes, pvp_wins, coop_minutes, topup_try FROM activity_events WHERE date BETWEEN :start AND :end")
    df_events = pd.read_sql(q, engine, params={"start": start_date, "end": as_of_date})

    df_state = _compute_user_state_from_events(df_events, as_of_date)

    processed = 0
    with engine.begin() as conn:
        # upsert user_state rows
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
            # perform upsert
            cols = ','.join(vals.keys())
            params = ','.join([f":{k}" for k in vals.keys()])
            updates = ','.join([f"{k}=EXCLUDED.{k}" for k in vals.keys() if k != 'user_id'])
            sql = text(f"INSERT INTO user_state ({cols}) VALUES ({params}) ON CONFLICT (user_id) DO UPDATE SET {updates}")
            conn.execute(sql, vals)
            processed += 1

        # 3) evaluate quests
        quests = pd.read_sql(text('SELECT * FROM quests WHERE is_active = true'), conn)

        # load current total_points from points_ledger aggregated
        total_points_df = pd.read_sql(text('SELECT user_id, COALESCE(SUM(points_delta),0) AS total_points FROM points_ledger GROUP BY user_id'), conn)
        total_map = dict(zip(total_points_df['user_id'], total_points_df['total_points']))

        # for each user in state, evaluate quests
        for _, s in df_state.iterrows():
            user_id = s['user_id']
            ctx = {k: int(s.get(k, 0)) for k in s.index if k != 'user_id'}
            # include total_points
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

            # select quest with minimum priority value
            triggered.sort(key=lambda x: x[1])
            selected = triggered[0]
            selected_qid, selected_priority, selected_points = selected
            triggered_qs = '|'.join([t[0] for t in triggered])
            suppressed = '|'.join([t[0] for t in triggered[1:]])

            ts = datetime.utcnow()
            award_id = f"QA-{int(ts.timestamp())}-{user_id}"
            # insert quest_awards
            conn.execute(text("INSERT INTO quest_awards (award_id, user_id, as_of_date, triggered_quests, selected_quest, reward_points, suppressed_quests, timestamp) VALUES (:award_id, :user_id, :as_of_date, :triggered, :selected, :points, :suppressed, :ts)"), {
                'award_id': award_id,
                'user_id': user_id,
                'as_of_date': as_of_date,
                'triggered': triggered_qs,
                'selected': selected_qid,
                'points': selected_points,
                'suppressed': suppressed,
                'ts': ts,
            })

            # insert points ledger
            ledger_id = f"L-{int(ts.timestamp())}-{user_id}"
            conn.execute(text("INSERT INTO points_ledger (ledger_id, user_id, points_delta, source, source_ref, created_at) VALUES (:l, :u, :delta, :src, :ref, :ts)"), {
                'l': ledger_id,
                'u': user_id,
                'delta': selected_points,
                'src': 'QUEST_REWARD',
                'ref': award_id,
                'ts': ts,
            })

            # insert quest decision
            decision_id = f"DQ-{int(ts.timestamp())}-{user_id}"
            conn.execute(text("INSERT INTO quest_decisions (decision_id, user_id, as_of_date, selected_reward_points, reason, timestamp) VALUES (:d, :u, :a, :p, :r, :ts)"), {
                'd': decision_id,
                'u': user_id,
                'a': as_of_date,
                'p': selected_points,
                'r': f"selected_quest={selected_qid}; priority=min",
                'ts': ts,
            })

            # insert notification
            notif_id = f"N-{int(ts.timestamp())}-{user_id}"
            conn.execute(text("INSERT INTO notifications (notification_id, user_id, channel, message, sent_at) VALUES (:n, :u, :ch, :m, :ts)"), {
                'n': notif_id,
                'u': user_id,
                'ch': 'BiP',
                'm': f"Kazanım: {selected_qid} görevi tamamlandı. +{selected_points} puan.",
                'ts': ts,
            })

        # update total_points in user_state from ledger
        conn.execute(text("UPDATE user_state SET total_points = COALESCE( (SELECT SUM(points_delta) FROM points_ledger WHERE points_ledger.user_id = user_state.user_id), 0 )"))

        # 4) Badge evaluation and idempotent awards
        badges = pd.read_sql(text('SELECT * FROM badges'), conn)
        # compute latest totals
        total_points_df = pd.read_sql(text('SELECT user_id, COALESCE(SUM(points_delta),0) AS total_points FROM points_ledger GROUP BY user_id'), conn)
        total_map = dict(zip(total_points_df['user_id'], total_points_df['total_points']))

        for user_id, total in total_map.items():
            for _, brow in badges.iterrows():
                cond = brow.get('condition')
                try:
                    if cond and isinstance(cond, str) and cond.strip():
                        ok = _safe_eval(cond, {'total_points': int(total)})
                    else:
                        ok = False
                except Exception:
                    ok = False
                if not ok:
                    continue
                # idempotency: only award if not already awarded
                exists = conn.execute(text('SELECT 1 FROM badge_awards WHERE user_id = :u AND badge_id = :b LIMIT 1'), {'u': user_id, 'b': brow['badge_id']}).fetchone()
                if exists:
                    continue
                ts = datetime.utcnow()
                conn.execute(text('INSERT INTO badge_awards (user_id, badge_id, awarded_at) VALUES (:u, :b, :ts)'), {'u': user_id, 'b': brow['badge_id'], 'ts': ts})
                # create notification for badge
                notif_id = f"N-{int(ts.timestamp())}-{user_id}-B{brow['badge_id']}"
                conn.execute(text("INSERT INTO notifications (notification_id, user_id, channel, message, sent_at) VALUES (:n, :u, :ch, :m, :ts)"), {
                    'n': notif_id,
                    'u': user_id,
                    'ch': 'BiP',
                    'm': f"Tebrikler! {brow['badge_name']} rozeti kazanıldı.",
                    'ts': ts,
                })

        # 5) Leaderboard generation (recreate)
        # build ranking from points_ledger aggregated
        lb = pd.read_sql(text('SELECT user_id, COALESCE(SUM(points_delta),0) AS total_points FROM points_ledger GROUP BY user_id ORDER BY total_points DESC, user_id ASC'), conn)
        # clear existing
        conn.execute(text('TRUNCATE TABLE leaderboard'))
        rank = 1
        for _, r in lb.iterrows():
            conn.execute(text('INSERT INTO leaderboard (rank, user_id, total_points) VALUES (:rank, :u, :tp)'), {'rank': rank, 'u': r['user_id'], 'tp': int(r['total_points'])})
            rank += 1

    return {"status": "ok", "processed_users": processed, "ingest_summary": ingest_summary}
"""CSV-driven pipeline prototype (lightweight).

This module is intentionally minimal — the full pipeline lives in the project plan.
Use it as a starting point to wire CSV ingestion and business logic.
"""
from pathlib import Path
import pandas as pd


def load_csvs(data_dir: str):
    p = Path(data_dir)
    users = pd.read_csv(p / 'users.csv')
    events = pd.read_csv(p / 'activity_events.csv')
    quests = pd.read_csv(p / 'quests.csv')
    badges = pd.read_csv(p / 'badges.csv')
    return users, events, quests, badges


def run(data_dir: str, as_of_date: str):
    users, events, quests, badges = load_csvs(data_dir)
    # pipeline steps will be implemented here
    return {"users": len(users), "events": len(events)}
