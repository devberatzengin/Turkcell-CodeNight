import os
from sqlalchemy import text
from .. import db


def _ensure_staging_schema(conn):
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS staging'))


def _create_staging_like(conn, table_name):
    conn.execute(text(f"DROP TABLE IF EXISTS staging.{table_name} CASCADE"))
    conn.execute(text(f"CREATE TABLE staging.{table_name} (LIKE {table_name} INCLUDING ALL)"))


def _copy_csv_to_staging(conn, table_name, csv_path, columns):
    # Use raw DBAPI connection COPY for performance (SQLAlchemy 2.x compatible)
    raw = conn.connection.dbapi_connection
    cur = raw.cursor()
    cols = ",".join(columns)
    sql = f"COPY staging.{table_name} ({cols}) FROM STDIN WITH CSV HEADER"
    with open(csv_path, 'r', encoding='utf-8') as f:
        cur.copy_expert(sql, f)
    raw.commit()


def _upsert_from_staging(conn, table_name, columns, pk_cols):
    cols = ",".join(columns)
    insert_cols = ",".join(columns)
    excluded = ",".join([f"{c}=EXCLUDED.{c}" for c in columns if c not in pk_cols])
    pk = ",".join(pk_cols)
    sql = f"INSERT INTO {table_name} ({insert_cols}) SELECT {cols} FROM staging.{table_name} ON CONFLICT ({pk}) DO UPDATE SET {excluded}"
    conn.execute(text(sql))


def run_ingest(dataset_dir: str = None) -> dict:
    """Ingest CSVs into staging and merge into production tables.

    dataset_dir defaults to workspace `datasets/`.
    Returns a summary dict.
    """
    if dataset_dir is None:
        dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')

    engine = db.engine
    summary = {}

    table_map = {
        'users': {
            'csv': os.path.join(dataset_dir, 'users.csv'),
            'columns': ['user_id', 'name', 'city', 'segment'],
            'pk': ['user_id'],
        },
        'games': {
            'csv': os.path.join(dataset_dir, 'games.csv'),
            'columns': ['game_id', 'game_name', 'genre'],
            'pk': ['game_id'],
        },
        'badges': {
            'csv': os.path.join(dataset_dir, 'badges.csv'),
            'columns': ['badge_id', 'badge_name', 'condition', 'level'],
            'pk': ['badge_id'],
        },
        'quests': {
            'csv': os.path.join(dataset_dir, 'quests.csv'),
            'columns': ['quest_id', 'quest_name', 'quest_type', 'condition', 'reward_points', 'priority', 'is_active'],
            'pk': ['quest_id'],
        },
        'activity_events': {
            'csv': os.path.join(dataset_dir, 'activity_events.csv'),
            'columns': ['event_id', 'user_id', 'date', 'game_id', 'login_count', 'play_minutes', 'pvp_wins', 'coop_minutes', 'topup_try'],
            'pk': ['event_id'],
        },
    }

    with engine.begin() as conn:
        # create staging schema
        _ensure_staging_schema(conn)

        for table_name, meta in table_map.items():
            csv_path = meta['csv']
            if not os.path.exists(csv_path):
                summary[table_name] = 'csv_missing'
                continue
            # create staging table like production
            _create_staging_like(conn, table_name)
            # COPY CSV into staging
            _copy_csv_to_staging(conn, table_name, csv_path, meta['columns'])
            # upsert into production
            _upsert_from_staging(conn, table_name, meta['columns'], meta['pk'])
            # count
            r = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            summary[table_name] = int(r)

    return summary
