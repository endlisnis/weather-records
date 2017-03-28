#!/usr/bin/python3
# -*- coding: utf-8 -*-
import glob, os

dirs = set()
pngs = []
svgdirs = []

for i in glob.glob('*/svg/*.svg') + glob.glob('*/svg/histogram/*.svg'):
    png = i.replace('/svg/', '/').replace('.svg', '.png')
    pngdir = os.path.dirname(png)
    dirs.add(pngdir)
    pngs.append(png)
    svgdirs.append(os.path.dirname(i))
    print('rsvg-convert -o "{png}" --background-color=white "{i}"; rm {i}'.format(**locals()))
