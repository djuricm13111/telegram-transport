from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

def rsd(x: float) -> str:
    # bez decimala, sa tačkama kao hiljadarskim
    n = Decimal(str(x)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    s = f"{int(n):,}".replace(",", ".")
    return f"{s} RSD"

def when(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def parse_amount(s: str) -> float:
    # 58.800/58,800 => 58800; podržava i 1.234,56 / 1,234.56
    t = s.strip().replace(" ", "").replace("\u00A0", "")
    if not t:
        raise ValueError("empty")
    has_dot = "." in t
    has_comma = "," in t
    if has_dot and has_comma:
        last = max(t.rfind("."), t.rfind(","))
        dec = t[last]
        frac = t[last+1:]
        if frac.isdigit() and 1 <= len(frac) <= 2:
            thou = "," if dec == "." else "."
            t = t.replace(thou, "")
            t = t.replace(dec, ".")
            return float(t)
        else:
            return float(t.replace(".", "").replace(",", ""))
    elif has_dot:
        parts = t.split(".")
        if all(p.isdigit() for p in parts) and all(len(p)==3 for p in parts[1:]):
            return float("".join(parts))
        return float(t.replace(",", ""))
    elif has_comma:
        parts = t.split(",")
        if all(p.isdigit() for p in parts) and all(len(p)==3 for p in parts[1:]):
            return float("".join(parts))
        return float(t.replace(".", "").replace(",", "."))
    else:
        return float(t)

def today_bounds_ts(tz) -> tuple[int, int]:
    now = datetime.now(tz)
    start = datetime(now.year, now.month, now.day, tzinfo=tz)
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return int(start.astimezone(timezone.utc).timestamp()), int(end.astimezone(timezone.utc).timestamp())
