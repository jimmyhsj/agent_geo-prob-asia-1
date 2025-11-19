from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl

from agent_geo.config import IndicatorDimension, IndicatorTemplate


class IndicatorStatus(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class IndicatorRecord(BaseModel):
    template_key: str
    dimension: IndicatorDimension
    indicator: str
    latest_value: Optional[str] = None
    direction: Optional[str] = None
    date: Optional[datetime] = None
    source_url: Optional[HttpUrl] = None
    confidence: str = "M"
    weight: int = 3
    color: IndicatorStatus = IndicatorStatus.YELLOW
    analyst_note: Optional[str] = None

    @classmethod
    def from_template(cls, template: IndicatorTemplate) -> "IndicatorRecord":
        return cls(
            template_key=template.key,
            dimension=template.dimension,
            indicator=template.indicator,
            weight=template.default_weight,
        )


__all__ = ["IndicatorRecord", "IndicatorStatus"]
