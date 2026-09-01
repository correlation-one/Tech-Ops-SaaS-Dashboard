#!/usr/bin/env python3
"""Assemble data.json in the ORIGINAL dashboard schema (legacy index.html),
plus review_flags.json and per-month audit CSVs."""
import json, csv, datetime
from collections import defaultdict

C = json.load(open('inputs/classified.json'))
clstab = json.load(open('inputs/classification_tab.json'))
apptot = json.load(open('inputs/app_totals_deployed.json'))
rows = json.load(open('inputs/gl_rows.json'))
try:
    LEGACY = {a['name']: a for a in json.load(open('inputs/legacy_data.json'))['apps']}
except FileNotFoundError:
    LEGACY = {}
try:
    RENEW = json.load(open('inputs/renewals.json'))
except FileNotFoundError:
    RENEW = {}
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul']
LBL25 = {'Oct25':'Oct 2025','Nov25':'Nov 2025','Dec25':'Dec 2025'}

O2N = {
 "GCP": "Google Cloud Platform",
 "Comptia": "CompTIA",
 "Google": "Google Workspace",
 "Aws": "Amazon Web Services",
 "Hubspot": "HubSpot",
 "Github": "GitHub",
 "Cake": "Pumble",
 "Saasoptics": "Maxio (formerly SaaSOptics)",
 "Maxio": "Maxio (formerly SaaSOptics)",
 "Perplexity": "Perplexity AI",
 "Lovable Dover": "Lovable",
 "Surveymonkey Inc": "SurveyMonkey",
 "Hireright Llc": "HireRight",
 "Mindhub": "MindHub",
 "Bamboohr": "BambooHR",
 "Cultureamp": "Culture Amp",
 "Launchdarkly": "LaunchDarkly",
 "Coderpad": "CoderPad",
 "Deepsource": "DeepSource",
 "Dnsimple": "DNSimple",
 "Godaddy": "GoDaddy",
 "Docusign": "DocuSign",
 "Paypal": "PayPal",
 "Zoominfo": "ZoomInfo",
 "Linkedin": "LinkedIn",
 "Digital Ocean": "DigitalOcean",
 "Salesforce - Tableau Cloud Creator": "Salesforce - Tableau Cloud",
 "Tableau": "Salesforce - Tableau Cloud",
 "Salesforce Inc": "Salesforce - Certification Exams",
 "Salesforce - Exams": "Salesforce - Certification Exams",
 "Slack - Internal": "Salesforce - Slack Internal",
 "Apprentiscope": "ApprentiScope",
 "Apprenti Apprentiscope": "ApprentiScope",
 "The Noun": "The Noun Project",
 "Imkey Breda": "Resume IO",
 "Vue Pearson": "Pearson VUE (Exam Vouchers)",
 "Guidde Inc": "Guidde",
 "Librato Solarwindaustin": "Librato",
 "Plus Docs": "PlusDocs",
 "Helix Pay": "HelixPay",
 "Fal Features": "Fal",
 "Anthropic": "Claude",
 "Sales Navigator": "LinkedIn Sales Navigator",
 "Cooper Square": "Cooper Square Technologies",
 "Quickbooks": "QuickBooks",
 "Quickbooks Payments": "QuickBooks",
 "Salesforce - Other": "Salesforce - Certification Exams",
 "Salesforce - Other (COGS)": "Salesforce - Certification Exams",
 "Salesforce - Other (Non-COGS)": "Salesforce - Tableau Cloud",
 "Noun Project": "The Noun Project"
}

REVIEW_DEPT = {
 "Google Cloud Platform": "Engineering",
 "CompTIA": "Operations",
 "Salesforce - Slack Enterprise": "Operations",
 "Codio": "Learning Experience Design",
 "Google Workspace": "Tech Operations and AI Enablement",
 "Salesforce - Certification Exams": "Operations",
 "Calendly": "Operations",
 "Worksuite": "People Operations",
 "Claude": "Tech Operations and AI Enablement",
 "Zoom": "Operations",
 "Okta": "Engineering",
 "1Password": "Tech Operations and AI Enablement",
 "Airtable": "Operations",
 "SurveyMonkey": "Operations",
 "HubSpot": "Operations",
 "Twilio": "Engineering",
 "Pumble": "Operations",
 "Profound": "Operations",
 "Zendesk": "Operations",
 "Sentry": "Engineering",
 "Salesforce - Slack Internal": "Operations",
 "Mailchimp": "Operations",
 "MindHub": "Operations",
 "Greenhouse": "People Operations",
 "Accredible": "Operations",
 "ChatGPT": "Tech Operations and AI Enablement",
 "Salesforce - Tableau Cloud": "Data Science & Analytics",
 "Outreach": "Sales",
 "Maxio (formerly SaaSOptics)": "Finance",
 "Adobe": "Tech Operations and AI Enablement",
 "Carta": "Operations",
 "ApprentiScope": "Operations",
 "Notion": "Tech Operations and AI Enablement",
 "LinkedIn": "Marketing",
 "Atlassian": "Engineering",
 "Lovable": "Operations",
 "Microsoft": "Tech Operations and AI Enablement",
 "ZoomInfo": "Sales",
 "BambooHR": "People Operations",
 "Workforce": "People Operations",
 "Culture Amp": "People Operations",
 "GitHub": "Engineering",
 "Cursor": "Engineering",
 "Hireflix": "Operations",
 "Pearson VUE (Exam Vouchers)": "Operations",
 "Tremendous": "Operations",
 "Yesware": "Operations",
 "LaunchDarkly": "Engineering",
 "PayPal": "Finance",
 "Figma": "Product",
 "Squadcast": "Engineering",
 "Typeform": "Product Management",
 "Zapier": "Operations",
 "Refiner": "Operations",
 "DeepSource": "Engineering",
 "Hook Security": "Operations",
 "Gamma": "Operations",
 "Artillery": "Engineering",
 "Paddle": "Finance",
 "Amazon Web Services": "Engineering",
 "Hex": "Engineering",
 "Loom": "Operations",
 "QuickBooks": "Operations",
 "Apollo": "Operations",
 "DNSimple": "Engineering",
 "CoderPad": "Engineering",
 "Geocode": "Engineering",
 "GoDaddy": "Engineering",
 "Mailgun": "Operations",
 "Artisan": "Operations",
 "Tango": "Engineering",
 "Perplexity AI": "Tech Operations and AI Enablement",
 "DocuSign": "People Operations",
 "Stape": "Engineering",
 "Vercel": "Engineering",
 "PlusDocs": "Operations",
 "Linear": "Engineering",
 "HireRight": "Operations",
 "LinkedIn Sales Navigator": "Operations",
 "Dmarcian": "Engineering",
 "Guidde": "Operations",
 "HelixPay": "Operations",
 "Fal": "Operations",
 "DigitalOcean": "Engineering",
 "Squarespace": "Engineering"
}

cls_n = {O2N.get(k, k): v for k, v in clstab.items()}
tot_n = {}
for k, v in apptot.items(): tot_n.setdefault(O2N.get(k, k), v)
leg_n = {}
for k, v in LEGACY.items(): leg_n.setdefault(O2N.get(k, k), v)
typ_by_app = defaultdict(set)
for r in rows: typ_by_app[r['app']].add(r['typ'])

mat, newmap, src = C['matrix'], C['new'], C['newsrc']
act25 = C['activity25']

def dept(a):
    return REVIEW_DEPT.get(a) or (cls_n.get(a, {}).get('dept') or '') or (tot_n.get(a, {}).get('dept') or '') or 'Unassigned'
def journaled(a):
    if a in cls_n: return cls_n[a]['journaled'].strip().lower() == 'true'
    return 'Journal Entry' in typ_by_app[a]
def project(series):
    proj = []
    for i in range(len(series)):
        if i == 0:
            proj.append(series[0])
        else:
            prior = [v for v in series[:i] if v > 0][-3:]
            proj.append(round(sum(prior) / len(prior), 2) if prior else 0)
    return proj

apps = []
flag_apps = {f['app'] for f in C['flags']}
for a in sorted(mat, key=lambda x: -sum(mat[x].values())):
    spend = [round(mat[a][m], 2) for m in MONTHS]
    leg = leg_n.get(a, {})
    ren = RENEW.get(a, {})
    apps.append(dict(
        name=a,
        classification=newmap[a],
        department=dept(a),
        journaled=journaled(a),
        category=ren.get('category') or leg.get('category'),
        spend=spend,
        projected=project(spend),
        renewalDate=ren.get('renewalDate') or leg.get('renewalDate'),
        renewalStatus=ren.get('renewalStatus') or leg.get('renewalStatus'),
        owner=ren.get('owner') or leg.get('owner'),
        annualCost=ren.get('annualCost') or leg.get('annualCost'),
        billingCycle=ren.get('billingCycle') or leg.get('billingCycle')))

monthly = []
for m in MONTHS:
    s = C['summary'][m]
    monthly.append(dict(total=s['total'], cogs=s['new_cogs'], nonCogs=s['new_non']))

data = dict(
    meta=dict(
        lastUpdated=str(datetime.date.today()),
        currency='USD',
        sources=dict(
            gl='Software Spend (Google Sheet) tabs Jan-July 26 Spend',
            classification='SaaS COGS / Non-COGS Classification Review - 2026 YTD - Final Classification (sole source of truth)'),
        notes=[
            'All months reclassified Aug 2026 per the Classification Review sheet.',
            'April restated to the current GL ($145,267.49); the ~$22.8K April GCP line was removed by finance after 21 Jul - open with ben@.',
            '10-month rule: apps with no spend Oct 2025 - Jul 2026 removed from the list.']),
    months=[f'2026-{i:02d}' for i in range(1, 8)],
    monthLabels=MONTHS,
    monthly=monthly,
    apps=apps)
json.dump(data, open('data.json', 'w'), indent=1)
print('data.json (legacy schema):', len(apps), 'apps,', len(MONTHS), 'months')

_today = datetime.date.today()
_matched = {a['name'] for a in apps if RENEW.get(a['name'])}
_active_names = {a['name'] for a in apps}
notion_sync = dict(
    matched=len(_matched),
    active_apps_missing_from_notion=sorted(_active_names - set(RENEW)),
    notion_rows_not_on_dashboard=sorted(set(RENEW) - _active_names),
    stale_renewal_dates=sorted([
        f"{a['name']}: {a['renewalDate']} ({a['renewalStatus']})" for a in apps
        if a['renewalDate'] and (datetime.date.fromisoformat(a['renewalDate']) - _today).days < -60]))
json.dump(dict(generated=str(datetime.date.today()),
               notion_renewal_sync=notion_sync,
               classification_flags=C['flags'],
               dropped_by_10_month_rule=C['dropped'],
               open_items=[
                 'April GCP/Sada line (~$22,812.62) removed from GL after 21 Jul - confirm with ben@ where April GCP consumption is booked',
                 'prepaid04.26 Codio accrual $14,893.37: no invoice, no reversing entry through July',
                 'Unidentified Wire (55000): two prepaid07.26 journal lines totaling $311.36 - ask ben@ for the vendor',
                 'PRO SAN FRANCISCO CA $21.25 (Jul) mapped to Perplexity AI by amount pattern - confirm',
                 'Indeed $67.35 (Jul, 96100) treated as an app - confirm SaaS vs recruiting spend',
                 'Slido $211.12 (Jul) - new app, needs owner/department',
                 '12 apps still need review-sheet rows (all account-defaulted; largest is Librato, $957 Jan-Jul)']),
          open('review_flags.json', 'w'), indent=1)

bym = defaultdict(list)
for r in rows: bym[r['mon']].append(r)
for m in MONTHS:
    with open(f'inputs/{m.lower()}_gl_2026.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['mon','app','amt','acct','typ','num','vendor'])
        w.writeheader()
        for r in sorted(bym[m], key=lambda x: -abs(x['amt'])): w.writerow(r)
print('review_flags.json + audit CSVs written')
