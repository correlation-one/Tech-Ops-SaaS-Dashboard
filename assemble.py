#!/usr/bin/env python3
"""Assemble data.json + review_flags.json + per-month audit CSVs from classified inputs."""
import json, csv, datetime
from collections import defaultdict

C = json.load(open('inputs/classified.json'))
clstab = json.load(open('inputs/classification_tab.json'))
apptot = json.load(open('inputs/app_totals_deployed.json'))
rows = json.load(open('inputs/gl_rows.json'))
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul']
LBL25 = {'Oct25':'Oct 2025','Nov25':'Nov 2025','Dec25':'Dec 2025'}

O2N = {'GCP':'Google Cloud Platform','Comptia':'CompTIA','Google':'Google Workspace','Aws':'Amazon Web Services',
 'Hubspot':'HubSpot','Github':'GitHub','Cake':'Pumble','Saasoptics':'Maxio (formerly SaaSOptics)','Maxio':'Maxio (formerly SaaSOptics)',
 'Perplexity':'Perplexity AI','Lovable Dover':'Lovable','Surveymonkey Inc':'SurveyMonkey','Hireright Llc':'HireRight',
 'Mindhub':'MindHub','Bamboohr':'BambooHR','Cultureamp':'Culture Amp','Launchdarkly':'LaunchDarkly','Coderpad':'CoderPad',
 'Deepsource':'DeepSource','Dnsimple':'DNSimple','Godaddy':'GoDaddy','Docusign':'DocuSign','Paypal':'PayPal',
 'Zoominfo':'ZoomInfo','Linkedin':'LinkedIn','Digital Ocean':'DigitalOcean','Salesforce - Tableau Cloud Creator':'Salesforce - Tableau Cloud',
 'Tableau':'Salesforce - Tableau Cloud','Salesforce Inc':'Salesforce - Certification Exams','Salesforce - Exams':'Salesforce - Certification Exams',
 'Slack - Internal':'Salesforce - Slack Internal','Apprentiscope':'ApprentiScope','Apprenti Apprentiscope':'ApprentiScope',
 'The Noun':'The Noun Project','Imkey Breda':'Resume IO','Vue Pearson':'Pearson VUE (Exam Vouchers)','Guidde Inc':'Guidde',
 'Librato Solarwindaustin':'Librato','Plus Docs':'PlusDocs','Helix Pay':'HelixPay','Fal Features':'Fal','Anthropic':'Claude',
 'Sales Navigator':'LinkedIn Sales Navigator','Cooper Square':'Cooper Square Technologies','Quickbooks':'QuickBooks',
 'Quickbooks Payments':'QuickBooks'}

REVIEW_DEPT = {'Google Cloud Platform':'Engineering','CompTIA':'Operations','Salesforce - Slack Enterprise':'Operations',
 'Codio':'Learning Experience Design','Google Workspace':'Tech Operations and AI Enablement','Salesforce - Certification Exams':'Operations',
 'Calendly':'Operations','Worksuite':'People Operations','Claude':'Tech Operations and AI Enablement','Zoom':'Operations',
 'Okta':'Engineering','1Password':'Tech Operations and AI Enablement','Airtable':'Operations','SurveyMonkey':'Operations',
 'HubSpot':'Operations','Twilio':'Engineering','Pumble':'Operations','Profound':'Operations','Zendesk':'Operations',
 'Sentry':'Engineering','Salesforce - Slack Internal':'Operations','Mailchimp':'Operations','MindHub':'Operations',
 'Greenhouse':'People Operations','Accredible':'Operations','ChatGPT':'Tech Operations and AI Enablement',
 'Salesforce - Tableau Cloud':'Data Science & Analytics','Outreach':'Sales','Maxio (formerly SaaSOptics)':'Finance',
 'Adobe':'Tech Operations and AI Enablement','Carta':'Operations','ApprentiScope':'Operations','Notion':'Tech Operations and AI Enablement',
 'LinkedIn':'Marketing','Atlassian':'Engineering','Lovable':'Operations','Microsoft':'Tech Operations and AI Enablement',
 'ZoomInfo':'Sales','BambooHR':'People Operations','Workforce':'People Operations','Culture Amp':'People Operations',
 'GitHub':'Engineering','Cursor':'Engineering','Hireflix':'Operations','Pearson VUE (Exam Vouchers)':'Operations',
 'Tremendous':'Operations','Yesware':'Operations','LaunchDarkly':'Engineering','PayPal':'Finance','Figma':'Product',
 'Squadcast':'Engineering','Typeform':'Product Management','Zapier':'Operations','Refiner':'Operations','DeepSource':'Engineering',
 'Hook Security':'Operations','Gamma':'Operations','Artillery':'Engineering','Paddle':'Finance','Amazon Web Services':'Engineering',
 'Hex':'Engineering','Loom':'Operations','QuickBooks':'Operations','Apollo':'Operations','DNSimple':'Engineering',
 'CoderPad':'Engineering','Geocode':'Engineering','GoDaddy':'Engineering','Mailgun':'Operations','Artisan':'Operations',
 'Tango':'Engineering','Perplexity AI':'Tech Operations and AI Enablement','DocuSign':'People Operations','Stape':'Engineering',
 'Vercel':'Engineering','PlusDocs':'Operations','Linear':'Engineering','HireRight':'Operations',
 'LinkedIn Sales Navigator':'Operations','Dmarcian':'Engineering','Guidde':'Operations','HelixPay':'Operations',
 'Fal':'Operations','DigitalOcean':'Engineering','Squarespace':'Engineering'}

cls_n = {O2N.get(k,k): v for k,v in clstab.items()}
tot_n = {}
for k,v in apptot.items(): tot_n.setdefault(O2N.get(k,k), v)
typ_by_app = defaultdict(set)
for r in rows: typ_by_app[r['app']].add(r['typ'])

mat, oldm, newm, src = C['matrix'], C['old'], C['new'], C['newsrc']
act25 = C['activity25']

def dept(a):
    return REVIEW_DEPT.get(a) or (cls_n.get(a,{}).get('dept') or '') or (tot_n.get(a,{}).get('dept') or '') or 'Unassigned'
def journaled(a):
    if a in cls_n: return cls_n[a]['journaled'].strip().lower()=='true'
    return 'Journal Entry' in typ_by_app[a]
def last_active(a):
    for m in reversed(MONTHS):
        if abs(mat[a][m])>0.005: return f'{m} 2026'
    for k in ['Dec25','Nov25','Oct25']:
        if abs(act25.get(a,{}).get(k,0))>0.005: return LBL25[k]
    return 'none in window'

apps = []
flag_apps = {f['app'] for f in C['flags']}
for a in sorted(mat, key=lambda x: -sum(mat[x].values())):
    monthly = [round(mat[a][m],2) for m in MONTHS]
    apps.append(dict(name=a, cogs=newm[a], oldCogs=oldm[a], changed=newm[a]!=oldm[a],
                     source=src[a], dept=dept(a), journaled=journaled(a),
                     flag=a in flag_apps, monthly=monthly, total=round(sum(monthly),2),
                     lastActive=last_active(a)))

monthly = []
for m in MONTHS:
    s = C['summary'][m]
    monthly.append(dict(total=s['total'], cogs=s['new_cogs'], nonCogs=s['new_non'],
                        oldCogs=s['old_cogs'], oldNonCogs=s['old_non']))

data = dict(
  meta=dict(
    generated=str(datetime.date.today()),
    build='Aug 2026 full rebuild: Jan-Jul 2026, reclassified per COGS/Non-COGS Classification Review',
    classificationSource='SaaS COGS / Non-COGS Classification Review - 2026 YTD (Final Classification column) - sole source of truth',
    verification='Jan/Feb/Mar/May regress to the published GL baseline to the cent on total and old-COGS; Jun matches the verified $171,927.88; Apr restated by finance (see notes)',
    notes=[
      'April 2026 restated: finance removed the ~$22,812.62 April GCP (Sada) line from the GL after 21 Jul 2026; no Sada invoice exists between INV317177 (Mar) and INV323897 (May). April total is now $145,267.49 (was $168,080.11). Open with ben@.',
      'April accrual prepaid04.26 (Codio, $14,893.37) remains booked with no invoice and no reversing entry through July.',
      'Classification supersedes the Jun-2026 ruling: Airtable, Twilio, Pumble (Cake) and Mailgun are COGS per the review sheet.',
      'Apps not in the review sheet are classified by GL-account default and flagged; add them to the review sheet to clear the flags.',
      '10-month rule: apps with no spend Oct 2025 - Jul 2026 are removed from the active list (see dropped).'
    ]),
  monthLabels=MONTHS,
  monthKeys=[f'2026-{i:02d}' for i in range(1,8)],
  monthly=monthly,
  apps=apps,
  dropped=C['dropped'],
  flags=C['flags'])
json.dump(data, open('data.json','w'), indent=1)
print('data.json:', len(apps), 'apps |', len(C["dropped"]), 'dropped |', len(C["flags"]), 'flags')

json.dump(dict(generated=str(datetime.date.today()),
               classification_flags=C['flags'],
               open_items=[
                 'April GCP/Sada line (~$22,812.62) removed from GL after 21 Jul - confirm with ben@ where April GCP consumption is booked',
                 'prepaid04.26 Codio accrual $14,893.37: no invoice, no reversing entry through July',
                 'Unidentified Wire (55000): two prepaid07.26 journal lines totaling $311.36 with wire-transfer memos - ask ben@ for the vendor',
                 'PRO SAN FRANCISCO CA $21.25 (Jul) mapped to Perplexity AI by amount pattern - confirm',
                 'Indeed $67.35 (Jul, 96100) treated as an app - confirm SaaS vs recruiting spend',
                 'Slido $211.12 (Jul) - new app, needs owner/department',
                 'Cooper Square Technologies - still needs classification in the review sheet (defaulted Non-COGS)']),
          open('review_flags.json','w'), indent=1)

# per-month audit CSVs
bym = defaultdict(list)
for r in rows: bym[r['mon']].append(r)
for m in MONTHS:
    with open(f'inputs/{m.lower()}_gl_2026.csv','w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['mon','app','amt','acct','typ','num','vendor'])
        w.writeheader()
        for r in sorted(bym[m], key=lambda x:-abs(x['amt'])): w.writerow(r)
print('audit CSVs written:', ', '.join(f'{m}:{len(bym[m])}' for m in MONTHS))

# quick headline sanity
print('\nNew classification headline (Jan-Jul):')
for m,s in zip(MONTHS, monthly):
    print(f"  {m}: total {s['total']:>11,.2f} | COGS {s['cogs']:>11,.2f} | Non-COGS {s['nonCogs']:>10,.2f}")
ytd = sum(s['total'] for s in monthly)
print(f'  YTD Jan-Jul: {ytd:,.2f}')
