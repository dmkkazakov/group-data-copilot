from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from .models import GroupProfile
from .analytics import financial_summary, revenue_concentration
from .graph import build_ownership_graph, graph_metrics, graph_edges_dataframe


def write_outputs(profile: GroupProfile, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "group_profile.json").write_text(
        json.dumps(profile.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    pd.DataFrame([e.model_dump() for e in profile.entities]).to_csv(out / "entities.csv", index=False)
    graph_edges_dataframe(profile.ownership).to_csv(out / "ownership_edges.csv", index=False)
    financial_summary(profile.financials).to_csv(out / "financial_summary.csv", index=False)
    revenue_concentration(profile.financials).to_csv(out / "revenue_concentration.csv", index=False)
    pd.DataFrame([r.model_dump() for r in profile.risk_flags]).to_csv(out / "risk_flags.csv", index=False)

    g = build_ownership_graph(profile.entities, profile.ownership)
    metrics = graph_metrics(g)

    md = render_markdown_report(profile, metrics)
    (out / "group_report.md").write_text(md, encoding="utf-8")


def render_markdown_report(profile: GroupProfile, metrics: dict) -> str:
    entity_count = len(profile.entities)
    flags_high = sum(1 for f in profile.risk_flags if f.severity == "high")
    flags_medium = sum(1 for f in profile.risk_flags if f.severity == "medium")

    lines = [
        f"# Group Data Dossier: {profile.group_name}",
        "",
        "## Executive summary",
        "",
        f"The agent identified **{entity_count} legal entities** and **{len(profile.ownership)} ownership links**.",
        f"The current risk scan produced **{flags_high} high** and **{flags_medium} medium** flags.",
        "",
        "## Graph metrics",
        "",
        f"- Nodes: {metrics['nodes']}",
        f"- Edges: {metrics['edges']}",
        f"- Weak components: {metrics['weak_components']}",
        f"- Directed acyclic graph: {metrics['is_dag']}",
        "",
        "## Entities",
        "",
        "| Entity ID | Name | INN | Role | Sector |",
        "|---|---|---|---|---|",
    ]

    for e in profile.entities:
        lines.append(f"| {e.entity_id} | {e.name} | {e.inn or ''} | {e.role} | {e.sector or ''} |")

    lines.extend(["", "## Risk flags", "", "| Severity | Entity ID | Flag | Explanation |", "|---|---|---|---|"])
    for f in profile.risk_flags:
        lines.append(f"| {f.severity} | {f.entity_id} | {f.flag} | {f.explanation} |")

    lines.extend([
        "",
        "## Analytical interpretation",
        "",
        "This dossier is a first-pass analytical layer. It does not replace official due diligence, legal verification, sanction screening, financial statement analysis or credit committee materials.",
        "",
        "Recommended next steps:",
        "",
        "1. Validate legal entity perimeter against official registries.",
        "2. Reconcile ownership links with shareholder disclosures.",
        "3. Load audited IFRS / RAS financials.",
        "4. Add payment-flow, supply-chain and contract-level data.",
        "5. Run credit limit allocation and liquidity stress scenarios."
    ])
    return "\n".join(lines)
