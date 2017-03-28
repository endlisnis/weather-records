#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import hourly, datetime, gnuplot, linear

data = hourly.load("ottawa")

sunniness = ('Clear', 'Mainly Clear')

now = datetime.datetime.now().date()

class SummerSunny():
    def __init__(self, mintemp):
        self.mintemp = mintemp
    def filter(self, year, month, day, hour):
        return ( hour >= 8 and hour <= 20 )
    def __call__(self, year, month, day, hour, fields):
        return ( self.filter(year, month, day, hour) and
                 fields.WEATHER in sunniness and
                 float(fields.TEMP) >= self.mintemp)

class Sunny():
    def __call__(self, timestamp, fields):
        if not ( timestamp.hour >= 8 and timestamp.hour <= 20 ):
            return None
        return fields.WEATHER in sunniness

class Snowy():
    def __call__(self, timestamp, fields):
        return ('snow' in fields.WEATHER.lower() )

class Thunder():
    def __call__(self, timestamp, fields):
        return ( 'thunder' in fields.WEATHER.lower() )

class MeanTemp():
    def __call__(self, timestamp, fields):
        if len(fields.TEMP) == 0:
            return None
        return Fraction(fields.TEMP)

class MeanTempSoFarThisYear():
    def __call__(self, timestamp, fields):
        if ( timestamp.month > now.month or
             ( timestamp.month == now.month and timestamp.day >= now.day ) or
             len(fields.TEMP) == 0 ):
            return None
        return Fraction(fields.TEMP)

class Sum:
    __slots__ = ()
    def __init__(self, total, count):
        self.total = total
        self.count = count
    def include(self, value):
        self.total += value
        self.count += 1
    def average(self):
        return Fraction(self.total) / self.count
    def __repr__(self):
        return "Sum(total=%r, count=%d)" % (self.total, self.count)

def totalHoursByMonth(filterFunc):
    matchCount = {}
    for timestamp in sorted(data.keys()):
        hourdata = data[timestamp]
        value = filterFunc(timestamp, hourdata)
        if value == None:
            continue
        #
        if timestamp.year not in matchCount:
            matchCount[timestamp.year] = {}
        if timestamp.month not in matchCount[timestamp.year]:
            matchCount[timestamp.year][timestamp.month] = Sum(0,0)
        matchCount[timestamp.year][timestamp.month].include(value)
    return matchCount

def totalByYear(valueFilter):
    matchByYear = {}
    for timestamp in sorted(data.keys()):
        hourdata = data[timestamp]
        value = valueFilter(timestamp, hourdata)
        if value == None:
            continue
        #
        if timestamp.year not in matchByYear:
            matchByYear[timestamp.year] = Sum(0,0)
        matchByYear[timestamp.year].include(value)
    return matchByYear

def yearByAverage(sumByYear):
    yearByAvg = {}
    for (year, sum) in sumByYear.iteritems():
        avg = sum.average()
        if avg not in yearByAvg:
            yearByAvg[avg] = []
        yearByAvg[avg].append(year)
    return yearByAvg

def plotMonthly(name, filterFunc):
    sunnyHoursByMonth = totalHoursByMonth(filterFunc)
    #
    monthVals = {}
    #
    currentYearVals = []
    lastYearVals = []
    #
    for year in sorted(sunnyHoursByMonth.keys()):
        for month in sorted(sunnyHoursByMonth[year].keys()):
            if month not in monthVals:
                monthVals[month] = []
            sunnySum = sunnyHoursByMonth[year][month]
            average = sunnySum.average()
            if year != now.year:
                monthVals[month].append(average)
            if year == now.year:
                print "%d/%02d: %.2f" % (year, month, average)
                currentYearVals.append((month, average))
            elif year == now.year - 1:
                lastYearVals.append((month, average))
    #
    plotAvg = []
    plotMin = []
    plotMax = []
    #
    for month in sorted(monthVals.keys()):
        Avg = sum(monthVals[month])/len(monthVals[month])
        Min = min(monthVals[month])
        Max = max(monthVals[month])
        print "%d: avg=%.2f, min=%.2f, max=%.2f" % (month, 
                                                    Avg,
                                                    Min,
                                                    Max)
        plotAvg.append((month, Avg))
        plotMin.append((month, Min))
        plotMax.append((month, Max))
    #
    #
    plot = gnuplot.Plot('ottawa/%s.%s' % (now.year, name), yaxis=2)
    plot.open(xtics=['"Jan" 1', '"Feb" 2', '"Mar" 3', '"Apr" 4', '"May" 5', '"Jun" 6',
                     '"Jul" 7', '"Aug" 8', '"Sep" 9', '"Oct" 10', '"Nov" 11', '"Dec" 12'])
    plot.addLine(gnuplot.Line('%d' % now.year, currentYearVals, lineColour='purple'))
    plot.addLine(gnuplot.Line('%d' % (now.year-1), lastYearVals, lineColour='orange'))
    plot.addLine(gnuplot.Line('Average', plotAvg, lineColour='green'))
    plot.addLine(gnuplot.Line('Min', plotMin, lineColour='blue'))
    plot.addLine(gnuplot.Line('Max', plotMax, lineColour='red'))
    plot.plot()
    plot.close()
    

plotMonthly('Sunny', Sunny())
plotMonthly('Snowy', Snowy())
plotMonthly('MeanTemp', MeanTemp())
plotMonthly('Thunder', Thunder())

#a = totalByYear(MeanTempSoFarThisYear())
#b = yearByAverage(a)

#for temp in sorted(b.keys()):
#    years = b[temp]
#    print '%.2f -> %s' % (temp + Fraction(5,1000), years)
