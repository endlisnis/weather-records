#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, posix, daily, gnuplot, linear, sys, datetime, numpy
from dailyFilters import *

def yearlyValues(cityData, year, field):
    values = []
    for date in daily.dayRange(datetime.date(year,1,1), datetime.date(year+1,1,1)):
    #for date in daily.dayRange(datetime.date(year,6,1), datetime.date(year,9,1)):
        try:
            val = field(cityData[date])
            if val != None:
                values.append(val)
        except KeyError:
            pass

    return values

def yearlySum(cityData, year, field):
    #print('yearlySum(', year, field.name, ')')
    sum = 0
    count = 0
    fakeCount = 0
    for date in daily.dayRange(datetime.date(year,1,1), datetime.date(year+1,1,1)):
    #for date in daily.dayRange(datetime.date(year,6,1), datetime.date(year,9,1)):
        try:
            val = field(cityData[date])
            if val is not None:
                sum += val
                count += 1
            elif cityData[date].MAX_TEMP is not None or cityData[date].MIN_TEMP is not None:
                fakeCount += 1
        except KeyError:
            pass

    #if count > 30:
    #    count += fakeCount
    #assert(count>0)
    #print('yearlySum(', year, field.name, ')=', (sum, count))
    return (sum, count)

def yearlyAverage(cityData, year, field):
    (sum, count) = yearlySum(cityData, year, field)

    avg = None
    if count > 0:
        avg = sum/count
    return avg

def normalYearlyAverage(cityData, beforeYear, field):
    sum = 0
    count = 0
    for year in range(cityData.minYear, beforeYear):
        (ysum, ycount) = yearlySum(cityData, year, field)
        sum += ysum
        count += ycount

    avg = None
    if count > 0:
        avg = sum/count

#print('debug: m=%d, f=%d, s=%d, c=%d, a=%d' % (month, field, sum, count, avg))
    return avg

def normalYearlySum(cityData, beforeYear, field):
    sum = 0
    count = 0
    for year in range(cityData.minYear, beforeYear):
        (ysum, ycount) = yearlySum(cityData, year, field)
        sum += ysum
        count += 1

    avg = None
    if count > 0:
        avg = sum/count
    return avg

def getAnnualValues(cityData, field, cumulative):
    data = []
    for year in range(cityData.minYear, cityData.maxYear+1):
        thisYearSum, thisYearCount = yearlySum(cityData, year, field)

        if thisYearCount > 300:
        #if thisYearCount > 80:
            #print("Including {year} because it had {thisYearCount} observations."
            #      .format(**locals()))
            v = thisYearSum
            if not cumulative:
                v /= thisYearCount
            data.append((year, v))
        else:
            pass
            #print("Skipping {year} because it only had {thisYearCount} observations."
            #      .format(**locals()))
    return data

def getAnnualStd(cityData, field):
    data = []
    for year in range(cityData.minYear, cityData.maxYear+1):
        thisYearValues = [float(a) for a in yearlyValues(cityData, year, field)]

        if len(thisYearValues) > 300:
            v = numpy.std(thisYearValues)
            data.append((year, v))
    return data


if __name__=="__main__":
    city=sys.argv[1]

    cityData = daily.load(city)

    for field in [FractionVal(daily.MAX_TEMP, "high temperature"),
                  FractionVal(daily.MIN_TEMP, 'low temperature'),
                  FractionVal(daily.AVG_WIND, 'wind'),
                  Avg(daily.MIN_TEMP, daily.MAX_TEMP, 'average temperature')]:
        fname = field.name
        print(fname)
        data = getAnnualValues(cityData, field, False)

        try:
            lineFit = linear.linearTrend(data)
        except ZeroDivisionError:
            print(data)
            raise

        for i in range(len(data)):
            year, val = data[i]
            lfitv = lineFit[i][1]
            print(year, float(val), lfitv)


        plot = gnuplot.Plot("%s/svg/Annual_%s" % (city, fname), yaxis=2)
        plot.open(title='%s %s per year' % (city.capitalize(), field.title),
                  ylabel = '%s in %s' % (field.title, field.units) )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Temp", data, lineColour='purple'))
        plot.plot()
        plot.close()

    for field in [FractionVal(daily.TOTAL_SNOW_CM, 'snow'),
                  FractionVal(daily.SNOW_ON_GRND_CM, 'snowpack'),
                  FractionVal(daily.TOTAL_RAIN_MM, 'rain'),
                  FractionVal(daily.TOTAL_PRECIP_MM, 'precipitation')]:
        fname = field.name
        print(fname)
        data = getAnnualValues(cityData, field, True)
        for year, val in data:
            print(year, float(val))

        try:
            lineFit = linear.linearTrend(data)
        except ZeroDivisionError:
            print(data)
            raise

        plot = gnuplot.Plot("%s/svg/Annual_%s" % (city, fname), yaxis=2)
        plot.open(title='%s %s per year' % (city.capitalize(), field.title),
                  ymin=0,
                  ylabel = '%s in %s' % (field.title, field.units) )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Amount", data, lineColour='purple'))
        plot.plot()
        plot.close()

    for field in [FractionVal(daily.MAX_TEMP, "high temperature"),
                  FractionVal(daily.MIN_TEMP, 'low temperature'),
                  FractionVal(daily.TOTAL_SNOW_CM, 'snow'),
                  FractionVal(daily.TOTAL_RAIN_MM, 'rain'),
                  FractionVal(daily.TOTAL_PRECIP_MM, 'precipitation')]:
        fname = field.name
        data = getAnnualStd(cityData, field)
        #for year, val in data:
        #    print(year, float(val))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("%s/svg/Annual_std_%s" % (city, fname), yaxis=2)
        plot.open(title='%s %s std per year' % (city.capitalize(), field.title),
                  ymin=0,
                  ylabel = '%s in %s' % (field.title, field.units) )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Std", data, lineColour='purple'))
        plot.plot()
        plot.close()
