"""Small read-only MCP stdio server pinned to protocol revision 2025-11-25."""
import json
import sys
from engine import CASES, load_corpus

VERSION = "2025-11-25"
TOOLS = [
    {"name": "case_list", "description": "List the five historical case identifiers.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "case_get", "description": "Read normalized source assertions and provenance for a case.",
     "inputSchema": {"type": "object", "properties": {"case": {"type": "string", "enum": list(CASES)}},
                     "required": ["case"], "additionalProperties": False}},
]


class Session:
    def __init__(self):
        self.ready = False
        self.initialized = False
        self.corpus = load_corpus()

    def handle(self, message):
        if (not isinstance(message, dict) or message.get("jsonrpc") != "2.0"
                or not isinstance(message.get("method"), str)
                or ("id" in message and type(message["id"]) not in (str, int))):
            return {"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32600, "message": "Invalid Request"}}
        request_id = message.get("id")
        method = message["method"]
        params = message.get("params", {})

        def result(value):
            return {"jsonrpc": "2.0", "id": request_id, "result": value}

        def error(code, description):
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": code, "message": description}}

        if "id" not in message:
            if method == "notifications/initialized" and self.initialized and isinstance(params, dict):
                self.ready = True
            return None
        if not isinstance(params, dict):
            return error(-32602, "Invalid params")
        if method == "initialize":
            client = params.get("clientInfo")
            if (self.initialized or not isinstance(params.get("protocolVersion"), str)
                    or not isinstance(params.get("capabilities"), dict)
                    or not isinstance(client, dict)
                    or any(not isinstance(client.get(k), str) or not client[k] for k in ("name", "version"))):
                return error(-32602, "Invalid initialization")
            self.initialized = True
            return result({"protocolVersion": VERSION, "capabilities": {"tools": {"listChanged": False}},
                           "serverInfo": {"name": "corporate-evidence-corpus", "version": "1.1.0"}})
        if method == "ping":
            return result({})
        if not self.ready:
            return error(-32000, "Initialization required")
        if method == "tools/list":
            return result({"tools": TOOLS})
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(name, str) or name not in {t["name"] for t in TOOLS}:
                return error(-32602, "Unknown tool")
            if not isinstance(arguments, dict):
                return error(-32602, "Invalid arguments")
            if name == "case_list":
                if arguments:
                    return error(-32602, "No arguments accepted")
                output = {"cases": list(CASES)}
            else:
                if (set(arguments) != {"case"} or not isinstance(arguments["case"], str)
                        or arguments["case"] not in CASES):
                    return error(-32602, "Invalid case")
                claims = [c for c in self.corpus["claims"] if c["case"] == arguments["case"]]
                source_ids = {c["source_id"] for c in claims}
                output = {"claims": claims, "sources": {k: v for k, v in self.corpus["sources"].items() if k in source_ids}}
            return result({"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}],
                           "structuredContent": output, "isError": False})
        return error(-32601, "Method not found")


def main():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    session = Session()
    for line in sys.stdin:
        try:
            response = session.handle(json.loads(line))
        except json.JSONDecodeError:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
