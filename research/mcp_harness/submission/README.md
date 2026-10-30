# SSRN publication package

Paper version 1.3, 30 October 2026. This package is prepared for submission; it has not been submitted to SSRN.

1. Upload [Corporate_Groups_SSRN_EN.pdf](../artifacts/Corporate_Groups_SSRN_EN.pdf).
2. Follow [SSRN_GUIDE_RU.docx](SSRN_GUIDE_RU.docx).
3. Copy the title, abstract, keywords and JEL codes from files 01–04. Add each keyword and JEL code separately in the form.
4. Use files 05–07 for AI disclosure, ethics and data availability where appropriate.
5. Files 08–09 are **conditional drafts**. Use their English statement only if true; omit the instruction line. The author must confirm funding and competing interests, upload rights and license selection, and set the confirmed NEIMARK University affiliation in the SSRN profile.

Content Format: **Paper**. Content Type: **Preprint**. Language: **English**. Date: **2026-10-30**.

The author is Dmitry Kazakov; contact: dmkkazakov@gmail.com. The author has confirmed the affiliation NEIMARK University, Nizhny Novgorod, Russia; it appears in both manuscripts and abstracts. ORCID, SSRN ID and DOI have not been invented. No journal acceptance or peer review is claimed.

[fields.json](fields.json) is the machine-readable counterpart. [CITATION.bib](CITATION.bib) is a provisional working-paper citation. Add the actual SSRN permalink and DOI after posting.

The PDF contains all five case appendices. The Russian paper is a companion translation. Do not upload the ZIP, this instruction document, or the Russian translation as the principal English submission.

The corpus, calculations and research code are unchanged from version 1.1. That baseline passed [GitHub Actions](https://github.com/dmkkazakov/group-data-copilot/actions/runs/41121713624). Version 1.3 updates the confirmed author affiliation throughout the publication materials. All original source-access and numerical limitations remain in the paper.

Policy sources checked 30 October 2026:

- https://www.elsevier.support/ssrn/answer/get-started
- https://www.elsevier.support/ssrn/answer/AI
- https://www.elsevier.support/ssrn/answer/cc-licensing
- https://supportcontent.elsevier.com/Support%20Hub/SSRN/SSRN_NewSubmissionForm.pdf

Rebuild the distributable archive from the repository root:

```bash
python3 research/mcp_harness/package_submission.py --output /tmp/SSRN_Submission_Package.zip
```
