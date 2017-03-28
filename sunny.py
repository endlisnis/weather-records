#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather, time, gnuplot, linear

data = weather.hourly.load("gatineau")

sunniness = ('Clear', 'Mainly Clear')

now = time.localtime()

(currentMonth, currentDay) = now[1:3]

class SummerSun():
    def __init__(self, year, mintemp):
        self.year = year
        self.mintemp = mintemp
    def __call__(self, timestamp, fields):
        return ( timestamp.year == self.year and
                 timestamp.hour >= 8 and
                 timestamp.hour <= 20 and
                 fields[weather.hourly.WEATHER] in sunniness and
                 float(fields[weather.hourly.TEMP]) >= self.mintemp);

class Snowy():
    def __init__(self, year):
        self.year = year
    def __call__(self, timestamp, fields):
        return ( timestamp.year == self.year and
                 'snow' in fields[weather.hourly.WEATHER].lower() );

def totalHours(field, filterFunc):
    matchCount = 0
    for timestamp in sorted(data.keys()):
        hourdata = data[timestamp]
        if filterFunc(timestamp, hourdata):
            matchCount += 1
    return matchCount

sunData = {10:[], 15:[], 20:[], 25:[], 30:[]}
sunRecord = {}
snowData = []

#uniqConditions = {}
#for t in data.values():
#    uniqConditions[t[weather.hourly.WEATHER]] = 1
#print sorted(uniqConditions.keys())


for year in range(1993, 2013):
    for t in sorted(sunData.keys()):
        if t not in sunRecord:
            sunRecord[t] = (0, 0)

        (recordYear, recordVal) = sunRecord[t]

        tempSunHours = totalHours(weather.hourly.WEATHER, SummerSun(year, t))
        sunData[t].append((year, tempSunHours))
        print "Sun: %4d %2dC %3d" % (year, t, tempSunHours)

        if tempSunHours > recordVal:
            sunRecord[t] = (year, tempSunHours)

#
    thisyearsnowy = totalHours(weather.hourly.WEATHER, Snowy(year))
    snowData.append((year, thisyearsnowy))
    print "Snow: %d\t%d" % (year, thisyearsnowy)

print sunRecord

sunLineFit = {10:[], 15:[], 20:[], 25:[], 30:[]}

for t in sunData:
    sunLineFit[t] = linear.linearTrend(sunData[t])

snowlineFit = linear.linearTrend(snowData)

plot = gnuplot.Plot("ottawa/SunnyHours", yaxis=2)
plot.open(ymin=0)
for t in sunData:
    plot.addLine(gnuplot.Line("Trend %d" % t, sunLineFit[t], plot='lines'))
    plot.addLine(gnuplot.Line("Sun %d" % t, sunData[t]))
plot.plot()
plot.close()

plot = gnuplot.Plot("ottawa/SnowHours", yaxis=2)
plot.open(ymin=0)
plot.addLine(gnuplot.Line("Trend", snowlineFit, lineColour='green', plot='lines'))
plot.addLine(gnuplot.Line("Snow", snowData, lineColour='purple'))
plot.plot()
plot.close()

