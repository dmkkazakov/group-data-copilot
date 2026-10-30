"""Bounded MCP replay with complete-case checks and validated checkpoints.

The evidence is a curated corpus, not an LLM extraction benchmark.
One writer per output directory is supported.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
from engine import ROOT, CASES, canonical, compute, gate, load_corpus


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def save(path, obj):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def validate_state(state, corpus, checksum):
    if not isinstance(state, dict) or set(state) != {"corpus_hash", "completed", "accepted", "audit"}:
        raise ValueError("Checkpoint schema mismatch")
    if state["corpus_hash"] != checksum:
        raise ValueError("Checkpoint belongs to another corpus")
    completed = state["completed"]
    if not isinstance(completed, list) or completed != list(CASES[:len(completed)]):
        raise ValueError("Checkpoint case order mismatch")
    expected_ids = []
    expected_audit = []
    previous = "0" * 64
    for case in completed:
        ids = [c["id"] for c in corpus["claims"] if c["case"] == case]
        expected_ids.extend(ids)
        event = {"case": case, "accepted_ids": ids, "previous": previous}
        event["hash"] = digest(event)
        previous = event["hash"]
        expected_audit.append(event)
    if state["accepted"] != expected_ids or state["audit"] != expected_audit:
        raise ValueError("Checkpoint state or audit mismatch")


def validate_inventory(cases):
    if not isinstance(cases, list) or cases != list(CASES):
        raise ValueError("Incomplete, reordered or duplicate case inventory")


def run(output, timeout=10.0, server_command=None):
    if timeout <= 0:
        raise ValueError("Timeout must be positive")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    corpus = load_corpus()
    checksum = digest(corpus)
    checkpoint = output / "checkpoint.json"
    state = {"corpus_hash": checksum, "completed": [], "accepted": [], "audit": []}
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
        validate_state(state, corpus, checksum)
    mode = "resume" if state["completed"] else "full"
    transcript = []
    proc = subprocess.Popen(server_command or [sys.executable, str(ROOT / "server.py")],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True, encoding="utf-8")
    responses = queue.Queue()

    def read_responses():
        while True:
            line = proc.stdout.readline(2_000_001)
            responses.put(line)
            if not line or len(line) > 2_000_000:
                return

    reader = threading.Thread(target=read_responses, daemon=True)
    reader.start()
    request_id = 0

    def call(method, params=None, notification=False):
        nonlocal request_id
        request_id += 1
        message = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if not notification:
            message["id"] = request_id
        proc.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        proc.stdin.flush()
        if notification:
            return None
        try:
            line = responses.get(timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError("MCP response deadline exceeded") from exc
        if not line or len(line) > 2_000_000:
            raise ValueError("Missing or oversized MCP response")
        answer = json.loads(line)
        if (not isinstance(answer, dict) or answer.get("jsonrpc") != "2.0"
                or type(answer.get("id")) is not int or answer["id"] != request_id
                or "error" in answer or "result" not in answer):
            raise ValueError("Invalid MCP response envelope")
        result = answer["result"]
        if not isinstance(result, dict) or result.get("isError"):
            raise ValueError("MCP tool execution failed")
        transcript.append({"method": method, "response_sha256": digest(answer)})
        return result

    try:
        init = call("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                    "clientInfo": {"name": "evidence-replay", "version": "1.1.0"}})
        if init.get("protocolVersion") != "2025-11-25":
            raise ValueError("Unsupported protocol")
        call("notifications/initialized", notification=True)
        tools = call("tools/list").get("tools", [])
        if sorted(t.get("name", "") for t in tools) != ["case_get", "case_list"]:
            raise ValueError("Unexpected tool surface")
        cases = call("tools/call", {"name": "case_list", "arguments": {}})["structuredContent"]["cases"]
        validate_inventory(cases)
        evidence = {c["id"]: c for c in corpus["claims"]}
        for case in cases:
            if case in state["completed"]:
                continue
            response = call("tools/call", {"name": "case_get", "arguments": {"case": case}})
            payload = response["structuredContent"]
            expected_claims = [c for c in corpus["claims"] if c["case"] == case]
            source_ids = {c["source_id"] for c in expected_claims}
            if payload.get("sources") != {k: corpus["sources"][k] for k in source_ids}:
                raise ValueError("Changed source metadata")
            candidates = payload.get("claims")
            if not isinstance(candidates, list):
                raise ValueError("Missing claims")
            ids = []
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    raise ValueError("Invalid claim")
                original = evidence.get(candidate.get("id"))
                reasons = gate(candidate, original, candidate.get("valid_on"), max(c["known_on"] for c in corpus["claims"]))
                if reasons:
                    raise ValueError(str(reasons))
                ids.append(candidate["id"])
            if ids != [c["id"] for c in expected_claims]:
                raise ValueError("Incomplete, reordered or duplicate case assertions")
            state["accepted"].extend(ids)
            state["completed"].append(case)
            event = {"case": case, "accepted_ids": ids,
                     "previous": state["audit"][-1]["hash"] if state["audit"] else "0" * 64}
            event["hash"] = digest(event)
            state["audit"].append(event)
            save(checkpoint, state)
        validate_state(state, corpus, checksum)
        if state["completed"] != list(CASES):
            raise ValueError("Not all cases completed")
        results = compute(corpus)
        results["corpus_sha256"] = checksum
        save(output / "results.json", results)
        log = output / "mcp_transcript_summary.json"
        history = json.loads(log.read_text(encoding="utf-8")) if log.exists() else {"runs": []}
        history["runs"].append({"mode": mode, "corpus_sha256": checksum, "responses": transcript})
        save(log, history)
        return results
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=min(timeout, 2.0))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
        reader.join(timeout=2)
        proc.stdout.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "results_local"))
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    print(json.dumps(run(args.output, timeout=args.timeout), indent=2))
