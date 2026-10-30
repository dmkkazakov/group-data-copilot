"""Run the corpus through MCP, gate each assertion, checkpoint and recompute.

This deterministic replay is not an LLM extraction or live retrieval benchmark.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from engine import ROOT, compute, gate, load_corpus

def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
def save(path,obj):
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w") as f:
        json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
    tmp.replace(path)

def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    corpus=load_corpus();checksum=digest(corpus);checkpoint=output/"checkpoint.json"
    state={"corpus_hash":checksum,"completed":[],"accepted":[],"audit":[]}
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text())
        if state["corpus_hash"]!=checksum:raise ValueError("Checkpoint belongs to another corpus")
        previous="0"*64
        for e in state["audit"]:
            payload={k:v for k,v in e.items() if k!="hash"}
            if payload["previous"]!=previous or digest(payload)!=e["hash"]:raise ValueError("Audit chain mismatch")
            previous=e["hash"]
        expected=[c["id"] for c in corpus["claims"] if c["case"] in state["completed"]]
        if sorted(expected)!=sorted(state["accepted"]) or len(state["completed"])!=len(set(state["completed"])):raise ValueError("Checkpoint state mismatch")
        # Replay completed assertions too: a hash chain alone does not authenticate its author.
        for cid in state["accepted"]:
            e=next(c for c in corpus["claims"] if c["id"]==cid)
            if gate(e,e,e["valid_on"],e["known_on"]):raise ValueError("Invalid checkpoint assertion")
    transcript=[]
    proc=subprocess.Popen([sys.executable,str(ROOT/"server.py")],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    request_id=0
    def call(method,params=None,notification=False):
        nonlocal request_id
        request_id+=1;m={"jsonrpc":"2.0","method":method,"params":params or {}}
        if not notification:m["id"]=request_id
        proc.stdin.write(json.dumps(m)+"\n");proc.stdin.flush()
        if notification:return
        answer=json.loads(proc.stdout.readline())
        if answer.get("id")!=request_id or "error" in answer:raise ValueError(str(answer))
        transcript.append({"method":method,"response_sha256":digest(answer)})
        return answer["result"]
    try:
        init=call("initialize",{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"evidence-replay","version":"1.0.0"}})
        if init["protocolVersion"]!="2025-11-25":raise ValueError("Unsupported protocol")
        call("notifications/initialized",notification=True)
        names={t["name"] for t in call("tools/list")["tools"]}
        if names!={"case_list","case_get"}:raise ValueError("Unexpected tool surface")
        cases=call("tools/call",{"name":"case_list","arguments":{}})["structuredContent"]["cases"]
        evidence={c["id"]:c for c in corpus["claims"]}
        for case in cases:
            if case in state["completed"]:continue
            response=call("tools/call",{"name":"case_get","arguments":{"case":case}})
            if response.get("isError"):raise ValueError("Tool execution error")
            ids=[]
            for candidate in response["structuredContent"]["claims"]:
                e=evidence.get(candidate["id"])
                reasons=gate(candidate,e,candidate["valid_on"],"2026-10-30")
                if reasons:raise ValueError(str(reasons))
                ids.append(candidate["id"])
            if sorted(ids)!=sorted(c["id"] for c in corpus["claims"] if c["case"]==case):raise ValueError("Incomplete case")
            state["accepted"]+=ids;state["completed"].append(case)
            event={"case":case,"accepted_ids":ids,"previous":state["audit"][-1]["hash"] if state["audit"] else "0"*64}
            event["hash"]=digest(event);state["audit"].append(event);save(checkpoint,state)
        results=compute(corpus);results["corpus_sha256"] = checksum
        save(output/"results.json",results);save(output/"mcp_transcript_summary.json",transcript)
        return results
    finally:
        proc.stdin.close();proc.wait(timeout=5);proc.stdout.close()

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default=str(ROOT/"results"));args=p.parse_args()
    print(json.dumps(run(args.output),indent=2))
