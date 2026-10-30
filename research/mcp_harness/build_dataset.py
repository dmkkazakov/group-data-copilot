"""Recreate the normalized, manually curated evidence corpus. No web scraping."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "MTS_CAP": {"title": "MTS Annual Report 2024 — Capital and Securities", "url": "https://ar2024.mts.ru/en/corporate-governance/capital-and-securities/", "locator": "Shareholder Capital; table at 31 December 2024; footnotes 1 and 2", "published": None},
    "MTS_NEWS": {"title": "MTS corporate restructuring announcement", "url": "https://nao.mts.ru/about/media-centr/soobshheniya-kompanii/novosti-mts-v-rossii-i-mire/2024-12-20/mts-prodolzhaet-transformaciyu-korporativnoj-struktury", "locator": "20 December 2024; paragraphs on appointments and Ecosystem MTS", "published": "2024-12-20"},
    "HSBC_SUB": {"title": "HSBC 2024 Annual Report — Note 19", "url": "https://www.sec.gov/Archives/edgar/data/1089113/000108911325000040/R98.htm", "locator": "Main subsidiaries; footnotes 1–3", "published": None},
    "HSBC_AR": {"title": "HSBC Holdings plc Annual Report and Accounts 2024", "url": "https://www.about.hsbc.com.hk/-/media/hong-kong/en/investor-relations/annual-results-2024/250219-annual-report-and-accounts-2024-en.pdf?sc_lang=en-GB", "locator": "printed pp. 237–238, 305, 320; PDF pages are printed pages + 2", "published": "2025-02-19"},
    "BRK_PROXY": {"title": "Berkshire Hathaway 2025 Proxy Statement", "url": "https://www.berkshirehathaway.com/meet01/2025proxystatement.pdf", "locator": "printed pp. 1 and 11 (PDF pp. 3 and 13); share counts and beneficial ownership at 5 March 2025", "published": "2025-03-14"},
    "BRK_AR": {"title": "Berkshire Hathaway 2024 Annual Report", "url": "https://www.berkshirehathaway.com/2024ar/2024ar.pdf", "locator": "K-19 (Pilot), K-80 (BHE), inside back cover (officers)", "published": "2025-02-22"},
    "TENCENT_AR": {"title": "Tencent Holdings Limited Annual Report 2024", "url": "https://static.www.tencent.com/uploads/2025/04/08/1132b72b565389d1b913aea60a648d73.pdf", "locator": "printed pp. 2, 60, 63, 67–69, 71, 76, 114; PDF pages = printed + 1", "published": "2025-04-08"},
    "SINGTEL_AR": {"title": "Singapore Telecommunications Limited Annual Report 2025", "url": "https://links.sgx.com/1.0.0/corporate-announcements/45HXB745U21ORPFV/850270_Singtel%20Annual%20Report%202025.pdf", "locator": "printed pp. 227, 230, 270–272; PDF pages = printed + 2", "published": "2025-06-30"}
}
for source in SOURCES.values():
    source["retrieved"] = "2026-10-30"
    source["origin"] = source["title"].split(" — ")[0]
SOURCES["HSBC_SUB"]["origin"] = SOURCES["HSBC_AR"]["origin"] = "HSBC annual report 2024"
SOURCES["MTS_CAP"]["access_note"] = "Official indexed HTML table and footnotes inspected; direct retrieval returned 502/503. No original byte hash claimed."

claims = []
def claim(cid, case, subject, relation, obj, value, basis, date, source, locator=None):
    claims.append(dict(id=cid, case=case, subject=subject, relation=relation, object=obj,
        value=value, basis=basis, valid_on=date, known_on="2026-10-30", source_id=source,
        locator=locator or SOURCES[source]["locator"], status="source_reported"))

for cid, name, count, pct, basis in [
    ("M01", "Sistema PJSFC", 841019563, "42.09", "aggregate_including_subsidiary"),
    ("M02", "MGTS PJSC", 5452327, "0.27", "reported_holder"),
    ("M03", "MTS Ecosystem LLC", 111145664, "5.56", "reported_holder"),
    ("M04", "Bastion LLC", 2348947, "0.12", "reported_holder"),
    ("M05", "MTS PJSC", 38645191, "1.93", "own_shares"),
    ("M06", "Free circulation", 999769883, "50.03", "residual_category")]:
    claim(cid,"RU",name,"interest_in","MTS PJSC",{"shares":count,"reported_pct":pct},basis,"2024-12-31","MTS_CAP")
claim("M07","RU","Sistema Telecom Assets LLC","interest_in","MTS PJSC",{"reported_pct":"11.03"},"included_in_M01","2024-12-31","MTS_CAP")
for cid, sub in [("M08","MGTS PJSC"),("M09","MTS Ecosystem LLC"),("M10","Bastion LLC")]:
    claim(cid,"RU","MTS PJSC","subsidiary",sub,None,"directness_and_percentage_unspecified","2024-12-31","MTS_CAP")
claim("M11","RU","Inessa Galaktionova","management_role","MTS PJSC","General Director","appointment_reported","2024-12-20","MTS_NEWS")
claim("M12","RU","Vyacheslav Nikolaev","management_role","MTS PJSC","Chairman of the Board","role_reported","2024-12-20","MTS_NEWS")

for cid, sub, pct in [("H01","HSBC Bank plc","100"),("H02","HSBC UK Bank plc","100"),("H03","Hang Seng Bank Limited","63.12")]:
    claim(cid,"UK","HSBC Holdings plc group","interest_in",sub,{"reported_pct":pct},"group_interest_direct_or_indirect","2024-12-31","HSBC_SUB")
claim("H04","UK","BlackRock Inc.","interest_in","HSBC Holdings plc",{"shares":1615527141,"reported_pct":"8.99"},"SFO_long_position","2024-12-19","HSBC_AR","printed p. 320; notice on 24 December 2024")
claim("H05","UK","Ping An Asset Management Co. Ltd.","interest_in","HSBC Holdings plc",{"shares":1502584731,"reported_pct":"7.98"},"SFO_long_position","2024-05-07","HSBC_AR","printed p. 320; notice on 10 May 2024")
claim("H06","UK","Georges Elhedery","management_role","HSBC Holdings plc","Group CEO","role_at_period_end","2024-12-31","HSBC_AR","printed p. 305; CEO from 2 September 2024")
claim("H07","UK","Mark Tucker","management_role","HSBC Holdings plc","Group Chairman","role_at_period_end","2024-12-31","HSBC_AR","printed p. 237")

claim("B01","US","Warren Buffett","interest_in","Berkshire Hathaway Inc.",{"class_A":206359,"class_B":951,"economic_pct":"14.4","vote_pct":"30.4"},"class_weighted_beneficial_interest","2025-03-05","BRK_PROXY")
for cid, sub, basis in [("B02","Berkshire Hathaway Energy Company","wholly_owned_directness_unspecified"),("B03","Pilot Travel Centers LLC","indirect_wholly_owned")]:
    claim(cid,"US","Berkshire Hathaway Inc.","interest_in",sub,{"reported_pct":"100"},basis,"2024-12-31","BRK_AR")
claim("B04","US","Warren Buffett","management_role","Berkshire Hathaway Inc.","Chairman and CEO","report_officer_list","2025-02-22","BRK_AR")
claim("B05","US","Gregory Abel","management_role","Berkshire Hathaway Inc.","Vice Chairman Non-Insurance Operations","report_officer_list","2025-02-22","BRK_AR")

claim("T01","CN","Ma Huateng","interest_in","Tencent Holdings Limited",{"shares":804859700,"reported_pct":"8.72"},"corporate_attributed_interest","2024-12-31","TENCENT_AR","printed pp. 67–68")
claim("T02","CN","Advance Data Services Limited","interest_in","Tencent Holdings Limited",{"shares":709859700},"direct_shares","2024-12-31","TENCENT_AR","printed p. 68 note 1")
claim("T03","CN","Ma Huateng Global Foundation","interest_in","Tencent Holdings Limited",{"shares":95000000},"direct_shares","2024-12-31","TENCENT_AR","printed p. 68 note 1")
claim("T04","CN","Ma Huateng","interest_in","Advance Data Services Limited",{"reported_pct":"100"},"wholly_owned_directness_unspecified","2024-12-31","TENCENT_AR","printed p. 68 note 1")
claim("T05","CN","Advance Data Services Limited","interest_in","Ma Huateng Global Foundation",{"reported_pct":"100"},"wholly_owned_directness_unspecified","2024-12-31","TENCENT_AR","printed p. 68 note 1")
claim("T06","CN","MIH Internet Holdings B.V.","interest_in","Tencent Holdings Limited",{"shares":2214863800,"reported_pct":"24.01"},"corporate_long_position","2024-12-31","TENCENT_AR","printed p. 76; same block attributed to Prosus and Naspers")
claim("T07","CN","Ma Huateng","interest_in","Shenzhen Tencent Computer Systems Company Limited",{"reported_pct":"54.29"},"registered_equity","2024-12-31","TENCENT_AR","printed pp. 69 and 71; Tencent Computer")
claim("T08","CN","Tencent group","contractual_control","Shenzhen Tencent Computer Systems Company Limited",None,"structure_contracts","2024-12-31","TENCENT_AR","printed pp. 69–72; no inferred equity percentage")
claim("T09","CN","Ma Huateng","management_role","Tencent Holdings Limited","Chairman and CEO","annual_report_biography","2025-04-08","TENCENT_AR","printed p. 60")
claim("T10","CN","Lau Chi Ping Martin","management_role","Tencent Holdings Limited","President","annual_report_biography","2025-04-08","TENCENT_AR","printed p. 63")

claim("S01","SG","Temasek Holdings (Private) Limited","interest_in","Singapore Telecommunications Limited",{"shares":8304071181,"reported_pct":"50.29"},"direct_interest_ex_treasury_denominator","2025-06-02","SINGTEL_AR","printed p. 270")
claim("S02","SG","Temasek Holdings (Private) Limited","interest_in","Singapore Telecommunications Limited",{"shares":277171369},"deemed_interest_not_cashflow_weight","2025-06-02","SINGTEL_AR","printed p. 270; deemed through subsidiaries and associates")
for cid, sub, loc in [("S03","NCS Pte. Ltd.","printed p. 227 note 46.1"),("S04","Singtel Optus Pty Limited","printed p. 230 note 46.2")]:
    claim(cid,"SG","Singtel group","interest_in",sub,{"reported_pct":"100"},"group_effective_equity","2025-03-31","SINGTEL_AR",loc)
claim("S05","SG","Lee Theng Kiat","management_role","Singapore Telecommunications Limited","Chairman","corporate_information_snapshot","2025-06-08","SINGTEL_AR","printed p. 272; section dated 8 June 2025")
claim("S06","SG","Yuen Kuan Moon","management_role","Singapore Telecommunications Limited","Group CEO","corporate_information_snapshot","2025-06-08","SINGTEL_AR","printed p. 272; section dated 8 June 2025")

for c in claims:
    c["date_basis"] = ("report_observation" if c["id"] in {"B04", "B05", "T09", "T10"}
                       else "announcement_observation" if c["id"] in {"M11", "M12"}
                       else "explicit_snapshot")

corpus = {"schema_version":"1.1.0","curation":"AI-assisted manual transcription from public primary sources; not an automated extraction benchmark", "sources":SOURCES,"claims":claims,
 "constants": {"MTS_total_shares":1998381575,"Berkshire_A_outstanding":544953,"Berkshire_B_outstanding":1339905639,"Berkshire_A_economic_weight":1500,"Berkshire_A_vote_weight":10000,"Tencent_total_shares":9224914953,"Singtel_total_issued_shares":16514634755,"Singtel_treasury_shares":2059079},
 "constant_evidence": {"MTS_total_shares":"MTS_CAP","Berkshire_A_outstanding":"BRK_PROXY p. 1","Berkshire_B_outstanding":"BRK_PROXY p. 1","Berkshire_A_economic_weight":"BRK_PROXY p. 11; class conversion basis","Berkshire_A_vote_weight":"BRK_PROXY p. 1","Tencent_total_shares":"TENCENT_AR p. 68 note 7","Singtel_total_issued_shares":"SINGTEL_AR p. 271; denominator excludes treasury under p. 270 note 1","Singtel_treasury_shares":"SINGTEL_AR pp. 270–271"}}

def main():
    target=ROOT/"data";target.mkdir(exist_ok=True)
    raw=(json.dumps(corpus,ensure_ascii=False,indent=2)+"\n").encode()
    (target/"cases.json").write_bytes(raw)
    (target/"cases.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  cases.json\n")
    print(f"{len(claims)} claims; {len(SOURCES)} sources")
if __name__ == "__main__":main()
