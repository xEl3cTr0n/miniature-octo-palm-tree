import json
from pathlib import Path

from claimlens_api.models import CaseCreate
from claimlens_api.pipeline import build_report

case_path = Path("datasets/synthetic_claims/rear_end_collision_case_001/case.json")
case = CaseCreate.model_validate_json(case_path.read_text())
report = build_report(case.case_id, case.title, case.claim_type, case.evidence)
print(json.dumps(report.model_dump(), indent=2))
