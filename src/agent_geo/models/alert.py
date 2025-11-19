from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from agent_geo.models.evidence import EvidenceRecord


class EntrapmentSignalStatus(BaseModel):
    key: str
    active: bool = False
    evidence: List[EvidenceRecord] = Field(default_factory=list)
    last_checked: datetime = datetime.utcnow()
    notes: str | None = None


__all__ = ["EntrapmentSignalStatus"]
