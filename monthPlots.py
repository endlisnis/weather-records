#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, datetime, posix, daily, sys, gnuplot, fnmatch
import makefit
import linear
from namedList import *
from collections import namedtuple
from plotdict import plotdict

def recentDate(date, now):
    return date < now and date >= datetime.date(now.year-31, now.month, 1)

def zeroIfNone(val):
    if val == None:
        return 0
    return val

colours = ['cyan', 'violet', 'pink']

def annualData(rawData, field, plotDate):
    dataByYear = {}
    #
    for year in range(rawData.minYear, rawData.maxYear+1):
        #
        nextMonthYear = year
        nextMonthMonth = plotDate.month
        if nextMonthMonth > 11:
            nextMonthMonth = 1
            nextMonthYear += 1
        for day in daily.dayRange(datetime.date(year, plotDate.month, 1),
                                  datetime.date(nextMonthYear, nextMonthMonth, 1)):
            if day in rawData:
                if len(rawData[day][field.index]) > 0:
                    dataByYear[day] = Fraction(rawData[day][field.index])

    return dataByYear

def valuesOfHighest10Keys(db):
    top10Values = []
    for val in reversed(sorted(db.keys())):
        top10Values += db[val]
        if len(top10Values) >= 10:
            break
    return top10Values

def valuesOfLowest10Keys(db):
    bottom10Values = []
    for val in sorted(db.keys()):
        bottom10Values += db[val]
        if len(bottom10Values) >= 10:
            break
    return bottom10Values

def filterDict(db, keyFilter):
    ret = {}
    for key in db:
        if key in keyFilter:
            ret[key] = db[key]
    return ret

def plotline(valueByYear, filename, chartTitle, yaxisLabel):
    data = sorted(tuple(valueByYear.items()))
    #lineFit = linear.linearTrend(data)
    plot = gnuplot.Plot(filename, yaxis=2)
    plot.open(title=chartTitle,
              ylabel=yaxisLabel)
    #plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
    plot.addLine(gnuplot.Line("Temp", data, lineColour='purple'))
    plot.plot()
    plot.close()
    return plot.fname

class MonthEqual():
    def __init__(self, date):
        self.date = date
    def __eq__(self, other):
        return ( self.date.year == other.year
                 and self.date.month == other.month )


def createPlot(plotData, city, name, yaxisLabel, fieldEnglishName, units, plotDate, plotZeros, verbose):
    yearByValue = {}
    valueByYear = {}
    for year in plotData:
        #
        value = plotData[year]
        #if value == None:
        #    value = 0
        if (value not in yearByValue):
            yearByValue[value] = [year]
        else:
            yearByValue[value].append(year)
        valueByYear[year] = value
        #print year, value

    top10Years = valuesOfHighest10Keys(yearByValue)
    bottom10Years = valuesOfLowest10Keys(yearByValue)

    allfname = plotdict(
        valueByYear,
        filename='{city}/svg/{name}.all'.format(**locals()),
        chartTitle='%s daily %s for %s' % (city.title(),
                                           fieldEnglishName,
                                           plotDate.strftime('%B')),
        yaxisLabel=yaxisLabel,
        thisYear=MonthEqual(plotDate),
        plotZeros=True,
        showAverage=False,
    )

    lineFname = plotline(
        valueByYear,
        filename='{city}/svg/{name}.line'.format(**locals()),
        chartTitle='%s daily %s for %s' % (city.title(),
                                           fieldEnglishName,
                                           plotDate.strftime('%B')),
        yaxisLabel=yaxisLabel,
    )

    top10Fname = plotdict(
        filterDict(valueByYear, top10Years),
        filename='%s/svg/%s.top10' % (city, name),
        chartTitle='Top 10 %s daily %ss for %s' % (city.title(),
                                                   fieldEnglishName,
                                                   plotDate.strftime('%B')),
        yaxisLabel=yaxisLabel,
        thisYear=MonthEqual(plotDate),
        plotZeros=True,
        showAverage=False,
    )

    print(filterDict(valueByYear, bottom10Years))
    bottom10Fname = plotdict(
        filterDict(valueByYear, bottom10Years),
        filename='%s/svg/%s.bottom10' % (city, name),
        chartTitle='Bottom 10 %s daily %ss for %s' % (city.title(),
                                                      fieldEnglishName,
                                                      plotDate.strftime('%b')),
        yaxisLabel=yaxisLabel,
        thisYear=MonthEqual(plotDate),
        plotZeros=True,
        showAverage=False,
    )

    values = sorted(yearByValue.keys())
    #
    chartTicks = []
    chartDataOtherYears = []
    chartDataThisYear = []
    chartIndex = 0
    count = 0
    recentValues = []
    maxValue = max(values)

    for value in values:
        # number of years with this value
        thiscount = len(yearByValue[value])
        #
        recentYearsWithThisValue = tuple(filter(lambda y: recentDate(y, plotDate), yearByValue[value]))
        if verbose:
            lrecent = len(recentValues)
            lrecentVal = len(recentYearsWithThisValue)
            isMedian = (lrecent <= 15) and (lrecent + lrecentVal > 15)
            #print lrecent, lrecentVal, map(float, recentValues)
            print("{}) {:.1f}{}, {}{}".format(count, float(value), units, yearByValue[value], ["","*** median"][isMedian]))
        recentValues += [value]*len(recentYearsWithThisValue)
        count += thiscount
        #
        if plotZeros == False and value == 0:
            # We've been told to skip zeros, so we don't plot them
            continue

        for year in yearByValue[value]:
            if year.year == plotDate.year and year.month == plotDate.month:
                chartDataThisYear.append((chartIndex, value, '# ' + str(year)))
            else:
                chartDataOtherYears.append((chartIndex, value, '# ' + str(year)))

            chartTicks.append('"{date}" {index}'.format(date=str(year), index=chartIndex))
            chartIndex += 1


    legend = 'on left'
    if maxValue < 0:
        legend = 'on right bottom'
    bmargin = 5

    plot = gnuplot.Plot('%s/svg/%s.yearOrdering' % (city, name), yaxis=2, output='svg')
    #
    plot.open(title='%s daily %s for %s' % (city.title(),
                                            fieldEnglishName,
                                            plotDate.strftime('%b %d')),
              xtics=chartTicks, xticsRotate=90, xticsFont='Arial,10', legend=legend,
              margins=[6,8,2,bmargin],
              ylabel=yaxisLabel,# ymin=0,
              xmin=-1, xmax=chartIndex)
    plot.addLine(gnuplot.Line('Other years', chartDataOtherYears, plot='boxes', lineColour='0x6495ED'))
    plot.addLine(gnuplot.Line('This year', chartDataThisYear, plot='boxes', lineColour='0x556B2F'))
    plot.plot()
    plot.close()
    return lineFname, bottom10Fname, top10Fname

def createPlots(city, field, name, plotDate=None, plotZeros=True, verbose=True, output='svg'):
    units = field.units
    #
    findex = field.index
    #
    rawData = daily.load(city)
    #
    if verbose:
        print ( 'annualData(..., field = %s, plotDate = %s)' %
                (field, plotDate) )

    #
    if plotDate == None:
        # if no date was provided, use the last date for which data is available
        plotDate = max(rawData.keys())
        plotDate = datetime.date(plotDate.year, plotDate.month, 1)
        print("No plot-date was provided, using {}".format(plotDate))
    #
    plotData = annualData(rawData = rawData, field = field, plotDate = plotDate)
    toDel = []
    for year in plotData:
        value = plotData[year]
        if value == None:
            toDel.append(year)
        if plotZeros == False and value == 0:
            # We've been told to skip zeros, so we don't plot them
            toDel.append(year)
    for year in toDel:
        del plotData[year]
    del toDel

    #culledPlotData = makefit.makeFit(plotData, 75)

    plotLine, plotTop10, plotBottom10 = createPlot(
        plotData,
        city,
        name,
        '%s (%s)' % (field.englishName, units),
        field.englishName, units, plotDate, plotZeros, verbose)

    returnValue = plotLine, plotTop10, plotBottom10
    yearByValue = {}
    valueByYear = {}
    recentValues = []
    for year in plotData:
        #
        value = plotData[year]
        #if value == None:
        #    value = 0
        if (value not in yearByValue):
            yearByValue[value] = [year]
        else:
            yearByValue[value].append(year)
        valueByYear[year] = value
        if year<plotDate.year and year>plotDate.year-31:
            recentValues.append(value)
    #
    if verbose:
        avg = sum(recentValues)/len(recentValues)
        print("Average is {:.1f}{}".format(float(avg), units))
        #
        currentVariance = "unknown"
        if plotDate.year in valueByYear:
            thisYearValue = valueByYear[plotDate.year]
            if plotDate.year in valueByYear:
                currentVariance = "%.1f%s %s average" % (abs(thisYearValue - avg), units, ["below", "above"][thisYearValue > avg])
                print("{} is {}".format(plotDate.year, currentVariance))
                print([float(v) for v in filter(lambda v: v < thisYearValue, recentValues)])
                print([float(v) for v in filter(lambda v: v == thisYearValue, recentValues)])
                print([float(v) for v in filter(lambda v: v > thisYearValue, recentValues)])
    #
    return returnValue

if __name__ == '__main__':
    (city, output, plotDate, inputPlotZeros) = (sys.argv[1:] + [None,None])[:4]
    if plotDate != None:
        plotDate = tuple(map(int, plotDate.split('-')))
        plotDate = datetime.date(plotDate[0],plotDate[1],1)
        print(plotDate)

    fieldByOutput = {
        "snow":             (daily.TOTAL_SNOW_CM, False),
        "snowOnTheGround":  (daily.SNOW_ON_GRND_CM, True),
        "rain":             (daily.TOTAL_RAIN_MM, False),
        'max':              (daily.MAX_TEMP, True),
        'min':              (daily.MIN_TEMP, True),
        'humidex':          (daily.MAX_HUMIDEX, True),
        'avgWindchill':     (daily.AVG_WINDCHILL, True),
        'minWindchill':     (daily.MIN_WINDCHILL, True),
        'wind':             (daily.AVG_WIND, True),
        'windGust':         (daily.SPD_OF_MAX_GUST_KPH, False),
        'meanTemp':         (daily.MEAN_TEMP, True),
        'meanHumidity':     (daily.MEAN_HUMIDITY, True),
        'minHumidity':      (daily.MIN_HUMIDITY, True),
    }

    matchCount = 0
    for fieldName in fieldByOutput:
        if fnmatch.fnmatch(fieldName, output):
            matchCount += 1
            field, plotZeros = fieldByOutput[fieldName]
            if inputPlotZeros != None:
                plotZeros = True

            createPlots(city,
                        field=field,
                        name='Month_'+field.name,
                        plotDate = plotDate,
                        plotZeros = plotZeros)
    if matchCount == 0:
        print(fieldByOutput.keys())
