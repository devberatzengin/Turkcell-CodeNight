#!/usr/bin/env python3
"""Simple DB connectivity check script.

Reads `DATABASE_URL` or `JDBC_URL` from backend/.env, connects using SQLAlchemy,
runs a test query `SELECT 1` and attempts `SELECT COUNT(*) FROM users`.

Usage:
    python backend/scripts/check_db.py
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys


def get_database_url():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
    raw = os.getenv('DATABASE_URL') or os.getenv('JDBC_URL')
    if not raw:
        print('DATABASE_URL or JDBC_URL not set in backend/.env', file=sys.stderr)
        sys.exit(2)
    # convert jdbc:postgresql://... to postgresql://...
    if raw.startswith('jdbc:'):
        return raw.replace('jdbc:', '', 1)
    return raw


def main():
    url = get_database_url()
    print('Using DATABASE_URL:', url)
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            r = conn.execute(text('SELECT 1')).scalar()
            print('SELECT 1 ->', r)
            try:
                c = conn.execute(text('SELECT COUNT(*) FROM users')).scalar()
                print('users table count ->', c)
            except Exception as e:
                print('Could not query users table:', e)
    except Exception as e:
        print('Failed to connect to DB:', e)
        sys.exit(3)


if __name__ == '__main__':
    main()
