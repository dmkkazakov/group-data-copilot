import math
from pathlib import Path
import pytest
from pydantic import ValidationError
from group_data_copilot.agent import GroupDataCopilot
from group_data_copilot.connectors import LocalDataConnector
from group_data_copilot.models import Entity, FinancialRecord, GroupProfile, OwnershipEdge
from group_data_copilot.analytics import financial_summary, revenue_concentration, detect_risk_flags
from group_data_copilot.graph import graph_edges_dataframe


def profile(**kw):
    values=dict(group_name="Test",entities=[Entity(entity_id="A",name="A"),Entity(entity_id="B",name="B")],
                ownership=[],financials=[],risk_flags=[])
    values.update(kw)
    return GroupProfile(**values)


def test_missing_metrics_remain_null():
    f=FinancialRecord(entity_id="A",year=2024)
    assert f.debt is None and f.cash is None
    summary=financial_summary([f])
    assert math.isnan(summary.loc[0,"debt"])


def test_partial_revenue_is_not_a_total():
    rows=[FinancialRecord(entity_id="A",year=2024,revenue=10),FinancialRecord(entity_id="B",year=2024)]
    assert math.isnan(financial_summary(rows).loc[0,"revenue"])
    assert revenue_concentration(rows).revenue_share.isna().all()


def test_zero_revenue_has_no_percentage():
    rows=[FinancialRecord(entity_id="A",year=2024,revenue=0)]
    assert revenue_concentration(rows).revenue_share.isna().all()


def test_negative_ebitda_is_not_a_negative_leverage_ratio():
    rows=[FinancialRecord(entity_id="A",year=2024,ebitda=-1,debt=10)]
    assert math.isnan(financial_summary(rows).loc[0,"debt_to_ebitda"])
    assert "nonpositive_ebitda" in {f.flag for f in detect_risk_flags([Entity(entity_id="A",name="A")],rows)}


def test_stale_record_is_flagged_in_latest_year():
    rows=[FinancialRecord(entity_id="A",year=2023),FinancialRecord(entity_id="B",year=2024)]
    flags=detect_risk_flags([Entity(entity_id="A",name="A"),Entity(entity_id="B",name="B")],rows)
    assert any(f.entity_id=="A" and f.flag=="missing_financials" for f in flags)


def test_identifiers_keep_leading_zeroes_and_blanks_are_null(tmp_path):
    (tmp_path/"entities.csv").write_text("entity_id,name,inn,sector\n001,Example,0012345678,\n",encoding="utf-8")
    e=LocalDataConnector(tmp_path).load_entities()[0]
    assert (e.entity_id,e.inn,e.sector)==("001","0012345678",None)


def test_missing_input_directory_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):LocalDataConnector(tmp_path/"absent")


def test_missing_entity_file_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):GroupDataCopilot("X",tmp_path).run(tmp_path/"out")


def test_duplicate_entity_rejected():
    with pytest.raises(ValidationError):profile(entities=[Entity(entity_id="A",name="A")]*2)


def test_unknown_edge_endpoint_rejected():
    with pytest.raises(ValidationError):profile(ownership=[OwnershipEdge(parent_id="A",child_id="Z",share=1)])


def test_duplicate_ownership_rejected():
    edge=OwnershipEdge(parent_id="A",child_id="B",share=.5)
    with pytest.raises(ValidationError):profile(ownership=[edge,edge])


def test_ownership_sum_above_one_rejected():
    with pytest.raises(ValidationError):profile(ownership=[OwnershipEdge(parent_id="A",child_id="B",share=.8),OwnershipEdge(parent_id="B",child_id="B",share=.3)])


def test_duplicate_entity_year_rejected():
    row=FinancialRecord(entity_id="A",year=2024,revenue=10)
    with pytest.raises(ValidationError):profile(financials=[row,row])


def test_unknown_financial_entity_rejected():
    with pytest.raises(ValidationError):profile(financials=[FinancialRecord(entity_id="Z",year=2024)])


def test_nonfinite_financial_value_rejected():
    for value in (float("nan"),float("inf")):
        with pytest.raises(ValidationError):FinancialRecord(entity_id="A",year=2024,debt=value)


def test_empty_ownership_csv_has_headers():
    assert list(graph_edges_dataframe([]).columns)==["parent_id","child_id","share"]
