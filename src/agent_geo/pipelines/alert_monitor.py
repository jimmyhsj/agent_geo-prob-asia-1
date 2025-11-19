from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

from agent_geo.config import ENTRAPMENT_SIGNALS, EntrapmentSignalDefinition
from agent_geo.models.alert import EntrapmentSignalStatus
from agent_geo.models.evidence import EvidenceRecord


class AlertMonitor:
    def __init__(self, definitions: Iterable[EntrapmentSignalDefinition] = ENTRAPMENT_SIGNALS) -> None:
        self.definitions = list(definitions)
        self.status: Dict[str, EntrapmentSignalStatus] = {
            definition.key: EntrapmentSignalStatus(key=definition.key)
            for definition in self.definitions
        }

    def update(
        self,
        key: str,
        *,
        active: bool,
        evidence: List[EvidenceRecord] | None = None,
        notes: str | None = None,
    ) -> EntrapmentSignalStatus:
        if key not in self.status:
            raise KeyError(f"Unknown signal {key}")
        status = self.status[key]
        status.active = active
        status.last_checked = datetime.utcnow()
        status.notes = notes
        if evidence:
            status.evidence.extend(evidence)
        return status

    def is_red(self) -> bool:
        return all(status.active for status in self.status.values())

    def summary(self) -> List[dict]:
        rows = []
        for definition in self.definitions:
            status = self.status[definition.key]
            rows.append(
                {
                    "key": definition.key,
                    "description": definition.description,
                    "active": status.active,
                    "evidence_count": len(status.evidence),
                    "last_checked": status.last_checked.isoformat(),
                }
            )
        return rows


__all__ = ["AlertMonitor"]
