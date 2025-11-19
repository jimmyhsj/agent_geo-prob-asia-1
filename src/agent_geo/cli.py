from __future__ import annotations

import argparse
from datetime import datetime

from rich.console import Console
from rich.table import Table

from agent_geo import (
    ENTRAPMENT_SIGNALS,
    INDICATOR_TEMPLATES,
    GeoRiskAgent,
    GLOBAL_SYSTEM_PROMPT,
    list_prompt_templates,
)
from agent_geo.datasources import list_sources, missing_prompt_sources
from agent_geo.models import IndicatorStatus
from agent_geo.models.forecast import ForecastEvent

console = Console()


def _color(value: str) -> IndicatorStatus:
    return IndicatorStatus(value.lower())


def cmd_init(agent: GeoRiskAgent) -> None:
    console.print("[bold]Indicator templates[/bold]")
    table = Table("Key", "Dimension", "Indicator", "Weight")
    for template in INDICATOR_TEMPLATES:
        table.add_row(template.key, template.dimension.value, template.indicator, str(template.default_weight))
    console.print(table)

    console.print("\n[bold]Entrapment signals[/bold]")
    signal_table = Table("Key", "Description", "Sources")
    for signal in ENTRAPMENT_SIGNALS:
        signal_table.add_row(signal.key, signal.description, "\n".join(signal.primary_sources))
    console.print(signal_table)


def cmd_search(agent: GeoRiskAgent, query: str, limit: int) -> None:
    results = agent.websearch.search(query)[:limit]
    table = Table("Title", "URL", "Source")
    for result in results:
        table.add_row(result.title, result.url, result.source or "web")
    console.print(table)


def cmd_panel_list(agent: GeoRiskAgent) -> None:
    rows = agent.panel_rows()
    if not rows:
        console.print("No panel entries yet. Run `panel update` or `panel export`." )
        return
    table = Table("Dimension", "Indicator", "Latest", "Dir", "Color", "Confidence")
    for row in rows:
        table.add_row(
            row["dimension"],
            row["indicator"],
            row.get("latest_value") or "-",
            row.get("direction") or "-",
            row.get("color") or "-",
            row.get("confidence") or "-",
        )
    console.print(table)


def cmd_panel_update(agent: GeoRiskAgent, args: argparse.Namespace) -> None:
    if args.query:
        record = agent.collect_indicator_from_web(
            key=args.key,
            query=args.query,
            latest_value=args.value,
            direction=args.direction,
            color=_color(args.color),
            confidence=args.confidence,
            analyst_note=args.note,
        )
    else:
        record = agent.panel.update_indicator(
            args.key,
            latest_value=args.value,
            direction=args.direction,
            source_url=args.source_url,
            color=_color(args.color),
            confidence=args.confidence,
            analyst_note=args.note,
            evidence=None,
        )
    console.print(f"Updated {record.indicator} with status {record.color.value}")


def cmd_panel_export(agent: GeoRiskAgent, path: str) -> None:
    exported = agent.export_panel_csv(path)
    console.print(f"Panel exported to {exported}")


def cmd_ach_add(agent: GeoRiskAgent, args: argparse.Namespace) -> None:
    evidence = agent.add_supporting_evidence(args.hypothesis, args.query, supports=args.kind == "support")
    if evidence:
        console.print(f"Logged evidence {evidence.title}")
    else:
        console.print("No evidence returned from web search")


def cmd_forecast_add(agent: GeoRiskAgent, args: argparse.Namespace) -> None:
    event = ForecastEvent(
        event=args.event,
        due_date=datetime.fromisoformat(args.due_date).date(),
        probability=args.probability,
        rationale=args.rationale,
    )
    agent.upsert_forecast(event)
    console.print(f"Logged forecast '{event.event}' at p={event.probability}")


def cmd_forecast_close(agent: GeoRiskAgent, args: argparse.Namespace) -> None:
    agent.finalize_forecast(args.event, args.outcome)
    console.print(f"Finalized {args.event} with outcome {args.outcome}")


def cmd_forecast_list(agent: GeoRiskAgent) -> None:
    rows = agent.forecast_rows()
    table = Table("Event", "Due", "p", "Outcome", "Brier")
    for row in rows:
        table.add_row(
            row["event"],
            row["due_date"],
            f"{row['probability']:.2f}",
            "-" if row["outcome"] is None else str(row["outcome"]),
            "-" if row["brier"] is None else f"{row['brier']:.3f}",
        )
    console.print(table)


def cmd_alert_set(agent: GeoRiskAgent, args: argparse.Namespace) -> None:
    active = True if getattr(args, "active", False) else False
    if getattr(args, "inactive", False):
        active = False
    agent.set_alert_state(args.key, active=active, notes=args.notes)
    console.print(f"Signal {args.key} => {'ACTIVE' if active else 'inactive'}")
    if agent.red_alert():
        console.print("[bold red]Entrapment red-line triggered![/bold red]")


def cmd_alert_status(agent: GeoRiskAgent) -> None:
    rows = agent.alerts.summary()
    table = Table("Key", "Description", "Active", "Evidence", "Checked")
    for row in rows:
        table.add_row(
            row["key"],
            row["description"],
            "yes" if row["active"] else "no",
            str(row["evidence_count"]),
            row["last_checked"],
        )
    console.print(table)


def cmd_prompts_list() -> None:
    table = Table("Key", "Title", "Description", "Default Sources")
    for template in list_prompt_templates():
        sources_preview = ", ".join(template.default_source_hints[:2])
        if len(template.default_source_hints) > 2:
            sources_preview += ", …"
        table.add_row(template.key, template.title, template.description, sources_preview or "-")
    console.print(table)


def cmd_prompts_show(agent: GeoRiskAgent, key: str, sources: list[str] | None) -> None:
    try:
        prompt_bundle = agent.prompt_messages(key, sources)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        return
    console.rule(prompt_bundle["title"])
    console.print(f"[italic]{prompt_bundle['description']}[/italic]\\n")
    console.print("[bold]System[/bold]")
    console.print(prompt_bundle["system"])
    console.print("\\n[bold]User[/bold]")
    console.print(prompt_bundle["user"])
    console.print("\\n[bold]Output Schema[/bold]")
    console.print(prompt_bundle["output_schema"])
    console.print("\\n[bold]Default Sources[/bold]")
    for url in prompt_bundle["default_sources"]:
        console.print(f"- {url}")


def cmd_sources_list() -> None:
    table = Table("Name", "Category", "URL", "Tags")
    for source in list_sources():
        tag_text = ", ".join(source.tags) if source.tags else "-"
        table.add_row(source.name, source.category, source.url, tag_text)
    console.print(table)


def cmd_sources_audit() -> None:
    missing = missing_prompt_sources()
    if not missing:
        console.print("[green]All prompt default sources are covered by the whitelist.[/green]")
        return
    console.print("[yellow]The following prompt sources are not yet in `data/source_whitelist.json`:[/yellow]")
    for url in missing:
        console.print(f"- {url}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Geo-risk agent control surface")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Show templates and signals")

    search = sub.add_parser("search", help="Run a web search via the tool")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=3)

    panel = sub.add_parser("panel", help="Panel operations")
    panel_sub = panel.add_subparsers(dest="panel_command")
    panel_sub.add_parser("list", help="List current panel values")
    panel_update = panel_sub.add_parser("update", help="Update an indicator")
    panel_update.add_argument("--key", required=True)
    panel_update.add_argument("--value", required=True)
    panel_update.add_argument("--direction")
    panel_update.add_argument("--color", default="yellow")
    panel_update.add_argument("--confidence", default="M")
    panel_update.add_argument("--note")
    panel_update.add_argument("--query", help="If provided, evidence will be auto-fetched")
    panel_update.add_argument("--source-url", dest="source_url")
    panel_sub.add_parser("export", help="Export panel to CSV").add_argument("path")

    ach = sub.add_parser("ach", help="ACH operations")
    ach_sub = ach.add_subparsers(dest="ach_command")
    ach_add = ach_sub.add_parser("add", help="Add support/refute evidence")
    ach_add.add_argument("--hypothesis", required=True)
    ach_add.add_argument("--query", required=True)
    ach_add.add_argument("--kind", choices=["support", "refute"], required=True)

    forecast = sub.add_parser("forecast", help="Forecast ledger")
    forecast_sub = forecast.add_subparsers(dest="forecast_command")
    forecast_add = forecast_sub.add_parser("add")
    forecast_add.add_argument("--event", required=True)
    forecast_add.add_argument("--due-date", required=True)
    forecast_add.add_argument("--probability", type=float, required=True)
    forecast_add.add_argument("--rationale")
    forecast_close = forecast_sub.add_parser("close")
    forecast_close.add_argument("--event", required=True)
    forecast_close.add_argument("--outcome", type=int, choices=[0, 1], required=True)
    forecast_sub.add_parser("list")

    alert = sub.add_parser("alert", help="Entrapment signal monitoring")
    alert_sub = alert.add_subparsers(dest="alert_command")
    alert_set = alert_sub.add_parser("set")
    alert_set.add_argument("--key", required=True)
    alert_toggle = alert_set.add_mutually_exclusive_group(required=True)
    alert_toggle.add_argument("--active", action="store_true")
    alert_toggle.add_argument("--inactive", action="store_true")
    alert_set.add_argument("--notes")
    alert_sub.add_parser("status")

    prompts = sub.add_parser("prompts", help="LLM prompt templates")
    prompts_sub = prompts.add_subparsers(dest="prompts_command")
    prompts_sub.add_parser("list", help="List available templates")
    prompts_show = prompts_sub.add_parser("show", help="Show one template")
    prompts_show.add_argument("--key", required=True)
    prompts_show.add_argument("--sources", nargs="*", help="Override [SOURCE_URLS]")

    sources = sub.add_parser("sources", help="Primary data sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    sources_sub.add_parser("list")
    sources_sub.add_parser("audit")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    agent = GeoRiskAgent()

    if args.command == "init":
        cmd_init(agent)
    elif args.command == "search":
        cmd_search(agent, args.query, args.limit)
    elif args.command == "panel":
        if args.panel_command == "list":
            cmd_panel_list(agent)
        elif args.panel_command == "update":
            cmd_panel_update(agent, args)
        elif args.panel_command == "export":
            cmd_panel_export(agent, args.path)
        else:
            console.print("panel command requires subcommand")
    elif args.command == "ach":
        if args.ach_command == "add":
            cmd_ach_add(agent, args)
        else:
            console.print("ach command requires subcommand")
    elif args.command == "forecast":
        if args.forecast_command == "add":
            cmd_forecast_add(agent, args)
        elif args.forecast_command == "close":
            cmd_forecast_close(agent, args)
        elif args.forecast_command == "list":
            cmd_forecast_list(agent)
        else:
            console.print("forecast command requires subcommand")
    elif args.command == "alert":
        if args.alert_command == "set":
            cmd_alert_set(agent, args)
        elif args.alert_command == "status":
            cmd_alert_status(agent)
        else:
            console.print("alert command requires subcommand")
    elif args.command == "prompts":
        if args.prompts_command == "list":
            cmd_prompts_list()
        elif args.prompts_command == "show":
            cmd_prompts_show(agent, args.key, args.sources)
        else:
            console.print("prompts command requires subcommand")
    elif args.command == "sources":
        if args.sources_command == "list":
            cmd_sources_list()
        elif args.sources_command == "audit":
            cmd_sources_audit()
        else:
            console.print("sources command requires subcommand")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
