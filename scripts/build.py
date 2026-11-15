# Builds the static site. Edit APPS / PUBLISHER here, run `python3 scripts/build.py`, commit.
import pathlib, datetime, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLISHER = "Compora Pte. Ltd."
EMAIL = "support@plainsailapps.com"
UPDATED = "15 November 2026"

APPS = [
  dict(slug="aigovernanceprep", name="AI Governance Prep",
       what="practice questions and mock exams for AI governance certifications",
       stored="your answers, scores, flagged questions and mock exam results",
       extra="", disclaimer="AI Governance Prep is an independent study aid and is not affiliated with, endorsed by or sponsored by the IAPP or ISACA."),
  dict(slug="rentreceiptbook", name="Rent Receipt Book",
       what="rent receipts and a rent ledger for small landlords",
       stored="the properties, tenants, payments, receipts and signature you enter",
       extra="If you turn on reminders, the app schedules notifications on your device; nothing is sent to us. If you export a backup file, it is created on your device and goes only where you choose to send or save it.",
       disclaimer="Receipts are records you create. The app does not give legal or tax advice for any country."),
  dict(slug="jobsheetpad", name="Job Sheet Pad",
       what="job sheets with labour, materials, photos and customer signatures for tradespeople",
       stored="your business details, customers, job sheets, photos and signatures",
       extra="Photos are taken or chosen only when you ask, and stay in the app on your device. If you export a backup file or share a PDF, it goes only where you choose to send or save it.",
       disclaimer=""),
]

CSS = """body{font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;max-width:680px;margin:0 auto;padding:2rem 1.2rem;line-height:1.6;color:#14202B}
h1{font-size:1.6rem;line-height:1.25}h2{font-size:1.1rem;margin-top:1.6rem}a{color:#0957EC}
.muted{color:#5B6875;font-size:.9rem}nav{margin-bottom:1.5rem;font-size:.95rem}ul{padding-left:1.2rem}"""

SHELL = (ROOT/"privacy.html").read_text()
HEAD = SHELL[:SHELL.index('<main')]
FOOT = SHELL[SHELL.index('</main>')+len('</main>'):]

def page(title, body, back=True):
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", HEAD, flags=re.S)
    head = head.replace(' aria-current="page"', '').replace('href="style.css"', 'href="/style.css"').replace('href="favicon.svg"', 'href="/favicon.svg"')
    return f"""{head}<main class="doc"><div class="wrap">
{body}
</div></main>{FOOT}"""

def privacy(a):
    return page(f"{a['name']}: Privacy Policy", f"""<h1>{a['name']}: Privacy Policy</h1>
<p class="muted">Last updated {UPDATED}. Publisher: {PUBLISHER}, Singapore.</p>
<p>{a['name']} is an app for {a['what']}.</p>
<h2>What we collect</h2>
<p>Nothing. The app has no accounts, no analytics, no advertising and no server. Everything you enter, including {a['stored']}, is stored only on your device. It is deleted when you delete the app.</p>
{f"<p>{a['extra']}</p>" if a['extra'] else ""}
<h2>Purchases</h2>
<p>Subscriptions and purchases are handled entirely by Apple (App Store) or Google (Google Play). We do not receive your name, email address or payment details. The app only asks the store whether your purchase is active.</p>
<h2>Children</h2>
<p>The app is intended for adults and does not knowingly collect information from anyone.</p>
<h2>Changes</h2>
<p>If this policy changes, the new version will be posted on this page with a new date.</p>
<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
{f'<p class="muted">{a["disclaimer"]}</p>' if a['disclaimer'] else ""}""")

def support(a):
    return page(f"{a['name']}: Support", f"""<h1>{a['name']}: Support</h1>
<p>Need help, found a problem or have a suggestion? Email <a href="mailto:{EMAIL}?subject={a['name'].replace(' ','%20')}">{EMAIL}</a> and include the app name, your device and what happened. We usually reply within two working days.</p>
<h2>Subscriptions</h2>
<ul><li><b>Restore purchases:</b> open the app's Settings and tap Restore purchases.</li>
<li><b>Cancel or change a subscription:</b> on iPhone or iPad, go to Settings, tap your name, then Subscriptions. On Android, open Google Play, tap your profile, then Payments &amp; subscriptions.</li>
<li><b>Refunds</b> are handled by Apple or Google under their own policies.</li></ul>
<h2>Your data</h2>
<p>Your data stays on your device. We can't see it, so we can't recover it if the app is deleted. Read the <a href="/{a['slug']}/privacy">privacy policy</a>.</p>
{f'<p class="muted">{a["disclaimer"]}</p>' if a['disclaimer'] else ""}""")

def index():
    items = "".join(f'<li><b>{a["name"]}</b>: {a["what"]}. <a href="/{a["slug"]}/privacy">Privacy</a> · <a href="/{a["slug"]}/support">Support</a></li>' for a in APPS)
    return page("Plainsail apps", f"""<h1>Plainsail apps</h1>
<p>Simple, private mobile apps for iPhone, iPad and Android. No accounts, no ads, and your data stays on your device.</p>
<ul>{items}</ul>
<p>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a></p>""", back=False)

for a in APPS:
    d = ROOT/a["slug"]; d.mkdir(exist_ok=True)
    (d/"privacy.html").write_text(privacy(a)); (d/"support.html").write_text(support(a))
(ROOT/"CNAME").write_text("plainsailapps.com\n")
(ROOT/"404.html").write_text(page("Page not found", '<h1>Page not found</h1><p><a href="/">Go to the apps</a></p>'))
print("built", len(APPS), "apps")
