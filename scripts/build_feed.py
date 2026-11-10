"""Writes feed.xml with every scheduled pin whose date is today or earlier (UTC)."""
import json, datetime, pathlib, os
from email.utils import format_datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://wolff2.github.io"
today = datetime.datetime.now(datetime.timezone.utc).date()
pins = json.loads((ROOT / "data/pins.json").read_text())
live = [p for p in pins if datetime.date.fromisoformat(p["date"]) <= today]
live.sort(key=lambda p: p["date"], reverse=True)

def item(p):
    d = datetime.datetime.combine(datetime.date.fromisoformat(p["date"]), datetime.time(6, 0), datetime.timezone.utc)
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

now = format_datetime(datetime.datetime.combine(today, datetime.time(6, 0), datetime.timezone.utc))
xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
 <channel>
  <title>LumivexaStore</title>
  <link>{SITE}/</link>
  <description>Spreadsheet templates for Google Sheets and Excel</description>
  <language>en</language>
  <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(item(p) for p in live)}
 </channel>
</rss>
"""
(ROOT / "feed.xml").write_text(xml)
print(f"{len(live)} of {len(pins)} pins live")
