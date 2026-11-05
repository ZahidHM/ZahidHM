#!/usr/bin/env python3
"""Genera assets/stats.svg y assets/langs.svg (estilo Tron/HUD) con la API de GitHub vía `gh`. Se ejecuta a diario en Actions."""
import json, os, subprocess, datetime, html

USER = os.environ.get('PROFILE_USER', 'ZahidHM')
CY, OR = '#00F7F7', '#FF6A00'
FONT = '"Segoe UI",Arial,Helvetica,sans-serif'; MONO = '"Consolas","Courier New",monospace'

def gh(*a):
    return json.loads(subprocess.check_output(['gh', 'api', *a], text=True))

user = gh(f'users/{USER}')
repos = [r for r in gh(f'users/{USER}/repos?per_page=100&type=owner') if not r['fork']]
stars = sum(r['stargazers_count'] for r in repos)
q = 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions}}}}'
try:
    contrib = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={q}', '-f', f'u={USER}'], text=True))['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
except Exception:
    contrib = 0
since = datetime.datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).year
langs = {}
for r in repos:
    try:
        for k, v in gh(f"repos/{USER}/{r['name']}/languages").items(): langs[k] = langs.get(k, 0) + v
    except Exception:
        pass
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

DEFS = f'''<defs><filter id="g" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="{OR}"/></linearGradient></defs>'''
BASE = '@media (prefers-reduced-motion:reduce){*{animation:none !important}}'

def card(name, w, h, title, tag, body, style=''):
    brackets = f'<path d="M2 26V2H26M{w - 2} 26V2H{w - 26}M2 {h - 26}v24h24M{w - 2} {h - 26}v24h-24" fill="none" stroke="{CY}" stroke-width="2.2" filter="url(#g)"/>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{html.escape(title)}">{DEFS}<style>{style}{BASE}</style>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="8" fill="#0D1117" stroke="{CY}" stroke-opacity=".3"/>{brackets}
<text x="{w / 2}" y="40" text-anchor="middle" font-family='{FONT}' font-weight="700" font-size="18" letter-spacing="5" fill="#fff" filter="url(#g)">{title}</text>
<text x="{w / 2}" y="58" text-anchor="middle" font-family='{MONO}' font-size="10" letter-spacing="4" fill="{OR}">{tag}</text>{body}</svg>'''
    os.makedirs('assets', exist_ok=True); open(f'assets/{name}', 'w', encoding='utf8').write(svg)

# ── estadísticas ──
cells = [('CONTRIBUTIONS', f'{contrib:,}', 'LAST 12 MONTHS'), ('PUBLIC REPOS', str(len(repos)), 'ORIGINAL BUILDS'), ('STARS', str(stars), 'EARNED'),
         ('FOLLOWERS', str(user['followers']), 'CONNECTIONS'), ('ONLINE SINCE', str(since), 'GITHUB GRID'), ('LANGUAGES', str(len(langs)), 'DETECTED')]
body = ''
for i, (lab, val, sub) in enumerate(cells):
    x = 40 + (i % 2) * 220; y = 92 + (i // 2) * 62
    body += f'''<g class="c" style="animation-delay:{i * 0.25:.2f}s"><text x="{x}" y="{y}" font-family='{MONO}' font-size="10" letter-spacing="3" fill="#7fb3b3">{lab}</text>
<text x="{x}" y="{y + 28}" font-family='{FONT}' font-weight="700" font-size="28" fill="#fff" filter="url(#g)">{val}</text><text x="{x + 8 + len(val) * 17}" y="{y + 26}" font-family='{MONO}' font-size="9" letter-spacing="2" fill="{CY}" opacity=".7">{sub}</text></g>'''
card('stats.svg', 480, 290, 'NETWORK STATS', 'GRID // LIVE DATA', body, '.c{animation:in .9s ease both}@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}')

# ── lenguajes ──
body = ''
for i, (k, v) in enumerate(top):
    pct = v * 100 / total; y = 86 + i * 32; bw = 400 * pct / 100
    body += f'''<text x="40" y="{y}" font-family='{FONT}' font-weight="600" font-size="13" fill="#e6fdfd">{html.escape(k)}</text><text x="440" y="{y}" text-anchor="end" font-family='{MONO}' font-weight="700" font-size="12" letter-spacing="2" fill="{CY}">{pct:.1f}%</text>
<rect x="40" y="{y + 7}" width="400" height="6" rx="3" fill="#0f2229"/><rect class="b" style="animation-delay:{i * 0.2:.2f}s;transform-origin:40px 0" x="40" y="{y + 7}" width="{max(bw, 4):.1f}" height="6" rx="3" fill="url(#bar)" filter="url(#g)"/>'''
card('langs.svg', 480, 290, 'TOP LANGUAGES', 'SYSTEM // CODE BYTES', body, '.b{animation:grow 1.2s cubic-bezier(.2,.8,.2,1) both}@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}')
print('stats ok', contrib, len(repos), stars, user['followers'], since, top[:3])
