#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, datetime, posix, daily, sys, gnuplot, fnmatch
import forecast
import makefit
import linear
from namedList import *
from collections import namedtuple
from plotdict import plotdict


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
        try:
            day = datetime.date(year, plotDate.month, plotDate.day)
        except ValueError:
            if plotDate.month == 2 and plotDate.day == 29:
                # Must be Feb 29th, skip
                continue
            raise
        if day in rawData:
            #print('{}: "{}"'.format(str(day), rawData[day][field.index]))
            if rawData[day][field.index] is not None:
                dataByYear[year] = rawData[day][field.index]
        else:
            #print('{}: ???'.format(str(day)))
            pass

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
    if len(data) > 1:
        lineFit = linear.linearTrend( tuple((a[0], float(a[1])) for a in data) )
    plot = gnuplot.Plot(filename, yaxis=2)
    plot.open(title=chartTitle,
              ylabel=yaxisLabel)
    if len(data) > 1:
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
    plot.addLine(gnuplot.Line("Temp", data, lineColour='purple'))
    plot.plot()
    plot.close()
    return plot.fname


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
                                           plotDate.strftime('%b %d')),
        yaxisLabel=yaxisLabel,
        thisYear=plotDate.year,
        plotZeros=True,
        showAverage=False,
    )

    lineFname = plotline(
        valueByYear,
        filename='{city}/svg/{name}.line'.format(**locals()),
        chartTitle='%s daily %s for %s' % (city.title(),
                                           fieldEnglishName,
                                           plotDate.strftime('%b %d')),
        yaxisLabel=yaxisLabel,
    )

    top10Fname = plotdict(
        filterDict(valueByYear, top10Years),
        filename='%s/svg/%s.top10' % (city, name),
        chartTitle='Top 10 %s daily %ss for %s' % (city.title(),
                                                   fieldEnglishName,
                                                   plotDate.strftime('%b %d')),
        yaxisLabel=yaxisLabel,
        thisYear=plotDate.year,
        plotZeros=True,
        showAverage=False,
    )

    print(filterDict(valueByYear, bottom10Years))
    bottom10Fname = plotdict(
        filterDict(valueByYear, bottom10Years),
        filename='%s/svg/%s.bottom10' % (city, name),
        chartTitle='Bottom 10 %s daily %ss for %s' % (city.title(),
                                                      fieldEnglishName,
                                                      plotDate.strftime('%b %d')),
        yaxisLabel=yaxisLabel,
        thisYear=plotDate.year,
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
        recentYearsWithThisValue = tuple(filter(lambda y: y<plotDate.year and y >plotDate.year-31, yearByValue[value]))
        if verbose:
            lrecent = len(recentValues)
            lrecentVal = len(recentYearsWithThisValue)
            isMedian = (lrecent <= 15) and (lrecent + lrecentVal > 15)
            #print lrecent, lrecentVal, map(float, recentValues)
            print("{}-{}) {:.1f}{}, {}{}"
                  .format(count+1,
                          len(valueByYear)-count,
                          value,
                          units,
                          yearByValue[value],
                          ["","*** median"][isMedian]))
        recentValues += [value]*len(recentYearsWithThisValue)
        count += thiscount
        #
        if plotZeros == False and value == 0:
            # We've been told to skip zeros, so we don't plot them
            continue

        for year in yearByValue[value]:
            if year == plotDate.year:
                chartDataThisYear.append((chartIndex, value, '# %d' % year))
            else:
                chartDataOtherYears.append((chartIndex, value, '# %d' % year))

            chartTicks.append('"%d" %d' % (year, chartIndex))
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
    rawForecast = forecast.getForecastDataEnvCan(city)
    #
    if verbose:
        print ( 'annualData(..., field = %s, plotDate = %s)' %
                (field, plotDate) )

    #
    if plotDate == None:
        # if no date was provided, use the last date for which data is available
        plotDate = max(rawData.keys())
        print("No plot-date was provided, using {}".format(plotDate))
    #
    for (date, val) in rawForecast.items():
        print(date, val)
    mergedData = daily.Data(rawData.copy())
    for k,v in rawForecast.items():
        if k not in mergedData:
            mergedData[k] = v
    plotData = annualData(rawData = mergedData, field = field, plotDate = plotDate)
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
        plotDate = datetime.date(plotDate[0],plotDate[1],plotDate[2])
        print(plotDate)

    fieldByOutput = {
        "snow":             (daily.TOTAL_SNOW_CM, False),
        "snowOnTheGround":  (daily.SNOW_ON_GRND_CM, True),
        "rain":             (daily.TOTAL_RAIN_MM, False),
        "precip":           (daily.TOTAL_PRECIP_MM, False),
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
                        name=field.name,
                        plotDate = plotDate,
                        plotZeros = plotZeros)
    if matchCount == 0:
        print(fieldByOutput.keys())
