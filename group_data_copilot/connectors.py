from __future__ import annotations

from pathlib import Path
import pandas as pd

from .models import Entity, OwnershipEdge, FinancialRecord


class LocalDataConnector:
    """Loads group data from local CSV files.

    Expected files:
    - entities.csv
    - ownership.csv
    - financials.csv
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def load_entities(self) -> list[Entity]:
        path = self.data_dir / "entities.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path, dtype={"inn": "string"}).where(pd.notnull(pd.read_csv(path, dtype={"inn": "string"})), None)
        return [Entity(**row) for row in df.to_dict(orient="records")]

    def load_ownership(self) -> list[OwnershipEdge]:
        path = self.data_dir / "ownership.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path)
        return [OwnershipEdge(**row) for row in df.to_dict(orient="records")]

    def load_financials(self) -> list[FinancialRecord]:
        path = self.data_dir / "financials.csv"
        if not path.exists():
            return []
        df = pd.read_csv(path)
        return [FinancialRecord(**row) for row in df.to_dict(orient="records")]
