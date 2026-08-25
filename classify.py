#!/usr/bin/env python3
"""Old-vs-new classification engine + regression + 10-month activity filter."""
import json
from collections import defaultdict

rows = json.load(open('inputs/gl_rows.json'))
act25 = json.load(open('inputs/activity_2025.json'))
clstab = json.load(open('inputs/classification_tab.json'))
apptot = json.load(open('inputs/app_totals_deployed.json'))
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul']

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
 'Quickbooks Payments':'QuickBooks','Mentimeter Stockholm':'Mentimeter','Circleci':'CircleCI','Lambdatest':'LambdaTest',
 'Goto':'GoTo','Ctfd':'CTFd','Askai':'AskAI','Sumup Social':'SumUp Social','Paypro':'PayPro','Playbookux':'PlaybookUX',
 'Recruitcrm':'RecruitCRM'}

# ---- per-app monthly matrix from GL ----
mat = defaultdict(lambda: {m:0.0 for m in MONTHS})
acct_by_app, typ_by_app = defaultdict(set), defaultdict(set)
for r in rows:
    mat[r['app']][r['mon']] = round(mat[r['app']][r['mon']] + r['amt'], 2)
    if r['acct']: acct_by_app[r['app']].add(r['acct'])
    typ_by_app[r['app']].add(r['typ'])

# ---- OLD classification (pre-review rules) for regression ----
SF_OLD = {'Salesforce - Slack Enterprise':'COGS','Salesforce - Slack Internal':'Non-COGS',
          'Salesforce - Certification Exams':'COGS','Salesforce - Tableau Cloud':'Non-COGS',
          'Salesforce - Sales Cloud Enterprise':'Non-COGS'}
FORCE_NONCOGS_OLD = {'Airtable','Twilio','Pumble','Mailgun'}
# The pre-review pipeline lumped Pearson VUE into CompTIA (COGS) and Sales Navigator into
# LinkedIn (Non-COGS); reproduce that here so the OLD splits regress against the published baseline.
OLD_OVERRIDES = {'Pearson VUE (Exam Vouchers)':'COGS','LinkedIn Sales Navigator':'Non-COGS'}
cls_new_names = {O2N.get(k,k): v for k,v in clstab.items()}
att_flag = {}
for k,v in apptot.items():
    n = O2N.get(k,k)
    if n not in att_flag or att_flag[n] is None:
        try: att_flag[n] = float(v['cogs'])
        except (TypeError,ValueError): att_flag[n] = None

def old_class(app):
    if app in OLD_OVERRIDES: return OLD_OVERRIDES[app]
    if app in SF_OLD: return SF_OLD[app]
    if app in FORCE_NONCOGS_OLD: return 'Non-COGS'
    if app in cls_new_names:
        return 'COGS' if cls_new_names[app]['cogs'].strip().upper()=='COGS' else 'Non-COGS'
    if att_flag.get(app) is not None:
        return 'COGS' if att_flag[app]==1.0 else 'Non-COGS'
    return 'COGS' if acct_by_app[app] & {53000,55000} else 'Non-COGS'

# ---- NEW classification: review sheet Final Classification (sole source) ----
REVIEW = {  # transcribed from "SaaS COGS / Non-COGS Classification Review - 2026 YTD", Final Classification column
 'Google Cloud Platform':'COGS','CompTIA':'COGS','Salesforce - Slack Enterprise':'COGS','Codio':'COGS',
 'Google Workspace':'Non-COGS','Salesforce - Certification Exams':'COGS','Calendly':'COGS','Worksuite':'COGS',
 'Claude':'Non-COGS','Zoom':'COGS','Okta':'COGS','1Password':'Non-COGS','Airtable':'COGS','SurveyMonkey':'COGS',
 'HubSpot':'Non-COGS','Twilio':'COGS','Pumble':'COGS','Profound':'Non-COGS','Zendesk':'COGS','Sentry':'Non-COGS',
 'Salesforce - Slack Internal':'Non-COGS','Mailchimp':'COGS','MindHub':'COGS','Greenhouse':'Non-COGS',
 'Accredible':'COGS','ChatGPT':'Non-COGS','Salesforce - Tableau Cloud':'Non-COGS','Outreach':'Non-COGS',
 'Maxio (formerly SaaSOptics)':'Non-COGS','Adobe':'Non-COGS','Carta':'Non-COGS','ApprentiScope':'COGS',
 'Notion':'Non-COGS','LinkedIn':'Non-COGS','Atlassian':'Non-COGS','Lovable':'Non-COGS','Microsoft':'Non-COGS',
 'ZoomInfo':'Non-COGS','BambooHR':'Non-COGS','Workforce':'Non-COGS','Culture Amp':'Non-COGS','GitHub':'Non-COGS',
 'Cursor':'Non-COGS','Hireflix':'Non-COGS','Pearson VUE (Exam Vouchers)':'COGS','Tremendous':'COGS',
 'Yesware':'Non-COGS','LaunchDarkly':'Non-COGS','PayPal':'Non-COGS','Figma':'Non-COGS','Squadcast':'Non-COGS',
 'Typeform':'COGS','Zapier':'Non-COGS','Refiner':'Non-COGS','DeepSource':'Non-COGS','Hook Security':'Non-COGS',
 'Gamma':'Non-COGS','Artillery':'Non-COGS','Paddle':'Non-COGS','Amazon Web Services':'COGS','Hex':'Non-COGS',
 'Loom':'Non-COGS','QuickBooks':'Non-COGS','Apollo':'Non-COGS','DNSimple':'Non-COGS','CoderPad':'Non-COGS',
 'Geocode':'Non-COGS','GoDaddy':'Non-COGS','Mailgun':'COGS','Artisan':'Non-COGS','Tango':'Non-COGS',
 'Perplexity AI':'Non-COGS','DocuSign':'Non-COGS','Stape':'Non-COGS','Vercel':'Non-COGS','PlusDocs':'Non-COGS',
 'Linear':'Non-COGS','HireRight':'Non-COGS','LinkedIn Sales Navigator':'Non-COGS','Dmarcian':'Non-COGS',
 'Guidde':'Non-COGS','HelixPay':'Non-COGS','Fal':'Non-COGS','DigitalOcean':'Non-COGS','Squarespace':'Non-COGS'}
json.dump(REVIEW, open('inputs/review_classification.json','w'), indent=1)

flags = []
def new_class(app):
    if app in REVIEW: return REVIEW[app], 'Review sheet'
    d = 'COGS' if acct_by_app[app] & {53000,55000} else 'Non-COGS'
    flags.append(dict(app=app, issue='NOT IN REVIEW SHEET - classification defaulted from GL account', defaulted=d,
                      accounts=sorted(acct_by_app[app]), h1_jul=round(sum(mat[app].values()),2)))
    return d, 'GL-account default (FLAGGED)'

# ---- splits ----
print('='*88)
print(f"{'':6}{'TOTAL':>13} | {'OLD COGS':>11}{'OLD NonC':>11} | {'NEW COGS':>11}{'NEW NonC':>11} | {'COGS shift':>11}")
base_t = {'Jan':151655.48,'Feb':157003.65,'Mar':163215.17,'May':146127.40}
base_c = {'Jan':72751.42,'Feb':75675.89,'Mar':82324.86,'May':62339.02}
oldmap = {a: old_class(a) for a in mat}
newmap, newsrc = {}, {}
for a in mat:
    newmap[a], newsrc[a] = new_class(a)
summary = {}
ok = True
for m in MONTHS:
    t  = sum(v[m] for v in mat.values())
    oc = sum(v[m] for a,v in mat.items() if oldmap[a]=='COGS')
    nc = sum(v[m] for a,v in mat.items() if newmap[a]=='COGS')
    summary[m] = dict(total=round(t,2), old_cogs=round(oc,2), old_non=round(t-oc,2),
                      new_cogs=round(nc,2), new_non=round(t-nc,2))
    reg = ''
    if m in base_c:
        dt, dc = round(t-base_t[m],2), round(oc-base_c[m],2)
        reg = f'   REG total {dt:+.2f} cogs {dc:+.2f}'
        if abs(dt)>0.02 or abs(dc)>0.02: ok = False; reg += '  <<< FAIL'
    print(f"{m:6}{t:>13,.2f} | {oc:>11,.2f}{t-oc:>11,.2f} | {nc:>11,.2f}{t-nc:>11,.2f} | {nc-oc:>+11,.2f}{reg}")
print('REGRESSION:', 'all verified months match to the cent' if ok else '!!! MISMATCH — DO NOT SHIP')

# ---- classification flips (apps whose class changed), with 2026 spend impact ----
print('\nApps whose classification CHANGED (old -> new), by Jan-Jul spend:')
for a in sorted(mat, key=lambda x: -sum(mat[x].values())):
    if oldmap[a]!=newmap[a]:
        print(f"  {a:<36} {oldmap[a]:>8} -> {newmap[a]:<8}  Jan-Jul {sum(mat[a].values()):>11,.2f}")

# ---- 10-month activity filter (Oct25..Jul26) ----
print('\n--- 10-month inactivity check (window Oct 2025 - Jul 2026) ---')
active = set(a for a in mat if any(abs(v)>0.005 for v in mat[a].values()))
active |= set(a for a in act25 if any(abs(v)>0.005 for v in act25[a].values()))
universe = set()
for k in list(apptot.keys()) + list(clstab.keys()):
    universe.add(O2N.get(k,k))
universe |= set(mat.keys())
universe.discard('__UNRESOLVED__'); universe.discard('__WONDER__'); universe.discard('Wonder')
dropped = sorted(universe - active)
print(f'universe={len(universe)}  active(10mo)={len(universe)-len(dropped)}  dropped={len(dropped)}')
print('DROPPED (no spend in any of the last 10 months):')
for a in dropped: print('   -', a)

json.dump(dict(matrix={a:mat[a] for a in mat}, old=oldmap, new=newmap, newsrc=newsrc,
               summary=summary, dropped=dropped, flags=flags,
               activity25={a:act25.get(a,{}) for a in mat}),
          open('inputs/classified.json','w'), indent=1)
print('\nFlags:', len(flags))
for f in flags: print('  ', f['app'], '->', f['defaulted'], f'(Jan-Jul {f["h1_jul"]:,.2f}, accts {f["accounts"]})')
