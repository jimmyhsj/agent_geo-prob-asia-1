from __future__ import annotations

from typing import Iterable, Optional

from agent_geo.models.ach import ACHTable
from agent_geo.models.evidence import EvidenceRecord
from agent_geo.models.forecast import ForecastEvent
from agent_geo.models.indicator import IndicatorRecord, IndicatorStatus
from agent_geo.pipelines import ACHManager, AlertMonitor, ForecastTracker, IndicatorPanelBuilder
from agent_geo.prompts import (
    GLOBAL_SYSTEM_PROMPT,
    PromptTemplate,
    get_prompt_template,
    list_prompt_templates,
)
from agent_geo.tools import WebSearchTool


class GeoRiskAgent:
    """High-level façade tying together the indicator panel, ACH, forecast ledger, and alerts."""

    def __init__(
        self,
        *,
        panel: IndicatorPanelBuilder | None = None,
        ach: ACHManager | None = None,
        forecasts: ForecastTracker | None = None,
        alerts: AlertMonitor | None = None,
        websearch: WebSearchTool | None = None,
    ) -> None:
        self.panel = panel or IndicatorPanelBuilder()
        self.ach = ach or ACHManager()
        self.forecasts = forecasts or ForecastTracker()
        self.alerts = alerts or AlertMonitor()
        self.websearch = websearch or WebSearchTool()
        self.prompt_templates = list_prompt_templates()

    def collect_indicator_from_web(
        self,
        *,
        key: str,
        query: str,
        latest_value: str,
        direction: Optional[str],
        color: IndicatorStatus,
        confidence: str = "M",
        analyst_note: Optional[str] = None,
    ) -> IndicatorRecord:
        evidence_list = self.websearch.search_as_evidence(query)
        evidence = evidence_list[0] if evidence_list else None
        return self.panel.update_indicator(
            key,
            latest_value=latest_value,
            direction=direction,
            source_url=str(evidence.url) if evidence else None,
            color=color,
            confidence=confidence,
            analyst_note=analyst_note,
            evidence=evidence,
        )

    def add_supporting_evidence(self, hypothesis: str, query: str, *, supports: bool) -> EvidenceRecord | None:
        evidence_list = self.websearch.search_as_evidence(query)
        if not evidence_list:
            return None
        evidence = evidence_list[0]
        if supports:
            self.ach.add_support(hypothesis, evidence)
        else:
            self.ach.add_refute(hypothesis, evidence)
        return evidence

    def upsert_forecast(self, event: ForecastEvent) -> None:
        self.forecasts.add_event(event)

    def finalize_forecast(self, event_name: str, outcome: int) -> None:
        self.forecasts.finalize(event_name, outcome)

    def set_alert_state(self, key: str, active: bool, notes: Optional[str] = None) -> None:
        self.alerts.update(key, active=active, evidence=None, notes=notes)

    def red_alert(self) -> bool:
        return self.alerts.is_red()

    def export_panel_csv(self, path: str) -> str:
        destination = self.panel.export_csv(path)
        return str(destination)

    def get_ach_table(self) -> ACHTable:
        return self.ach.table

    def panel_rows(self) -> list[dict]:
        return self.panel.to_rows()

    def forecast_rows(self) -> list[dict]:
        return self.forecasts.to_rows()

    def prompts(self) -> list[PromptTemplate]:
        return self.prompt_templates

    def prompt_messages(self, key: str, source_urls: list[str] | None = None) -> dict:
        template = get_prompt_template(key)
        user_prompt = template.render_user_prompt(source_urls)
        return {
            "key": template.key,
            "title": template.title,
            "description": template.description,
            "system": GLOBAL_SYSTEM_PROMPT,
            "user": user_prompt,
            "output_schema": template.output_schema,
            "default_sources": template.default_source_hints,
        }


__all__ = ["GeoRiskAgent"]
