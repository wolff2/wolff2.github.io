"""Writes feed.xml with every scheduled pin whose date is today or earlier (UTC)."""
import json, datetime, pathlib, os
from email.utils import format_datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://wolff2.github.io"
today = datetime.datetime.now(datetime.timezone.utc).date()
pins = json.loads((ROOT / "data/pins.json").read_text())
live = [p for p in pins if datetime.date.fromisoformat(p["date"]) <= today]
# first time an item goes live, stamp it with the real time so Pinterest sees it as new
pub_path = ROOT / "data/published.json"
published = json.loads(pub_path.read_text()) if pub_path.exists() else {}
stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
for p in live:
    published.setdefault(p["guid"], stamp)
pub_path.write_text(json.dumps(published, indent=1))
live.sort(key=lambda p: published[p["guid"]], reverse=True)

def item(p):
    d = datetime.datetime.fromisoformat(published[p["guid"]])
    size = (ROOT / "pins" / p["image"].rsplit("/", 1)[1]).stat().st_size
    return f"""  <item>
   <title>{escape(p['title'])}</title>
   <link>{escape(p['link'])}</link>
   <description>{escape(p['description'])}</description>
   <guid isPermaLink="false">{p['guid']}</guid>
   <pubDate>{format_datetime(d)}</pubDate>
   <enclosure url="{escape(p['image'])}" length="{size}" type="image/jpeg"/>
   <media:content url="{escape(p['image'])}" medium="image" type="image/jpeg"/>
  </item>"""

def write(name, items, title):
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
 <channel>
  <title>{title}</title>
  <link>{SITE}/</link>
  <description>Spreadsheet templates for Google Sheets and Excel</description>
  <language>en</language>
  <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(item(p) for p in items)}
 </channel>
</rss>
"""
    (ROOT / name).write_text(xml)

now = format_datetime(datetime.datetime.now(datetime.timezone.utc))
write("feed.xml", live, "LumivexaStore")
for slug, t in [("home-bakery-system", "Home Bakery"), ("family-care-hub", "Family Care"), ("estate-executor-kit", "Estate Executor")]:
    write(f"feed-{slug}.xml", [p for p in live if p.get("feed") == slug], f"LumivexaStore - {t}")
print(f"{len(live)} of {len(pins)} pins live")
