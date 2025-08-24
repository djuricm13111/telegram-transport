import time, uuid
from ..db import db

def calc_balance(pair_id: str) -> float:
    with db() as conn:
        r = conn.execute("SELECT COALESCE(SUM(amount),0) AS s FROM tx WHERE pair_id=?", (pair_id,)).fetchone()
        return float(r["s"] or 0.0)

def add_tx(pair_id: str, actor: int, amount: float, note: str = "") -> dict:
    ts = int(time.time())
    rid = uuid.uuid4().hex[:8]
    with db() as conn:
        conn.execute(
            "INSERT INTO tx(id,pair_id,ts,actor,amount,note) VALUES (?,?,?,?,?,?)",
            (rid, pair_id, ts, actor, amount, note)
        )
    return {"id": rid, "ts": ts}

def get_history(pair_id: str, limit: int = 10):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM tx WHERE pair_id=? ORDER BY ts DESC LIMIT ?",
            (pair_id, limit)
        ).fetchall()
