"""Deterministic corruption controls; not extraction accuracy or independent truth."""
import argparse
import copy
import json
from pathlib import Path
from engine import CLAIM_FIELDS, load_corpus, gate
from harness import digest, save


def mutation(claim, field):
    candidate = copy.deepcopy(claim)
    if field in ("valid_on", "known_on"):
        candidate[field] = "1900-01-01"
    elif field == "value":
        candidate[field] = {"changed": True}
    else:
        candidate[field] = str(candidate[field]) + "_changed"
    return candidate


def evaluate(corpus=None):
    corpus = corpus or load_corpus()
    rows = []
    clean_accepted = sum(not gate(c, c, c["valid_on"], c["known_on"]) for c in corpus["claims"])
    for field in CLAIM_FIELDS:
        rejected = 0
        baseline_accepted = 0
        for original in corpus["claims"]:
            candidate = mutation(original, field)
            # Weak baseline: a populated source field is treated as sufficient.
            baseline_accepted += bool(candidate.get("source_id"))
            rejected += bool(gate(candidate, original, original["valid_on"], original["known_on"]))
        rows.append({"mutated_field": field, "trials": len(corpus["claims"]),
                     "presence_baseline_accepted": baseline_accepted, "full_gate_rejected": rejected})
    return {"design": "One deliberate field corruption per assertion; deterministic controls, not held-out predictions",
            "corpus_sha256": digest(corpus), "clean_controls": len(corpus["claims"]),
            "clean_accepted": clean_accepted, "corrupted_controls": sum(r["trials"] for r in rows),
            "corrupted_rejected": sum(r["full_gate_rejected"] for r in rows), "by_field": rows,
            "interpretation": "Checks exact replay integrity only. Cannot detect an error shared by reference and candidate; no extraction accuracy estimate."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results_local/mutation_results.json")
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    result = evaluate()
    save(path, result)
    print(json.dumps(result, indent=2))
