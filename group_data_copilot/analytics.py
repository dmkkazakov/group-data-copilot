from __future__ import annotations

import pandas as pd
from .models import Entity, FinancialRecord, RiskFlag


def financial_summary(financials: list[FinancialRecord]) -> pd.DataFrame:
    if not financials:
        return pd.DataFrame(columns=["year", "revenue", "ebitda", "debt", "cash", "net_debt", "debt_to_ebitda"])
    df = pd.DataFrame([f.model_dump() for f in financials])
    out = df.groupby("year", as_index=False).agg({"revenue": "sum", "ebitda": "sum", "debt": "sum", "cash": "sum"})
    out["net_debt"] = out["debt"] - out["cash"]
    out["debt_to_ebitda"] = out.apply(lambda r: r["debt"] / r["ebitda"] if r["ebitda"] else None, axis=1)
    return out


def revenue_concentration(financials: list[FinancialRecord]) -> pd.DataFrame:
    if not financials:
        return pd.DataFrame(columns=["entity_id", "year", "revenue", "revenue_share"])
    df = pd.DataFrame([f.model_dump() for f in financials])
    totals = df.groupby("year")["revenue"].transform("sum")
    df["revenue_share"] = df["revenue"] / totals.replace({0: pd.NA})
    return df[["entity_id", "year", "revenue", "revenue_share"]].sort_values(["year", "revenue_share"], ascending=[True, False])


def detect_risk_flags(entities: list[Entity], financials: list[FinancialRecord]) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    entity_ids_with_fin = {f.entity_id for f in financials}

    for e in entities:
        if e.entity_id not in entity_ids_with_fin:
            flags.append(RiskFlag(
                entity_id=e.entity_id,
                severity="medium",
                flag="missing_financials",
                explanation="No financial records were provided for the entity."
            ))

    if financials:
        df = pd.DataFrame([f.model_dump() for f in financials])
        latest_year = int(df["year"].max())
        latest = df[df["year"] == latest_year]
        total_revenue = latest["revenue"].sum()
        if total_revenue > 0:
            for _, row in latest.iterrows():
                share = row["revenue"] / total_revenue
                if share >= 0.5:
                    flags.append(RiskFlag(
                        entity_id=row["entity_id"],
                        severity="high",
                        flag="revenue_concentration",
                        explanation=f"Entity generates {share:.1%} of group revenue in {latest_year}."
                    ))
        for _, row in latest.iterrows():
            if row["ebitda"] > 0 and row["debt"] / row["ebitda"] > 4:
                flags.append(RiskFlag(
                    entity_id=row["entity_id"],
                    severity="high",
                    flag="high_leverage",
                    explanation=f"Debt / EBITDA exceeds 4.0x in {latest_year}."
                ))
    return flags
