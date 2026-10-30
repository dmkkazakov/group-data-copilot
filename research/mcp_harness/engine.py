"""Typed evidence gates and exact arithmetic; replay is not source verification."""
import hashlib
import json
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLAIM_FIELDS = ("id", "case", "subject", "relation", "object", "basis", "value",
                "valid_on", "known_on", "date_basis", "source_id", "locator", "status")
CASES = ("RU", "UK", "US", "CN", "SG")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def iso_date(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError("Expected an ISO calendar date")
    return value


def validate_corpus(corpus):
    ids = set()
    for c in corpus["claims"]:
        if set(c) != set(CLAIM_FIELDS) or c["id"] in ids:
            raise ValueError("Duplicate or malformed claim")
        ids.add(c["id"])
        if c["case"] not in CASES or c["source_id"] not in corpus["sources"]:
            raise ValueError("Unknown case or source")
        if c["date_basis"] not in {"explicit_snapshot", "announcement_observation", "report_observation"}:
            raise ValueError("Unknown date basis")
        if c["status"] != "source_reported" or not c["locator"]:
            raise ValueError("Missing provenance or invalid status")
        iso_date(c["valid_on"]); iso_date(c["known_on"])
        canonical(c)
    if {c["case"] for c in corpus["claims"]} != set(CASES):
        raise ValueError("Incomplete case inventory")
    if set(corpus["constants"]) != set(corpus["constant_evidence"]):
        raise ValueError("Missing constant provenance")
    return corpus


def load_corpus():
    raw = (ROOT / "data/cases.json").read_bytes()
    expected = (ROOT / "data/cases.sha256").read_text(encoding="utf-8").split()[0]
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("Corpus checksum mismatch")
    return validate_corpus(json.loads(raw))


def gate(candidate, evidence, valid_on, known_on):
    """Exact typed comparison, plus explicit valid-time and knowledge-time gates."""
    if not evidence:
        return ["missing_evidence"]
    if not isinstance(candidate, dict) or set(candidate) != set(CLAIM_FIELDS):
        return ["invalid_claim_schema"]
    reasons = []
    for key in CLAIM_FIELDS:
        try:
            same = canonical(candidate[key]) == canonical(evidence[key])
        except (TypeError, ValueError):
            same = False
        if not same:
            reasons.append("source_mismatch" if key == "source_id" else "mismatch_" + key)
    try:
        iso_date(valid_on); iso_date(known_on)
        if evidence["valid_on"] != valid_on:
            reasons.append("snapshot_date_mismatch")
        if evidence["known_on"] > known_on:
            reasons.append("not_yet_known_to_corpus")
    except (TypeError, ValueError):
        reasons.append("invalid_query_date")
    if candidate["status"] != "source_reported":
        reasons.append("unsupported_promotion")
    return reasons


def weighted_interest(a, b, total_a, total_b, a_weight):
    if any(type(v) is not int for v in (a, b, total_a, total_b, a_weight)):
        raise ValueError("Share counts and this class weight must be integers")
    if min(a, b, total_a, total_b) < 0 or a > total_a or b > total_b or a_weight <= 0:
        raise ValueError("Invalid class counts")
    den = total_a * a_weight + total_b
    if not den:
        raise ValueError("Empty denominator")
    return F(a * a_weight + b, den)


def path_product(edges):
    """Multiply only compatible dated direct equity edges in a simple path."""
    if not edges:
        raise ValueError("Empty path")
    snapshot = iso_date(edges[0]["valid_on"])
    product = F(1)
    seen = {edges[0]["subject"]}
    for i, edge in enumerate(edges):
        if edge["basis"] != "direct_equity" or edge["valid_on"] != snapshot:
            raise ValueError("Incompatible edge")
        if i and edges[i - 1]["object"] != edge["subject"]:
            raise ValueError("Disconnected path")
        if edge["object"] in seen:
            raise ValueError("Cycle requires separate model")
        seen.add(edge["object"])
        weight = F(edge["value"]["reported_pct"]) / 100
        if not 0 <= weight <= 1:
            raise ValueError("Invalid equity weight")
        product *= weight
    return product


def cross_holding_2x2(a, b, x, y):
    """Outside stakes (a,b); X owns x of Y; Y owns y of X. Restricted model."""
    a, b, x, y = map(F, (a, b, x, y))
    if any(v < 0 or v > 1 for v in (a, b, x, y)) or a + y > 1 or b + x > 1:
        raise ValueError("Infeasible ownership")
    if x * y >= 1:
        raise ValueError("No unique solution")
    return ((a + b * y) / (1 - x * y), (b + a * x) / (1 - x * y))


def percent(value):
    """Six-place display value; calculations retain exact rational fractions."""
    with localcontext() as ctx:
        ctx.prec = 40
        return float((Decimal(value.numerator) * 100 / Decimal(value.denominator))
                     .quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))

def compute(corpus):
    c={x["id"]:x for x in corpus["claims"]};k=corpus["constants"]
    sg_den=k["Singtel_total_issued_shares"]-k["Singtel_treasury_shares"]
    br=c["B01"]["value"]
    economic=weighted_interest(br["class_A"],br["class_B"],k["Berkshire_A_outstanding"],k["Berkshire_B_outstanding"],k["Berkshire_A_economic_weight"])
    voting=weighted_interest(br["class_A"],br["class_B"],k["Berkshire_A_outstanding"],k["Berkshire_B_outstanding"],k["Berkshire_A_vote_weight"])
    return {
      "claims":len(c),"sources":len(corpus["sources"]),"cases":len({x["case"] for x in c.values()}),
      "MTS":{"sum_shares":sum(c[f"M{i:02}"]["value"]["shares"] for i in range(1,7)),"total_shares":k["MTS_total_shares"],"rounded_sum_pct":str(sum(F(c[f"M{i:02}"]["value"]["reported_pct"]) for i in range(1,7))),"naive_double_count_pct":str(F(100)+F(c["M07"]["value"]["reported_pct"]))},
      "HSBC":{"group_Hang_Seng_pct":c["H03"]["value"]["reported_pct"],"direct_parent_identified_by_selected_table":False,"shareholder_snapshot_dates":[c["H04"]["valid_on"],c["H05"]["valid_on"]]},
      "Berkshire":{"economic_pct":percent(economic),"vote_pct":percent(voting),"reported_economic_pct":br["economic_pct"],"economic_reconciliation":"unresolved_outside_direct_one_decimal_rounding_interval","economic_difference_pp":round(float(F(br["economic_pct"])-100*economic),6),"vote_to_economic_ratio":round(float(voting/economic),6),"economic_fraction":str(economic),"vote_fraction":str(voting)},
      "Tencent":{"Ma_total_shares":c["T02"]["value"]["shares"]+c["T03"]["value"]["shares"],"Ma_pct":percent(F(c["T01"]["value"]["shares"],k["Tencent_total_shares"])),"MIH_pct":percent(F(c["T06"]["value"]["shares"],k["Tencent_total_shares"])),"registered_OPCO_pct":c["T07"]["value"]["reported_pct"],"VIE_equity_percentage":None},
      "Singtel":{"denominator_ex_treasury":sg_den,"direct_pct":percent(F(c["S01"]["value"]["shares"],sg_den)),"deemed_pct":percent(F(c["S02"]["value"]["shares"],sg_den)),"direct_plus_deemed_disclosure_pct":percent(F(c["S01"]["value"]["shares"]+c["S02"]["value"]["shares"],sg_den)),"dates":["2025-03-31","2025-06-02","2025-06-08"]},
      "synthetic_cycle":{"outside_A":[str(v) for v in cross_holding_2x2(F(4,5),0,F(1,10),F(1,5))],"outside_B":[str(v) for v in cross_holding_2x2(0,F(9,10),F(1,10),F(1,5))]}}

if __name__=="__main__":print(json.dumps(compute(load_corpus()),indent=2))
