import time, uuid
from ..db import db

def create_reset_request(pair_id: str, initiator: int) -> str:
    token = uuid.uuid4().hex[:8]
    ts = int(time.time())
    with db() as conn:
        conn.execute("INSERT INTO reset_pending(token,pair_id,initiator,ts) VALUES (?,?,?,?)",
                     (token, pair_id, initiator, ts))
    return token

def get_pending_by_token(token: str):
    with db() as conn:
        return conn.execute("SELECT * FROM reset_pending WHERE token=?", (token,)).fetchone()

def clear_pending(token: str):
    with db() as conn:
        conn.execute("DELETE FROM reset_pending WHERE token=?", (token,))

def clear_all_tx(pair_id: str):
    with db() as conn:
        conn.execute("DELETE FROM tx WHERE pair_id=?", (pair_id,))
