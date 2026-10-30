"""Check consistency of the distributed evidence, results, manuscripts and hashes."""
import hashlib
import json
from pathlib import Path
import re
from engine import ROOT, compute, load_corpus
from harness import digest, validate_state
from evaluate import evaluate


def verify():
    corpus = load_corpus()
    current = compute(corpus)
    current["corpus_sha256"] = digest(corpus)
    assert current == json.loads((ROOT / "results/results.json").read_text(encoding="utf-8")), "Stale results"
    assert evaluate(corpus) == json.loads((ROOT / "results/mutation_results.json").read_text(encoding="utf-8")), "Stale mutation controls"
    validate_state(json.loads((ROOT / "results/checkpoint.json").read_text(encoding="utf-8")), corpus, digest(corpus))
    en = (ROOT / "paper_en.md").read_text(encoding="utf-8")
    ru = (ROOT / "paper_ru.md").read_text(encoding="utf-8")
    metadata = (ROOT / "SSRN_SUBMISSION.md").read_text(encoding="utf-8")
    abstract = en.split("## Abstract\n\n", 1)[1].split("\n\nKeywords:", 1)[0]
    assert metadata.split("## Abstract to paste\n\n", 1)[1].split("\n\n## Submission notes", 1)[0] == abstract, "Submission abstract drift"
    fields = json.loads((ROOT / "submission/fields.json").read_text(encoding="utf-8"))
    assert fields["abstract"] == abstract == (ROOT / "submission/02_ABSTRACT.txt").read_text(encoding="utf-8").strip(), "Form abstract drift"
    assert fields["title"] == en.splitlines()[0][2:] == (ROOT / "submission/01_TITLE.txt").read_text(encoding="utf-8").strip()
    assert fields["paper_version"] == "1.2" and "Version 1.2" in en and "Версия 1.2" in ru
    assert fields["abstract_word_count"] == len(abstract.split()) and fields["abstract_character_count"] == len(abstract)
    assert fields["ai_disclosure"] == en.split("## AI assistance disclosure\n\n", 1)[1].split("\n\n", 1)[0]
    assert "OpenAI ChatGPT and Codex" in abstract
    assert fields["funding_statement"]["author_confirmed"] is False and fields["competing_interests"]["author_confirmed"] is False
    pattern = r"^\$\$(.*?)\$\$$"
    en_equations = re.findall(pattern, en, flags=re.M)
    assert en_equations == re.findall(pattern, ru, flags=re.M), "Translation equation drift"
    assert [int(re.search(r"\\tag\{(\d+)\}", eq).group(1)) for eq in en_equations] == list(range(1, 17))
    for text, decimal, separator in [(en, ".", ","), (ru, ",", " ")]:
        for key, field in [("Berkshire", "economic_pct"), ("Berkshire", "vote_pct"),
                           ("Tencent", "Ma_pct"), ("Tencent", "MIH_pct"),
                           ("Singtel", "direct_pct"), ("Singtel", "deemed_pct"),
                           ("Singtel", "direct_plus_deemed_disclosure_pct")]:
            assert str(current[key][field]).replace(".", decimal) in text, f"Missing calculated value: {key}.{field}"
        # Every six-row MTS partition input must match the evidence, not merely the grand total.
        for c in corpus["claims"]:
            if c["id"] in {f"M{i:02d}" for i in range(1, 7)}:
                count = format(c["value"]["shares"], ",").replace(",", separator)
                assert count in text, f"Manuscript count drift: {c['id']}"
    assert f"D={corpus['constants']['Singtel_total_issued_shares']}-{corpus['constants']['Singtel_treasury_shares']}={current['Singtel']['denominator_ex_treasury']}" in en_equations[-1]
    tests = json.loads((ROOT / "results/test_report.json").read_text())
    assert tests["successful"] and tests["tests_run"] == 48 and tests["failures"] == tests["errors"] == 0
    assert "48 research test methods" in en and "48 тестов исследовательского пакета" in ru
    manifest_path = ROOT / "release_manifest.json"
    assert manifest_path.exists(), "Missing release manifest"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for record in manifest["files"]:
            data = (ROOT / record["path"]).read_bytes()
            assert len(data) == record["size_bytes"] and hashlib.sha256(data).hexdigest() == record["sha256"], record["path"]
    print("Verified corpus, arithmetic, checkpoint, 520 corruption controls, bilingual equations, manuscript numbers, abstract and release hashes.")


if __name__ == "__main__":
    verify()
