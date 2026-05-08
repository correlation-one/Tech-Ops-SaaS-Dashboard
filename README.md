# IT SaaS Spend Dashboard

A static, zero-cost dashboard for tracking monthly SaaS spend across the IT portfolio. Hosted on GitHub Pages.

**Live demo:** _replace with your GitHub Pages URL once deployed_

## What it shows

- Total spend per month, split by COGS vs Non-COGS
- Top apps by spend (current month)
- Spend by category
- Biggest month-over-month increases and decreases
- Full per-app table with share of total and MoM delta

## How to update each month

All data lives in **`data.json`**. To add a new month:

1. Open `data.json`.
2. Append the new month to the `months` array, e.g. `"2026-05"`.
3. For every app in `apps[]`, append the month's spend value to its `spend` array.
   - Use `0` if the app had no spend that month.
   - To add a brand-new app: pad its `spend` array with `0`s for all prior months, then append this month's value.
4. Update `meta.lastUpdated`.
5. Commit & push. GitHub Pages will redeploy automatically (~30s).

### Auto-converting from a finance CSV

If your monthly finance export looks like:

```
App Name, Category, Classification, Spend
AWS, Cloud Infrastructure, COGS, 61500
Snowflake, Data Warehouse, COGS, 31200
...
```

…ask Claude to "merge this into `data.json` for month 2026-05" and paste the CSV. Claude will produce the updated `data.json` for you.

## Deploying to GitHub Pages

1. Create a new GitHub repo (e.g. `IT-dashboard`).
2. Push these files (`index.html`, `data.json`, `README.md`) to the `main` branch.
3. Go to **Settings → Pages**.
4. Under **Source**, select **Deploy from a branch**, branch = `main`, folder = `/ (root)`. Save.
5. After ~1 min, the dashboard is live at `https://<your-org>.github.io/<repo-name>/`.

## File layout

```
.
├── index.html      # Dashboard (HTML + JS, single file)
├── data.json       # All spend data — edit this each month
└── README.md       # This file
```

## Data schema

```json
{
  "meta": { "lastUpdated": "YYYY-MM-DD", "currency": "USD" },
  "months": ["2025-05", "2025-06", ...],
  "apps": [
    {
      "name": "AWS",
      "category": "Cloud Infrastructure",
      "classification": "COGS",          // or "Non-COGS"
      "department": "Engineering",        // for Spend by Department widget
      "renewalDate": "2026-12-15",        // or null; feeds Renewal Radar + color-coded pills
      "journaled": true,                  // boolean tag for filtering
      "spend":     [42100, 43200, ...],   // actual spend per month
      "projected": [43500, 38300, ...]    // projected/budgeted spend per month
    }
  ]
}
```

### Field details

- **`department`** (string): used by the Spend-by-Department widget and the department filter. Free-form — any value you use becomes a filter option automatically.
- **`renewalDate`** (string `YYYY-MM-DD` or `null`): the contract renewal date. Drives:
  - The colored **Renewal pill** in the All Apps table (green > 90d, yellow 31–90d, red ≤ 30d, grey if expired).
  - The **Renewal Radar** widget, which auto-populates with all apps renewing in the next 90 days or expired in the last 60.
  - Set to `null` for usage-based / no-fixed-renewal contracts.
- **`journaled`** (boolean): flags apps that are journaled / tracked separately for accounting. Adds a "Journaled" badge throughout the UI and enables the Journaled filter.
- **`projected`** (array of numbers): one budget/forecast value per month, in the same order as `months`. Used by Actual vs. Projected widgets. If you don't have projections yet, fill with `0` or copy actuals.

## Widgets

- **KPI tiles**: total spend, COGS, Non-COGS, active app count, with MoM deltas.
- **Total Spend Trend**: stacked area of COGS vs Non-COGS over time.
- **Top Apps by Spend**: ranked horizontal bars for the selected month.
- **Spend by Category**: doughnut chart for the selected month.
- **MoM Increases / Decreases**: tables of biggest movers.
- **Actual vs. Projected — Trend**: overlay line chart, actual vs budget across all months.
- **Spend by Department**: horizontal bars by department for the selected month.
- **Outliers & Anomalies**: apps deviating ±25% from their trailing 3-month average, plus newly added or discontinued apps.
- **Renewal Radar**: upcoming renewals (next 90 days) and recently expired contracts, color-coded.
- **Actual vs. Projected — By App**: per-app variance table.
- **All Apps**: full table with department, classification, renewal status, spend, share, MoM delta, and Journaled tags.

## Filters

- **View Month** — pick any month to refocus all widgets.
- **Classification** — All / COGS / Non-COGS.
- **Top N apps** — 5 / 10 / 15 / All.
- **Department** — auto-populated from your data.
- **Journaled** — All / Journaled only / Not journaled.

## Customizing

- **Add a classification** (e.g. R&D vs G&A): extend the `classification` field and update the filter dropdown in `index.html`.
- **Change colors / theme**: edit the CSS variables at the top of `index.html`.
- **Add a chart**: Chart.js is already loaded — add a `<canvas>` and a `drawChart()` call.
