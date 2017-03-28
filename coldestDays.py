#!/usr/bin/python3
# -*- coding: utf-8 -*-
import weather, sys, copy

belowValue = int(round(float(sys.argv[1])*10))
minLen = int(sys.argv[2])

#field = weather.daily.TOTAL_RAIN_MM
#field = weather.daily.MIN_WINDCHILL
field = {'min': weather.daily.MIN_TEMP, 'max': weather.daily.MAX_TEMP}[sys.argv[3]]

data = weather.daily.load('ottawa')

dayBySnow = {}

daysBelow = {}

def updateAndClear():
    if len(daysBelow) >= minLen:
        print daysBelow
        dayBySnow[len(daysBelow)] = copy.copy(daysBelow)
    daysBelow.clear()

def isSummer(date):
    return ( date.month == 7 
             or date.month == 8
             or (date.month == 6 and date.day >= 22)
             or (date.month == 9 and date.day < 20) );


for date in sorted(data.keys()):
    val = data[date][field.index]

    if isSummer(date) and len(val):
        val = float(val)
        val = int(round(val*10))
        if val < belowValue:
            daysBelow[date] = val
        else:
            updateAndClear()
    else:
        updateAndClear()
updateAndClear()


snows = dayBySnow.keys()
snows.sort()
snows.reverse()

nth = 1
for snow in snows:
    print "%d) %.1f:" % (nth, snow), dayBySnow[snow]
    nth += len(dayBySnow[snow])
