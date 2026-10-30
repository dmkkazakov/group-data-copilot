# Group Data Copilot

Public-source corporate-group research and a separate offline CSV analysis prototype by Dmitry Kazakov.

## Research paper and reproducible evidence

The [research package](research/mcp_harness/README.md) contains an English working paper prepared for SSRN, a Russian companion and five historical public cases: MTS, HSBC, Berkshire Hathaway, Tencent and Singtel. It includes 40 dated assertions, primary-source locators, 16 equations, a read-only MCP server and a deterministic harness.

- [English paper PDF](research/mcp_harness/artifacts/Corporate_Groups_SSRN_EN.pdf)
- [Russian paper PDF](research/mcp_harness/artifacts/MCP_Harness_Corporate_Groups_RU.pdf)
- [Russian editable Word document](research/mcp_harness/artifacts/MCP_Harness_Corporate_Groups.docx)
- [Data and results](research/mcp_harness/README.md)
- [Audit findings and corrections](research/mcp_harness/AUDIT.md)
- [SSRN submission fields](research/mcp_harness/SSRN_SUBMISSION.md)

The package has 48 research tests and a controlled experiment with 520 corrupted records and 40 clean controls. These verify replay integrity and arithmetic; they do not establish autonomous extraction accuracy. The disclosed Berkshire rounding discrepancy remains unresolved. No SSRN submission or acceptance is claimed.

Research calculations use only the Python 3.10+ standard library:

```bash
cd research/mcp_harness
python3 -m unittest -v test_research.py
python3 harness.py --output /tmp/corporate-groups-replay
python3 evaluate.py --output /tmp/corporate-groups-replay/mutation_results.json
python3 verify_release.py
```

## Offline CSV application

The separate `group_data_copilot` application reads a user-supplied entity perimeter, ownership edges and annual financial records. It validates identifiers and duplicate records, builds an ownership graph, calculates simple metrics and writes JSON, CSV and Markdown reports. It has 17 additional tests.

There is no live registry lookup, tax-ID search, LLM runtime or connector framework in this application. The research MCP server serves the curated research corpus; it does not add those capabilities to the CSV application.

Financial totals are **unconsolidated sums of supplied entity records**. Currency, units, dates and accounting basis must already be aligned. Intercompany eliminations are not performed. Missing metrics remain null, and incomplete metric totals remain missing. An omitted entity can still make the supplied perimeter incomplete.

Install and run from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q tests
group-data-copilot run --group-name "Demo Industrial Group" --data-dir examples/data --output-dir output/demo_group
```

On Windows, activate with `.venv\Scripts\activate`. The equivalent module entry point is `python -m group_data_copilot run` with the same arguments.

`entities.csv` is required. `ownership.csv` and `financials.csv` are optional. Identifiers are strings. The examples are synthetic. Each entity-year must occur once, ownership endpoints must exist in the supplied perimeter, and direct ownership shares must not exceed one per investee.

Generated files: `group_profile.json`, `entities.csv`, `ownership_edges.csv`, `financial_summary.csv`, `revenue_concentration.csv`, `risk_flags.csv` and `group_report.md`.

## Reproducibility and citation

[Research citation metadata](research/mcp_harness/CITATION.cff) identify the paper. Cite the repository commit as well as the manuscript version. The top-level [CITATION.cff](CITATION.cff) identifies the software prototype.

The repository's license file applies to its original code and documentation. Copyright in linked issuer reports remains with their respective rights holders; the original reports are not redistributed.
