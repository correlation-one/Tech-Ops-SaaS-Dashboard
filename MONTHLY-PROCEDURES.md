# Tech Ops SaaS Dashboard — Monthly Update Runbook

_Last updated: 2026-05-29_

This is the checklist for refreshing the dashboard each month. The dashboard lives at
**https://correlation-one.github.io/Tech-Ops-SaaS-Dashboard/** (repo `correlation-one/Tech-Ops-SaaS-Dashboard`).
It is a static site: one `index.html` (layout + charts) and one `data.json` (all the numbers). Updating = regenerating `data.json` and pushing.

---

## 1. Data sources (where every number comes from)

| What | Source | Notes |
|---|---|---|
| Per-app spend, **Jan–Mar** | "App spend totals" tab in the **2026 SaaS Spend** Google Sheet (`fileId 1Cr6AhulaGHzkNYSnjNTj3nYSQiwKeLvOgWpUkFVT6zM`) | The Tableau row is a **duplicate** of "Salesforce - Tableau Cloud Creator" — exclude it. |
| Classification (COGS / Non-COGS), **Department**, Journaled flags | "SaaS Apps Classifcation" tab in the same sheet (note the misspelling) | **Source of truth** for classification + department. |
| Headline monthly totals (KPIs) | "Dashboard" tab of the same sheet | Used for Total / COGS / Non-COGS headline figures. |
| Per-app spend, **April onward** | Uploaded `Software_Spend.xlsx`, tab "Apr 26 Spend" | New month = new tab (e.g. "May 26 Spend"). 7 columns: Date, Transaction Type, Num, Name, Memo/Description, Account, Amount. |
| Renewal calendar (dates, status, owner, annual cost, category, billing cycle) | **Notion** "SaaS Apps" database (`collection://c08d6bf9-fc36-4a55-95ca-cbccf4062c6b`) | Manual snapshot — pulled on request, does not auto-refresh. |

---

## 2. Monthly steps

1. **Get the new month's GL** as a tab in `Software_Spend.xlsx` (same 7-column format).
2. **Map every GL line to an app name** using `naming-map.json`:
   - `vendor_aliases` rolls raw GL descriptors up to an app (e.g. all `COMPTIA` / `PEARSON VUE` / `VUE*COMPTIA` lines → `Comptia`). **Order matters: most specific first.**
   - `non_saas_exclude` drops non-SaaS rows (food delivery, reimbursements, etc.).
   - `name_map` applies final display renames (e.g. `Salesforce Inc` → `Salesforce - Other`).
   - **Confirm the new-month total matches the GL grand total** (minus excluded non-SaaS) before trusting it.
   - **Salesforce consolidation (do every month):** Salesforce must collapse to exactly **four** entries, kept classification-accurate:
     - `Salesforce - Slack Enterprise` (COGS) — keep separate
     - `Salesforce - Slack Internal` (Non-COGS) — keep separate
     - `Salesforce - Other` (COGS) — fold in every **COGS** Salesforce SKU (generic Salesforce Inc, Exams, etc.)
     - `Salesforce - Other (Non-COGS)` — fold in every **Non-COGS** Salesforce SKU (Tableau Cloud Creator, Sales Cloud Enterprise, etc.)
     - If a **new** Salesforce SKU appears: look up its COGS/Non-COGS in the Classification tab, then fold it into the matching "Other" bucket. Never merge across classifications (that would throw off the COGS/Non-COGS split).
3. **Reconcile classification + department** against the "SaaS Apps Classifcation" tab.
4. **Run the new-app + journaling review** (Section 3) — flag anything ambiguous.
5. **Refresh renewals from Notion** if dates have changed.
6. Regenerate `data.json`, validate, screenshot-check, and push `index.html` + `data.json`.
7. **Hard-refresh** the live page (Cmd/Ctrl+Shift+R) — GitHub Pages caches aggressively.

---

## 3. Manual review rules (the part finance does NOT do automatically)

### 3a. Journaling — finance only journals payments **above $5,000**
So some real subscriptions/COGS are **not** journaled simply because each payment was under $5k.
Example: **Hook Security** is not journaled because its payments are below the threshold.

**Heuristic to catch these:** any app with **one big spend and little/nothing the other months** needs a manual check —
is it a **one-time payment** or a **subscription** (annual/lump or just a small recurring one that fell under $5k)?

The build script auto-flags apps matching any of:
- only **1 month** of spend in the year (one-time vs new subscription?),
- **one month much larger** than the rest (>3× the next — possible annual/lump),
- a **single payment ≥ $5k that is NOT journaled** (verify it should be),
- spend that **stopped before the latest month** (cancelled, or annual that already billed?).

For each flagged app: decide **one-time vs recurring**, and **whether it should be journaled**. I can either
(a) flag the list for you to confirm, or (b) make a judgment call and note it — your call per item.

### 3b. New apps that appear need two classifications
Whenever a vendor shows up that wasn't there before, it needs:
- **COGS vs Non-COGS**, and
- **Department**.

If either is **ambiguous**, flag it for review rather than guessing. If it's clearly the same family as an
existing app (e.g. another Salesforce SKU), apply the obvious answer and note it.

---

## 4. Current open review items (as of 2026-05-29)

These are flagged by the heuristic above and need a one-time/subscription + journaling decision.
See `review_flags.json` for the full machine-readable list. Highest-value first:

**Large & not journaled (most likely SHOULD be journaled — verify the $5k rule):**
- **Comptia** — COGS, ~$20–24k/mo every month, not journaled. Clearly recurring COGS; likely a journaling gap.
- **Salesforce - Slack Enterprise** — COGS, ~$22–24k/mo, not journaled. Same — likely a journaling gap.
- **Codio** — COGS, ramping $3.9k→$14.9k, not journaled. Recurring; verify journaling.
- **Claude** — Non-COGS, ramping to $5.3k in Apr, not journaled. Recurring (monthly billing); verify.

**Single-month / stopped — one-time vs subscription?**
- Hireflix ($3.6k Jan only), Apprenticeships For ($1.9k Feb only), Typeform ($1,622 Jan only),
  Docusign ($327 Apr only), Hireright Llc ($224 Jan only), Helix Pay ($27 Jan only), Squarespace ($24 Mar only).
- Stopped before April: Apprentiscope, Cake, Hook Security, Tremendous, Quickbooks Payments, Resume IO,
  Salesforce - Slack Internal, Paypal, Squadcast, Hex, Fal Features.

**Possible annual/lump (one big month):**
- Zapier, Apprenti Apprentiscope, Figma, Loom, Aws, Perplexity.

> Note: Several of the "stopped before April" items may simply be **annual** (already billed for the year) or
> **cancelled**. The dashboard's Outliers & Anomalies panel surfaces these live each month too.

---

## 5. Files in this project

| File | Purpose |
|---|---|
| `index.html` | Dashboard layout, charts, per-app drill-down. Rarely changes month to month. |
| `data.json` | All numbers. **This is what you regenerate monthly.** |
| `naming-map.json` | Finance/vendor name → dashboard name. **Add new renames + vendor roll-ups here.** |
| `MONTHLY-PROCEDURES.md` | This file. |
| `review_flags.json` | Auto-generated list of apps needing a journaling / one-time decision. |

---

## 6. data.json schema (for reference)

```
meta        { lastUpdated, currency, sources }
months      ["2026-01", ...]            ISO month keys
monthLabels ["Jan", ...]
monthly     [ { total, cogs, nonCogs }, ... ]   one per month (headline KPIs)
apps        [ {
                name, classification ("COGS"|"Non-COGS"), department, journaled (bool),
                category, spend[per month], projected[per month],
                renewalDate, renewalStatus, owner, annualCost, billingCycle
            }, ... ]
```
