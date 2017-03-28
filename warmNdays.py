#!/usr/bin/python
from __future__ import print_function
import weather, sys, copy

field = weather.daily.MAX_TEMP

data = weather.daily.load('ottawa')

dcount = 4
warmDays = {}
ldates = [None]*dcount
lvs = [None]*dcount

for date in sorted(data.keys()):
    if date.month != 1:
        continue
    val = data[date].MAX_TEMP
    if len(val):
        val = float(val)

        ldates.append(date)
        ldates.pop(0)
        lvs.append(val)
        lvs.pop(0)

        mv = min(lvs)
        if mv not in warmDays:
            warmDays[mv] = []
        warmDays[mv].append( copy.copy(ldates) )

warmest = sorted(warmDays.keys())[-10:]

for warm in warmest:
    print warm, warmDays[warm]
