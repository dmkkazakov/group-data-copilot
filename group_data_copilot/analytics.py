from __future__ import annotations

import pandas as pd
from .models import Entity, FinancialRecord, RiskFlag


def financial_summary(financials: list[FinancialRecord]) -> pd.DataFrame:
    """Unconsolidated sums of supplied entity records in user-aligned units."""
    columns = ["year", "revenue", "ebitda", "debt", "cash", "net_debt", "debt_to_ebitda"]
    if not financials:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame([f.model_dump() for f in financials])
    grouped = df.groupby("year")
    # If any supplied record lacks a metric, do not publish a partial sum as a total.
    out = grouped[["revenue", "ebitda", "debt", "cash"]].agg(lambda s: s.sum() if s.notna().all() else float("nan")).reset_index()
    out["net_debt"] = out["debt"] - out["cash"]
    out["debt_to_ebitda"] = out["debt"] / out["ebitda"].where(out["ebitda"] > 0)
    return out[columns]


def revenue_concentration(financials: list[FinancialRecord]) -> pd.DataFrame:
    columns = ["entity_id", "year", "revenue", "revenue_share"]
    if not financials:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame([f.model_dump() for f in financials])
    totals = df.groupby("year")["revenue"].transform(lambda s: s.sum() if s.notna().all() else float("nan"))
    df["revenue_share"] = df["revenue"] / totals.where(totals > 0)
    return df[columns].sort_values(["year", "revenue_share"], ascending=[True, False])


def detect_risk_flags(entities: list[Entity], financials: list[FinancialRecord]) -> list[RiskFlag]:
    flags = []
    latest_year = max((f.year for f in financials), default=None)
    latest = [f for f in financials if f.year == latest_year]
    entity_ids = {f.entity_id for f in latest}
    for entity in entities:
        if entity.entity_id not in entity_ids:
            flags.append(RiskFlag(entity_id=entity.entity_id, severity="medium", flag="missing_financials",
                                  explanation="No financial record for the latest supplied year."))
    complete_revenue = bool(latest) and all(f.revenue is not None for f in latest)
    total_revenue = sum(f.revenue for f in latest) if complete_revenue else None
    for f in latest:
        if any(getattr(f, k) is None for k in ("revenue", "ebitda", "debt", "cash")):
            flags.append(RiskFlag(entity_id=f.entity_id, severity="medium", flag="incomplete_financials",
                                  explanation=f"At least one financial metric is missing for {latest_year}."))
        if total_revenue is not None and total_revenue > 0 and f.revenue / total_revenue >= 0.5:
            flags.append(RiskFlag(entity_id=f.entity_id, severity="high", flag="revenue_concentration",
                                  explanation=f"Entity contributes {f.revenue / total_revenue:.1%} of supplied unconsolidated revenue in {latest_year}."))
        if f.ebitda is not None and f.ebitda <= 0:
            flags.append(RiskFlag(entity_id=f.entity_id, severity="high", flag="nonpositive_ebitda",
                                  explanation=f"EBITDA is nonpositive in {latest_year}; leverage ratio is not meaningful."))
        elif f.ebitda is not None and f.debt is not None and f.debt / f.ebitda > 4:
            flags.append(RiskFlag(entity_id=f.entity_id, severity="high", flag="high_leverage",
                                  explanation=f"Debt / EBITDA exceeds 4.0x in {latest_year}."))
    return flags
