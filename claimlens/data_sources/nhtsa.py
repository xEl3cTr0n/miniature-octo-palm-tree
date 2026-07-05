from __future__ import annotations

import json
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import certifi

from claimlens.core.models import EvidenceItem, EvidenceType

NHTSA_COMPLAINTS_URL = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
NHTSA_RECALLS_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle"


class NHTSADataSourceError(RuntimeError):
    """Raised when NHTSA data cannot be fetched or parsed."""


def build_vehicle_evidence(
    *,
    make: str,
    model: str,
    year: int,
    complaints: list[dict[str, Any]],
    recalls: list[dict[str, Any]],
) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    vehicle = f"{year} {make.upper()} {model.upper()}"

    for complaint in complaints:
        odi_number = _text(complaint.get("odiNumber"))
        if not odi_number:
            continue
        components = _text(complaint.get("components"), default="UNKNOWN COMPONENT")
        summary = _text(complaint.get("summary"))
        content = " ".join(
            part
            for part in [
                f"NHTSA complaint {odi_number} for {vehicle}.",
                f"Manufacturer: {_text(complaint.get('manufacturer'), default='unknown')}.",
                f"Component: {components}.",
                _sentence("Incident date", complaint.get("dateOfIncident")),
                _sentence("Complaint filed", complaint.get("dateComplaintFiled")),
                _sentence("Crash reported", complaint.get("crash")),
                _sentence("Fire reported", complaint.get("fire")),
                _sentence("Injuries", complaint.get("numberOfInjuries")),
                _sentence("Deaths", complaint.get("numberOfDeaths")),
                f"Summary: {summary}" if summary else "",
            ]
            if part
        )
        evidence.append(
            EvidenceItem(
                id=f"nhtsa-complaint-{odi_number}",
                type=EvidenceType.TEXT,
                title=f"NHTSA complaint {odi_number}: {components}",
                content=content,
                metadata={
                    "source": "nhtsa_complaints",
                    "make": make,
                    "model": model,
                    "year": str(year),
                    "odi_number": odi_number,
                    "components": components,
                },
            )
        )

    for recall in recalls:
        campaign_number = _text(recall.get("NHTSACampaignNumber"))
        if not campaign_number:
            continue
        component = _text(recall.get("Component"), default="UNKNOWN COMPONENT")
        content = " ".join(
            part
            for part in [
                f"NHTSA recall {campaign_number} for {vehicle}.",
                f"Component: {component}.",
                _sentence("Report received", recall.get("ReportReceivedDate")),
                f"Summary: {_text(recall.get('Summary'))}" if recall.get("Summary") else "",
                f"Consequence: {_text(recall.get('Consequence'))}" if recall.get("Consequence") else "",
                f"Remedy: {_text(recall.get('Remedy'))}" if recall.get("Remedy") else "",
            ]
            if part
        )
        evidence.append(
            EvidenceItem(
                id=f"nhtsa-recall-{campaign_number}",
                type=EvidenceType.TEXT,
                title=f"NHTSA recall {campaign_number}: {component}",
                content=content,
                metadata={
                    "source": "nhtsa_recalls",
                    "make": make,
                    "model": model,
                    "year": str(year),
                    "campaign_number": campaign_number,
                    "component": component,
                },
            )
        )

    return evidence


def fetch_vehicle_evidence(
    *,
    make: str,
    model: str,
    year: int,
    max_complaints: int = 10,
    max_recalls: int = 5,
    timeout_seconds: float = 15.0,
) -> list[EvidenceItem]:
    complaints = _fetch_results(
        NHTSA_COMPLAINTS_URL,
        {"make": make, "model": model, "modelYear": str(year)},
        timeout_seconds=timeout_seconds,
    )[:max_complaints]
    recalls = _fetch_results(
        NHTSA_RECALLS_URL,
        {"make": make, "model": model, "modelYear": str(year)},
        timeout_seconds=timeout_seconds,
    )[:max_recalls]
    return build_vehicle_evidence(
        make=make,
        model=model,
        year=year,
        complaints=complaints,
        recalls=recalls,
    )


def evidence_to_dict(item: EvidenceItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "type": item.type.value,
        "title": item.title,
        "content": item.content,
        "metadata": item.metadata,
    }


def _fetch_results(
    base_url: str,
    params: dict[str, str],
    *,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    url = f"{base_url}?{urlencode(params)}"
    tls_context = ssl.create_default_context(cafile=certifi.where())
    try:
        with urlopen(url, timeout=timeout_seconds, context=tls_context) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise NHTSADataSourceError(f"Unable to fetch NHTSA data from {url}: {exc}") from exc

    results = payload.get("results")
    if not isinstance(results, list):
        raise NHTSADataSourceError(f"NHTSA response from {url} did not include a results list")
    return [item for item in results if isinstance(item, dict)]


def _text(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _sentence(label: str, value: Any) -> str:
    text = _text(value)
    if not text:
        return ""
    return f"{label}: {text}."
