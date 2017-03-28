#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import hourly, sys, copy

aboveValue = None
belowValue = None

sys.stderr.write(str(sys.argv))
sys.stderr.flush()

if sys.argv[1][0] == '>':
    aboveValue = int(round(float(sys.argv[1][1:])*10))
    print "aboveValue: ", aboveValue
else:
    belowValue = int(round(float(sys.argv[1])*10))
minLen = int(sys.argv[2])

field = sys.argv[3]
#field = {'temp': hourly.TEMP, 'windchill': hourly.weather.daily.MAX_TEMP}[sys.argv[3]]

data = hourly.load('ottawa')
monthMatch = None
if len(sys.argv) > 4:
    (f,v) = sys.argv[4].split('=')
    if f == 'month':
        monthMatch = int(v)

dayBySnow = {}
daysBelow = {}

def printDict(dict):
    keys = dict.keys()
    popyear = int(round(sum([i.year for i in keys])/float(len(keys))))
    print '==>', popyear, len(dict),
    for key in sorted(dict.keys()):
        print '%s: %s, ' % (key, dict[key]),
    print

def updateAndClear():
    if len(daysBelow) >= minLen:
        printDict(daysBelow)
        dayBySnow[len(daysBelow)] = copy.copy(daysBelow)
    daysBelow.clear()

for date in sorted(data.keys()):
    if monthMatch != None and date.month != monthMatch:
        updateAndClear()
        continue
    #
    if field == 'temp':
        val = data[date].TEMP
        if len(val) == 0:
            val = None
        else:
            val = float(val)
    elif field == 'windchill':
        val = data[date].windchill
    elif field == 'humidex':
        val = data[date].humidex
    #
    if val != None:
        val = int(round(val*10))
        if ( belowValue != None and val < belowValue ) or ( aboveValue != None and val > aboveValue ):
            daysBelow[date] = val
        else:
            updateAndClear()
    else:
        updateAndClear()
updateAndClear()


#snows = dayBySnow.keys()
#snows.sort()
#snows.reverse()

#nth = 1
#for snow in snows:
#    print "%d) %.1f:" % (nth, snow), dayBySnow[snow]
#    nth += len(dayBySnow[snow])
