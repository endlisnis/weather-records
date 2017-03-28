#!/usr/bin/python
from __future__ import print_function
import daily, datetime

def meanstdv(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std

weatherData = daily.load('farm')

rawData = {}

for year in range(weatherData.minYear, weatherData.maxYear+1):
    rawData[year] = []

    startDay = datetime.date(year, 1, 1)
    endDay = datetime.date(year, 2, 1)
    for date in daily.dayRange(startDay, endDay):
        try:
            dayValues = weatherData[date]
        except KeyError:
            continue

        v = dayValues.MAX_TEMP
        if v != None and len(v) > 0:
            rawData[year].append(float(v))

yearBySwing = {}

for year in sorted(rawData.keys()):
    d = rawData[year]
    if len(d) > 0:
        swings = []
        for i in range(1, len(d)):
            swings.append(d[i] - d[i-1])

        yearBySwing[meanstdv(swings)[1]] = year
        #print year, meanstdv(swings)
#print rawData

for swing in sorted(yearBySwing.keys()):
    print "%d: %.1f" % (yearBySwing[swing], swing)
