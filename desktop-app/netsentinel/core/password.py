"""Local password strength estimator (entropy + dictionary).

No external lookups. No password is ever transmitted.
"""
from __future__ import annotations
import math
import re
from pathlib import Path
from functools import lru_cache

DICT_PATH = Path(__file__).with_name("common_passwords.txt")


@lru_cache(maxsize=1)
def _dictionary() -> set[str]:
    try:
        return {l.strip().lower() for l in DICT_PATH.read_text(encoding="utf-8").splitlines() if l.strip()}
    except Exception:
        return set()


def analyze(pw: str) -> dict:
    if not pw:
        return {"entropy": 0, "strength": 0, "label": "Empty",
                "crack_time": "instant", "tips": ["Enter a password."]}

    pool = 0
    if re.search(r"[a-z]", pw): pool += 26
    if re.search(r"[A-Z]", pw): pool += 26
    if re.search(r"\d",   pw): pool += 10
    if re.search(r"[^A-Za-z0-9]", pw): pool += 33
    pool = max(pool, 1)
    entropy = len(pw) * math.log2(pool)

    in_dict = pw.lower() in _dictionary()
    if in_dict:
        entropy = min(entropy, 12)  # penalize harshly

    # ~10^10 guesses/sec (offline, GPU-class).
    seconds = (2 ** entropy) / 1e10
    crack = _humanize(seconds)

    strength = min(100, int(entropy * 1.2))
    if   strength < 25: label = "Very Weak"
    elif strength < 45: label = "Weak"
    elif strength < 65: label = "Fair"
    elif strength < 85: label = "Strong"
    else:               label = "Excellent"

    tips = []
    if in_dict:                              tips.append("Found in common password list — avoid.")
    if len(pw) < 12:                         tips.append("Use at least 12 characters.")
    if not re.search(r"[A-Z]", pw):          tips.append("Add uppercase letters.")
    if not re.search(r"\d",   pw):           tips.append("Add digits.")
    if not re.search(r"[^A-Za-z0-9]", pw):   tips.append("Add symbols (!@#$…).")
    if re.search(r"(.)\1{2,}", pw):          tips.append("Avoid repeated characters.")
    if not tips: tips.append("Looks good. Store it in a password manager.")

    return {"entropy": round(entropy, 1), "strength": strength,
            "label": label, "crack_time": crack, "tips": tips}


def _humanize(seconds: float) -> str:
    if seconds < 1:           return "instant"
    units = [("years", 31536000), ("days", 86400),
             ("hours", 3600), ("minutes", 60), ("seconds", 1)]
    for name, n in units:
        if seconds >= n:
            val = seconds / n
            if val > 1e9: return f"{val:.1e} {name}"
            return f"{val:.1f} {name}"
    return f"{seconds:.1f} seconds"
