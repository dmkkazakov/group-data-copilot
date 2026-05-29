from __future__ import annotations

import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .agent import GroupDataCopilot

console = Console()


def run_agent(args: argparse.Namespace) -> None:
    agent = GroupDataCopilot(group_name=args.group_name, data_dir=args.data_dir)
    profile = agent.run(output_dir=args.output_dir)

    table = Table(title="Group Data Copilot result")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Group", profile.group_name)
    table.add_row("Entities", str(len(profile.entities)))
    table.add_row("Ownership links", str(len(profile.ownership)))
    table.add_row("Financial records", str(len(profile.financials)))
    table.add_row("Risk flags", str(len(profile.risk_flags)))
    table.add_row("Output", str(args.output_dir))
    console.print(table)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Group Data Copilot: corporate group data collection agent")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run group data collection and report generation")
    run.add_argument("--group-name", required=True, help="Name of the corporate group")
    run.add_argument("--data-dir", required=True, type=Path, help="Directory with entities.csv, ownership.csv, financials.csv")
    run.add_argument("--output-dir", default=Path("output/group"), type=Path, help="Output directory")
    run.set_defaults(func=run_agent)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
