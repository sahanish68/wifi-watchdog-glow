"""Security audit & scoring for WiFi networks."""
from __future__ import annotations

WEAK = ("open", "wep", "wpa ", "wpa-personal", "wpa1")
MED  = ("wpa2",)
STRONG = ("wpa3", "wpa2/wpa3", "wpa3-personal", "sae")


def assess(security: str) -> tuple[str, int, list[str]]:
    """Return (verdict, score 0-100, recommendations)."""
    s = (security or "").strip().lower()
    recs: list[str] = []
    if not s or "open" in s:
        recs += [
            "Network is OPEN — anyone can join and sniff traffic.",
            "Enable WPA3 (or WPA2-AES at minimum) and set a strong passphrase.",
        ]
        return "Critical", 5, recs
    if "wep" in s:
        recs += ["WEP is broken — switch to WPA3 immediately."]
        return "Critical", 10, recs
    if any(w in s for w in ("wpa1", "wpa-personal")) and "wpa2" not in s:
        recs += ["WPA1 is deprecated — upgrade to WPA2/WPA3."]
        return "Weak", 30, recs
    if "wpa3" in s:
        recs += ["Good. Keep firmware updated and rotate passphrase yearly."]
        return "Strong", 95, recs
    if "wpa2" in s:
        recs += [
            "Acceptable. Prefer WPA3 if your router supports it.",
            "Disable WPS — it's brute-forceable.",
            "Use AES (CCMP), not TKIP.",
        ]
        return "Good", 75, recs
    return "Unknown", 50, ["Unable to classify — verify router settings manually."]


def overall_score(networks) -> int:
    if not networks: return 0
    scores = [assess(n.security)[1] for n in networks]
    return int(sum(scores) / len(scores))
