from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class EvidenceRecord(BaseModel):
    title: str
    date: Optional[datetime] = None
    source: str
    quote: str
    url: HttpUrl
    quality: str = "L"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hash: str | None = None

    @field_validator("hash", mode="before")
    @classmethod
    def ensure_hash(cls, value, values):  # type: ignore[override]
        if value:
            return value
        fingerprint = "|".join(
            [
                values.get("title", ""),
                (values.get("source") or ""),
                (values.get("quote") or ""),
                str(values.get("url") or ""),
            ]
        )
        return sha256(fingerprint.encode("utf-8")).hexdigest()


__all__ = ["EvidenceRecord"]
