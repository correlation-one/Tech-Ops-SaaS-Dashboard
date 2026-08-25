# Deploy — Aug 2026 release

## What this release does
1. **Reclassifies every month (Jan–Jul 2026)** to the review sheet's Final Classification. Roughly $35–38K/month moves from Non-COGS to COGS; the biggest flips are GCP, Pearson VUE, Zoom, Okta, Airtable, Pumble, Twilio, AWS, Mailgun (→ COGS) and Loom (→ Non-COGS).
2. **Adds July 2026:** $152,483.62 (COGS 98,794.11 / Non-COGS 53,689.51), including the July Sada invoice INV330351 ($23,189.92) and three new vendors (Slido, Indeed, one unidentified 55000 wire journal — flagged).
3. **Restates April** to the current GL: $145,267.49. Finance removed the ~$22,812.62 April GCP line after 21 Jul; the dashboard follows the ledger and the change is documented in the notes panel.
4. **Prunes the app list** by the 10-month rule: 98 active apps stay, 38 inactive apps are removed (listed under the notes panel).

## The numbers now on the dashboard
| 2026 | Total | COGS | Non-COGS | COGS old rules |
|---|---|---|---|---|
| Jan | 151,655.48 | 110,935.23 | 40,720.25 | 72,751.42 |
| Feb | 157,003.65 | 111,716.97 | 45,286.68 | 75,675.89 |
| Mar | 163,215.17 | 119,254.49 | 43,960.68 | 82,324.86 |
| Apr | 145,267.49 | 96,265.76 | 49,001.73 | 83,793.33 |
| May | 146,127.40 | 98,038.67 | 48,088.73 | 62,339.02 |
| Jun | 171,927.88 | 118,719.33 | 53,208.55 | 83,298.34 |
| Jul | 152,483.62 | 98,794.11 | 53,689.51 | 63,426.67 |

YTD Jan–Jul: **$1,087,680.69**. Verification: Jan/Feb/Mar/May reproduce the previously published GL baseline to the cent (total *and* old-rules COGS); Jun matches the verified $171,927.88.

## Deploy (from your machine)
    cd ~/Tech-Ops-SaaS-Dashboard        # your local clone
    unzip -o ~/Downloads/Tech-Ops-SaaS-Dashboard-AUG-2026.zip
    git add -A
    git commit -m "Aug 2026: reclassify Jan-Jul per review sheet; add July; restate April; prune inactive apps"
    git pull --rebase origin main
    git push origin main

## Verify after Pages rebuilds (hard refresh — data.json caches)
- "Reclassified · Aug 2026" badge shows; YTD header reads $1,087,681.
- July selected by default: 152,483.62 / COGS 98,794.11.
- Click Jan: 151,655.48 / COGS 110,935.23; the dashed "old rules" line sits well below the COGS bars.
- Applications panel: 98 apps; "Changed (9)" and "Flagged (13)" chips work; row click opens monthly detail.
- Notes panel lists the April restatement and 38 dropped apps.

## Open items for Ben
1. April GCP/Sada (~$22,812.62) removed from the April GL after 21 Jul — where is April GCP consumption booked now?
2. prepaid04.26 Codio $14,893.37 — still no invoice and no reversing entry.
3. Two prepaid07.26 journal lines in 55000 ($218.25 + $93.12) carry only wire-transfer memos — which vendor?
4. Cooper Square Technologies ($9,798.75 Jan–Jul) plus 12 smaller apps need review-sheet rows (currently account-defaulted and flagged).
5. "PRO SAN FRANCISCO CA" $21.25 (Jul) mapped to Perplexity AI by amount pattern; Indeed $67.35 treated as an app — confirm both.

## After deploy
Step two: update the "2026 SaaS Spend" classification tab to match the review sheet (separate session, per plan).


## v2 (same day) — original design restored
Per Ahmad: the Aug redesign is replaced by the ORIGINAL dashboard design (renewal calendar/radar, Outliers & Anomalies, Actual vs Projected, movers, per-app drill-down). The notes & open items panel is gone from the page — open items live in `review_flags.json` and this doc. `data.json` is emitted in the original schema with the same verified reclassified numbers (regression gate unchanged). Footer source line updated to name the Classification Review sheet. Re-upload `index.html` and `data.json` (or everything) exactly as before, then hard-refresh.