# MCP and harness study of corporate groups

Five public cases: **MTS (Russia), HSBC (UK), Berkshire Hathaway (US), Tencent (China operating group; Cayman parent), Singtel (Singapore)**.

- [English paper](paper_en.md) · [SSRN PDF](artifacts/Corporate_Groups_SSRN_EN.pdf)
- [Russian paper](paper_ru.md) · [Russian Word document](artifacts/MCP_Harness_Corporate_Groups.docx)
- [Submission metadata](SSRN_SUBMISSION.md)
- [SSRN form fields and guide](submission/README.md) · [Russian submission guide](submission/SSRN_GUIDE_RU.docx)
- [Normalized evidence](data/cases.json) · [Computed results](results/results.json)
- [Recorded tests](results/test_report.json) · [Source recheck](data/source_recheck.json) · [Release checksums](release_manifest.json)

The package contains **40 source assertions, eight primary-source entries representing seven issuer documents, 16 numbered equations and 48 research tests and 17 separate CSV-application tests**. Dates are historical, mainly FY2024 and Singtel FY2025. Retrieval date: 2026-10-30.

## Reproduce the results

The calculations, server, harness and tests require only the Python 3.10+ standard library. From the repository root:

```bash
cd research/mcp_harness
python3 -m unittest -v test_research.py
python3 harness.py --output /tmp/corporate-groups-replay
python3 evaluate.py --output /tmp/corporate-groups-replay/mutation_results.json
python3 verify_release.py
```

Use a fresh output directory for a full MCP replay. Running the harness again in the same directory validates and resumes its checkpoint without duplicating accepted claims. To regenerate the normalized data from its explicit transcription source:

```bash
python3 build_dataset.py
```

The corpus checksum covers the exact JSON bytes. The results corpus hash uses canonical JSON; the two digests intentionally differ. Neither certifies factual truth. Original issuer reports are not redistributed. Sources and page locators are in the corpus and paper.

## What is implemented

`server.py` is a small read-only MCP stdio server pinned to revision 2025-11-25. It supports initialize, notifications/initialized, ping, tools/list and tools/call. The tools are case_list and case_get. The server has no shell or arbitrary URL capability. It is a research example, not a general MCP implementation or hardened hosted service.

`harness.py` starts that server as a real subprocess, discovers tools, retrieves the five cases, compares assertions to the frozen corpus, saves atomic checkpoints, records a hash chain and computes results. All assertions retain their individual snapshot dates. Exact replay checks do not validate the initial transcription independently. The package has no LLM runtime, live registry connector or automated web-extraction benchmark.

`engine.py` contains class-weighted fractions, typed path restrictions and a restricted two-company cross-holding solver. All 13 claim fields and the complete case inventory are checked. Requests have a configurable ten-second response deadline. Checkpoint events must match the accepted case records. General graph closure and interval propagation are mathematical discussion in the paper, not implemented production features.

## Findings that must remain qualified

Berkshire's published counts imply **14.348232%** economic participation while its table reports **14.4%**. Direct one-decimal rounding does not reconcile these values. Both are retained and the difference is explicitly unresolved. This is not a claim that the issuer's number is erroneous.

HSBC's selected table reports direct or indirect group interests. Tencent's contractual-control edge has no inferred equity percentage. Singtel's shareholder observations are dated June, not the March financial year end; deemed interests are not cash-flow weights. MTS's included 11.03% block is not added again.

The 48 passing research test methods are software verification, not an extraction accuracy estimate. The five selected cases are not a representative sample. The corpus was transcribed with AI assistance and has not received independent human double coding.

## Build the documents

Install the pinned document dependencies in a separate environment, then run:

```bash
python3 -m pip install -r requirements-documents.txt
python3 build_documents.py
python3 build_submission.py
```

This creates the two DOCX files from Markdown and equation images. Convert them with LibreOffice or Word to PDF. The delivered PDFs were rendered and checked page by page. No model or network access is required to rebuild DOCX files.

Generative AI assisted source discovery, transcription, writing, translation and software development. The disclosure appears in the paper and abstract. Author declarations and any platform submission remain the author's responsibility. No SSRN submission or acceptance is claimed.

Code is covered by the repository's MIT license. Copyright in linked issuer reports remains with the respective rights holders. See the paper-specific [CITATION.cff](CITATION.cff).

## Audit and controlled corruption experiment

Version 1.1 adds 520 one-field corruptions of the 40 reference assertions. The full gate rejects all 520 and accepts all 40 unchanged controls; a source-field-presence baseline accepts both sets. These are constructed integrity controls, not independent extraction predictions. See [per-field results](results/mutation_results.json) and the [audit report](AUDIT.md). A reference transcription error can still pass exact replay.

The build regenerates equations from current TeX every time and does not rewrite the manuscript sources. The release manifest records delivered bytes; Word/PDF rebuilding may differ in timestamps or renderer metadata. One harness writer per output directory is supported.

Version 1.2 names OpenAI ChatGPT and Codex in both language versions and their abstracts, and adds a submission guide plus separate form-field files. The case corpus and numerical findings are unchanged from version 1.1. Funding, competing interests, profile affiliation and license choices are not asserted on the author's behalf.
