from __future__ import annotations

from dataclasses import dataclass

from claimlens.core.models import EvidenceItem, EvidenceType


@dataclass(frozen=True)
class DemoCase:
    title: str
    claim_type: str
    source: str
    evidence: list[EvidenceItem]


def build_demo_case() -> DemoCase:
    return DemoCase(
        title="Demo: 2020 Honda Accord evidence review",
        claim_type="vehicle_safety",
        source="demo_fixture",
        evidence=[
            EvidenceItem(
                id="demo-adjuster-note",
                type=EvidenceType.TEXT,
                title="Demo adjuster note",
                content=(
                    "Rear bumper damage is visible in the uploaded photo and "
                    "repair estimate. The reviewer should verify whether the "
                    "damage relates to the reported rear camera warning."
                ),
                metadata={"source": "demo_fixture", "category": "adjuster_note"},
            ),
            EvidenceItem(
                id="demo-nhtsa-recall-20v771000",
                type=EvidenceType.TEXT,
                title="Demo NHTSA recall 20V771000",
                content=(
                    "A body control module software issue may affect rearview "
                    "camera behavior and exterior lighting on certain 2020 "
                    "Honda Accord vehicles."
                ),
                metadata={"source": "demo_fixture", "category": "recall"},
            ),
            EvidenceItem(
                id="demo-owner-complaint",
                type=EvidenceType.TEXT,
                title="Demo owner complaint summary",
                content=(
                    "The owner reported intermittent dashboard warning lights "
                    "and a rear camera display failure after starting the "
                    "vehicle. No private customer information is included."
                ),
                metadata={"source": "demo_fixture", "category": "complaint"},
            ),
        ],
    )
