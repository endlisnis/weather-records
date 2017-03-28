#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather

#field = weather.daily.TOTAL_RAIN_MM
#field = weather.daily.MIN_WINDCHILL
field = weather.daily.MAX_TEMP

data = weather.daily.load('ottawa')

dayBySnow = {}

for date in sorted(data.keys()):
    val = data[date][field.index]
    if date.month != 7:
        continue
    if len(val):
        val = float(val)
        val = int(round(val*10))
        if val < 19.4:
            if val not in dayBySnow:
                dayBySnow[val] = []
            dayBySnow[val].append(date)
            if val <= -217:
                print date, val


snows = dayBySnow.keys()
snows.sort()
#snows.reverse()

nth = 1
for snow in snows:
    print "%d) %.1f:" % (nth, snow/10.0), dayBySnow[snow]
    nth += len(dayBySnow[snow])
