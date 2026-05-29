from __future__ import annotations

from pathlib import Path

from .connectors import LocalDataConnector
from .models import GroupProfile
from .analytics import detect_risk_flags
from .report import write_outputs


class GroupDataCopilot:
    def __init__(self, group_name: str, data_dir: str | Path):
        self.group_name = group_name
        self.connector = LocalDataConnector(data_dir)

    def run(self, output_dir: str | Path) -> GroupProfile:
        entities = self.connector.load_entities()
        ownership = self.connector.load_ownership()
        financials = self.connector.load_financials()
        risk_flags = detect_risk_flags(entities, financials)

        profile = GroupProfile(
            group_name=self.group_name,
            entities=entities,
            ownership=ownership,
            financials=financials,
            risk_flags=risk_flags,
        )
        write_outputs(profile, output_dir)
        return profile
