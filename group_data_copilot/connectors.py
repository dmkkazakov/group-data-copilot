from __future__ import annotations

import csv
from pathlib import Path
from .models import Entity, OwnershipEdge, FinancialRecord


class LocalDataConnector:
    """Read local CSV records without turning missing values into zero."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"Data directory does not exist: {self.data_dir}")

    def _read(self, name, model, required=False):
        path = self.data_dir / name
        if not path.exists():
            if required:
                raise FileNotFoundError(path)
            return []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = csv.DictReader(handle)
            return [model(**{k: (v.strip() if v and v.strip() else None)
                             for k, v in row.items()}) for row in rows]

    def load_entities(self) -> list[Entity]:
        return self._read("entities.csv", Entity, required=True)

    def load_ownership(self) -> list[OwnershipEdge]:
        return self._read("ownership.csv", OwnershipEdge)

    def load_financials(self) -> list[FinancialRecord]:
        return self._read("financials.csv", FinancialRecord)
