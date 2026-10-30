"""Evidence gates and exact arithmetic. These gates do not establish source truth."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load_corpus():
    raw=(ROOT/"data/cases.json").read_bytes()
    expected=(ROOT/"data/cases.sha256").read_text().split()[0]
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError("Corpus checksum mismatch")
    return json.loads(raw)

def gate(candidate, evidence, valid_on, known_on):
    """Accept only an exact source assertion at its explicit snapshot date."""
    reasons=[]
    if not evidence: return ["missing_evidence"]
    if candidate.get("source_id")!=evidence.get("source_id"):reasons.append("source_mismatch")
    for key in ("subject","relation","object","basis","value"):
        if candidate.get(key)!=evidence.get(key):reasons.append("mismatch_"+key)
    if evidence["valid_on"]!=valid_on:reasons.append("snapshot_date_mismatch")
    if evidence["known_on"]>known_on:reasons.append("not_yet_known_to_corpus")
    if candidate.get("status")!="source_reported":reasons.append("unsupported_promotion")
    return reasons

def weighted_interest(a,b,total_a,total_b,a_weight):
    if min(a,b,total_a,total_b)<0 or a>total_a or b>total_b or a_weight<=0:
        raise ValueError("Invalid class counts")
    den=total_a*a_weight+total_b
    if not den:raise ValueError("Empty denominator")
    return F(a*a_weight+b,den)

def path_product(edges):
    """Only compatible dated direct equity edges can be multiplied."""
    if not edges:raise ValueError("Empty path")
    date=edges[0]["valid_on"];p=F(1);seen={edges[0]["subject"]}
    for i,e in enumerate(edges):
        if e["basis"]!="direct_equity" or e["valid_on"]!=date:raise ValueError("Incompatible edge")
        if i and edges[i-1]["object"]!=e["subject"]:raise ValueError("Disconnected path")
        if e["object"] in seen:raise ValueError("Cycle requires separate model")
        seen.add(e["object"])
        w=F(e["value"]["reported_pct"])/100
        if not 0<=w<=1:raise ValueError("Invalid equity weight")
        p*=w
    return p

def cross_holding_2x2(a,b,x,y):
    """Outside stake (a,b); X owns x of Y; Y owns y of X. Restricted model."""
    a,b,x,y=map(F,(a,b,x,y))
    if any(v<0 or v>1 for v in (a,b,x,y)) or a+y>1 or b+x>1:
        raise ValueError("Infeasible ownership")
    if x*y>=1:raise ValueError("No unique solution")
    return ((a+b*y)/(1-x*y),(b+a*x)/(1-x*y))

def percent(x):return round(float(x*100),6)

def compute(corpus):
    c={x["id"]:x for x in corpus["claims"]};k=corpus["constants"]
    sg_den=k["Singtel_total_issued_shares"]-k["Singtel_treasury_shares"]
    br=c["B01"]["value"]
    economic=weighted_interest(br["class_A"],br["class_B"],k["Berkshire_A_outstanding"],k["Berkshire_B_outstanding"],1500)
    voting=weighted_interest(br["class_A"],br["class_B"],k["Berkshire_A_outstanding"],k["Berkshire_B_outstanding"],10000)
    return {
      "claims":len(c),"sources":len(corpus["sources"]),"cases":len({x["case"] for x in c.values()}),
      "MTS":{"sum_shares":sum(c[f"M{i:02}"]["value"]["shares"] for i in range(1,7)),"total_shares":k["MTS_total_shares"],"rounded_sum_pct":str(sum(F(c[f"M{i:02}"]["value"]["reported_pct"]) for i in range(1,7))),"naive_double_count_pct":str(F(100)+F(c["M07"]["value"]["reported_pct"]))},
      "HSBC":{"group_Hang_Seng_pct":c["H03"]["value"]["reported_pct"],"direct_parent_identified_by_selected_table":False,"shareholder_snapshot_dates":[c["H04"]["valid_on"],c["H05"]["valid_on"]]},
      "Berkshire":{"economic_pct":percent(economic),"vote_pct":percent(voting),"reported_economic_pct":br["economic_pct"],"economic_reconciliation":"unresolved_outside_direct_one_decimal_rounding_interval","economic_difference_pp":round(float(F(br["economic_pct"])-100*economic),6),"vote_to_economic_ratio":round(float(voting/economic),6),"economic_fraction":str(economic),"vote_fraction":str(voting)},
      "Tencent":{"Ma_total_shares":c["T02"]["value"]["shares"]+c["T03"]["value"]["shares"],"Ma_pct":percent(F(c["T01"]["value"]["shares"],k["Tencent_total_shares"])),"MIH_pct":percent(F(c["T06"]["value"]["shares"],k["Tencent_total_shares"])),"registered_OPCO_pct":c["T07"]["value"]["reported_pct"],"VIE_equity_percentage":None},
      "Singtel":{"denominator_ex_treasury":sg_den,"direct_pct":percent(F(c["S01"]["value"]["shares"],sg_den)),"deemed_pct":percent(F(c["S02"]["value"]["shares"],sg_den)),"direct_plus_deemed_disclosure_pct":percent(F(c["S01"]["value"]["shares"]+c["S02"]["value"]["shares"],sg_den)),"dates":["2025-03-31","2025-06-02","2025-06-08"]},
      "synthetic_cycle":{"outside_A":[str(v) for v in cross_holding_2x2(F(4,5),0,F(1,10),F(1,5))],"outside_B":[str(v) for v in cross_holding_2x2(0,F(9,10),F(1,10),F(1,5))]}}

if __name__=="__main__":print(json.dumps(compute(load_corpus()),indent=2))
