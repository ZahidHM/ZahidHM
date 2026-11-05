#!/usr/bin/env python3
"""Genera assets/snake.svg: la serpiente recorre tu calendario de contribuciones (datos reales vía `gh`) con el estilo HUD/Tron.
Sin dependencias externas ni Actions: `python scripts/gen_snake.py`."""
import json, os, subprocess

USER = os.environ.get('PROFILE_USER', 'ZahidHM')
CY, OR = '#00F7F7', '#FF6A00'
LEVELS = {'NONE': '#101a21', 'FIRST_QUARTER': '#073b40', 'SECOND_QUARTER': '#0a6f74', 'THIRD_QUARTER': '#00b5b5', 'FOURTH_QUARTER': CY}
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
N = len(path_pts); DUR = max(18, N * 0.05)       # segundos por vuelta
d_attr = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in path_pts)

# celdas: se "comen" cuando pasa la cabeza
cells = ''
for i, (w, d) in enumerate(order):
    day = weeks[w]['contributionDays'][d]; col = LEVELS.get(day['contributionLevel'], LEVELS['NONE']); t = i / N
    x, y = PAD + w * (C + G), TOP + d * (C + G)
    # toda celda se "come": destello al pasar la cabeza y luego desaparece (también las vacías, para que se note el recorrido)
    e = min(t + 0.003, 1); f = min(t + 0.03, 1)
    anim = f'<animate attributeName="fill" dur="{DUR:.1f}s" repeatCount="indefinite" values="{col};{col};#ffffff;#0D1117;#0D1117" keyTimes="0;{t:.4f};{e:.4f};{f:.4f};1"/>'
    cells += f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="2.5" fill="{col}">{anim}</rect>'

# cuerpo de la serpiente (cabeza + segmentos con retraso)
SEG = 12; snake = ''
for k in range(SEG):
    size = C - 1 - k * 0.35; fill = CY if k == 0 else f'{CY}'; op = 1 - k * 0.06
    delay = -(k * 0.05)
    snake += (f'<rect width="{size:.1f}" height="{size:.1f}" x="{-size / 2:.1f}" y="{-size / 2:.1f}" rx="3" fill="{fill if k else "#ffffff"}" opacity="{op:.2f}" filter="url(#g)">'
              f'<animateMotion dur="{DUR:.1f}s" repeatCount="indefinite" begin="{delay}s" path="{d_attr}" calcMode="linear"/></rect>')

b = 22
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Contribution grid de {USER}">
<defs><filter id="g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>@media (prefers-reduced-motion:reduce){{animate,animateMotion{{display:none}}}}</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="#0D1117" stroke="{CY}" stroke-opacity=".3"/>
<path d="M2 {b}V2H{b}M{W - 2} {b}V2H{W - b}M2 {H - b}v{b - 2}h{b - 2}M{W - 2} {H - b}v{b - 2}h-{b - 2}" fill="none" stroke="{CY}" stroke-width="2.2" filter="url(#g)"/>
<text x="{W / 2}" y="32" text-anchor="middle" font-family='"Segoe UI",Arial,sans-serif' font-weight="700" font-size="17" letter-spacing="6" fill="#fff" filter="url(#g)">CONTRIBUTION GRID</text>
<text x="{W / 2}" y="46" text-anchor="middle" font-family='"Consolas","Courier New",monospace' font-size="9" letter-spacing="4" fill="{OR}">SNAKE // CONSUMING DATA</text>
{cells}{snake}</svg>'''
os.makedirs('assets', exist_ok=True); open('assets/snake.svg', 'w', encoding='utf8').write(svg)
print('snake ok', cols, 'semanas', N, 'celdas', f'{DUR:.0f}s', len(svg) // 1024, 'KB')
