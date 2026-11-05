#!/usr/bin/env python3
"""Genera assets/snake-hud.svg: la serpiente recorre tu calendario de contribuciones (datos reales vía `gh`) con el estilo HUD/Tron.
Sin dependencias externas ni Actions: `python scripts/gen_snake.py`."""
import json, os, subprocess

USER = os.environ.get('PROFILE_USER', 'ZahidHM')
THEMES = {  # claro/oscuro: fondo, celda vacía, niveles 1-4, acento, naranja, texto/cabeza
    '': dict(bg='#0D1117', none='#16232b', lv=['#0b5a62', '#0f9aa0', '#19d9d9', '#00F7F7'], cy='#00F7F7', orr='#FF6A00', ink='#ffffff', blur=2.2),
    '-light': dict(bg='#EAF5F7', none='#dcebee', lv=['#a9dfe2', '#5fc6cb', '#22a8ae', '#007a80'], cy='#009aa0', orr='#E05A00', ink='#0D1117', blur=0.8),
}
LV = ['FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']
Q = '''query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{contributionLevel date}}}}}}'''
weeks = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={Q}', '-f', f'u={USER}'], text=True))['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

C, G, PAD, TOP = 12, 3, 34, 54          # celda, separación, margen, espacio del título
cols = len(weeks); W = PAD * 2 + cols * (C + G) - G; H = TOP + 7 * (C + G) - G + PAD
cx = lambda w: PAD + w * (C + G) + C / 2
cy = lambda d: TOP + d * (C + G) + C / 2

# la serpiente va directa de contribución en contribución (por la rejilla), sin recorrer las celdas vacías
order = [(w, d) for w, wk in enumerate(weeks) for d in range(len(wk['contributionDays']))]
targets = [(w, d) for w, d in order if weeks[w]['contributionDays'][d]['contributionLevel'] != 'NONE']
N = len(order)
x, y = PAD - 24, cy(targets[0][1]) if targets else cy(3)
pts = [(x, y)]; dist = [0.0]; hit = {}
for w, d in targets:
    for nx, ny in ((cx(w), y), (cx(w), cy(d))):       # primero en horizontal, luego en vertical
        if (nx, ny) != (x, y): dist.append(dist[-1] + abs(nx - x) + abs(ny - y)); pts.append((nx, ny)); x, y = nx, ny
    hit[(w, d)] = dist[-1]
pts.append((W - PAD + 24, y)); dist.append(dist[-1] + (W - PAD + 24 - x)); LEN = dist[-1]
d_attr = 'M' + ' L'.join(f'{px:.1f} {py:.1f}' for px, py in pts)
INTRO, HOLD, STEP = 4.0, 3.0, 0.18                  # aparición de stats, pausa final, segundos por celda (15 px)
SPEED = (C + G) / STEP; RUN = LEN / SPEED; T = INTRO + RUN + HOLD
fa, fb = INTRO / T, (INTRO + RUN) / T               # fracciones del ciclo en que empieza/acaba el recorrido

def build(P):
    BG, WH, NO, CY, OR = P['bg'], P['ink'], P['none'], P['cy'], P['orr']
    LVL = dict(zip(LV, P['lv']))
    # celdas: aparecen primero (en cascada por columna) y luego la serpiente se las come
    cells = ''; eaten_at = []                           # instantes (fracción) en que se come cada contribución
    for i, (w, d) in enumerate(order):
        day = weeks[w]['contributionDays'][d]; col = LVL.get(day['contributionLevel'], P['none'])
        x, y = PAD + w * (C + G), TOP + d * (C + G)
        ta = 0.01 + (w / cols) * (fa - 0.02); te = fa + hit.get((w, d), 0) / LEN * (fb - fa)
        if day['contributionLevel'] != 'NONE': eaten_at.append(te)
        if day['contributionLevel'] != 'NONE':   # la contribución se "come": destello y queda vacía
            anim = (f'<animate attributeName="fill" dur="{T:.1f}s" repeatCount="indefinite" values="{BG};{BG};{col};{col};{WH};{NO};{NO}" '
                    f'keyTimes="0;{ta:.4f};{ta + 0.012:.4f};{te:.4f};{te + 0.003:.4f};{te + 0.015:.4f};1"/>')
        else:                                     # las vacías solo aparecen y se quedan
            anim = (f'<animate attributeName="fill" dur="{T:.1f}s" repeatCount="indefinite" values="{BG};{BG};{NO};{NO}" keyTimes="0;{ta:.4f};{ta + 0.012:.4f};1"/>')
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
    <defs><filter id="g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{P['blur']}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <style>@media (prefers-reduced-motion:reduce){{animate,animateMotion{{display:none}}}}</style>
    <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="{BG}" stroke="{CY}" stroke-opacity=".3"/>
    <path d="M2 {b}V2H{b}M{W - 2} {b}V2H{W - b}M2 {H - b}v{b - 2}h{b - 2}M{W - 2} {H - b}v{b - 2}h-{b - 2}" fill="none" stroke="{CY}" stroke-width="2.2" filter="url(#g)"/>
    <text x="{W / 2}" y="32" text-anchor="middle" font-family='"Segoe UI",Arial,sans-serif' font-weight="700" font-size="17" letter-spacing="6" fill="{WH}" filter="url(#g)">CONTRIBUTION GRID</text>
    <text x="{W / 2}" y="46" text-anchor="middle" font-family='"Consolas","Courier New",monospace' font-size="9" letter-spacing="4" fill="{OR}">SNAKE // CONSUMING DATA</text>
    {cells}{snake}</svg>'''
    return svg

os.makedirs('assets', exist_ok=True)
for suf, P in THEMES.items():
    svg = build(P); open(f'assets/snake-eat{suf}.svg', 'w', encoding='utf8').write(svg)
    print('snake ok', suf or 'dark', cols, 'semanas', N, f'{T:.0f}s', len(svg) // 1024, 'KB')
