#!/usr/bin/env python3
"""Genera assets/snake-hud.svg: la serpiente recorre tu calendario de contribuciones (datos reales vía `gh`) con el estilo HUD/Tron.
Sin dependencias externas ni Actions: `python scripts/gen_snake.py`."""
import json, os, subprocess

USER = os.environ.get('PROFILE_USER', 'ZahidHM')
CY, OR = '#00F7F7', '#FF6A00'
LEVELS = {'NONE': '#16232b', 'FIRST_QUARTILE': '#0b5a62', 'SECOND_QUARTILE': '#0f9aa0', 'THIRD_QUARTILE': '#19d9d9', 'FOURTH_QUARTILE': CY}
Q = '''query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{contributionLevel date}}}}}}'''
weeks = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={Q}', '-f', f'u={USER}'], text=True))['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

C, G, PAD, TOP = 12, 3, 34, 54          # celda, separación, margen, espacio del título
cols = len(weeks); W = PAD * 2 + cols * (C + G) - G; H = TOP + 7 * (C + G) - G + PAD
cx = lambda w: PAD + w * (C + G) + C / 2
cy = lambda d: TOP + d * (C + G) + C / 2

# recorrido en serpentina: columna a columna, bajando y subiendo
path_pts, order = [], []
for w, wk in enumerate(weeks):
    days = list(range(len(wk['contributionDays'])))
    if w % 2: days.reverse()
    for d in days: path_pts.append((cx(w), cy(d))); order.append((w, d))
N = len(path_pts)
INTRO, STEP, HOLD = 4.0, 0.12, 3.0                 # aparición de stats, segundos por celda, pausa final
RUN = N * STEP; T = INTRO + RUN + HOLD
fa, fb = INTRO / T, (INTRO + RUN) / T               # fracciones del ciclo en que empieza/acaba el recorrido
d_attr = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in path_pts)
BG = '#0D1117'; WH = '#ffffff'

# celdas: aparecen primero (en cascada por columna) y luego la serpiente se las come
cells = ''; eaten_at = []                           # instantes (fracción) en que se come cada contribución
for i, (w, d) in enumerate(order):
    day = weeks[w]['contributionDays'][d]; col = LEVELS.get(day['contributionLevel'], LEVELS['NONE'])
    x, y = PAD + w * (C + G), TOP + d * (C + G)
    ta = 0.01 + (w / cols) * (fa - 0.02); te = fa + (i / N) * (fb - fa)
    if day['contributionLevel'] != 'NONE': eaten_at.append(te)
    anim = (f'<animate attributeName="fill" dur="{T:.1f}s" repeatCount="indefinite" values="{BG};{BG};{col};{col};{WH};{BG};{BG}" '
            f'keyTimes="0;{ta:.4f};{ta + 0.012:.4f};{te:.4f};{te + 0.002:.4f};{te + 0.012:.4f};1"/>')
    cells += f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="2.5" fill="{BG}">{anim}</rect>'

# serpiente: empieza corta y crece con cada contribución que se come
BASE = 6; SEG = BASE + min(len(eaten_at), 30); snake = ''; dt = STEP
for k in range(SEG):
    size = max(C - 1 - k * 0.2, 6); op = max(1 - k * 0.025, .45)
    t0 = fa + k * dt / T
    if k >= BASE: t0 = max(t0, eaten_at[k - BASE] + 0.002)
    t1 = min(fb + (k + 1) * dt / T, 0.995)
    kt = f'0;{t0:.4f};{t0 + 0.0005:.4f};{t1:.4f};{t1 + 0.0005:.4f};1'
    snake += (f'<rect width="{size:.1f}" height="{size:.1f}" x="{-size / 2:.1f}" y="{-size / 2:.1f}" rx="3" fill="{WH if k == 0 else CY}" opacity="0" filter="url(#g)">'
              f'<animate attributeName="opacity" dur="{T:.1f}s" repeatCount="indefinite" values="0;0;{op:.2f};{op:.2f};0;0" keyTimes="{kt}"/>'
              f'<animateMotion dur="{T:.1f}s" repeatCount="indefinite" begin="{-k * dt}s" path="{d_attr}" calcMode="linear" keyPoints="0;0;1;1" keyTimes="0;{fa:.4f};{fb:.4f};1"/></rect>')

b = 22
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Contribution grid de {USER}">
<defs><filter id="g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>@media (prefers-reduced-motion:reduce){{animate,animateMotion{{display:none}}}}</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="#0D1117" stroke="{CY}" stroke-opacity=".3"/>
<path d="M2 {b}V2H{b}M{W - 2} {b}V2H{W - b}M2 {H - b}v{b - 2}h{b - 2}M{W - 2} {H - b}v{b - 2}h-{b - 2}" fill="none" stroke="{CY}" stroke-width="2.2" filter="url(#g)"/>
<text x="{W / 2}" y="32" text-anchor="middle" font-family='"Segoe UI",Arial,sans-serif' font-weight="700" font-size="17" letter-spacing="6" fill="#fff" filter="url(#g)">CONTRIBUTION GRID</text>
<text x="{W / 2}" y="46" text-anchor="middle" font-family='"Consolas","Courier New",monospace' font-size="9" letter-spacing="4" fill="{OR}">SNAKE // CONSUMING DATA</text>
{cells}{snake}</svg>'''
os.makedirs('assets', exist_ok=True); open('assets/snake-hud.svg', 'w', encoding='utf8').write(svg)
print('snake ok', cols, 'semanas', N, 'celdas', f'{T:.0f}s', len(svg) // 1024, 'KB')
