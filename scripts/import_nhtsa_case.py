from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from claimlens.core.pipeline import answer_claim
from claimlens.data_sources.nhtsa import evidence_to_dict, fetch_vehicle_evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ClaimLens against live NHTSA vehicle data.")
    parser.add_argument("--make", default="Honda")
    parser.add_argument("--model", default="Accord")
    parser.add_argument("--year", type=int, default=2020)
    parser.add_argument(
        "--question",
        default="Do complaints or recalls mention warning lights or rear camera failure?",
    )
    parser.add_argument("--max-complaints", type=int, default=10)
    parser.add_argument("--max-recalls", type=int, default=5)
    args = parser.parse_args()

    evidence = fetch_vehicle_evidence(
        make=args.make,
        model=args.model,
        year=args.year,
        max_complaints=args.max_complaints,
        max_recalls=args.max_recalls,
    )
    answer = answer_claim(args.question, evidence, claim_type="vehicle_safety")

    print(
        json.dumps(
            {
                "source": "nhtsa",
                "vehicle": {
                    "make": args.make,
                    "model": args.model,
                    "year": args.year,
                },
                "question": args.question,
                "evidence_count": len(evidence),
                "answer": asdict(answer),
                "evidence": [evidence_to_dict(item) for item in evidence],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
