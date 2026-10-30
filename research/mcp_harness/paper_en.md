# Evidence Constrained Reconstruction of Corporate Groups with MCP and an Agent Harness

Dmitry Kazakov

Independent research · dmkkazakov@gmail.com

Working paper · 30 October 2026 · Version 1.0

## Abstract

Public corporate disclosures contain enough information to reconstruct useful parts of a business group, but they rarely describe ownership, voting power, management and consolidation in one consistent language. This paper develops a typed, dated evidence model and a bounded execution harness connected through the Model Context Protocol (MCP). A purposive study of MTS, HSBC, Berkshire Hathaway, Tencent and Singtel contributes a reproducible corpus of 40 assertions, five case reconstructions and executable arithmetic checks. The cases expose aggregate interests mistaken for direct holdings, different observation dates within one report, unequal share classes and contractual control without equivalent registered equity. Recalculation also leaves one numerical discrepancy open: Berkshire's disclosed share counts imply 14.348232% economic participation for Warren Buffett, while its table reports 14.4%. The released implementation preserves both values instead of silently reconciling them. Thirty software tests pass, including a real MCP subprocess exchange and checkpoint replay. These results establish reproducibility for a small curated corpus; they do not estimate the accuracy of autonomous extraction. Generative AI assisted source discovery, drafting, translation and code development. Numerical checks are reproducible in the accompanying repository.

Keywords: corporate ownership; public disclosures; evidence provenance; Model Context Protocol; agent harness; corporate governance

JEL classifications: G32, G34, C88

## 1 The problem begins with the meaning of a percentage

A corporate diagram can be precise to two decimal places and still be wrong. A group interest may be drawn as a direct shareholding. A nominee may become an ultimate owner. A newly appointed chief executive may be inserted into a historical snapshot. None of these errors requires a bad source. A good source read carelessly is sufficient.

Large language models make this problem easier to overlook because they produce fluent explanations of incompatible facts. Fluency is useful for finding and explaining evidence; it does not determine what a shareholding means. Confidence is a presentation style, not a share class.

The research question is therefore narrow: which structural and numerical errors can a transparent evidence model and a deterministic harness expose when reconstructing selected parts of corporate groups from public disclosures? The intended output is an inspectable collection of source assertions and qualified calculations. It is not a complete global ownership database or a legal determination of beneficial ownership.

The contribution has three parts. First, a claim schema separates direct equity, attributed interests, votes, management roles and contractual control. Second, a small MCP implementation makes the underlying evidence accessible to a reproducible harness. Third, five public cases show where ordinary arithmetic is valid and where it must stop. The matrix algebra is standard; the contribution lies in making its assumptions operational and showing the consequences on disclosed data.

## 2 Existing work and the role of MCP

Corporate network research already treats ownership as a graph and recognizes that cross-holdings complicate the propagation of economic interests and control [16]. This paper does not introduce a new theory of control. It addresses an earlier problem: how to avoid putting incompatible observations into the same graph.

The Beneficial Ownership Data Standard represents people, entities and relationships through statements [5]. W3C PROV provides a vocabulary for the origin and transformation of information [6]. GLEIF's Level 2 data concern accounting-consolidation parents, a useful but narrower relation than ultimate beneficial ownership [7]. These resources support a statement-based model with explicit provenance. They do not remove the need to interpret each disclosure.

MCP standardizes communication between a host and external capabilities, including discoverable tools and structured results [1–3]. It does not certify the truth of a tool response. A harness is the surrounding execution program: it chooses the next operation, stores progress, checks outputs and decides whether a result may be released. Work on long-running agents motivates persistent state and explicit completion criteria [4]. Here those ideas are applied to evidence handling.

The released example pins protocol revision 2025-11-25 for reproducibility. It is a deliberately small stdio implementation, not a claim to implement every optional MCP capability or the latest protocol revision. The collection phase used public web retrieval. The released MCP server replays the curated evidence corpus; it does not claim live access to corporate registries.

## 3 Research design and source collection

The sample comprises one group associated with each requested jurisdiction: Russia, the United Kingdom, the United States, China and Singapore. Selection was purposive. Each group publishes accessible reports and illustrates a different failure mode. Tencent is a China-based operating group whose listed parent is incorporated in the Cayman Islands. Operational geography and legal domicile are recorded separately.

The study uses financial years ending in 2024, except Singtel's year ending 31 March 2025. Shareholder and officer dates follow the individual disclosure, even when they fall after the financial year end. Retrieval occurred on 30 October 2026. These are retrospective reconstructions, not descriptions of the groups' current ownership or management.

Eight primary-source entries support 40 selected assertions. HSBC's SEC table and annual-report PDF are two representations of the same underlying report; they are not independent corroboration. In total the corpus represents seven underlying issuer documents. Claims were transcribed with AI assistance and checked against named sections or pages. They have not undergone independent double coding by human reviewers.

Collection followed a fixed sequence: locate the issuer's report or exchange filing; identify the legal entity and reporting date; read the relevant table together with its footnotes; separate source statements from calculations; then preserve unresolved questions. Search snippets were useful for discovery. For MTS's capital table, the issuer's indexed HTML text supplied the table and both footnotes when direct retrieval was unreliable. The release records this access limitation. The other four groups' PDFs were downloaded and read locally. Original issuer reports are linked rather than redistributed.

The case scope is intentionally partial. Each appendix contains selected shareholders, selected group relationships and named management roles. A missing intermediate company remains missing. The paper makes no claim to have reconstructed every subsidiary, trust, nominee or ultimate natural person behind these groups.

## 4 A claim is more than an edge

Let a source assertion be

$$c=(s,r,o,b,x,t_v,t_k,e). \tag{1}$$

Here s and o are identified subjects and objects; r is the relation; b is its semantic basis; x is a value or an explicit null; t_v is the date to which the assertion applies; t_k is the date it entered this corpus; and e identifies the source and locator. The released data also retain the claim identifier and its source_reported status. The public filing date is source metadata and must not be confused with t_k.

The graph has separate layers for registered or direct equity, attributed interests, votes, management, contractual control and accounting consolidation. An edge in one layer cannot silently migrate to another. In particular, an issuer's subsidiary list does not necessarily identify the immediate parent of each subsidiary. A person's registered interest in an operating company does not settle how that company's economic benefits are allocated under contracts.

For a snapshot-only corpus, eligibility is conservative:

$$A(c;t,\tau)=\mathbf{1}\{t_v=t\}\mathbf{1}\{t_k\leq\tau\}. \tag{2}$$

This rule refuses to carry a June observation back into March. It also refuses to treat silence after a dated observation as proof that nothing changed. A production system may store valid-time and knowledge-time intervals, but it must distinguish observed endpoints from assumed persistence. This release implements exact snapshots, not a full bitemporal database.

Entity matching is similarly conservative. Official identifiers should dominate names when available. Legal name, jurisdiction, address and issuer context can support a match; a shared director or a similar brand cannot establish identity. Corpus identifiers are internal anchors, not substitutes for registry numbers. Extending the dataset requires a documented entity-resolution decision before adding cross-document edges.

## 5 Mathematics with stated conditions

### 5.1 Direct and indirect economic participation

Let W be a non-negative ownership matrix, with W_ij the fraction of company j's compatible equity directly held by entity i. Rows identify owners; columns identify investees. A valid complete partition satisfies

$$0\leq W_{ij}\leq1,\qquad \sum_i W_{ij}\leq1. \tag{3}$$

The column constraint applies to non-overlapping direct holdings on the same date and denominator. Aggregated and deemed interests are excluded. A sum below one can represent an unobserved remainder; it is not evidence that the remainder has no owner. The MTS case demonstrates why an aggregate row and a subsidiary already included in it cannot be added again.

For a directed acyclic graph, a path contribution is the product of compatible edge weights. Summing disjoint ownership routes gives

$$u_{ij}=\sum_{p\in\mathcal{P}_{ij}}\prod_{(a,b)\in p}W_{ab},\qquad M=\sum_{k=1}^{n-1}W^k. \tag{4}$$

The formula assumes proportional economic rights, aligned dates and a correctly specified direct graph. It must not be applied to a mixture of direct and already aggregated holdings. It measures participation transmitted through the specified equity network. It is not a legal control test and does not identify an undisclosed beneficial owner.

### 5.2 Cross-holdings

Cycles require a different calculation. Let b be an outside investor's direct holdings across the internal companies. Under proportional economic rights and a spectral radius below one,

$$u=b+uW,\qquad u=b(I-W)^{-1},\qquad \rho(W)<1. \tag{5}$$

For an illustrative two-company system, X owns 10% of Y and Y owns 20% of X. Outside investor A owns the other 80% of X; investor B owns the other 90% of Y. Then

$$u_A=(40/49,4/49),\qquad u_B=(9/49,45/49). \tag{6}$$

Each column sums to one. This is a synthetic numerical example, not a finding about one of the five groups. The released solver handles this restricted two-company case and rejects a closed 100% cross-holding. It does not estimate a general control network. Contractual waterfalls, preferred rights and treasury-share rules would require a different model.

### 5.3 Economic rights and voting rights

For share classes k, let n_ik be investor i's shares, N_k outstanding shares, a_k economic weights and v_k voting weights. The two interests are

$$E_i=\frac{\sum_k a_kn_{ik}}{\sum_k a_kN_k},\qquad V_i=\frac{\sum_k v_kn_{ik}}{\sum_k v_kN_k}. \tag{7}$$

Berkshire supplies a concrete example. Using Class B units, Class A has economic weight 1,500 and voting weight 10,000 [12]. Applying the disclosed counts gives

$$E_B=\frac{1500(206359)+951}{1500(544953)+1339905639}=0.143482322\ldots \tag{8}$$

$$V_B=\frac{10000(206359)+951}{10000(544953)+1339905639}=0.303941455\ldots \tag{9}$$

The vote-to-economic ratio is approximately 2.118320. Equalizing the two layers would erase a material feature of the capital structure. The underlying table reports 30.4% votes and 14.4% economic interest. The former agrees with direct rounding; the latter requires a separate reconciliation discussed in Appendix C.

### 5.4 Rounding and incomplete information

If a percentage is conventionally rounded to d decimal places, a useful compatibility interval, in percentage points, is

$$I(q,d)=[q-0.5\cdot10^{-d},\ q+0.5\cdot10^{-d}). \tag{10}$$

Endpoint conventions depend on the stated rounding rule. This paper uses the interval as a diagnostic, not as proof of the issuer's rounding policy. Berkshire's computed 14.348232 lies just below the interval [14.35, 14.45) associated with 14.4 at one decimal place. The difference is 0.051768 percentage points. The release retains an unresolved discrepancy without asserting that the issuer is wrong or inventing an explanation.

For an acyclic network of non-negative edge intervals, compatible path products are monotone. A simple bound is

$$\sum_p\prod_{e\in p}\ell_e\leq u_{ij}\leq\sum_p\prod_{e\in p}h_e. \tag{11}$$

Joint constraints can tighten these bounds. Unknown routes can invalidate an apparent upper bound, so a complete network boundary is necessary. An undisclosed percentage is stored as null. Replacing it with zero would turn absence of evidence into evidence of absence.

## 6 From source assertions to a released result

The released server exposes only case_list and case_get. The client performs an initialize handshake, declares readiness, discovers the tool schema and requests each case through newline-delimited JSON-RPC over stdio [17]. The harness compares returned assertions with the frozen corpus, checks their dates and semantic fields, then writes a checkpoint after each completed case.

This exact comparison is intentionally modest. It detects corrupted replay and prohibited transformations. It does not independently verify whether the initial transcription is true. The five case calculations provide additional arithmetic checks, while a reviewer can inspect the linked primary sources. Neither a schema validator nor a passing unit test can take over the reviewer's job.

The decision rule is conjunctive:

$$G(c)=g_{source}g_{identity}g_{relation}g_{basis}g_{value}g_{time}g_{status}. \tag{12}$$

Each implemented gate is binary. A failed gate rejects the proposed assertion. Source-reported and calculated values remain separate. A source can legitimately be quoted as reporting 14.4% while the calculation is separately marked unreconciled. The system must not label the combined result confirmed merely because the citation exists.

Checkpoint files contain the corpus digest, completed cases, accepted claim identifiers and a chained event record:

$$h_j=H(h_{j-1}\Vert\operatorname{canonical}(event_j)). \tag{13}$$

The implementation hashes a canonical JSON payload containing the preceding digest. This detects accidental changes in the tested workflow. It is not an independently signed or tamper-proof audit trail: an attacker who can rewrite the complete file can recompute the chain. The corpus checksum similarly identifies bytes; it does not certify factual accuracy.

For future autonomous retrieval, the harness would also need request budgets, timeouts, rate limits, source-origin deduplication and controls against instructions embedded in retrieved text [3]. Those features are design requirements, not results demonstrated by this offline corpus server. Public documents remain data; their contents do not authorize shell commands or changes to tool permissions.

## 7 Results and what the tests establish

Table 1 summarizes the five reconstructions. The appendices provide the numerical inputs, management observations and source locators.

| Case | Main observable result | Transformation refused |
|---|---|---|
| MTS | Six capital-table rows sum to 1,998,381,575 shares | Adding an included 11.03% block again |
| HSBC | Selected Hang Seng group interest is 63.12% | Calling the group interest a direct parent edge |
| Berkshire | 14.348232% calculated economics and 30.394146% votes | Equating votes with economics or hiding the 14.4% disclosure |
| Tencent | 804,859,700 shares reconcile to 8.724847% | Turning contractual control into registered equity |
| Singtel | Treasury-adjusted denominator reproduces 50.29% | Treating June shareholders as a March snapshot |

All 30 test methods pass. They cover the public arithmetic, changed values and entities, date mismatches, incompatible relation types, missing evidence, share-class denominators, a synthetic cross-holding calculation, initialization requirements, rejected tool arguments, subprocess communication and checkpoint replay. Forty unmodified source assertions pass the replay gates. These are acceptance and regression checks over a constructed corpus, not 40 independently adjudicated predictions.

There is no model comparison, held-out extraction set or measured retrieval recall. Consequently, this study reports no extraction-accuracy percentage, latency advantage or reduction in analyst hours. A useful next evaluation would separate discovery, extraction, entity resolution and interpretation, with independent annotation and a locked test split.

For such an evaluation, report both precision and the fraction of questions answered:

$$P=\frac{TP}{TP+FP},\qquad C=\frac{N_{answered}}{N_{eligible}}. \tag{14}$$

Increasing precision by refusing every difficult case would make C uninformative unless both measures are shown. A practical decision policy should also expose the relative cost of a false ownership assertion and an abstention:

$$L=\lambda_{FP}FP+\lambda_{FN}FN+\lambda_A N_{abstain}. \tag{15}$$

The loss weights depend on the intended use and are not estimated here. Counting citations is not a replacement for this evaluation. Three copies of one announcement are one source with a larger entourage.

## 8 Limitations and implications

The sample favors large listed groups with comparatively rich disclosure. Private groups, multilingual registries, historic company-name changes and inaccessible filings may be substantially harder. The selected graphs omit many subsidiaries and owners. No group-wide completeness rate can be inferred from this release.

The study also separates registered holdings from economic participation and legal control without resolving every jurisdiction's beneficial-ownership rules. The treatment of Singtel's deemed interests and Tencent's contractual arrangements is intentionally descriptive. The paper records what the selected disclosures say; it does not offer a current legal opinion.

The central result is operational: a useful corporate reconstruction must preserve the meaning and date of every edge before it multiplies percentages. MCP supplies the transport. The harness supplies repeatable checks. Public evidence supplies the claims, and unresolved discrepancies remain visible. A polished diagram is the last step, not the standard of proof.

## Data and software availability

The reproducibility package is available at https://github.com/dmkkazakov/group-data-copilot/tree/main/research/mcp_harness. It includes the normalized corpus, provenance, exact arithmetic, MCP server, harness, tests, recorded results and editable manuscript sources. Python 3.10 or later is sufficient for the research calculations. Document generation has separately listed dependencies. Source reports remain at their issuer or exchange URLs. The English PDF is the SSRN submission version; the Russian manuscript is a companion version of the same study.

## AI assistance disclosure

Generative AI assisted source discovery, transcription, drafting, translation and code development. The release contains source locators and executable checks so that readers can inspect the work. No independent human double-coding exercise, peer review or external validation is claimed.

<!-- pagebreak -->

## Appendix A Russia and the MTS group

The capital snapshot is 31 December 2024. The management observation is the issuer's announcement of 20 December 2024. MTS PJSC is the Russian listed parent used as the case anchor, with ticker MTSS. The selected capital rows are reproduced as normalized facts, not as a complete register of beneficial owners [8].

| Reported category | Ordinary shares | Reported capital share |
|---|---|---|
| Sistema PJSFC including its subsidiary | 841,019,563 | 42.09% |
| MGTS PJSC | 5,452,327 | 0.27% |
| MTS Ecosystem LLC | 111,145,664 | 5.56% |
| Bastion LLC | 2,348,947 | 0.12% |
| MTS PJSC own shares | 38,645,191 | 1.93% |
| Free circulation | 999,769,883 | 50.03% |
| Total | 1,998,381,575 | 100.00% |

Footnote 1 places Sistema Telecom Assets LLC's 11.03% inside the 42.09% aggregate. Footnote 2 identifies MGTS, MTS Ecosystem and Bastion as MTS subsidiaries. The source does not specify the directness or percentage of each downward subsidiary edge in that table. Those fields therefore remain unspecified.

The calculation reproduces the total exactly. A deliberately wrong procedure that adds 11.03% as a seventh independent block returns 111.03%. That is a double count, not exceptional shareholder productivity. The own-share and subsidiary-held rows also warn against treating the capital table as an unadjusted voting-power table.

The December announcement names Inessa Galaktionova as General Director and Vyacheslav Nikolaev as Chairman. It also discusses the planned structure around Ecosystem MTS [9]. Announced future organizational steps are not coded as completed transactions merely because they appear in the same paragraph as an appointment.

To verify: open [8], read the table headed with 31 December 2024 and both footnotes; add the six integer counts. Then open [9] and inspect the appointment paragraphs. Corpus identifiers are M01–M12. The result is a limited, dated reconstruction of selected capital and management relationships.

<!-- pagebreak -->

## Appendix B Britain and the HSBC group

HSBC Holdings plc is the British parent. The selected subsidiary table applies to 31 December 2024. Its first footnote explicitly allows direct or indirect holdings [10].

| Relationship reported by the group | Value | Correct interpretation |
|---|---|---|
| HSBC Bank plc | 100% | Group interest |
| HSBC UK Bank plc | 100% | Group interest |
| Hang Seng Bank Limited | 63.12% | Selected strategic group holding |
| BlackRock long position | 8.99% | Position on 19 December 2024 |
| Ping An Asset Management long position | 7.98% | Position on 7 May 2024 |

The two shareholder rows come from the Hong Kong statutory-interest discussion in the annual report, not from a complete economic-ownership register. Their notification dates are 24 December and 10 May respectively. The report also contains older UK notifications and later January 2025 information. These observations must not be merged into a single undated list [11].

The 63.12% Hang Seng row is not an instruction to add a direct edge from HSBC Holdings plc. The table separately discusses trading-book holdings and different notification dates. This release retains the selected strategic group figure with its basis rather than inventing an immediate-parent chain or a combined percentage.

For management, the report identifies Mark Tucker as Group Chairman and Georges Elhedery as Group CEO; the latter assumed the CEO role on 2 September 2024 [11]. These roles are distinct from ownership claims. An officer biography does not establish a controlling shareholding.

To verify: inspect Note 19's main-subsidiary table and footnotes in [10], then printed pages 237, 305 and 320 of [11]. The PDF page numbers are two higher. Corpus identifiers are H01–H07. The refusal to infer the immediate parent is an explicit result, not an unfinished calculation.

<!-- pagebreak -->

## Appendix C The United States and Berkshire Hathaway

The group relationships come from the 2024 annual report. The shareholder calculation uses the proxy's record date of 5 March 2025. The dates are kept separate [12,13].

| Input | Class A | Class B |
|---|---|---|
| Outstanding and entitled to vote | 544,953 | 1,339,905,639 |
| Warren Buffett beneficial holdings | 206,359 | 951 |
| Economic weight in Class B units | 1,500 | 1 |
| Voting weight in Class B units | 10,000 | 1 |

Equations 8 and 9 reproduce 14.348232% economic participation and 30.394146% voting power. The proxy reports 14.4% and 30.4%. The 0.051768 percentage-point economic difference is retained as an open reconciliation issue. Direct rounding to one decimal place gives 14.3%. The selected source does not explain the difference, so the paper does not attribute it to an error, a hidden adjustment or a particular rounding sequence.

This is a useful distinction between two valid statements: the issuer reports one figure, and a specified calculation from the reported inputs yields another. A system that overwrites either value has made the evidence harder to inspect. A passing test here means that the discrepancy remains visible, not that it has been resolved.

The annual report states that Berkshire Hathaway Energy became wholly owned during 2024 and that Pilot Travel Centers became an indirect wholly owned subsidiary. It lists Warren Buffett as Chairman and CEO and Gregory Abel as Vice Chairman for Non-Insurance Operations [13]. These are historical report observations, not a claim about the current leadership in October 2026. BHE's directness is not inferred from the phrase wholly owned.

To verify: read printed pages 1 and 11 of [12] and recompute both fractions. In [13], inspect K-19, K-80 and the inside back cover. Corpus identifiers are B01–B05. The open issue is included in results.json as economic_reconciliation.

<!-- pagebreak -->

## Appendix D China and the Tencent group

The ownership snapshot is 31 December 2024. Tencent Holdings Limited is incorporated in the Cayman Islands and has its group head office in Shenzhen. This is a China operating-group case, not a claim that the listed parent is incorporated in mainland China [14].

| Selected observation | Value | Basis |
|---|---|---|
| Ma Huateng attributed Tencent interest | 804,859,700 shares | Corporate interest |
| Advance Data Services direct holding | 709,859,700 shares | Direct shares |
| Ma Huateng Global Foundation holding | 95,000,000 shares | Through the ADS subsidiary |
| MIH Internet Holdings disclosed block | 2,214,863,800 shares | Same block attributed up its control chain |
| Ma's Tencent Computer registered equity | 54.29% | Different legal entity and rights |

The two components of Ma's listed-company interest sum exactly to 804,859,700. Dividing by 9,224,914,953 issued shares gives 8.724847%, consistent with the reported 8.72%. The MIH block similarly gives 24.009585%, consistent with 24.01%. The report attributes that same block to MIH, Prosus and Naspers. Adding those three attributions would count the same shares three times.

The report describes Structure Contracts governing the relevant operating companies. Contractual control is therefore a separate relation from registered equity. Ma's 54.29% in Tencent Computer cannot be substituted for his 8.72% attributed interest in the listed parent, and the contractual relation cannot be assigned a fabricated 100% equity weight.

The report's biographies identify Ma Huateng as Chairman and CEO and Lau Chi Ping Martin as President. These are report-date observations. To verify the case, inspect printed pages 2, 60, 63, 67–69, 71, 76 and 114 of [14]; PDF pages are one higher. Corpus identifiers are T01–T10. The unresolved field is the equity percentage of the contractual-control edge, which remains null.

<!-- pagebreak -->

## Appendix E Singapore and the Singtel group

Singtel's financial year ends on 31 March 2025, its shareholder table is dated 2 June, and its corporate-information section is dated 8 June. All three dates occur in one annual report [15].

| Observation | Value | Date |
|---|---|---|
| NCS group effective equity | 100% | 31 March 2025 |
| Singtel Optus group effective equity | 100% | 31 March 2025 |
| Temasek direct shares | 8,304,071,181 | 2 June 2025 |
| Temasek deemed shares | 277,171,369 | 2 June 2025 |
| Total issued shares | 16,514,634,755 | 2 June 2025 |
| Treasury shares | 2,059,079 | 2 June 2025 |

The shareholder-table footnote excludes treasury shares from the percentage denominator. The reproducible denominator is therefore

$$D=16514634755-2059079=16512575676. \tag{16}$$

Temasek's direct block divided by D gives 50.289375%, reproducing the disclosed 50.29%. The deemed block corresponds to 1.678547% on the same denominator. The arithmetic sum is 51.967923%; it is a sum of disclosed direct and deemed interests, not an independently established cash-flow ownership percentage. The report says the deemed interest arises through subsidiaries and associated companies. Their underlying fractions are not reconstructed here.

The management section identifies Lee Theng Kiat as Chairman and Yuen Kuan Moon as Group CEO as of 8 June. The selected NCS and Optus figures are group effective interests; immediate-parent chains are not inferred from the table heading.

To verify: inspect Note 46, printed pages 227 and 230, then pages 270–272 of [15]. PDF page numbers are two higher. Corpus identifiers are S01–S06. A request for a strict 31 March shareholder snapshot must abstain on the June observations instead of quietly borrowing them from the future.

<!-- pagebreak -->

## References

[1] Model Context Protocol. Architecture. Specification revision 2025-11-25. https://modelcontextprotocol.io/specification/2025-11-25/architecture

[2] Model Context Protocol. Tools. Specification revision 2025-11-25. https://modelcontextprotocol.io/specification/2025-11-25/server/tools

[3] Model Context Protocol. Security Best Practices. https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices

[4] Anthropic. Effective harnesses for long-running agents. 26 November 2025. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

[5] Open Ownership. Beneficial Ownership Data Standard 0.4. Data model. https://standard.openownership.org/en/latest/primer/datamodel.html

[6] W3C. PROV-O The PROV Ontology. Recommendation, 30 April 2013. https://www.w3.org/TR/prov-o/

[7] GLEIF. Level 2 Data Who Owns Whom. https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom

[8] MTS. Annual Report 2024. Capital and Securities, shareholder table and footnotes. https://ar2024.mts.ru/en/corporate-governance/capital-and-securities/

[9] MTS. Corporate restructuring announcement. 20 December 2024. https://nao.mts.ru/about/media-centr/soobshheniya-kompanii/novosti-mts-v-rossii-i-mire/2024-12-20/mts-prodolzhaet-transformaciyu-korporativnoj-struktury

[10] HSBC Holdings plc. Annual Report 2024, Note 19, SEC HTML table. https://www.sec.gov/Archives/edgar/data/1089113/000108911325000040/R98.htm

[11] HSBC Holdings plc. Annual Report and Accounts 2024. Published 19 February 2025. https://www.about.hsbc.com.hk/-/media/hong-kong/en/investor-relations/annual-results-2024/250219-annual-report-and-accounts-2024-en.pdf?sc_lang=en-GB

[12] Berkshire Hathaway Inc. Proxy Statement 2025. 14 March 2025, pp. 1 and 11. https://www.berkshirehathaway.com/meet01/2025proxystatement.pdf

[13] Berkshire Hathaway Inc. Annual Report 2024. K-19, K-80 and officers. https://www.berkshirehathaway.com/2024ar/2024ar.pdf

[14] Tencent Holdings Limited. Annual Report 2024. https://static.www.tencent.com/uploads/2025/04/08/1132b72b565389d1b913aea60a648d73.pdf

[15] Singapore Telecommunications Limited. Annual Report 2025. SGX filing of 30 June 2025. https://links.sgx.com/1.0.0/corporate-announcements/45HXB745U21ORPFV/850270_Singtel%20Annual%20Report%202025.pdf

[16] Vitali, S., Glattfelder, J. B., and Battiston, S. 2011. The Network of Global Corporate Control. PLOS ONE 6(10), e25995. https://doi.org/10.1371/journal.pone.0025995

[17] Model Context Protocol. Transports. Specification revision 2025-11-25. https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

Web sources accessed on 30 October 2026. The cited report years and individual observation dates govern the historical case results.
