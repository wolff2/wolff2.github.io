"""Publishes guides whose date is today or earlier (UTC), plus the guides index, sitemap.xml and robots.txt."""
import json, datetime, pathlib, html, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://wolff2.github.io"
VERIFY = '<meta name="p:domain_verify" content="78d2c715a4f9c9f269c093ad3d5ba599"/>'
today = datetime.datetime.now(datetime.timezone.utc).date()

PRODUCTS = {
    "bake": dict(name="Home Bakery Business System", page="/shop/home-bakery-system.html", c1="#6b2342", c2="#d9879d",
                 etsy="https://www.etsy.com/listing/4610553452/home-bakery-business-spreadsheet-cake",
                 pitch="Cake pricing calculator, recipe costing, order tracker with deposits, customer message scripts and a profit dashboard, ready in Google Sheets and Excel."),
    "care": dict(name="Family Care Hub", page="/shop/family-care-hub.html", c1="#2f5d50", c2="#c8743a",
                 etsy="https://www.etsy.com/listing/4611107142/family-caregiver-planner-medication-log",
                 pitch="Medication log with refill dates, appointments, care schedule, tasks and a fair cost split between family members, ready in Google Sheets and Excel."),
    "exec": dict(name="Estate Executor Kit", page="/shop/estate-executor-kit.html", c1="#1f3a5f", c2="#b8862f",
                 etsy="https://www.etsy.com/listing/4613051306/estate-executor-checklist-spreadsheet",
                 pitch="54 pre-written executor tasks, accounts to close, estate ledger, beneficiary distribution and 8 letter templates, ready in Google Sheets and Excel."),
}

CSS = """*{box-sizing:border-box;margin:0;padding:0}body{font-family:Georgia,'Times New Roman',serif;color:#1d2430;background:#faf8f5;line-height:1.65}
.w{max-width:760px;margin:0 auto;padding:28px 20px 60px}header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;padding-bottom:18px;border-bottom:1px solid #e6e1d8;margin-bottom:28px}
header a{color:#1d2430;text-decoration:none;font-weight:700;font-size:20px}nav a{font-family:system-ui,sans-serif;font-size:14px;margin-left:14px;color:#555;font-weight:400}
h1{font-size:36px;line-height:1.15;margin:8px 0 14px}h2{font-size:24px;margin:32px 0 10px;color:var(--c1)}p,li,td,th,blockquote{font-family:system-ui,-apple-system,sans-serif;font-size:17px}
p{margin:10px 0}ul,ol{padding-left:24px;margin:10px 0}li{margin:5px 0}.k{font-family:system-ui,sans-serif;letter-spacing:3px;font-size:13px;font-weight:700;color:var(--c2)}
table{border-collapse:collapse;width:100%;margin:14px 0;background:#fff}td,th{border:1px solid #e3ded5;padding:8px 10px;text-align:left;font-size:15px}th{background:#f1ede6}
blockquote{background:#fff;border-left:4px solid var(--c2);padding:12px 16px;margin:12px 0;border-radius:6px}a{color:var(--c1)}
.cta{background:#fff;border:2px solid var(--c1);border-radius:14px;padding:20px 22px;margin:30px 0}.cta b{font-family:Georgia,serif;font-size:21px;display:block;margin-bottom:6px}
.btn{display:inline-block;background:var(--c1);color:#fff!important;font-family:system-ui,sans-serif;font-weight:700;padding:13px 26px;border-radius:40px;text-decoration:none;font-size:17px;margin-top:10px}
.meta{font-family:system-ui,sans-serif;color:#777;font-size:14px}.list a{display:block;background:#fff;border-radius:12px;padding:16px 18px;margin:12px 0;text-decoration:none;color:#1d2430;box-shadow:0 4px 14px rgba(0,0,0,.05)}
.list b{font-family:Georgia,serif;font-size:19px;display:block}.list span{font-family:system-ui,sans-serif;font-size:14px;color:#666}
footer{margin-top:50px;font-family:system-ui,sans-serif;font-size:13px;color:#888}"""

NAV = '<header><a href="/">LumivexaStore</a><nav><a href="/guides/">Guides</a><a href="/shop/home-bakery-system.html">Bakery</a><a href="/shop/family-care-hub.html">Caregiving</a><a href="/shop/estate-executor-kit.html">Executor</a></nav></header>'
FOOT = '<footer>LumivexaStore · Spreadsheet templates for Google Sheets and Excel · <a href="https://www.etsy.com/shop/LumivexaStore">Visit the shop on Etsy</a></footer></div></body></html>'

def page(title, desc, url, c1, c2, body, extra=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">
{VERIFY}<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="article">{extra}
<style>{CSS}</style></head><body style="--c1:{c1};--c2:{c2}"><div class="w">{NAV}{body}{FOOT}"""

def cta(P, where):
    link = P["etsy"] + f"?utm_source=lumivexa_guides&utm_medium=referral&utm_campaign={where}"
    return f'<div class="cta"><b>{P["name"]}</b><p>{P["pitch"]}</p><a class="btn" href="{link}">See it on Etsy →</a></div>'

def build():
    guides = json.loads((ROOT / "data/guides.json").read_text())
    live = [g for g in guides if datetime.date.fromisoformat(g["date"]) <= today]
    out = ROOT / "guides"; out.mkdir(exist_ok=True)
    for g in live:
        P = PRODUCTS[g["product"]]
        body = g["body"]
        h2s = [m.start() for m in re.finditer(r"<h2>", body)]
        if len(h2s) >= 3:  # mid-article box before the third heading
            body = body[:h2s[2]] + cta(P, g["slug"] + "_mid") + body[h2s[2]:]
        url = f"{SITE}/guides/{g['slug']}.html"
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
                         "datePublished": g["date"], "image": f"{SITE}/pins/guide-{g['slug']}.jpg",
                         "author": {"@type": "Organization", "name": "LumivexaStore"}, "mainEntityOfPage": url})
        others = [x for x in live if x["product"] == g["product"] and x["slug"] != g["slug"]]
        more = "".join(f'<a href="/guides/{x["slug"]}.html"><b>{html.escape(x["title"])}</b></a>' for x in others)
        content = (f'<div class="k">GUIDE</div><h1>{html.escape(g["title"])}</h1>'
                   f'<p class="meta">Updated {datetime.date.fromisoformat(g["date"]).strftime("%B %-d, %Y")} · LumivexaStore</p>'
                   f'{body}{cta(P, g["slug"] + "_end")}'
                   + (f'<h2>More guides</h2><div class="list">{more}</div>' if more else ""))
        (out / f"{g['slug']}.html").write_text(page(g["title"], g["desc"], url, P["c1"], P["c2"], content,
                                                    f'<script type="application/ld+json">{ld}</script>'))
    items = "".join(f'<a href="/guides/{g["slug"]}.html"><b>{html.escape(g["title"])}</b><span>{html.escape(g["desc"])}</span></a>'
                    for g in sorted(live, key=lambda g: g["date"], reverse=True))
    (out / "index.html").write_text(page("Guides for Home Bakers, Family Caregivers and Executors | LumivexaStore",
        "Practical, step-by-step guides for home bakers, family caregivers and estate executors.", f"{SITE}/guides/",
        "#1f3a5f", "#b8862f", f'<h1>Guides</h1><p>Practical, step-by-step guides for home bakers, family caregivers and estate executors.</p><div class="list">{items}</div>'))
    urls = [f"{SITE}/", f"{SITE}/guides/"] + [f"{SITE}{P['page']}" for P in PRODUCTS.values()] + [f"{SITE}/guides/{g['slug']}.html" for g in live]
    sm = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /data/\nDisallow: /scripts/\nSitemap: {SITE}/sitemap.xml\n")
    print(f"{len(live)} of {len(guides)} guides live")

if __name__ == "__main__":
    build()
