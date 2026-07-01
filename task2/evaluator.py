from typing import Any

from config import (
    PASS_THRESHOLD,
    WEIGHT_COVERAGE,
    WEIGHT_SIMILARITY,
    WEIGHT_STRUCTURE,
)
from coverage import score_coverage
from similarity import score_similarity
from structure import score_structure


def evaluate_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    ticket_id = ticket.get("ticket_id", "unknown")
    original = ticket.get("original_text", "")
    summary = ticket.get("generated_summary", "")

    struct_score, struct_reasons = score_structure(summary)
    cov_score, cov_reasons, missing = score_coverage(original, summary)
    sim_score, sim_reasons = score_similarity(original, summary)

    overall = (
        WEIGHT_STRUCTURE * struct_score
        + WEIGHT_COVERAGE * cov_score
        + WEIGHT_SIMILARITY * sim_score
    )

    passed = overall >= PASS_THRESHOLD and not missing
    reasons = struct_reasons + cov_reasons + sim_reasons
    if not passed:
        if overall < PASS_THRESHOLD:
            reasons.append(f"overall score {overall:.3f} below threshold {PASS_THRESHOLD}")
        if missing:
            reasons.append("failed: missing critical terms (hard gate)")

    return {
        "ticket_id": ticket_id,
        "passed": passed,
        "overall_score": round(overall, 4),
        "structure_score": round(struct_score, 4),
        "coverage_score": round(cov_score, 4),
        "similarity_score": round(sim_score, 4),
        "missing_terms": missing,
        "reasons": reasons,
    }


def evaluate_all(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_ticket(t) for t in tickets]
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": round(passed_count / len(results), 4) if results else 0.0,
        },
        "results": results,
    }
