#!/usr/bin/env python3
"""Accumulate this repo's GitHub traffic (views) into a lifetime total and
render assets/visitors.svg. GitHub only keeps 14 days of traffic, so daily
counts are stored by date in assets/visitors.json and merged idempotently."""
import json, os, urllib.request
from pathlib import Path

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["TRAFFIC_TOKEN"]
data_file, svg_file = Path("assets/visitors.json"), Path("assets/visitors.svg")

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/traffic/views?per=day",
    headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
)
with urllib.request.urlopen(req) as r:
    views = json.load(r)["views"]

days = json.loads(data_file.read_text()) if data_file.exists() else {}
for v in views:
    days[v["timestamp"][:10]] = v["count"]  # overwrite by date: no double counting
data_file.write_text(json.dumps(dict(sorted(days.items())), indent=1) + "\n")

total = sum(days.values())
label, value = "visitors", f"{total:,}"
lw, vw = 70, 14 + 8 * len(value)
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{lw+vw}" height="20" role="img" aria-label="{label}: {value}">
<rect width="{lw}" height="20" rx="3" fill="#555"/><rect x="{lw}" width="{vw}" height="20" rx="3" fill="#0077B5"/>
<rect x="{lw-3}" width="6" height="20" fill="#555"/><rect x="{lw}" width="3" height="20" fill="#0077B5"/>
<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">
<text x="{lw/2}" y="14">{label}</text><text x="{lw+vw/2}" y="14">{value}</text></g></svg>
"""
svg_file.write_text(svg)
print("total views:", total)
