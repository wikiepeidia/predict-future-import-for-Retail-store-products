# Save as find_username_wayback.py
# Requires: requests, beautifulsoup4
# pip install requests beautifulsoup4

import requests, csv, time, re
from bs4 import BeautifulSoup

USERNAME = "wikiepeidia"   # <- change this
CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
WAYBACK_FETCH = "https://web.archive.org/web/{timestamp}id_/{original}"

# 1) query CDX for URLs that include the username in the URL (substring search)
# Note: adjust 'url' pattern or params if needed.
params = {
    "url": f"*{USERNAME}*",
    "output": "json",
    "fl": "original,timestamp,statuscode,mimetype",  # fields returned
    "filter": "statuscode:200",
    "limit": "10000"   # increase carefully; CDX may paginate
}

print("Querying CDX...")
r = requests.get(CDX_ENDPOINT, params=params, timeout=30)
r.raise_for_status()
data = r.json()

# first row is header (if JSON)
if not data or len(data) < 2:
    print("No CDX results.")
    exit(0)

headers = data[0]
rows = data[1:]
print(f"Found {len(rows)} CDX rows (URLs).")

matches = []
checked = 0

for original, timestamp, status, mimetype in rows:
    checked += 1
    # fetch the archived snapshot (use 'id_' to get raw content id)
    snap_url = WAYBACK_FETCH.format(timestamp=timestamp, original=original)
    try:
        resp = requests.get(snap_url, timeout=30)
    except Exception as e:
        print("fetch error", e)
        continue

    if resp.status_code != 200:
        continue

    html = resp.text
    # quick text search (case-insensitive). You can refine with regex or fuzzy matching.
    if re.search(re.escape(USERNAME), html, re.IGNORECASE):
        # extract short snippet and tag context
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        # find snippet around first occurrence
        m = re.search(re.escape(USERNAME), text, re.IGNORECASE)
        snippet = text[m.start()-80:m.end()+80] if m else text[:160]
        matches.append({"url": original, "timestamp": timestamp, "snippet": snippet})
        print("MATCH:", original, timestamp)

    # be polite
    time.sleep(0.5)  # increase sleep for larger jobs

print("Done. Matches:", len(matches))

# write CSV
with open("username_matches.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url","timestamp","snippet"])
    writer.writeheader()
    for m in matches:
        writer.writerow(m)

print("Wrote username_matches.csv")
