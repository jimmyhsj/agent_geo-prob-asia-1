from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from agent_geo.config import INDICATOR_TEMPLATES, IndicatorTemplate
from agent_geo.models.evidence import EvidenceRecord
from agent_geo.models.indicator import IndicatorRecord, IndicatorStatus
from agent_geo.storage import EvidenceStore, PanelStore


class IndicatorPanelBuilder:
    def __init__(
        self,
        templates: Iterable[IndicatorTemplate] = INDICATOR_TEMPLATES,
        panel_store: PanelStore | None = None,
        evidence_store: EvidenceStore | None = None,
    ) -> None:
        self.templates = list(templates)
        self.panel_store = panel_store or PanelStore()
        self.evidence_store = evidence_store or EvidenceStore()
        self.records: Dict[str, IndicatorRecord] = {t.key: IndicatorRecord.from_template(t) for t in self.templates}
        self._load_existing()

    def _load_existing(self) -> None:
        existing = {record.template_key: record for record in self.panel_store.load()}
        self.records.update(existing)

    def update_indicator(
        self,
        key: str,
        *,
        latest_value: str,
        direction: Optional[str],
        source_url: Optional[str],
        color: IndicatorStatus,
        confidence: str = "M",
        analyst_note: Optional[str] = None,
        evidence: Optional[EvidenceRecord] = None,
    ) -> IndicatorRecord:
        if key not in self.records:
            raise KeyError(f"Unknown indicator key: {key}")
        record = self.records[key]
        record.latest_value = latest_value
        record.direction = direction
        record.source_url = source_url  # type: ignore[assignment]
        record.color = color
        record.confidence = confidence
        record.analyst_note = analyst_note
        record.date = datetime.utcnow()
        if evidence:
            self.evidence_store.append(evidence)
        self.panel_store.save(self.records.values())
        return record

    def to_rows(self) -> List[dict]:
        rows = []
        for record in self.records.values():
            rows.append(
                {
                    "dimension": record.dimension.value,
                    "indicator": record.indicator,
                    "latest_value": record.latest_value,
                    "direction": record.direction,
                    "date": record.date.isoformat() if record.date else None,
                    "source_url": str(record.source_url) if record.source_url else None,
                    "confidence": record.confidence,
                    "weight": record.weight,
                    "color": record.color.value,
                    "analyst_note": record.analyst_note,
                }
            )
        return rows

    def export_csv(self, path: Path | str) -> Path:
        import csv

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "dimension",
                    "indicator",
                    "latest_value",
                    "direction",
                    "date",
                    "source_url",
                    "confidence",
                    "weight",
                    "color",
                    "analyst_note",
                ],
            )
            writer.writeheader()
            writer.writerows(self.to_rows())
        return destination


__all__ = ["IndicatorPanelBuilder"]
