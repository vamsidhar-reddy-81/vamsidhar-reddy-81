#!/usr/bin/env python3
"""Builds assets/commit-log.svg from the PUBLIC GitHub contribution calendar.
No data is invented. Usage: python scripts/build_commit_log.py <username>"""
import re, sys, os, datetime as dt, urllib.request, html
USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USERNAME", "vamsidhar-reddy-81")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "commit-log.svg")
req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

cells = {}
for m in re.finditer(r"<td[^>]*?>", page):
    tag = m.group(0)
    d = re.search(r'data-date="([\d-]+)"', tag); i = re.search(r'\bid="([^"]+)"', tag); l = re.search(r'data-level="(\d)"', tag)
    if d and i: cells[i.group(1)] = [d.group(1), int(l.group(1)) if l else 0, 0]
for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>\s*([^<]+?)\s*</tool-tip>', page):
    n = re.match(r"(\d+) contribution", m.group(2))
    if m.group(1) in cells: cells[m.group(1)][2] = int(n.group(1)) if n else 0
days = sorted(cells.values())
if not days: sys.exit("No contribution data found; keeping the old file.")

total = sum(c for _, _, c in days); active = sum(1 for _, _, c in days if c)
best = max(days, key=lambda x: x[2])
longest = cur = 0; ls = le = start = prev = None
for d, _, c in days:
    dd = dt.date.fromisoformat(d)
    if c:
        cur = cur + 1 if (prev and (dd - prev).days == 1) else 1
        if cur == 1: start = dd
        if cur > longest: longest, ls, le = cur, start, dd
        prev = dd
    else: cur = 0; prev = None
cs = 0
for d, _, c in reversed(days):
    if c: cs += 1
    elif d != days[-1][0] or cs: break

def fmt(d): x = dt.date.fromisoformat(d) if isinstance(d, str) else d; return f"{x.day} {x:%b %Y}"
ACC, ACC2, TXT, MUT, LINE = "#5EEAD4", "#818CF8", "#EEF2FF", "#94A3B8", "#3B4A7A"
SERIF = 'Georgia,"Iowan Old Style","Palatino Linotype",serif'; MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'
LEV = ["#161B33", "#2B3A7A", "#4F5FD0", "#5EC8E0", "#5EEAD4"]
def T(x, y, s, cls, size, fill, extra=""):
    f = SERIF if cls == "s" else MONO
    return f'<text x="{x}" y="{y}" font-family=\'{f}\' font-size="{size}" fill="{fill}" {extra}>{html.escape(str(s))}</text>'

W, H = 1200, 360
body = T(40, 52, "COMMIT LOG · REAL GITHUB ACTIVITY", "m", 11.5, ACC, 'letter-spacing="2"')
body += f'<text x="40" y="100" font-family=\'{SERIF}\' font-size="26" fill="{TXT}">A year of building, <tspan font-style="italic" fill="{ACC}">one square</tspan> at a time.</text>'
stats = [("CONTRIBUTIONS", f"{total:,}", f"{fmt(days[0][0])[3:]} – {fmt(days[-1][0])[3:]}"), ("ACTIVE DAYS", active, f"of {len(days)} days"),
         ("LONGEST STREAK", longest, "consecutive days"), ("BUSIEST DAY", best[2], fmt(best[0]))]
for i, (k, v, s) in enumerate(stats):
    x = 600 + i * 145
    body += T(x, 52, k, "m", 10, MUT, 'letter-spacing="2"') + T(x, 96, v, "s", 38, TXT) + T(x, 118, s, "m", 10.5, MUT)
# heatmap
x0, y0, cell, gap = 40, 165, 17, 4
first = dt.date.fromisoformat(days[0][0]); off = (first.weekday() + 1) % 7  # Sunday-first
lastm = None
for idx, (d, lvl, c) in enumerate(days):
    col, row = (idx + off) // 7, (idx + off) % 7
    x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
    dd = dt.date.fromisoformat(d)
    if row == 0 and dd.month != lastm and col < 51 and (idx > 20 or dd.day <= 7 and col > 2): body += T(x, y0 - 10, f"{dd:%b}", "m", 10, MUT); lastm = dd.month
    body += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{LEV[lvl]}"><title>{c} contributions on {d}</title></rect>'
body += T(40, H - 24, f"Source: public GitHub contribution calendar for @{USER} · snapshot {fmt(dt.date.today())} · refreshed daily", "m", 10, MUT)
lx = W - 230
body += T(lx - 40, H - 24, "Less", "m", 10, MUT)
for i, c in enumerate(LEV): body += f'<rect x="{lx + i*18}" y="{H-35}" width="13" height="13" rx="3" fill="{c}"/>'
body += T(lx + 5 * 18 + 6, H - 24, "More", "m", 10, MUT)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub activity: {total} contributions in the last year, {active} active days, longest streak {longest} days, busiest day {best[2]} contributions.">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B1020"/><stop offset="1" stop-color="#070A14"/></linearGradient>
<radialGradient id="gl" cx="85%" cy="20%" r="60%"><stop offset="0" stop-color="{ACC2}" stop-opacity=".35"/><stop offset="1" stop-color="{ACC2}" stop-opacity="0"/></radialGradient>
<clipPath id="cl"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<style>@keyframes up{{from{{opacity:0}}to{{opacity:1}}}} rect[rx="3"]{{animation:up .8s ease both}}</style>
<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#gl)"><animate attributeName="opacity" values=".5;1;.5" dur="6s" repeatCount="indefinite"/></rect>
{body}</g><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}" stroke-opacity=".7"/></svg>'''
open(OUT, "w").write(svg)
print(f"total={total} active={active} longest={longest} ({ls}→{le}) best={best[2]} on {best[0]} current={cs}")
