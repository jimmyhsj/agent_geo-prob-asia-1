from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ForecastEvent(BaseModel):
    event: str
    due_date: date
    probability: float = Field(ge=0.0, le=1.0)
    outcome: Optional[int] = Field(default=None, ge=0, le=1)
    brier: Optional[float] = None
    rationale: Optional[str] = None
    postmortem_link: Optional[HttpUrl] = None

    def finalize(self, outcome: int) -> None:
        self.outcome = outcome
        self.brier = (self.probability - outcome) ** 2


__all__ = ["ForecastEvent"]
