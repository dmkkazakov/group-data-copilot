from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid", str_strip_whitespace=True)


class Entity(Record):
    entity_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    inn: Optional[str] = None
    country: str = "RU"
    role: str = "unknown"
    sector: Optional[str] = None


class OwnershipEdge(Record):
    parent_id: str
    child_id: str
    share: float = Field(ge=0, le=1)


class FinancialRecord(Record):
    entity_id: str
    year: int
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    debt: Optional[float] = None
    cash: Optional[float] = None


class RiskFlag(Record):
    entity_id: str
    severity: str
    flag: str
    explanation: str


class GroupProfile(Record):
    group_name: str
    entities: list[Entity]
    ownership: list[OwnershipEdge]
    financials: list[FinancialRecord]
    risk_flags: list[RiskFlag]

    @model_validator(mode="after")
    def coherent_input(self):
        ids = [e.entity_id for e in self.entities]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("A nonempty, unique entity list is required")
        edges = set()
        incoming = {}
        for e in self.ownership:
            if e.parent_id not in ids or e.child_id not in ids:
                raise ValueError("Ownership refers to an unknown entity")
            key = (e.parent_id, e.child_id)
            if key in edges:
                raise ValueError("Duplicate ownership edge")
            edges.add(key)
            incoming[e.child_id] = incoming.get(e.child_id, 0) + e.share
        if any(value > 1 + 1e-12 for value in incoming.values()):
            raise ValueError("Direct ownership total exceeds 100 percent")
        financial_keys = set()
        for f in self.financials:
            if f.entity_id not in ids:
                raise ValueError("Financials refer to an unknown entity")
            key = (f.entity_id, f.year)
            if key in financial_keys:
                raise ValueError("Duplicate entity-year financial record")
            financial_keys.add(key)
        return self
