# Group Data Dossier: Demo Industrial Group

## Executive summary

The agent identified **5 legal entities** and **5 ownership links**.
The current risk scan produced **3 high** and **1 medium** flags.

## Graph metrics

- Nodes: 5
- Edges: 5
- Weak components: 1
- Directed acyclic graph: True

## Entities

| Entity ID | Name | INN | Role | Sector |
|---|---|---|---|---|
| E001 | Demo Industrial Group Holding | 7700000001 | holding | diversified |
| E002 | Demo Machinery Plant | 7700000002 | operating | manufacturing |
| E003 | Demo Logistics | 7700000003 | service | transport |
| E004 | Demo Trading House | 7700000004 | trading | wholesale |
| E005 | Demo Finance SPV | 7700000005 | financing | financial services |

## Risk flags

| Severity | Entity ID | Flag | Explanation |
|---|---|---|---|
| medium | E001 | missing_financials | No financial records were provided for the entity. |
| high | E002 | revenue_concentration | Entity generates 54.5% of group revenue in 2025. |
| high | E004 | high_leverage | Debt / EBITDA exceeds 4.0x in 2025. |
| high | E005 | high_leverage | Debt / EBITDA exceeds 4.0x in 2025. |

## Analytical interpretation

This dossier is a first-pass analytical layer. It does not replace official due diligence, legal verification, sanction screening, financial statement analysis or credit committee materials.

Recommended next steps:

1. Validate legal entity perimeter against official registries.
2. Reconcile ownership links with shareholder disclosures.
3. Load audited IFRS / RAS financials.
4. Add payment-flow, supply-chain and contract-level data.
5. Run credit limit allocation and liquidity stress scenarios.