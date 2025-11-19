from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from agent_geo.models.evidence import EvidenceRecord
from agent_geo.models.indicator import IndicatorRecord
from agent_geo.models.forecast import ForecastEvent
from agent_geo.models.ach import ACHTable


class EvidenceStore:
    def __init__(self, path: Path | str = Path("data/evidence_log.jsonl")) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: EvidenceRecord) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(record.model_dump_json())
            fh.write("\n")

    def load(self) -> List[EvidenceRecord]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as fh:
            return [EvidenceRecord.model_validate_json(line) for line in fh]


class PanelStore:
    def __init__(self, path: Path | str = Path("data/indicator_panel.json")) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, records: Iterable[IndicatorRecord]) -> None:
        payload = [record.model_dump() for record in records]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> List[IndicatorRecord]:
        if not self.path.exists():
            return []
        return [IndicatorRecord.model_validate(obj) for obj in json.loads(self.path.read_text(encoding="utf-8"))]


class ForecastStore:
    def __init__(self, path: Path | str = Path("data/forecast_ledger.json")) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, events: Iterable[ForecastEvent]) -> None:
        payload = [event.model_dump() for event in events]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> List[ForecastEvent]:
        if not self.path.exists():
            return []
        return [ForecastEvent.model_validate(obj) for obj in json.loads(self.path.read_text(encoding="utf-8"))]


class ACHStore:
    def __init__(self, path: Path | str = Path("data/ach_table.json")) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, table: ACHTable) -> None:
        self.path.write_text(table.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")

    def load(self) -> ACHTable:
        if not self.path.exists():
            return ACHTable.bootstrap()
        return ACHTable.model_validate_json(self.path.read_text(encoding="utf-8"))


__all__ = ["EvidenceStore", "PanelStore", "ForecastStore", "ACHStore"]
