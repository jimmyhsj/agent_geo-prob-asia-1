from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import List, Sequence

from agent_geo.prompts import PROMPT_TEMPLATES


@dataclass(slots=True)
class DataSource:
    name: str
    url: str
    category: str
    notes: str
    tags: List[str] = field(default_factory=list)


_SOURCE_PATH = Path(__file__).resolve().parents[1] / "data" / "source_whitelist.json"


def load_sources(path: Path | None = None) -> List[DataSource]:
    """Load the source registry from disk so the whitelist can evolve without touching code."""

    target = path or _SOURCE_PATH
    if not target.exists():
        raise FileNotFoundError(f"Source whitelist not found at {target}")
    records = json.loads(target.read_text(encoding="utf-8"))
    return [DataSource(**record) for record in records]


def list_sources() -> List[DataSource]:
    return SOURCE_WHITELIST


def known_urls(sources: Sequence[DataSource] | None = None) -> set[str]:
    dataset = sources or SOURCE_WHITELIST
    return {source.url for source in dataset}


def prompt_hint_urls() -> set[str]:
    urls: set[str] = set()
    for template in PROMPT_TEMPLATES:
        urls.update(template.default_source_hints)
    return urls


def missing_prompt_sources(sources: Sequence[DataSource] | None = None) -> List[str]:
    """Return prompt default URLs that have not yet been added to the whitelist."""

    known = known_urls(sources)
    missing = sorted(prompt_hint_urls() - known)
    return missing


SOURCE_WHITELIST = load_sources()


__all__ = [
    "DataSource",
    "SOURCE_WHITELIST",
    "load_sources",
    "list_sources",
    "missing_prompt_sources",
]
