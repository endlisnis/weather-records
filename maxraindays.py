#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather

field = weather.daily.TOTAL_RAIN_MM

data = weather.daily.load('ottawa')

dayBySnow = {}

lastVal = 0
lastDate = 0
for date in data:
    val = data[date][field.index]
    if len(val):
        val = int(float(val)*10+0.5)
        if val > 0:
            if val not in dayBySnow:
                dayBySnow[val] = []
            dayBySnow[val].append(date)

            lastVal = val
            lastDate = date


snows = dayBySnow.keys()
snows.sort()
snows.reverse()

nth = 1
for snow in snows:
    print "%d) %.1f:" % (nth, snow/10.0), dayBySnow[snow]
    nth += len(dayBySnow[snow])
