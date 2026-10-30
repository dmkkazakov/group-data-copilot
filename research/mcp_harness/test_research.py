import copy
import json
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest
from engine import load_corpus, gate, compute, weighted_interest, path_product, cross_holding_2x2
from harness import run
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
    def test_direct_path(self):self.assertEqual(path_product([self.c["T04"],self.c["T05"]]),F(1))
    def test_disconnected_path_rejected(self):
        with self.assertRaises(ValueError):path_product([self.c["T05"],self.c["T04"]])
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

if __name__=="__main__":unittest.main(verbosity=2)
