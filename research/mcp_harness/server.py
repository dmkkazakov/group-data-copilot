"""Minimal read-only MCP stdio server for the released evidence corpus.

Implements initialize, ping, tools/list and tools/call, protocol 2025-11-25.
No network access, shell tools, authentication, sampling or registry connector.
"""
import json
import sys
from engine import load_corpus

VERSION="2025-11-25"
TOOLS=[
 {"name":"case_list","description":"List the five historical case identifiers.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
 {"name":"case_get","description":"Read normalized source assertions and provenance for a case.","inputSchema":{"type":"object","properties":{"case":{"type":"string","enum":["RU","UK","US","CN","SG"]}},"required":["case"],"additionalProperties":False}}
]

class Session:
    def __init__(self):self.ready=False;self.initialized=False;self.corpus=load_corpus()
    def handle(self,m):
        if not isinstance(m,dict) or m.get("jsonrpc")!="2.0":
            return {"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid Request"}}
        request_id=m.get("id");method=m.get("method");p=m.get("params",{})
        def result(v):return {"jsonrpc":"2.0","id":request_id,"result":v}
        def error(code,msg):return {"jsonrpc":"2.0","id":request_id,"error":{"code":code,"message":msg}}
        if method=="notifications/initialized":
            if self.initialized:self.ready=True
            return None
        if "id" not in m:return None
        if not isinstance(p,dict):return error(-32602,"Invalid params")
        if method=="initialize":
            if not isinstance(p.get("clientInfo"),dict) or not isinstance(p.get("capabilities"),dict):return error(-32602,"Missing client fields")
            self.initialized=True
            return result({"protocolVersion":VERSION,"capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"corporate-evidence-corpus","version":"1.0.0"}})
        if method=="ping":return result({})
        if not self.ready:return error(-32000,"Initialization required")
        if method=="tools/list":return result({"tools":TOOLS})
        if method=="tools/call":
            name=p.get("name");args=p.get("arguments",{})
            if name not in {t["name"] for t in TOOLS}:return error(-32602,"Unknown tool")
            if not isinstance(args,dict):return error(-32602,"Invalid arguments")
            if name=="case_list":
                if args:return error(-32602,"No arguments accepted")
                out={"cases":["RU","UK","US","CN","SG"]}
            else:
                if set(args)!={"case"} or args["case"] not in {"RU","UK","US","CN","SG"}:return error(-32602,"Invalid case")
                claims=[c for c in self.corpus["claims"] if c["case"]==args["case"]]
                out={"claims":claims,"sources":{k:v for k,v in self.corpus["sources"].items() if k in {c["source_id"] for c in claims}}}
            return result({"content":[{"type":"text","text":json.dumps(out,ensure_ascii=False)}],"structuredContent":out,"isError":False})
        return error(-32601,"Method not found")

def main():
    session=Session()
    for line in sys.stdin:
        try:
            request=json.loads(line);response=session.handle(request)
        except json.JSONDecodeError:
            response={"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":"Parse error"}}
        if response is not None:print(json.dumps(response,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
