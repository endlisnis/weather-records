#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import daily, time

field = daily.TOTAL_RAIN_MM

data = daily.load('ottawa')

last=[]

for date in sorted(data.keys()):
    rainStr = data[date].TOTAL_RAIN_MM
    if len(rainStr):
        rain = int(round(float(rainStr)*10))
        both = sum(last) + rain
        last.append(rain)
        if both >= 500:
            print date, both, last
        last.pop(0)
    else:
        last.append(0)
        last.pop(0)
