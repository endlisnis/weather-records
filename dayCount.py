#!/usr/bin/python3
# -*- coding: utf-8 -*-
import daily, sys, datetime
from collections import namedtuple
from namedList import *
from fieldOperators import *

now = datetime.datetime.now().date()

weatherData = daily.load('ottawa')
SumCount = namedList('SumCount', ('sum', 'count'))

ValueWithYearA = namedStruct('ValueWithYear', 'value year')

class ValueWithYear(ValueWithYearA):
    def __lt__(self, other):
        return self.value < other.value

DistrobutionCount = namedStruct('DistrobutionCount', ('sum=0', 'count=0', 'average=None', 'min=None', 'max=None'))

def JustJanuary(day):
    return day.month == 1

class JustAMonth:
    def __init__(self, month):
        self.month = month
    def __call__(self, day):
        return self.month == day.month

def BeforeToday(day):
    return day.month < now.month or ( day.month == now.month and day.day < now.day)

def rawdata(year, expr, dayFilter = None):
    ret = []

    startDay = datetime.date(year, 1, 1) #January 1st
    endDay = datetime.date(year+1, 1, 1) #January 1st

    for day in daily.dayRange(startDay, endDay):
        if dayFilter != None and not dayFilter(day):
            continue

        try:
            dayValues = weatherData[day]
        except KeyError:
            continue

        result = expr(dayValues)
        if result != None:
            ret.append(result)

    return ret

def rawcount(year, expr, dayFilter = None):
    ret = SumCount(sum=0, count=0)
    #
    startDay = datetime.date(year, 1, 1) #January 1st
    endDay = datetime.date(year+1, 1, 1) #January 1st
    observedDays = 0
    totalDays = 0
    #
    for day in daily.dayRange(startDay, endDay):
        if dayFilter != None and not dayFilter(day):
            continue
        #
        try:
            dayValues = weatherData[day]
        except KeyError:
            #print("Skipping day", day)
            continue
        #
        totalDays += 1
        result = expr(dayValues)
        if result != None:
            observedDays += 1

        if result is not False and result is not None:
            ret.count += 1
            ret.sum += result
            #print("Day {} does meet criteria".format(day, result))
        else:
            #print("Day {} does not meet criteria".format(day), dayValues)
            pass
    #
    if year != now.year and observedDays * 5 < totalDays * 4:
        return None
    return ret

def averageCount(beforeYear, expr, dayFilter):
    total = SumCount(sum = 0, count = 0)
    count = 0

    for year in range(weatherData.minYear, weatherData.maxYear+1):
        if year >= beforeYear:
            continue
        yearData = rawcount(year, expr, dayFilter)
        if yearData == None:
            continue
        total.count += yearData.count
        total.sum += yearData.sum
        count += 1

    avg = SumCount(count = Fraction(total.count, count), sum = total.sum / count)
    return avg


def distrobutionCount(beforeYear, expr, dayFilter, thisYearCount=None):
    data = []

    for year in range(weatherData.minYear, weatherData.maxYear+1):
        if year >= beforeYear:
            continue
        yearData = rawdata(year, expr, dayFilter)
        yearCountData = rawcount(year, expr, dayFilter)
        if yearCountData == None:
            print("skipping %d because of insufficient data" % year)
            continue

        yearCount = yearCountData.count
        #if thisYearCount != None and yearCount >= 5:
        print(year, yearCount)

        data.append(ValueWithYear(len(yearData), year))

    total = sum([a.value for a in data])
    ret = DistrobutionCount(sum=total,
                            count=len(data),
                            average=Fraction(total,len(data)),
                            min=min(data),
                            max=max(data))
    return ret

def displaycount(year, expr, name, dayFilter = None):
    thisYearCount = rawcount(year, expr, dayFilter).count
    print( year, name, "was", thisYearCount, "normal is %.1f" % averageCount(year, expr, dayFilter).count)

    print( distrobutionCount(year, expr, dayFilter, thisYearCount))
    #for year in range(weatherData.minYear, weatherData.maxYear+1):
    #    print year, rawcount(year, expr, dayFilter)[0]

if __name__ == '__main__':
    month = None
    if len(sys.argv) > 1:
        month = int(sys.argv[1])
    df = None
    if month != None:
        df = JustAMonth(month)

    #displaycount(2014, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 0), "days with snow", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.SNOW_ON_GRND_CM, 0), "days with snowpack", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 10), "days with > 10cm of snow", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 20), "days with > 20cm of snow", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 30), "days with > 30cm of snow", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 40), "days with > 40cm of snow", dayFilter = df)

    #displaycount(2014, lambda x: LessThan(x.MIN_TEMP, 0), "days with frost", dayFilter = df)
    #displaycount(2014, lambda x: LessThan(x.MIN_TEMP, -15), "nights below -15", dayFilter = df)
    displaycount(2016, lambda x: LessThan(x.MIN_TEMP, -20), "nights below -20", dayFilter = df)
    #displaycount(2014, lambda x: LessThanOrEqual(x.MAX_TEMP, 20), "Days below 20", dayFilter = df)
    #displaycount(2014, lambda x: LessThan(x.MAX_TEMP, 0), "days below zero", dayFilter = df)
    #displaycount(2014, lambda x: LessThan(x.MAX_TEMP, -10), "days below -10", dayFilter = df)
    #displaycount(2014, lambda x: LessThan(x.MAX_TEMP, -20), "days below -20", dayFilter = df)
    #displaycount(2014, lambda x: LessThan(x.MAX_TEMP, -25), "days below -25", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.MAX_TEMP, 0), "days above 0C", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.MAX_TEMP, 20), "days above 20C", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.MAX_TEMP, 25), "days above 25C", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.MAX_TEMP, 30), "days above 30C", dayFilter = df)
    #displaycount(2014, lambda x: GreaterThan(x.MAX_HUMIDEX, 30), "days with humidex above 30C", dayFilter = df)

    #for m in range(1,13):
    #    displaycount(2013, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 0), "%d days with snow" % m, dayFilter = JustAMonth(m))

#from dayCount import *
#rawcount(2010, lambda x: GreaterThan(x.MAX_TEMP, 20), None)
#rawcount(2013, lambda x: GreaterThan(x.TOTAL_SNOW_CM, 0), None)
