#!/usr/bin/env python3
"""Fetch REAL player photos under FREE licenses (CC BY / CC BY-SA / CC0 / PD) from Wikimedia Commons.
Legal real-star imagery for editorial clips. Prints attribution; downloads JPEG/PNG.
Usage: python3 fetch_cc_photos.py "Ousmane Dembele" dembele"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUERY = sys.argv[1] if len(sys.argv) > 1 else "Ousmane Dembele"
SLUG = sys.argv[2] if len(sys.argv) > 2 else "player"
OUT = ROOT / "photos" / SLUG; OUT.mkdir(parents=True, exist_ok=True)
UA = "aabyzov-football-marketing/1.0 (editorial use; contact anton)"
FREE = ("cc0", "cc-by", "cc by", "public domain", "pd-", "no restrictions")

def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())

def strip(html): return re.sub(r"<[^>]+>", "", html or "").strip()

d = api({"action": "query", "generator": "search", "gsrsearch": f"{QUERY} football",
         "gsrnamespace": "6", "gsrlimit": "25", "prop": "imageinfo",
         "iiprop": "url|extmetadata|mime|size", "iiurlwidth": "1280", "format": "json"})
pages = (d.get("query", {}).get("pages", {}) or {}).values()
picked = []
print(f"=== Commons results for '{QUERY}' ===")
for p in pages:
    ii = (p.get("imageinfo") or [{}])[0]
    if not ii: continue
    em = ii.get("extmetadata", {})
    lic = (em.get("LicenseShortName", {}).get("value") or "").lower()
    artist = strip(em.get("Artist", {}).get("value", ""))
    mime = ii.get("mime", "")
    title = p.get("title", "")
    free = any(f in lic for f in FREE) and "nd" not in lic and "nc" not in lic.replace("license", "")
    if mime not in ("image/jpeg", "image/png"): continue
    tag = "FREE" if free else "skip"
    print(f"  [{tag}] {lic[:18]:18} | {artist[:28]:28} | {title[:42]}")
    if free and "(cropped)" not in title.lower():
        picked.append({"title": title, "url": ii.get("thumburl") or ii.get("url"),
                       "license": strip(em.get("LicenseShortName", {}).get("value", "")),
                       "artist": artist, "credit": strip(em.get("Credit", {}).get("value", "")),
                       "licurl": em.get("LicenseUrl", {}).get("value", "")})

PRIORITY = ("senegal", "world cup", "france", "2026", "trophy", "2018")
def score(ph):
    t = ph["title"].lower()
    return next((len(PRIORITY) - i for i, k in enumerate(PRIORITY) if k in t), 0)
picked.sort(key=score, reverse=True)
picked = picked[:10]
print(f"\n=== downloading {len(picked)} free-licensed (priority-sorted) ===")
manifest = []
for i, ph in enumerate(picked):
    try:
        time.sleep(1.3)
        req = urllib.request.Request(ph["url"], headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=60).read()
        ext = ".png" if ph["url"].lower().split("?")[0].endswith(".png") else ".jpg"
        f = OUT / f"{SLUG}_{i}{ext}"; f.write_bytes(data)
        ph["file"] = str(f); ph["bytes"] = len(data); manifest.append(ph)
        print(f"  OK {f.name} {len(data)//1024}KB | {ph['license']} | {ph['artist'][:30]}")
    except Exception as e:
        print(f"  FAIL {ph['title'][:40]} :: {e}")
(OUT / "ATTRIBUTION.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"\nattribution -> {OUT/'ATTRIBUTION.json'}")
