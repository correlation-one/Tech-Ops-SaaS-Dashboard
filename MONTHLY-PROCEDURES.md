# Monthly build runbook — Tech Ops SaaS Dashboard (v3 · Aug 2026)

## What changed in v3
- **Classification source of truth:** the *SaaS COGS / Non-COGS Classification Review – 2026 YTD* Google Sheet, **Final Classification** column. Never GL account coding, never the finance sheet, never the old classification tab. Apps missing from the review sheet ship with a GL-account default **and a visible flag** until a row is added.
- Full history (Jan 2026 onward) was rebuilt on this classification in Aug 2026, verified against the GL to the cent.
- Active app list is pruned by the **10-month rule**: no spend in the trailing 10 months → removed from the list (recomputed every build; see `dropped` in data.json).
- Pipeline: `build.py` runs `parse_gl.py → classify.py → assemble.py`, then a **regression gate** that freezes history.

## Monthly steps
1. **Get the data.** Export finance's "Software Spend" workbook as xlsx (Drive `download_file_content` with `exportMimeType: xlsx`) and save to `inputs/software_spend.xlsx`. Never use the markdown/`read_file_content` path — it backslash-escapes negatives, misaligns blank cells, and truncates large tabs silently.
2. **Register the new month.**
   - `parse_gl.py`: add the tab to `TABS`, e.g. `'Aug 26 Spend': ('2026','Aug')` (copy the tab name exactly — casing drifts).
   - `classify.py` and `assemble.py`: append the month key to `MONTHS`.
3. **Run** `python3 build.py`.
4. **Unresolved vendors?** The build prints them and refuses to pass silently. Add `["REGEX","App Name"]` pairs to `naming-map.json` — first match wins, so specific patterns go before generic ones. Re-run.
5. **New flags?** Those apps aren't in the review sheet. Get a Final Classification row added, then mirror it in `REVIEW` (classify.py) and `REVIEW_DEPT` (assemble.py). Until then they ship flagged with the account default (53000/55000 → COGS, else Non-COGS).
6. **Regression gate must pass.** History is frozen to the cent in `EXPECTED` (build.py). If a past month moves, finance restated the GL — investigate, document in data.json notes, then update `EXPECTED` deliberately. Never paper over it.
7. **Smoke-check locally:** `python3 -m http.server` and open index.html (data.json loads via fetch, so file:// won't work). Check KPIs, month tabs, movers, table, flags panel.
8. **Ship:** commit and push from the local clone (SSH from the sandbox is blocked). GitHub Pages caches data.json — hard refresh to verify.

## Dashboard design & data.json schema
The dashboard is the ORIGINAL leadership design (renewal calendar/radar, Outliers & Anomalies, Actual vs Projected, movers, drill-down modal). `index.html` is month-dynamic and is never regenerated; only `data.json` changes each build. Notes and open items live in `review_flags.json` and the deploy doc, never on the page.
`data.json` app fields (legacy schema, keep exactly): name, classification ("COGS"|"Non-COGS"), department, journaled, category, spend[], projected[] (avg of last <=3 non-zero prior months), renewalDate, renewalStatus, owner, annualCost, billingCycle. Renewal fields carry over from `inputs/legacy_data.json` (currently null) until renewals are re-synced from Notion.

## Parsing rules (encoded in parse_gl.py — for reference)
- Parse **by header names**, never fixed column indexes; the schema drifts monthly.
- Account = **last 5-digit group** of the account path. Prefer `Full name` / `Account full name`; never `Item split account` (that's the payment source).
- Include accounts **53000, 55000, 81000, 96100**. Always exclude **81500** (hotels/flights/events) and WONDER (food delivery).
- Journal rows with blank accounts are included when the vendor resolves to a known app.
- **Slack routing:** any resolved Slack row under $5K → *Salesforce - Slack Internal* (the memo is often just "Slack" for the internal plan).
- The row-1 checksum cell covers the **card/AP portion only**; month-end journals add on top.
- Credits are real negatives in xlsx exports — keep them.

## Classification rules
- Review sheet Final Classification, full stop. This **supersedes the Jun-2026 ruling** — Airtable, Twilio, Pumble (Cake), and Mailgun are **COGS**.
- The Salesforce GL family stays split into five canonical apps: Slack Enterprise (COGS), Slack Internal (Non-COGS), Certification Exams (COGS), Tableau Cloud (Non-COGS), Sales Cloud Enterprise (flagged).
- CompTIA and Pearson VUE (Exam Vouchers) are now **separate apps**; LinkedIn and LinkedIn Sales Navigator likewise.

## Known history notes
- **Apr 2026 restated by finance after 21 Jul 2026:** the ~$22,812.62 April GCP (Sada) line was removed; no Sada invoice exists between INV317177 (Mar) and INV323897 (May). April total is 145,267.49 (previously published 168,080.11). Open with ben@.
- **prepaid04.26** (Codio, $14,893.37): still booked with no invoice and no reversing entry — open with ben@.
- **Codio Jun $35,976.27 is correct** (invoice-date shift caught two cycles: INV-1728 bills May, INV-1767 bills June). Do not reverse.
- The **"App spend totals" tab** in the 2026 SaaS Spend sheet is a stale copy of the pre-rebuild dashboard. Never reconcile against it — the GL is the only spend truth.
