#!/usr/bin/env python3
"""Da fondo oscuro, borde HUD y esquinas neón a assets/snake.svg (la serpiente de Platane/snk sale con fondo transparente)."""
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else 'assets/snake.svg'
s = open(p, encoding='utf8').read()
if 'data-hud' not in s:
    m = re.search(r'<svg[^>]*viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"[^>]*>', s)
    x, y, w, h = (float(v) for v in m.groups()); CY = '#00F7F7'
    pad = 6; x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad; b = 22
    hud = (f'<g data-hud="1"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" fill="#0D1117" stroke="{CY}" stroke-opacity=".3"/>'
           f'<path d="M{x0} {y0 + b}V{y0}H{x0 + b}M{x1} {y0 + b}V{y0}H{x1 - b}M{x0} {y1 - b}V{y1}H{x0 + b}M{x1} {y1 - b}V{y1}H{x1 - b}" fill="none" stroke="{CY}" stroke-width="2"/></g>')
    # amplía el viewBox para el marco y coloca el fondo antes del contenido
    s = s.replace(m.group(0), m.group(0).replace(m.group(1) + ' ' + m.group(2) + ' ' + m.group(3) + ' ' + m.group(4), f'{x0} {y0} {x1 - x0} {y1 - y0}'), 1)
    s = re.sub(r'(<svg[^>]*>)', lambda mm: mm.group(1) + hud, s, count=1)
    open(p, 'w', encoding='utf8').write(s)
print('snake styled')
