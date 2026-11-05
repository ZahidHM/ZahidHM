#!/usr/bin/env python3
"""Genera la variante clara (*-light.svg) de cada SVG oscuro, remapeando la paleta. `python scripts/make_light.py`"""
import re, glob, os
MAP = {  # oscuro -> claro (en minúsculas)
    '#0d1117': '#eaf5f7', '#05080d': '#e6f4f6', '#0a1620': '#eef8fa', '#06141a': '#e3f1f3', '#0f2229': '#d3e6e9', '#101a21': '#dcebee',
    '#fff': '#0d1117', '#ffffff': '#0d1117', '#e6fdfd': '#0d1117', '#cfeeee': '#16363a', '#8fb5b5': '#3d6c70', '#7fb3b3': '#3d6c70', '#5f8f8f': '#4a7a7e',
    '#00f7f7': '#009aa0', '#ff6a00': '#e05a00', '#2effa3': '#0a9f5f',
}
for p in glob.glob('assets/*.svg'):
    if p.endswith('-light.svg') or 'snake-eat' in p: continue
    s = open(p, encoding='utf8').read()
    s = re.sub(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b', lambda m: MAP.get(m.group(0).lower(), m.group(0)), s)
    s = re.sub(r'stdDeviation="[\d.]+"', 'stdDeviation="0.8"', s)
    open(p[:-4] + '-light.svg', 'w', encoding='utf8').write(s)
    print(p)
