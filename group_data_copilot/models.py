from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    entity_id: str
    name: str
    inn: Optional[str] = None
    country: str = "RU"
    role: str = "unknown"
    sector: Optional[str] = None


class OwnershipEdge(BaseModel):
    parent_id: str
    child_id: str
    share: float = Field(ge=0, le=1)


class FinancialRecord(BaseModel):
    entity_id: str
    year: int
    revenue: float = 0.0
    ebitda: float = 0.0
    debt: float = 0.0
    cash: float = 0.0


class RiskFlag(BaseModel):
    entity_id: str
    severity: str
    flag: str
    explanation: str


class GroupProfile(BaseModel):
    group_name: str
    entities: List[Entity]
    ownership: List[OwnershipEdge]
    financials: List[FinancialRecord]
    risk_flags: List[RiskFlag]
