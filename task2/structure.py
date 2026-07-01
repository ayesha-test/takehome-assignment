from config import MAX_SUMMARY_LENGTH, MIN_SUMMARY_LENGTH


def score_structure(summary: str) -> tuple[float, list[str]]:
    """Layer 1: non-empty summary within length bounds. Returns (score 0-1, reasons)."""
    text = summary.strip()
    if not text:
        return 0.0, ["summary is empty"]

    length = len(text)
    min_ok = length >= MIN_SUMMARY_LENGTH
    max_ok = length <= MAX_SUMMARY_LENGTH
    reasons: list[str] = []

    if not min_ok:
        reasons.append(f"summary too short ({length} < {MIN_SUMMARY_LENGTH} chars)")
    if not max_ok:
        reasons.append(f"summary too long ({length} > {MAX_SUMMARY_LENGTH} chars)")
    if min_ok and max_ok:
        reasons.append("structure ok")

    return (int(min_ok) + int(max_ok)) / 2, reasons
