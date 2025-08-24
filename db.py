import sqlite3
import logging
from .config import DB_PATH

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS pairs (
            pair_id TEXT PRIMARY KEY,
            user1 INTEGER NOT NULL,
            user2 INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tx (
            id TEXT PRIMARY KEY,
            pair_id TEXT NOT NULL,
            ts INTEGER NOT NULL,
            actor INTEGER NOT NULL,
            amount REAL NOT NULL,
            note TEXT DEFAULT '',
            FOREIGN KEY(pair_id) REFERENCES pairs(pair_id)
        );
        CREATE TABLE IF NOT EXISTS reset_pending (
            token TEXT PRIMARY KEY,
            pair_id TEXT NOT NULL,
            initiator INTEGER NOT NULL,
            ts INTEGER NOT NULL,
            FOREIGN KEY(pair_id) REFERENCES pairs(pair_id)
        );
        CREATE TABLE IF NOT EXISTS user_active_pair (
            user_id INTEGER PRIMARY KEY,
            pair_id TEXT,
            FOREIGN KEY(pair_id) REFERENCES pairs(pair_id)
        );
        """)
    logging.info("DB ready")
