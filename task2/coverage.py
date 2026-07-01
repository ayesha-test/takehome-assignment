import re

KEYWORDS = (
    "payment", "payments", "login", "crash", "crashes", "failing", "failed",
    "workaround", "update", "password", "token", "dashboard", "invoice",
    "export", "authentication", "billing", "csv", "notification", "notifications",
    "mobile", "slow", "loading", "import", "importing", "delayed", "2fa",
    "two-factor", "admin", "panel",
)

MULTI_WORD_PHRASES = (
    "no workaround",
    "password reset",
    "invalid token",
    "two-factor authentication",
)

PLATFORM_VERSION_PATTERN = re.compile(
    r"\b(Android|iOS)\s+(?:version\s+)?(\d+(?:\.\d+)*)\b", re.I
)
VERSION_PATTERN = re.compile(r"\bversion\s+(\d+(?:\.\d+)*)\b", re.I)
PLATFORM_PATTERN = re.compile(r"\b(Android|iOS|iPhone|iPad|web|mobile)\b", re.I)


def extract_critical_terms(original_text: str) -> list[str]:
    """Pull must-mention terms from the ticket using simple rules (no NLP libs)."""
    terms: list[str] = []
    seen: set[str] = set()

    def add(term: str) -> None:
        key = term.lower()
        if key not in seen:
            seen.add(key)
            terms.append(term)

    lower = original_text.lower()

    for phrase in MULTI_WORD_PHRASES:
        if phrase in lower:
            add(phrase)

    for keyword in KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lower):
            add(keyword)

    for match in PLATFORM_VERSION_PATTERN.finditer(original_text):
        add(f"{match.group(1)} {match.group(2)}")

    for match in PLATFORM_PATTERN.finditer(original_text):
        add(match.group(0))

    for match in VERSION_PATTERN.finditer(original_text):
        # Only the number — "version 14" in original, "Android 14" in summary still matches
        add(match.group(1))

    return terms


def score_coverage(original_text: str, summary: str) -> tuple[float, list[str], list[str]]:
    """Layer 2: critical terms from original must appear in summary."""
    terms = extract_critical_terms(original_text)
    if not terms:
        return 1.0, ["no critical terms extracted"], []

    summary_norm = summary.lower().replace("2fa", "two-factor authentication")
    missing: list[str] = []
    matched: list[str] = []

    for term in terms:
        if term.lower() in summary_norm:
            matched.append(term)
        else:
            missing.append(term)

    score = len(matched) / len(terms)
    reasons: list[str] = []
    if missing:
        reasons.append(f"missing critical terms: {', '.join(missing)}")
    else:
        reasons.append(f"all {len(terms)} critical terms present")
    return score, reasons, missing
