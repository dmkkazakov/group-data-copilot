from pathlib import Path
from group_data_copilot.agent import GroupDataCopilot


def test_agent_runs(tmp_path):
    data_dir = Path(__file__).resolve().parents[1] / "examples" / "data"
    agent = GroupDataCopilot("Demo Industrial Group", data_dir)
    profile = agent.run(tmp_path)
    assert len(profile.entities) == 5
    assert (tmp_path / "group_report.md").exists()
    assert (tmp_path / "group_profile.json").exists()
