from ..db import db

def get_pair_by_user(uid: int):
    with db() as conn:
        return conn.execute("SELECT * FROM pairs WHERE user1=? OR user2=?", (uid, uid)).fetchone()

def user_belongs(pair, uid: int) -> bool:
    return pair and (pair["user1"] == uid or pair["user2"] == uid)

def other_of(pair, uid: int) -> int:
    return pair["user2"] if pair["user1"] == uid else pair["user1"]

def upsert_pair(user_a: int, user_b: int, pair_id: str):
    a, b = (user_a, user_b) if user_a < user_b else (user_b, user_a)
    with db() as conn:
        row = conn.execute(
            "SELECT pair_id FROM pairs WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)",
            (a, b, b, a)
        ).fetchone()
        if row:
            return row["pair_id"]
        conn.execute("INSERT INTO pairs(pair_id,user1,user2) VALUES (?,?,?)", (pair_id, a, b))
    return pair_id
def list_pairs(uid: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM pairs WHERE user1=? OR user2=? ORDER BY pair_id",
            (uid, uid)
        ).fetchall()

def set_active_pair(uid: int, pair_id: str):
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM pairs WHERE pair_id=?", (pair_id,)).fetchone()
        if not exists:
            raise ValueError("pair not found")
        conn.execute("""
            INSERT INTO user_active_pair(user_id, pair_id)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET pair_id=excluded.pair_id
        """, (uid, pair_id))

def get_active_pair(uid: int):
    with db() as conn:
        row = conn.execute("""
            SELECT p.* FROM user_active_pair uap
            JOIN pairs p ON p.pair_id = uap.pair_id
            WHERE uap.user_id=?
        """, (uid,)).fetchone()
        return row