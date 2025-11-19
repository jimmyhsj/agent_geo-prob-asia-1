from __future__ import annotations

from datetime import date
from statistics import mean
from typing import Iterable, List

from agent_geo.models.forecast import ForecastEvent
from agent_geo.storage import ForecastStore


class ForecastTracker:
    def __init__(self, store: ForecastStore | None = None) -> None:
        self.store = store or ForecastStore()
        self.events: List[ForecastEvent] = self.store.load()

    def add_event(self, event: ForecastEvent) -> None:
        self.events.append(event)
        self.store.save(self.events)

    def finalize(self, event_name: str, outcome: int) -> None:
        for event in self.events:
            if event.event == event_name:
                event.finalize(outcome)
                self.store.save(self.events)
                return
        raise KeyError(f"Event not found: {event_name}")

    def pending(self) -> List[ForecastEvent]:
        today = date.today()
        return [event for event in self.events if event.outcome is None and event.due_date >= today]

    def aggregate_brier(self) -> float | None:
        scored = [event.brier for event in self.events if event.brier is not None]
        if not scored:
            return None
        return float(mean(scored))

    def to_rows(self) -> List[dict]:
        rows = []
        for event in self.events:
            rows.append(
                {
                    "event": event.event,
                    "due_date": event.due_date.isoformat(),
                    "probability": event.probability,
                    "outcome": event.outcome,
                    "brier": event.brier,
                    "rationale": event.rationale,
                }
            )
        return rows


__all__ = ["ForecastTracker"]
