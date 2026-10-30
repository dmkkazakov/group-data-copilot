# Reproduce this repository

Clone the existing repository:

```bash
git clone https://github.com/dmkkazakov/group-data-copilot.git
cd group-data-copilot
```

For the working paper and five source cases, follow [the research README](../research/mcp_harness/README.md). No external Python dependencies are needed for the research calculations.

For the separate CSV application, install `python -m pip install -e '.[dev]'`, run `python -m pytest -q tests`, then use the documented CLI in [README](../README.md). The example inputs are synthetic and the financial sums are unconsolidated.

When changing a source assertion, update `build_dataset.py`, regenerate the corpus, rerun research tests and the harness in a fresh output directory, regenerate the mutation controls and documents, then update the release manifest. Do not describe replay tests as independent source verification.

Commit source, tests and intentional release outputs. Do not commit Python bytecode, environment folders or generated egg-info.
