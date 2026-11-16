# Builds the whole static site. Edit APPS / PUBLISHER here, run `python3 scripts/build.py`, commit.
# Generates: index.html, /<slug>/index.html (app page), /<slug>/privacy.html, /<slug>/support.html, 404.html,
# and re-wraps the hand-written <main> of privacy.html and support.html in the shared header and footer.
import pathlib, re, html, hashlib

# Cache-busting: every /assets/... image gets ?v=<content hash>, so a replaced screenshot shows at once.
def _bust(text):
    def rep(m):
        f = ROOT / m.group(1).lstrip("/")
        return f'src="{m.group(1)}?v={hashlib.sha1(f.read_bytes()).hexdigest()[:8]}"' if f.exists() else m.group(0)
    return re.sub(r'src="(/assets/[^"?]+)"', rep, text)
_write = pathlib.Path.write_text
pathlib.Path.write_text = lambda self, data, *a, **k: _write(self, _bust(data) if self.suffix == ".html" else data, *a, **k)

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLISHER = "Compora Pte. Ltd."
EMAIL = "support@plainsailapps.com"
UPDATED = "15 November 2026"
EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"

# Inline stroke icons (24x24), referenced by name below.
ICONS = {
  "receipt": '<path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
  "receipt-tick": '<path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 11l2 2 4-4"/>',
  "list": '<path d="M4 6h16M4 12h16M4 18h10"/>',
  "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21h4"/>',
  "lock": '<rect x="3" y="10" width="18" height="11" rx="2"/><path d="M7 10V7a5 5 0 0 1 10 0v3"/>',
  "download": '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 21h16"/>',
  "phone": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/>',
  "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  "box": '<path d="M3 7l9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7"/><path d="M12 11v10"/>',
  "camera": '<path d="M4 7h3l2-3h6l2 3h3v13H4z"/><circle cx="12" cy="13" r="4"/>',
  "pen": '<path d="M4 20c3-1 4-4 6-4s2 3 5 3 4-3 5-4"/><path d="M15 4l5 5-8 8H7v-5z"/>',
  "copy": '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V4H3v13h5"/>',
  "wifi-off": '<path d="M2 8.5a15 15 0 0 1 20 0"/><path d="M5 12a10 10 0 0 1 14 0"/><circle cx="12" cy="17" r="1.5"/><path d="M3 3l18 18"/>',
  "shield": '<path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
  "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  "book": '<path d="M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-4a2 2 0 0 0-2 2"/><path d="M20 4v14h-6"/>',
  "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  "tablet": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M11 18h2"/>',
  "jar": '<path d="M8 3h8M7 6h10"/><path d="M7 6c-2 1-3 3-3 6v6a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3v-6c0-3-1-5-3-6"/><circle cx="12" cy="14" r="3"/>',
  "check": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 12l3 3 5-6"/>',
  "users": '<circle cx="9" cy="8" r="4"/><path d="M2 21c1-4 4-6 7-6s6 2 7 6"/><path d="M16 4a4 4 0 0 1 0 8M22 21c-.6-2.4-2-4-4-5"/>',
  "coin": '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .9-3 2s1.3 1.7 3 2 3 .9 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6v2M12 16v2"/>',
  "user-off": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/><path d="M3 3l18 18"/>',
  "note": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  "flame": '<path d="M12 22c4 0 7-3 7-7 0-5-4-7-5-12-2 2-3 4-3 6-1-1-2-2-2-4-2 2-4 5-4 10 0 4 3 7 7 7z"/>',
  "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  "ad-off": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 3l18 18"/>',
}

def svg(name, cls="", stroke="currentColor", size=None):
    s = f' width="{size}" height="{size}"' if size else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c}{s} viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

COMMON_FAQ = [
  ("Do I need an account?", "No. Open the app and start. There's nothing to sign up for."),
  ("Where is my information kept?", "Only on your device. We have no server and can't see it."),
  ("Does it work on iPad and Android tablets?", "Yes. The same app runs on iPhone, iPad, Android phones and Android tablets."),
]

APPS = [
  dict(slug="financekids", who_title="For P1 to P5 children and their parents.", name="FinanceKids", subtitle="Five minutes a day of money habits, for primary school",
       accent="#5B52C7", soft="#ECEBFA", icon=None, icon_svg="coin",
       status="In testing", platforms="iPhone & iPad", ios_only=True, store_label="In testing for",
       cta="FinanceKids is in testing now, on iPhone and iPad.", privacy_custom=True, own_faq_only=True,
       support_data="FinanceKids is a simulation and never handles real money.",
       short="A daily money-habits game for Singapore primary-school children, P1 to P5. Each day is a short lesson, a quiz and a challenge, hosted by Finn the Fox.",
       chips=["Ages 7 to 11", "5 minutes a day", "Parent area with PIN"],
       h1="Money habits, five minutes a day.",
       lead="A short lesson, a quiz and a daily challenge, hosted by Finn the Fox. Keep the streak going and your pet grows. Made for Singapore primary-school children from P1 to P5.",
       price_line="In testing on iPhone and iPad",
       shots=[("screen-1.webp", 'Say hi to Finn', 'Finn greets your child and shows their level.'),
              ("screen-2.webp", 'Short lessons with Finn', 'Singapore coins and notes, one idea at a time.'),
              ("screen-3.webp", 'A quiz after every lesson', 'Instant feedback, with coins and XP to earn.'),
              ("screen-4.webp", 'A dashboard for parents', 'Lessons passed, streak, average score and class level.')],
       features=[("book", "30 lessons", "Bite-sized money lessons that build from P1 to P5."),
                 ("check", "A quiz every day", "Check what stuck, with Finn the Fox cheering them on."),
                 ("target", "360 daily challenges", "A fresh money challenge each day, so it never repeats too soon."),
                 ("flame", "A pet that grows", "Keep the daily streak going and the pet grows with it."),
                 ("lock", "Grown-ups area", "Progress for parents, behind a PIN."),
                 ("users", "Talk about it at home", "A conversation prompt for every lesson, to chat through together.")],
       who="Children in Singapore primary schools, from P1 to P5 (ages 7 to 11), and the parents who want them to grow up confident with money. It's simulation only and never handles real money.",
       prices=[], price_note="Pricing will be announced at launch.",
       faq=[("Does it use real money?", "No. FinanceKids is a simulation. It never handles real money and never connects to a bank."),
            ("How long does it take each day?", "About five minutes: one short lesson, a quiz and the daily challenge.")],
       disclaimer="FinanceKids is an educational game. It does not handle real money or give financial advice.",
       what="", stored="", extra=""),
  dict(slug="aigovernanceprep", who_title="For anyone sitting the AIGP exam.", name="AI Governance Prep", subtitle="AIGP exam practice questions",
       accent="#0957EC", soft="#E3ECFD", icon=None, icon_svg="shield",
       short="500 original, scenario-based questions mapped to the current AIGP Body of Knowledge, with an explanation for every right and wrong answer. Practise by domain or sit full mock exams.",
       chips=["iPhone, iPad & Android", "30 free questions", "Five mock exams"],
       h1="Walk into the AIGP exam ready.",
       lead="Original, scenario-based practice questions for the IAPP AI Governance Professional exam, with clear explanations that teach the reasoning, not just the answer.",
       price_line="30 free questions · then $9.99 a month",
       shots=[("screen-1.webp", 'Everything from one home screen', 'Practice, mock exams, review and progress.'),
              ("screen-2.webp", 'Scenario-based questions', 'Practise all four domains or one at a time.'),
              ("screen-3.webp", 'Every answer explained', "Why the right answer is right, and why yours wasn't."),
              ("screen-4.webp", 'Simple plans', '$9.99 a month or $24.99 for three months.')],
       features=[("book", "500 original questions", "Written from scratch and mapped to the AIGP Body of Knowledge."),
                 ("target", "Practise by domain", "Focus on the areas you find hardest, one domain at a time."),
                 ("clock", "Full mock exams", "Five 100-question timed exams with no repeated questions."),
                 ("check", "Every answer explained", "Learn why the right answer is right and why the others are wrong."),
                 ("chart", "Progress by domain", "See your scores improve and where to spend your study time."),
                 ("tablet", "Study anywhere", "iPhone, iPad and Android, and it works offline.")],
       who="People preparing for the IAPP AIGP certification: privacy, risk, compliance, legal and technology professionals who need to understand how AI is governed. Questions for ISACA's AAISM and AAIA exams will be added to the same app later.",
       prices=[("Free", "$0", "", "30 sample questions across all four domains."),
               ("Monthly", "$9.99", "/month", "Every question, every mock exam."),
               ("3 months", "$24.99", "", "Enough time to prepare, at a lower price.", "Best value")],
       price_note="Prices in US dollars; your store shows your local price. Subscriptions renew automatically and can be cancelled in your App Store or Google Play settings.",
       faq=[("Are these real exam questions?", "No. Every question is original and written for practice. We never use or copy questions from the real exam or the official practice exam.")],
       disclaimer="AI Governance Prep is an independent study aid and is not affiliated with, endorsed by or sponsored by the IAPP or ISACA. AIGP is a trademark of the IAPP; AAISM and AAIA are trademarks of ISACA.",
       what="practice questions and mock exams for AI governance certifications",
       stored="your answers, scores, flagged questions and mock exam results", extra=""),
  dict(slug="chorejar", who_title="For parents who want help around the house.", name="Chore Jar", subtitle="Kids' chores & pocket money",
       accent="#C1305F", soft="#FBE3EA", icon=None, icon_svg="jar",
       short="A chore chart that pays out. Kids tick off their jobs, pocket money follows the rules you set, and balances stay behind a parent PIN.",
       chips=["Chore chart", "Pocket money rules", "Parent PIN"],
       h1="Chores done. Pocket money earned.",
       lead="A chore chart and a piggy bank in one. Set the daily jobs and the rules once, and every tick goes towards your child's pocket money.",
       price_line="Coming soon to the App Store and Google Play",
       shots=[("screen-1.webp", 'A week of chores per child', "What they've earned, and how many ticks to go."),
              ("screen-2.webp", 'Tick off each day', 'Every-day chores and paid extras, Monday to Sunday.'),
              ("screen-3.webp", 'Grown-ups behind a PIN', 'Children can tick; only parents handle the money.'),
              ("screen-4.webp", 'A passbook for every child', 'Money in, money out, and a savings goal.')],
       features=[("check", "Chores first", "The app opens on today's chores, so ticking one off takes a second."),
                 ("coin", "Pocket money that follows your rules", "Pay a weekly amount when chores are done, with bonuses for a perfect week."),
                 ("jar", "A jar for each child", "Every child sees what they've earned and what they're saving for."),
                 ("lock", "Balances behind a PIN", "Grown-ups manage money behind a parent PIN."),
                 ("users", "The whole household can tick", "Parents, grandparents or a helper can mark chores done on the same device."),
                 ("phone", "Private and offline", "No account, no ads, and nothing leaves your device.")],
       who="Parents who want their children to help around the house and learn that money is earned, without a bank card, an online account or adverts aimed at kids.",
       prices=[], price_note="Pricing will be announced at launch.",
       faq=[("Does my child need a bank account or card?", "No. Chore Jar keeps a record of what you owe each child. You hand over the money however you like.")],
       disclaimer="Chore Jar is a record-keeping app for parents. It does not hold money or connect to a bank.",
       what="tracking children's chores and pocket money for parents",
       stored="your children's first names, chores, ticks, balances and your parent PIN", extra="",
       children="Chore Jar is set up and managed by a parent. Children may tick off their own chores, but the app collects nothing from them: the names and records you enter stay on your device, and nothing is sent to us or to anyone else. There are no adverts and no links out of the app for children to follow."),
  dict(slug="rentreceiptbook", who_title="For small, private landlords.", name="Rent Receipt Book", subtitle="Landlord rent ledger & tracker",
       accent="#06445D", soft="#DCEBF1", icon="icon.webp",
       short="Record a payment in a few taps and send your tenant a numbered, signed PDF receipt. See who has paid at a glance, get a nudge when rent is due, and export a year-end summary for your tax return.",
       chips=["PDF receipts", "Ledger per tenant", "Year-end CSV"],
       h1="Rent receipts in under a minute.",
       lead="Give your tenant proper proof of payment, keep a clean record of every month, and have your rental income ready at tax time.",
       price_line="Free for one property · Pro from $2.99 a month",
       shots=[("screen-1.webp", "All your lets on one screen", "Who's paid, who's due and who's overdue."),
              ("screen-2.webp", "Record a payment", "Period, amount and method are filled in for you."),
              ("screen-3.webp", "A ledger for every tenant", "Paid, late and upcoming months, with each receipt."),
              ("screen-4.webp", "Ready for tax time", "Income per property as a PDF or a spreadsheet.")],
       features=[("receipt", "Numbered PDF receipts", "Period, amount, method, both names, the address and your signature."),
                 ("list", "Ledger per tenant", "Paid, late and outstanding months, all on one screen."),
                 ("bell", "Due-date reminders", "A nudge on your phone when rent is due or overdue."),
                 ("lock", "Deposit receipts", "A separate receipt for the deposit, kept with the tenant."),
                 ("download", "Backup to a file", "Move everything to a new phone with one export file."),
                 ("phone", "Private and offline", "No account, no ads. Your records never leave your device.")],
       who="Private landlords with one to five properties, or a lodger in the spare room, who collect rent by bank transfer or cash and don't want property-management software. Any currency, any country.",
       prices=[("Free", "$0", "", "1 property, 1 tenant and 5 receipts."),
               ("Pro monthly", "$2.99", "/month", "Unlimited properties, tenants and receipts."),
               ("Pro yearly", "$19.99", "/year", "Everything in Pro for less than half the monthly price.", "Best value"),
               ("Lifetime", "$39.99", "", "Pay once and keep Pro for good.")],
       price_note="Prices in US dollars; your store shows your local price. Subscriptions renew automatically and can be cancelled in your App Store or Google Play settings.",
       faq=[("Does it work in my country?", "Yes, in any currency, and every receipt field can be edited. Receipt rules differ by country, so the app doesn't give legal or tax advice.")],
       disclaimer="Receipts are records you create. The app does not give legal or tax advice for any country.",
       what="rent receipts and a rent ledger for small landlords",
       stored="the properties, tenants, payments, receipts and signature you enter",
       extra="If you turn on reminders, the app schedules notifications on your device; nothing is sent to us. If you export a backup file, it is created on your device and goes only where you choose to send or save it."),
  dict(slug="fermata", who_title="For anyone learning an instrument.", name="Fermata: Practice Log", subtitle="Practice timer & log for musicians",
       accent="#8A5A00", soft="#FBF0D9", icon=None, icon_svg="note",
       short="Tap to start timing your practice, tap to stop. See your streak, your weekly totals and a calendar of the days you played.",
       chips=["One-tap timer", "Streaks", "Weekly totals"],
       h1="Practise more. Know you did.",
       lead="A one-tap practice timer and log. Every session is saved with notes and a rating, so you can see your streak and how much you really played this week.",
       price_line="Free to use · Pro US$4.99 once",
       shots=[("screen-1.webp", 'Today at a glance', 'Minutes against your goal, and your streak.'),
              ("screen-2.webp", 'One-tap timer', 'Tap to start, tap to stop.'),
              ("screen-3.webp", 'Log a session', 'Length, instrument, a rating and a note.'),
              ("screen-4.webp", 'See your progress', 'This week, your streaks and the last five weeks.')],
       features=[("clock", "One-tap timer", "Tap to start, tap to stop. The session is logged for you."),
                 ("flame", "Streaks", "See how many days in a row you've played."),
                 ("chart", "Weekly totals", "Minutes practised this week against your goal."),
                 ("calendar", "Practice calendar", "Every day you played, at a glance."),
                 ("note", "Notes and ratings", "Jot down what you worked on and how it went, per instrument."),
                 ("download", "Export to CSV", "Take your practice log to a spreadsheet or a teacher.")],
       who="Students, adult learners and working musicians who want a simple record of their practice, without an account, a social feed or adverts.",
       prices=[("Free", "$0", "", "Timer, streaks, goals, reminders and your last 30 days of practice."),
               ("Pro", "$4.99", "once", "Full history, a 6-month calendar, all-time totals, top pieces and CSV export.", "One-time")],
       price_note="Prices in US dollars; your store shows your local price. Pro is a one-time purchase, not a subscription, and can be shared with your family.",
       faq=[("Can I log more than one instrument?", "Yes. Add each instrument once and pick it when you start a session.")],
       disclaimer="",
       what="timing and logging music practice",
       stored="your practice sessions, notes, ratings, instruments, goals and settings",
       extra="If you turn on the daily reminder, the app schedules a notification on your device; nothing is sent to us. If you export your practice log as a CSV file, it goes only where you choose to send or save it."),
  dict(slug="jobsheetpad", who_title="For sole traders and small firms.", name="Job Sheet Pad", subtitle="Daywork sheets & signatures",
       accent="#282F3B", soft="#E4E7EC", icon="icon.webp",
       short="Replace the paper pad in the van. Log labour, materials and before-and-after photos, get the customer to sign on screen, and send a tidy PDF before you leave site, even with no signal.",
       chips=["Day work & price work", "Photos & signature", "Fully offline"],
       h1="Signed job sheets, done on site.",
       lead="Log the hours and the materials, take before-and-after photos and get the customer's signature on screen. Send a tidy PDF before you've packed up the van.",
       price_line="5 free job sheets · Pro from $4.99 a month",
       shots=[("screen-1.webp", "Every job in one list", "Search by customer, site or job number."),
              ("screen-2.webp", "Day work or price work", "Start and finish times, or a fixed price."),
              ("screen-3.webp", "Signed on screen", "The customer signs, and the totals add up for you."),
              ("screen-4.webp", "Saved materials", "Your usual parts and prices, ready to reuse.")],
       features=[("clock", "Labour your way", "Hours, start and finish times or price work, per person."),
                 ("box", "Materials with markup", "Quantity, unit price and an optional markup on each line."),
                 ("camera", "Before and after photos", "Attach photos to the sheet as proof of the work."),
                 ("pen", "Customer signature", "Signed on screen with printed name and date."),
                 ("copy", "Repeat jobs in a tap", "Duplicate a past sheet and saved customers for quick reuse."),
                 ("wifi-off", "Works with no signal", "Everything stays on your phone. No account, no ads.")],
       who="Self-employed tradespeople and one- or two-person firms (builders, joiners, plumbers, electricians, heating engineers, locksmiths, handymen and landscapers) who fill in a paper pad today and don't want a full job-management platform.",
       prices=[("Free", "$0", "", "5 completed job sheets, with every feature."),
               ("Pro monthly", "$4.99", "/month", "Unlimited job sheets."),
               ("Pro yearly", "$34.99", "/year", "Everything in Pro, about five months free.", "Best value"),
               ("Lifetime", "$79.99", "", "Pay once and keep Pro for good.")],
       price_note="Prices in US dollars (UK: £3.99 a month, £27.99 a year, £64.99 lifetime); your store shows your local price. Subscriptions renew automatically and can be cancelled in your App Store or Google Play settings.",
       faq=[("Does it add VAT or GST?", "Yes, if you turn it on. Set your rate once and every sheet adds it for you.")],
       disclaimer="",
       what="job sheets with labour, materials, photos and customer signatures for tradespeople",
       stored="your business details, customers, job sheets, photos and signatures",
       extra="Photos are taken or chosen only when you ask, and stay in the app on your device. If you export a backup file or share a PDF, it goes only where you choose to send or save it."),
]

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M15 3 L15 23 L5 23 Z" fill="#1F6F8B"/>'
        '<path d="M17 7 L17 23 L26 23 Z" fill="#7FB3C4"/><path d="M4 26 H28 L25 29 H7 Z" fill="#0B1B2B"/></svg>')

WORDS = {3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}

def head(title, desc, style=""):
    st = f' style="{style}"' if style else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta name="theme-color" content="#0B1B2B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
</head>
<body{st}>
<header class="site"><div class="wrap">
  <a class="brand" href="/">{LOGO}Plainsail Apps</a>
  <nav class="site" aria-label="Main"><a href="/#apps">Apps</a><a href="/support.html">Support</a><a href="/privacy.html">Privacy</a><a class="pill" href="mailto:{EMAIL}">Contact us</a></nav>
</div></header>
"""

def foot(extra_links=""):
    return f"""<footer class="site"><div class="wrap">
  <nav aria-label="Footer">{extra_links}<a href="/support.html">Support</a><a href="/privacy.html">Privacy Policy</a><a href="{EULA}">Terms of Use</a><a href="mailto:{EMAIL}">{EMAIL}</a></nav>
  <div>&copy; 2026 {PUBLISHER}, Singapore</div>
</div></footer>
</body>
</html>
"""

def style_vars(a):
    return f"--accent:{a['accent']};--accent-soft:{a['soft']};--accent-ink:#ffffff"

def icon(a, cls="icon", size=64):
    if a.get("icon"):
        return f'<img class="{cls}" src="/assets/{a["slug"]}/{a["icon"]}" width="{size}" height="{size}" alt="">'
    r = round(size * .25)
    return (f'<span class="{cls}" style="display:inline-flex;align-items:center;justify-content:center;width:{size}px;height:{size}px;'
            f'border-radius:{r}px;background:{a["accent"]};color:#fff">{svg(a["icon_svg"], size=round(size*.55))}</span>')

def phone(a, i=0, lazy=True):
    if a["shots"]:
        f, t, _ = a["shots"][i]
        ld = ' loading="lazy"' if lazy else ""
        return f'<div class="phone"><img src="/assets/{a["slug"]}/{f}" width="390" height="844" alt="{a["name"]}: {html.escape(t)}"{ld}></div>'
    return (f'<div class="phone placeholder"><div style="flex-direction:column;align-items:center;justify-content:center;gap:16px;background:#fff">'
            f'{icon(a, "icon", 88)}<span>Screens coming soon</span></div></div>')

def index():
    promises = [("user-off", "No account to create"), ("ad-off", "No adverts, ever"), ("phone", "Data stays on your device"), ("wifi-off", "Works offline")]
    pr = "".join(f'<div class="promise">{svg(i)}{t}</div>' for i, t in promises)
    rrb, jsp = APPS[1], APPS[2]
    cards = ""
    for a in APPS:
        chips = "".join(f"<span>{html.escape(c)}</span>" for c in a["chips"])
        cards += f"""
    <a class="card" href="/{a['slug']}/" style="{style_vars(a)}">
      <div class="card-copy">
        <div class="app-id">{icon(a)}<div><strong>{a['name']}</strong><span>{html.escape(a['subtitle'])}</span></div></div>
        <p>{html.escape(a['short'])}</p>
        <div class="chips">{chips}</div>
        <div class="status">{html.escape(a.get("status", "Coming soon to the App Store and Google Play"))}</div>
        <div class="more">Explore {a['name']} →</div>
      </div>
      <div class="card-art" aria-hidden="true">{phone(a, 0)}</div>
    </a>"""
    names = ", ".join(a["name"] for a in APPS)
    return head("Plainsail Apps: simple apps that do one job brilliantly",
                f"Simple, private mobile apps for iPhone, iPad and Android: {names}. No accounts, no ads, your data stays on your device.") + f"""
<main>
  <section class="hero"><div class="wrap">
    <div class="hero-copy">
      <p class="eyebrow">Mobile apps for iPhone, iPad and Android</p>
      <h1>Simple apps that do one job brilliantly.</h1>
      <p class="lead">Exam prep, rent receipts, job sheets, pocket money, music practice and money lessons for kids. Each app is built for one kind of person and one task, and works without an account, an advert or a signal.</p>
      <div class="btns"><a class="btn" href="#apps">See the apps</a><a class="btn ghost" href="#how">How we treat your data</a></div>
    </div>
    <div class="hero-shots" aria-hidden="true">
      <div class="phone"><img src="/assets/rentreceiptbook/screen-1.webp" width="390" height="844" alt=""></div>
      <div class="phone"><img src="/assets/jobsheetpad/screen-3.webp" width="390" height="844" alt=""></div>
      <div class="phone"><img src="/assets/rentreceiptbook/screen-3.webp" width="390" height="844" alt=""></div>
    </div>
  </div></section>

  <section class="promises"><div class="wrap">{pr}</div></section>

  <section class="section" id="apps"><div class="wrap">
    <p class="eyebrow">The apps</p>
    <h2>{WORDS[len(APPS)]} tools, each built around one job.</h2>
    <div class="cards">{cards}
    </div>
  </div></section>

  <section class="section dark" id="how"><div class="wrap">
    <h2>Built the plain way, on purpose.</h2>
    <div class="cols">
      <div><h3>Private by design</h3><p>No accounts, no ads, no tracking. What you type stays on your phone or tablet. The one exception is FinanceKids, which sends anonymous usage counts and a streak backup, and says exactly what in its own policy. <a href="/privacy.html" style="color:#fff">Read the privacy policy</a>.</p></div>
      <div><h3>Fair, clear pricing</h3><p>Try each app free first. Pay through the App Store or Google Play, and cancel there whenever you like.</p></div>
      <div><h3>Every screen size</h3><p>One app for iPhone, iPad, Android phones and Android tablets, so you can use whichever device is to hand.</p></div>
    </div>
  </div></section>
</main>
""" + foot()

def stores(a):
    st = a.get("store_label", "Coming soon to")
    out = f'<span class="store"><small>{st} the</small>App Store</span>'
    if not a.get("ios_only"): out += f'<span class="store"><small>{st}</small>Google Play</span>'
    return out

def app_page(a):
    s = a["slug"]
    shots = ""
    if a["shots"]:
        figs = "".join(f'<figure class="shot">{phone(a, i)}<figcaption><strong>{html.escape(t)}</strong><span>{html.escape(c)}</span></figcaption></figure>'
                       for i, (f, t, c) in enumerate(a["shots"]))
        shots = f"""
  <section class="section" id="screens"><div class="wrap">
    <p class="eyebrow">See it in action</p>
    <h2>{len(a['shots'])} screens, one job.</h2>
    {'<p class="preview-note">Design preview. The finished app may look a little different.</p>' if a.get('preview') else ''}
    <div class="shots">{figs}</div>
  </div></section>"""
    feats = "".join(f'<div class="feature">{svg(i)}<h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>' for i, t, d in a["features"])
    prices = ""
    if a["prices"]:
        cells = ""
        for p in a["prices"]:
            name, amt, per, desc = p[:4]; badge = p[4] if len(p) > 4 else ""
            b = f'<span class="badge">{badge}</span>' if badge else ""
            cells += (f'<div class="price{" best" if badge else ""}"><div class="name"><span>{name}</span>{b}</div>'
                      f'<div class="amt">{amt}<small>{" " + per if per else ""}</small></div><p>{html.escape(desc)}</p></div>')
        prices = f"""
  <section class="section" id="pricing"><div class="wrap">
    <h2>Start free. Upgrade when you need more.</h2>
    <div class="prices">{cells}</div>
    <p class="fine">{html.escape(a['price_note'])}</p>
  </div></section>"""
    faqs = a["faq"] + ([] if a.get("own_faq_only") else COMMON_FAQ) + ([] if a.get("own_faq_only") else [("How do I restore a purchase or cancel?",
            f'Restore purchases is in the app\'s Settings. Subscriptions are cancelled in your App Store or Google Play account. <a href="/{s}/support">More help</a>')])
    faq = "".join(f"<details><summary>{html.escape(q)}</summary><p>{ans if '<a' in ans else html.escape(ans)}</p></details>" for q, ans in faqs)
    disc = f'<p class="disclaimer">{html.escape(a["disclaimer"])}</p>' if a["disclaimer"] else ""
    hero_art = phone(a, 0, lazy=False)
    return head(f"{a['name']}: {a['subtitle']}", f"{a['name']} for iPhone, iPad and Android. {a['short']}", style_vars(a)) + f"""
<main>
  <section class="app-hero"><div class="wrap">
    <div class="copy">
      <div class="app-id">{icon(a, "bigicon", 84)}<div class="tagline">{a['name']}<br>For {html.escape(a.get('platforms', 'iPhone, iPad & Android'))}</div></div>
      <h1>{html.escape(a['h1'])}</h1>
      <p class="lead">{html.escape(a['lead'])}</p>
      <div class="btns">
        {stores(a)}
      </div>
      <p class="note">{html.escape(a['price_line'])}</p>
    </div>
    <div class="art" aria-hidden="true">{hero_art}</div>
  </div></section>
{shots}
  <section class="section tint" id="features"><div class="wrap">
    <h2>Everything it needs. Nothing it doesn't.</h2>
    <div class="features">{feats}</div>
  </div></section>

  <section class="section"><div class="wrap">
    <p class="eyebrow">Who it's for</p>
    <h2>{html.escape(a['who_title'])}</h2>
    <p class="who">{html.escape(a['who'])}</p>
  </div></section>
{prices}
  <section class="section tint" id="faq"><div class="wrap faq">
    <h2 style="margin-bottom:32px">Questions</h2>
    {faq}
    {disc}
  </div></section>

  <section class="cta"><div class="wrap">
    <h2>{html.escape(a.get('cta', a['name'] + ' is coming soon to the App Store and Google Play.'))}</h2>
    <a class="btn ghost" href="mailto:{EMAIL}?subject={a['name'].replace(' ', '%20')}">Ask us a question</a>
  </div></section>
</main>
""" + foot(f'<a href="/">All apps</a><a href="/{s}/support">{a["name"]} support</a>' + (f'<a href="/{s}/privacy">{a["name"]} privacy</a>' if a.get("privacy_ready", True) else ""))

def doc(title, desc, body, a=None):
    style = style_vars(a) if a else ""
    crumb = f'<p class="crumb"><a href="/{a["slug"]}/">← {a["name"]}</a></p>' if a else ""
    return head(title, desc, style) + f'<main class="doc"><div class="wrap">\n{crumb}{body}\n</div></main>\n' + foot()

def privacy(a):
    return doc(f"{a['name']}: Privacy Policy", f"Privacy policy for {a['name']}.", f"""<h1>{a['name']}: Privacy Policy</h1>
<p class="muted">Last updated {UPDATED}. Publisher: {PUBLISHER}, Singapore.</p>
<p>{a['name']} is an app for {a['what']}.</p>
<h2>What we collect</h2>
<p>Nothing. The app has no accounts, no analytics, no advertising and no server. Everything you enter, including {a['stored']}, is stored only on your device. It is deleted when you delete the app.</p>
{f"<p>{a['extra']}</p>" if a['extra'] else ""}
<h2>Purchases</h2>
<p>Subscriptions and purchases are handled entirely by Apple (App Store) or Google (Google Play). We do not receive your name, email address or payment details. The app only asks the store whether your purchase is active.</p>
<h2>Children</h2>
<p>{a.get("children", "The app is intended for adults and does not knowingly collect information from anyone.")}</p>
<h2>Changes</h2>
<p>If this policy changes, the new version will be posted on this page with a new date.</p>
<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
{f'<p class="muted">{a["disclaimer"]}</p>' if a['disclaimer'] else ""}""", a)

def support(a):
    return doc(f"{a['name']}: Support", f"Help and support for {a['name']}.", f"""<h1>{a['name']}: Support</h1>
<p>Need help, found a problem or have a suggestion? Email <a href="mailto:{EMAIL}?subject={a['name'].replace(' ','%20')}">{EMAIL}</a> and include the app name, your device and what happened. We usually reply within two working days.</p>
<h2>Subscriptions</h2>
<ul><li><b>Restore purchases:</b> open the app's Settings and tap Restore purchases.</li>
<li><b>Cancel or change a subscription:</b> on iPhone or iPad, go to Settings, tap your name, then Subscriptions. On Android, open Google Play, tap your profile, then Payments &amp; subscriptions.</li>
<li><b>Refunds</b> are handled by Apple or Google under their own policies.</li></ul>
<h2>Your data</h2>
<p>{a.get("support_data", "Your data stays on your device. We can't see it, so we can't recover it if the app is deleted.")} Read the <a href="{'/' + a['slug'] + '/privacy' if a.get('privacy_ready', True) else '/privacy.html'}">privacy policy</a>.</p>
{f'<p class="muted">{a["disclaimer"]}</p>' if a['disclaimer'] else ""}""", a)

def rewrap(name, title, desc):
    p = ROOT / name
    src = p.read_text()
    m = re.search(r'<main class="doc">\s*<div class="wrap">(.*?)</div>\s*</main>', src, re.S)
    p.write_text(doc(title, desc, m.group(1).strip()))

def rewrap_app_privacy(a):
    p = ROOT / a["slug"] / "privacy.html"
    m = re.search(r'<main class="doc">\s*<div class="wrap">(.*?)</div>\s*</main>', p.read_text(), re.S)
    body = re.sub(r'^<p class="crumb">.*?</p>', "", m.group(1).strip(), flags=re.S)
    p.write_text(doc(f"{a['name']}: Privacy Policy", f"Privacy policy for {a['name']}.", body, a))

(ROOT/"index.html").write_text(index())
for a in APPS:
    d = ROOT/a["slug"]; d.mkdir(exist_ok=True)
    (d/"index.html").write_text(app_page(a))
    if a.get("privacy_custom"): rewrap_app_privacy(a)  # hand-written <main>: this app has a server
    elif a.get("privacy_ready", True): (d/"privacy.html").write_text(privacy(a))
    (d/"support.html").write_text(support(a))
rewrap("privacy.html", "Privacy Policy: Plainsail Apps", "How Plainsail Apps handle your information: no accounts, no ads, no tracking.")
rewrap("support.html", "Support: Plainsail Apps", "Help with Plainsail Apps: purchases, subscriptions, refunds and moving to a new phone.")
(ROOT/"CNAME").write_text("plainsailapps.com\n")
(ROOT/"404.html").write_text(doc("Page not found", "Page not found.", '<h1>Page not found</h1><p><a href="/">Go to the apps</a></p>'))
print("built", len(APPS), "apps")
