# GitHub instruction

## 1. Create repository

Repository name:

```text
group-data-copilot
```

Description:

```text
Agentic workflow for collecting, structuring and reporting corporate group data for credit analytics.
```

Topics:

```text
corporate-banking, credit-risk, data-agent, ai-agent, ownership-graph, financial-analysis, graph-analytics, due-diligence, synthetic-data
```

## 2. Upload project

Upload all files from the ZIP archive or push by command line:

```bash
git init
git add .
git commit -m "Initial release: Group Data Copilot"
git branch -M main
git remote add origin https://github.com/<username>/group-data-copilot.git
git push -u origin main
```

## 3. Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
group-data-copilot run --group-name "Demo Industrial Group" --data-dir examples/data --output-dir output/demo_group
```

## 4. What to show during demo

Open these files:

```text
output/demo_group/group_report.md
output/demo_group/group_profile.json
output/demo_group/risk_flags.csv
output/demo_group/ownership_edges.csv
```

## 5. Honest positioning

Use this wording:

```text
This is my AI-ready Group Data Copilot prototype. It demonstrates an agentic workflow for corporate group data collection, normalization, ownership graph construction, first-pass risk flagging and analyst report generation.
```

Avoid saying that it directly connects to official registries unless you add real connectors.
