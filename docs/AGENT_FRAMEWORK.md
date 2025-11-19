# Agent Framework Quickstart

This repository now ships a minimal but end-to-end scaffold that mirrors the blueprint inside `README.md`. The pieces are intentionally lightweight so you can swap in your preferred storage, schedulers, or LLM layers.

## Components

- `agent_geo.config` – structured indicator templates, ACH question, and entrapment signal definitions lifted directly from §4–§6 of the README.
- `agent_geo.datasources` – curated whitelist of primary sources (MOFA, MOD, JPX, GPIF, etc.) to keep ICD-203 traceability.
- `agent_geo.models` – Pydantic models for indicators, evidence packets, ACH rows, forecast ledger events, and red-line signals.
- `agent_geo.tools.WebSearchTool` – DuckDuckGo-backed web search wrapper that converts hits into `EvidenceRecord` objects.
- `agent_geo.pipelines` – helper classes for the indicator panel, ACH maintenance, Brier scoreboard, and entrapment monitor.
- `agent_geo.agent.GeoRiskAgent` – façade that wires the pipelines together, invoking the WebSearch tool when you call `collect_indicator_from_web` or `add_supporting_evidence`.
- `agent_geo.cli` – Rich-powered CLI published as the `agent-geo` console entry so you can start logging evidence immediately.
- `agent_geo.prompts` – codifies the README prompt packs (#0–#10) so you can hand the LLM a consistent system/user/schema triple for each task type.
- `data/source_whitelist.json` + `agent_geo.datasources` – editable registry of white-listed primary URLs plus CLI tooling (`agent-geo sources ...`) to keep it aligned with the README prompt hints.

## Install & Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
agent-geo init            # Show templates and entrapment signals
agent-geo search "反击能力"   # Run the websearch tool
agent-geo panel update --key institution_article9 --value "Cabinet reiterates ..." --color yellow --query "存立危机事态" --direction "stable"
agent-geo forecast add --event "Trilateral bundles Russia FE" --due-date 2025-06-30 --probability 0.35 --rationale "Awaiting summit communique"
agent-geo alert set --key trilateral_packaging --active
agent-geo prompts list       # View the available LLM task templates
agent-geo prompts show --key capability_line --sources https://www.mod.go.jp/en/press/
```

Outputs land in `data/`:

- `indicator_panel.json` + optional CSV export
- `evidence_log.jsonl` hashed by title/source/quote/URL
- `ach_table.json`
- `forecast_ledger.json`
- `source_whitelist.json` (authoritative registry used by prompts/datasources/audit tooling)

Use these files to plug into your ACH weight recalculations, Brier scorecards, or downstream OODA automations.

## Prompt Library

- Run `agent-geo prompts list` to see every template lifted from the README (institution, capability, alliance, JPX, GPIF, opinion, entrapment, ACH, Brier, flash brief).
- `agent-geo prompts show --key <name>` prints the global system directive, the task-specific user instructions (with optional `--sources` override), and the JSON schema exactly as prescribed.
- In code, call `GeoRiskAgent().prompt_messages("alliance_line")` to get a dict with `system`, `user`, `output_schema`, and default source hints ready for your LLM client.

## Source Registry Hygiene

- Edit `data/source_whitelist.json` whenever you add/retire URLs; the Python layer simply loads this file.
- `agent-geo sources list` shows the current canonical whitelist (name/category/tags/URL).
- `agent-geo sources audit` compares that file against every `default_source_hints` entry inside the prompt catalog so you can spot new URLs introduced in the README and add metadata before running collection.
