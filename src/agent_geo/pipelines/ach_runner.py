from __future__ import annotations

from typing import Iterable

from agent_geo.models.ach import ACHTable
from agent_geo.models.evidence import EvidenceRecord
from agent_geo.storage import ACHStore


class ACHManager:
    def __init__(self, store: ACHStore | None = None) -> None:
        self.store = store or ACHStore()
        self.table = self.store.load()

    def _get_entry(self, hypothesis: str):
        for entry in self.table.entries:
            if entry.hypothesis == hypothesis:
                return entry
        raise KeyError(f"Unknown hypothesis: {hypothesis}")

    def add_support(self, hypothesis: str, evidence: EvidenceRecord) -> None:
        entry = self._get_entry(hypothesis)
        entry.supports.append(evidence)
        entry.recompute()
        self.store.save(self.table)

    def add_refute(self, hypothesis: str, evidence: EvidenceRecord) -> None:
        entry = self._get_entry(hypothesis)
        entry.refutes.append(evidence)
        entry.recompute()
        self.store.save(self.table)

    def set_gaps(self, hypothesis: str, gaps: Iterable[str]) -> None:
        entry = self._get_entry(hypothesis)
        entry.key_gaps = list(gaps)
        self.store.save(self.table)

    def set_next_collection(self, hypothesis: str, tasks: Iterable[str]) -> None:
        entry = self._get_entry(hypothesis)
        entry.next_collection = list(tasks)
        self.store.save(self.table)


__all__ = ["ACHManager"]
