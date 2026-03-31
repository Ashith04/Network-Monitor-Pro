# health_score.py

def calculate_score(status, latency):
    score = 100

    if status == "Offline":
        return 0                        # device is down = 0

    if latency is not None:
        score -= (latency / 10)         # penalize high latency
        score -= (latency / 200) * 10   # extra penalty if very high

    score = max(0, min(100, score))     # keep between 0-100
    return round(score, 1)

def score_label(score):
    if score >= 80:
        return "[OK] Excellent"
    elif score >= 50:
        return "[WARN] Fair"
    else:
        return "[CRIT] Critical"


def calculate_health_score(latency, packet_loss, status):
    """Compatibility wrapper for the dashboard.

    Dashboard calls this with (latency, packet_loss, status). Delegate to
    existing `calculate_score(status, latency)` implementation.
    """
    # delegate to existing calculate_score, preserving semantics
    try:
        return calculate_score(status, latency)
    except Exception:
        return 0