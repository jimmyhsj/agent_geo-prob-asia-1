from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from agent_geo.config import ACH_HYPOTHESES, ACH_QUESTION
from agent_geo.models.evidence import EvidenceRecord


class ACHEntry(BaseModel):
    hypothesis: str
    supports: List[EvidenceRecord] = Field(default_factory=list)
    refutes: List[EvidenceRecord] = Field(default_factory=list)
    net_assessment: int = 0  # +1 support heavy, -1 refute heavy
    confidence: str = "M"
    key_gaps: List[str] = Field(default_factory=list)
    next_collection: List[str] = Field(default_factory=list)

    def recompute(self) -> None:
        self.net_assessment = len(self.supports) - len(self.refutes)


class ACHTable(BaseModel):
    question: str = ACH_QUESTION
    entries: List[ACHEntry] = Field(default_factory=list)

    @classmethod
    def bootstrap(cls) -> "ACHTable":
        return cls(entries=[ACHEntry(hypothesis=h) for h in ACH_HYPOTHESES])


__all__ = ["ACHEntry", "ACHTable"]
