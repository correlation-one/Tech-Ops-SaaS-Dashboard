# Deploy — May + June 2026

The live dashboard was still showing **Jan–Apr**; the May release and the later
Jan–May rebuild were both built but never pushed. This package covers **Jan–Jun**
in one go, rebuilt from the raw GL tabs.

## Push (run locally — the sandbox has no GitHub credentials)

```bash
cd ~/Tech-Ops-SaaS-Dashboard
unzip -o ~/Downloads/saas-dashboard-jun-2026.zip
git add -A && git commit -m "May + June 2026: full Jan-Jun rebuild from GL, reproducible build script"
git push
```

Then hard-refresh the live page (Cmd/Ctrl+Shift+R) — Pages caches aggressively.

`index.html` is unchanged: it reads `monthLabels` dynamically and picks up the
two new months on its own.

## 30-second sanity check

| Month | Total | COGS | Non-COGS |
|---|---|---|---|
| Jan | 151,655.48 | 72,751.42 | 78,904.06 |
| Feb | 157,003.68 | 75,675.91 | 81,327.77 |
| Mar | 163,215.20 | 82,324.88 | 80,890.32 |
| Apr | 168,080.11 | 83,793.33 | 84,286.78 |
| May | 146,127.40 | 62,339.02 | 83,788.38 |
| Jun | 171,927.89 | 83,298.34 | 88,629.55 |

Jan–May reproduce the previously verified figures (Feb/Mar within 2–3¢ of float
drift in the source tab). If any month reads differently after deploy, the wrong
`data.json` got pushed.

## Two things baked in that you should know about

1. **April GCP is patched.** The `Apr 26 Spend` tab has no Sada/GCP row at all —
   April's 53000 account holds a single $54 AWS line. The $22,812.62 GCP invoice
   is injected from the verified April build (`PATCH` in `build.py`). Ask Ben why
   it never landed in the tab.
2. **June Codio is as-booked at $35,976.27** — both INV-1728 ($18,790.48) and the
   catch-up INV-1767 ($17,185.79). To back the catch-up out once Ben confirms:
   ```bash
   python3 build.py --reverse-codio
   ```
   That gives June: total 154,742.10, COGS 66,112.55, Non-COGS 88,629.55.

## Running it next month

```bash
python3 build.py          # writes data.json + review_flags.json
```
Requires `software_spend.xlsx` (xlsx export of the Software Spend sheet) in the
same directory, plus `naming-map.json`, `classification.json`, `prior_build.json`,
`known_apps.json`. Add the new tab name to `TABS` in `gl.py`.
