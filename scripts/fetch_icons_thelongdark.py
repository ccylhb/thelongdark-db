# -*- coding: utf-8 -*-
"""Conan icon fetcher — infobox `image` field is a direct filename.

fandom static host for this wiki is `intothelongdark` (gamepedia legacy),
and MediaWiki forces first-letter capitalization on file names:
  https://static.wikia.nocookie.net/intothelongdark/images/<h1>/<h2>/<File>
where <h1>/<h2> = first 1/2 chars of md5(Capitalized filename).
No API calls needed.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "src", "data")
ICON_DIR = os.path.join(BASE_DIR, "public", "icons")
DL_HOST = "https://static.wikia.nocookie.net/intothelongdark/images"
UA = "LongDarkDB/1.0 (site: thelongdark-db.pages.dev; contact franceiwhdbks865@gmail.com)"

DATASETS = ["food", "clothing", "firstaid", "tools", "afflictions"]


def cap_first(name):
    return name[0].upper() + name[1:] if name else name


def icon_url(fname):
    cap = cap_first(fname)
    h = hashlib.md5(cap.encode()).hexdigest()
    return f"{DL_HOST}/{h[0]}/{h[:2]}/{urllib.parse.quote(cap)}"


def fetch(args):
    fname, outpath = args
    if os.path.exists(outpath) and os.path.getsize(outpath) > 0:
        return fname, "cached"
    url = icon_url(fname)
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=25).read()
            if len(data) < 100:
                return fname, f"tiny:{len(data)}"
            with open(outpath, "wb") as f:
                f.write(data)
            return fname, "ok"
        except Exception as e:
            if attempt == 2:
                return fname, f"fail:{str(e)[:50]}"
    return fname, "fail:?"


def main():
    os.makedirs(ICON_DIR, exist_ok=True)
    jobs = []
    owners = {}  # fname -> [(dataset, item)]
    for ds in DATASETS:
        path = os.path.join(DATA_DIR, f"thelongdark_{ds}.json")
        items = json.load(open(path, encoding="utf-8"))
        for it in items:
            img = (it.get("image") or "").strip()
            if not img or "{" in img:
                continue
            m = re.search(r"([\w\- .]+\.(?:png|jpg|jpeg|gif))", img, flags=re.I)
            if not m:
                continue
            fname = m.group(1).strip().replace(" ", "_")
            it["icon"] = fname
            owners.setdefault(fname, []).append((path, it))
            if not any(j[0] == fname for j in jobs):
                jobs.append((fname, os.path.join(ICON_DIR, fname)))
        json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"unique icon files: {len(jobs)}")

    stats = {"ok": 0, "cached": 0, "fail": 0, "tiny": 0}
    fails = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for fname, status in ex.map(fetch, jobs):
            stats[status.split(":")[0]] = stats.get(status.split(":")[0], 0) + 1
            if status.startswith("fail") or status.startswith("tiny"):
                fails.append((fname, status))
    print("stats:", stats)
    if fails:
        print("failed sample:", fails[:10])
        json.dump(fails, open(os.path.join(BASE_DIR, "scripts", "icon_fails.json"), "w"), indent=1)
    # mark items whose icon file exists on disk
    total, have = 0, 0
    for ds in DATASETS:
        path = os.path.join(DATA_DIR, f"thelongdark_{ds}.json")
        items = json.load(open(path, encoding="utf-8"))
        for it in items:
            if "icon" in it:
                total += 1
                if os.path.exists(os.path.join(ICON_DIR, it["icon"])):
                    have += 1
                    it["icon_file"] = it["icon"]
                del it["icon"]
        json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"coverage: {have}/{total}")


if __name__ == "__main__":
    main()
