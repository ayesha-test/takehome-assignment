#!/usr/bin/env python3
"""CLI entry point — fetch summaries, evaluate, print report, write report.json."""

import json
import sys
from pathlib import Path

from client import SummariesClient
from evaluator import evaluate_all


def print_report(report: dict) -> None:
    summary = report["summary"]
    print(f"\n=== Summary Evaluation Report ===")
    print(f"Total: {summary['total']}  Passed: {summary['passed']}  Failed: {summary['failed']}")
    print(f"Pass rate: {summary['pass_rate']:.0%}\n")

    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['ticket_id']}  score={result['overall_score']:.3f}")
        print(
            f"  structure={result['structure_score']:.2f}  "
            f"coverage={result['coverage_score']:.2f}  "
            f"similarity={result['similarity_score']:.2f}"
        )
        for reason in result["reasons"]:
            print(f"  - {reason}")
        print()


def main() -> int:
    try:
        tickets = SummariesClient().get_summaries()
    except Exception as exc:
        print(f"Error fetching summaries: {exc}", file=sys.stderr)
        return 1

    report = evaluate_all(tickets)
    print_report(report)

    out_path = Path(__file__).parent / "report.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Report written to {out_path}")

    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
