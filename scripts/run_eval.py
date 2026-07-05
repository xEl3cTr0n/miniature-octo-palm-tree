from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from claimlens.evaluators.harness import (
    DEFAULT_EVAL_DATASET,
    load_evaluation_dataset,
    run_evaluation,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic ClaimLens evaluations.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_EVAL_DATASET,
        help="Path to an evaluation dataset JSON file.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    summary = run_evaluation(load_evaluation_dataset(args.dataset))
    if args.format == "json":
        print(json.dumps(asdict(summary), indent=2))
        return

    print(f"ClaimLens evals: {summary.passed_count}/{summary.example_count} passed")
    print(f"Pass rate: {summary.pass_rate:.3f}")
    print(f"Average citation coverage: {summary.average_citation_coverage:.3f}")
    print(
        "Average expected citation recall: "
        f"{summary.average_expected_citation_recall:.3f}"
    )
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"- {status} {result.id}: "
            f"coverage={result.citation_coverage:.3f}, "
            f"expected_recall={result.expected_citation_recall:.3f}"
        )


if __name__ == "__main__":
    main()
