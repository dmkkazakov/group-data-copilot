import copy
import json
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest
from engine import load_corpus, gate, compute, weighted_interest, path_product, cross_holding_2x2
from harness import run, digest, validate_inventory, validate_state
from engine import CLAIM_FIELDS, validate_corpus
from evaluate import evaluate, mutation
import sys
from server import Session

class ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=load_corpus();cls.c={c["id"]:c for c in cls.corpus["claims"]};cls.r=compute(cls.corpus)
    def check_mutation(self,cid,key,value,reason):
        c=copy.deepcopy(self.c[cid]);c[key]=value
        self.assertIn(reason,gate(c,self.c[cid],c["valid_on"],"2026-10-30"))
    def test_all_assertions_have_primary_provenance(self):
        for c in self.c.values():
            self.assertIn(c["source_id"],self.corpus["sources"]);self.assertTrue(c["locator"])
            self.assertEqual(gate(c,c,c["valid_on"],"2026-10-30"),[])
    def test_mts_exact_partition(self):self.assertEqual(self.r["MTS"]["sum_shares"],1998381575)
    def test_mts_double_count_exceeds_partition(self):self.assertEqual(F(self.r["MTS"]["naive_double_count_pct"]),F("111.03"))
    def test_mts_aggregate_not_direct(self):self.check_mutation("M01","basis","direct_equity","mismatch_basis")
    def test_hsbc_group_interest_not_direct(self):self.check_mutation("H03","basis","direct_equity","mismatch_basis")
    def test_hsbc_notice_not_period_end_snapshot(self):
        e=self.c["H04"];self.assertIn("snapshot_date_mismatch",gate(e,e,"2024-12-31","2026-10-30"))
    def test_berkshire_rounding_discrepancy_preserved(self):
        self.assertEqual(round(self.r["Berkshire"]["economic_pct"],1),14.3)
        self.assertEqual(self.r["Berkshire"]["reported_economic_pct"],"14.4")
        self.assertGreater(self.r["Berkshire"]["economic_difference_pp"],0.05)
        self.assertEqual(round(self.r["Berkshire"]["vote_pct"],1),30.4)
    def test_berkshire_votes_not_economic(self):self.assertGreater(self.r["Berkshire"]["vote_to_economic_ratio"],2)
    def test_empty_class_denominator_rejected(self):
        with self.assertRaises(ValueError):weighted_interest(0,0,0,0,1500)
    def test_impossible_class_count_rejected(self):
        with self.assertRaises(ValueError):weighted_interest(2,0,1,1,1500)
    def test_tencent_share_reconciliation(self):self.assertEqual(self.r["Tencent"]["Ma_total_shares"],804859700)
    def test_tencent_published_rounding(self):
        self.assertEqual(round(self.r["Tencent"]["Ma_pct"],2),8.72);self.assertEqual(round(self.r["Tencent"]["MIH_pct"],2),24.01)
    def test_tencent_vie_not_equity(self):self.check_mutation("T08","relation","interest_in","mismatch_relation")
    def test_missing_percentage_stays_missing(self):self.assertIsNone(self.r["Tencent"]["VIE_equity_percentage"])
    def test_singtel_direct_percentage(self):self.assertEqual(round(self.r["Singtel"]["direct_pct"],2),50.29)
    def test_singtel_deemed_not_direct(self):self.check_mutation("S02","basis","direct_equity","mismatch_basis")
    def test_singtel_june_cannot_backfill_march(self):
        e=self.c["S01"];self.assertIn("snapshot_date_mismatch",gate(e,e,"2025-03-31","2026-10-30"))
    def test_missing_evidence_rejected(self):self.assertEqual(gate(self.c["M01"],None,"2024-12-31","2026-10-30"),["missing_evidence"])
    def test_not_known_before_ingestion(self):
        e=self.c["M01"];self.assertIn("not_yet_known_to_corpus",gate(e,e,e["valid_on"],"2025-01-01"))
    def test_changed_entity_rejected(self):self.check_mutation("M11","object","Another MTS","mismatch_object")
    def test_changed_value_rejected(self):self.check_mutation("H03","value",{"reported_pct":"100"},"mismatch_value")
    def test_no_upgrade_to_confirmed_ubo(self):self.check_mutation("T01","status","confirmed_UBO","unsupported_promotion")
    def synthetic_path(self):
        return [{"subject":"A", "object":"B", "basis":"direct_equity", "valid_on":"2024-12-31", "value":{"reported_pct":"80"}},
                {"subject":"B", "object":"C", "basis":"direct_equity", "valid_on":"2024-12-31", "value":{"reported_pct":"25"}}]
    def test_direct_path(self):self.assertEqual(path_product(self.synthetic_path()),F(1,5))
    def test_disconnected_path_rejected(self):
        with self.assertRaises(ValueError):path_product(list(reversed(self.synthetic_path())))
    def test_cross_holding_solution_and_conservation(self):
        a=cross_holding_2x2(F(4,5),0,F(1,10),F(1,5));b=cross_holding_2x2(0,F(9,10),F(1,10),F(1,5))
        self.assertEqual(a,(F(40,49),F(4,49)));self.assertEqual(tuple(x+y for x,y in zip(a,b)),(1,1))
    def test_closed_cycle_rejected(self):
        with self.assertRaises(ValueError):cross_holding_2x2(0,0,1,1)
    def test_server_initialization_required(self):self.assertIn("error",Session().handle({"jsonrpc":"2.0","id":1,"method":"tools/list"}))
    def test_server_schema_rejects_arbitrary_url(self):
        s=Session();s.ready=True
        r=s.handle({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"case_get","arguments":{"case":"RU","url":"https://example.org"}}})
        self.assertIn("error",r)
    def test_end_to_end_mcp_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            a=run(d);b=run(d);self.assertEqual(a,b)
            state=json.loads((Path(d)/"checkpoint.json").read_text())
            self.assertEqual(len(state["accepted"]),40);self.assertEqual(len(state["audit"]),5)
    def test_changed_checkpoint_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            run(d);p=Path(d)/"checkpoint.json";s=json.loads(p.read_text());s["audit"][0]["case"]="changed";p.write_text(json.dumps(s))
            with self.assertRaises(ValueError):run(d)



    def test_every_field_corruption_rejected(self):
        for claim in self.c.values():
            for field in CLAIM_FIELDS:
                with self.subTest(claim=claim["id"], field=field):
                    self.assertTrue(gate(mutation(claim,field),claim,claim["valid_on"],claim["known_on"]))
    def test_mutation_controls_are_complete(self):
        r=evaluate(self.corpus)
        self.assertEqual((r["clean_accepted"],r["corrupted_controls"],r["corrupted_rejected"]),(40,520,520))
        self.assertEqual(sum(x["presence_baseline_accepted"] for x in r["by_field"]),520)
    def test_extra_and_missing_fields_rejected(self):
        for action in ("extra","missing"):
            c=copy.deepcopy(self.c["M01"])
            if action=="extra":c["invented"]=1
            else:del c["locator"]
            self.assertEqual(gate(c,self.c["M01"],"2024-12-31","2026-10-30"),["invalid_claim_schema"])
    def test_integer_and_float_values_not_identical(self):
        c=copy.deepcopy(self.c["M01"]);c["value"]["shares"]=float(c["value"]["shares"])
        self.assertIn("mismatch_value",gate(c,self.c["M01"],c["valid_on"],c["known_on"]))
    def test_invalid_calendar_date_rejected(self):
        c=self.c["M01"]
        self.assertIn("invalid_query_date",gate(c,c,"2024-02-30",c["known_on"]))
    def test_fractional_or_boolean_share_count_rejected(self):
        for count in (True,1.5):
            with self.assertRaises(ValueError):weighted_interest(count,0,5,5,1500)
    def test_duplicate_corpus_identifier_rejected(self):
        corpus=copy.deepcopy(self.corpus);corpus["claims"][1]["id"]=corpus["claims"][0]["id"]
        with self.assertRaises(ValueError):validate_corpus(corpus)
    def test_wholly_owned_is_not_a_direct_path(self):
        with self.assertRaises(ValueError):path_product([self.c["T04"],self.c["T05"]])
    def test_missing_or_duplicate_inventory_rejected(self):
        for cases in (["RU","UK","US","CN"],["RU","UK","US","CN","SG","SG"],["XX"]):
            with self.assertRaises(ValueError):validate_inventory(cases)
    def test_rehashed_checkpoint_must_match_state(self):
        with tempfile.TemporaryDirectory() as d:
            run(d);p=Path(d)/"checkpoint.json";s=json.loads(p.read_text())
            s["audit"][0]["accepted_ids"]=[]
            previous="0"*64
            for event in s["audit"]:
                event["previous"]=previous;event.pop("hash");event["hash"]=digest(event);previous=event["hash"]
            p.write_text(json.dumps(s))
            with self.assertRaises(ValueError):run(d)
    def test_unknown_completed_case_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            run(d);p=Path(d)/"checkpoint.json";s=json.loads(p.read_text());s["completed"].append("unknown");p.write_text(json.dumps(s))
            with self.assertRaises(ValueError):run(d)
    def test_resume_keeps_original_transcript(self):
        with tempfile.TemporaryDirectory() as d:
            run(d);run(d);log=json.loads((Path(d)/"mcp_transcript_summary.json").read_text())
            self.assertEqual([r["mode"] for r in log["runs"]],["full","resume"])
            self.assertEqual([len(r["responses"]) for r in log["runs"]],[8,3])
    def test_partial_checkpoint_resume(self):
        with tempfile.TemporaryDirectory() as d:
            expected=run(d);p=Path(d)/"checkpoint.json";s=json.loads(p.read_text())
            s["completed"]=s["completed"][:2];s["audit"]=s["audit"][:2]
            s["accepted"]=[i for e in s["audit"] for i in e["accepted_ids"]];p.write_text(json.dumps(s))
            self.assertEqual(run(d),expected)
    def test_hung_server_times_out(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(TimeoutError):run(d,timeout=0.05,server_command=[sys.executable,"-c","import time;time.sleep(1)"])
            self.assertFalse((Path(d)/"results.json").exists())
    def test_server_invalid_types_do_not_crash(self):
        session=Session();session.ready=True
        for params in ({"name":[]},{"name":"case_get","arguments":{"case":[]}}, {"name":"case_get","arguments":None}):
            result=session.handle({"jsonrpc":"2.0","id":1,"method":"tools/call","params":params})
            self.assertIn("error",result)
        self.assertIn("result",session.handle({"jsonrpc":"2.0","id":2,"method":"ping"}))
    def test_server_rejects_missing_method_and_bad_id(self):
        session=Session()
        for message in ({"jsonrpc":"2.0","id":1},{"jsonrpc":"2.0","id":True,"method":"ping"}):
            self.assertEqual(session.handle(message)["error"]["code"],-32600)
    def test_initialization_requires_protocol_and_client_fields(self):
        s=Session()
        self.assertIn("error",s.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{},"clientInfo":{}}}))

    def test_distinct_paths_can_share_a_prefix(self):
        def edge(a,b,p):
            return {"subject":a,"object":b,"basis":"direct_equity","valid_on":"2024-12-31","value":{"reported_pct":p}}
        ab=edge("A","B","100")
        paths=[[ab,edge("B","C","20")],[ab,edge("B","D","30"),edge("D","C","10")]]
        self.assertEqual(sum(path_product(p) for p in paths),F(23,100))

if __name__=="__main__":unittest.main(verbosity=2)
