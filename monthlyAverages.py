#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, datetime, posix, daily, gnuplot, linear, sys, copy, numpy
import argparse
import forecast

import decimal
import math
from dailyFilters import *
from makefit import makeFit
from reversedict import reverseDict
from monthName import monthName
D = decimal.Decimal


class MonthFilter():
    def __init__(self, month):
        self.month = month
    #
    def __call__(self, year):
        #import pdb; pdb.set_trace()
        if type(year) != tuple:
            year = (year,)
        for y in year:
            baseDate = datetime.date(y, self.month, 1)

            endYear = y
            endMonth = self.month+1
            if endMonth > 12:
                endMonth = 1
                endYear += 1

            endDate = datetime.date(endYear, endMonth, 1)
            yield from daily.dayRange(baseDate, endDate)

    def __str__(self):
        return "MonthFilter(month=%s)" % (self.month)

    @property
    def filenamePart(self):
        return '%02d' % self.month

    @property
    def chartTitle(self):
        return monthName(self.month)

class BeforeDateFilter():
    def __init__(self, month, day):
        self.month = month
        self.day = day
    #
    def __call__(self, year):
        if type(year) != tuple:
            year = (year,)
        for y in year:
            if self.month == 1 and self.day == 1:
                yield from daily.dayRange(
                    datetime.date(y, 1, 1),
                    datetime.date(y+1, 1, 1))
            else:
                yield from daily.dayRange(
                    datetime.date(y, 1, 1),
                    datetime.date(y, self.month, self.day))

    @property
    def filenamePart(self):
        return 'before-%02d-%02d' % (self.month, self.day)

    @property
    def chartTitle(self):
        return 'before %s %02d' % (monthName(self.month), self.day)

class BetweenDatesFilter():
    def __init__(self, month1, day1, month2, day2):
        self.month1 = month1
        self.day1 = day1
        self.month2 = month2
        self.day2 = day2
    #
    def __call__(self, year):
        if type(year) != tuple:
            year = (year,)
        for y in year:
                yield from daily.dayRange(
                    datetime.date(y, self.month1, self.day1),
                    datetime.date(y, self.month2, self.day2))

    @property
    def filenamePart(self):
        return 'between-%02d-%02d,%02d-%02d' % (self.month1, self.day1)

    @property
    def chartTitle(self):
        return 'before %s %02d' % (monthName(self.month), self.day)

#class MonthFilter():
#    def __init__(self, month):
#        self.month = month
#    #
#    def __call__(self, date):
#        month = datetime.date.fromordinal(date).month
#        return month == self.month

class OneDayFilter():
    def __init__(self, month, day):
        self.month = month
        self.day = day

    def __call__(self, year):
        if type(year) != tuple:
            year = (year,)
        for y in year:
            yield datetime.date(y, self.month, self.day)

def filterData(year, dayFilter, field):
    data = []
    #
    #import pdb; pdb.set_trace()
    for dateTime in dayFilter(year):
        if dateTime in cityData:
            val = field(cityData[dateTime])
            #print("'%s'" % strval)
            if val != None:
                #data.append( (time.strftime('%Y-%m-%d', time.gmtime(dateTime)), val) )
                data.append(val)
    return data

class Sum:
    def __init__(self, total, count):
        self.total = total
        self.count = count

def filterSum(dayFilter, field):
    data = filterData(dayFilter, field)

    return Sum(total = sum(data), count = len(data))

class Monthly:
    def __init__(self,
                 average,
                 minimum, maximum,
                 count,
                 std,
                 minYear = None, maxYear = None):
        self.average = average
        self.minimum = minimum
        self.maximum = maximum
        self.count = count
        self.minYear = minYear
        self.maxYear = maxYear
        self.std = std

    def __str__(self):
        return "average(%.2f),minimum(%.1f),maximum(%.2f),count(%d),minYear(%s),maxYear(%s)" % (self.average, self.minimum, self.maximum, self.count, self.minYear, self.maxYear)


def filterAverage(dayFilter, field):
    data = filterData(dayFilter, field)

    ret = None

    if len(data):
        ret = Monthly(sum(data)/len(data), min(data), max(data), len(data), std=numpy.std([float(a) for a in data]))
    return ret


def average(values):
    avg = None
    if len(values):
        avg = sum(values)/len(values)

    return avg

def yearDatas(dayFilter, field, lastYear, cumulative):
    yearCountVal = []
    dataByYear = {}

    maxCount = 0
    for year in range(cityData.minYear, lastYear+1):
        #if year == 2016:
        #    import pudb; pu.db
        md = filterData(year, dayFilter, field)
        if len(md) > 0:
            if len(md) > maxCount:
                maxCount = len(md)
            v = sum(md)
            if not cumulative:
                v /= len(md)
                precision = int(math.log10(len(md))+field.precision)
                v = v.quantize(D('.'+'0'*(precision-1)+'1'))

            yearCountVal.append( (year, len(md), v) )

    validCount = int(maxCount * 0.85)


    for (year, count, value) in yearCountVal:
        if count < validCount and year != lastYear:
            print("Discarding %d because it only has %d/%d values" % (year, count, maxCount))
            continue
        dataByYear[year] = value
    return dataByYear


def normalMonthlyDatas(year, dayFilter, field, cumulative, historyYears=30):
    valByYear = yearDatas(dayFilter, field, now.year-1, cumulative)

    if len(valByYear.keys()) == 0:
        return None
    dataSum = 0
    dataCount = 0
    recentVals = []

    minVal = None
    minYear = 0
    maxVal = None
    maxYear = 0

    for y, val in valByYear.items():
        if y > year - historyYears - 1 and y < year:
            recentVals.append(val)
            dataCount += 1
            dataSum += val
        if minVal == None or val < minVal:
            minVal = val
            minYear = y
        if maxVal == None or val > maxVal:
            maxVal = val
            maxYear = y

    std = numpy.std([float(a) for a in recentVals])
    #print(dataSum, [float(a) for a in recentVals])

    return Monthly(dataSum / dataCount, minVal, maxVal, dataCount, std, minYear, maxYear)

def normalMonthlyAverage(year, dayFilter, field):
    return normalMonthlyDatas(year, dayFilter, field, cumulative = False)

def normalMonthlySum(year, dayFilter, field):
    return normalMonthlyDatas(year, dayFilter, field, cumulative = True)

def thisMonthOverTime(month):
    for fname in ['MEAN_TEMP']:
        findex = daily.fields._fields.index(fname)
        data = []
        for year in range(min(cityData.keys()),2017):
            avg = filterAverage(YearMonthFilter(year, month), findex)
            if avg != None:
                data.append((year,avg.average))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("ThisMonthOverTime_%s_%s" % (fname, monthName(month)), yaxis=2)
        plot.open()
        plot.addLine(gnuplot.Line(fname, data, lineColour='blue'))
        plot.addLine(gnuplot.Line('linear', lineFit, lineColour='green'))
        plot.plot()
        plot.close()


    for fname in ['TOTAL_SNOW_CM', 'TOTAL_PRECIP_MM']:
        findex = daily.fields._fields.index(fname)
        data = []
        for year in range(min(cityData.keys()),2017):
            data.append((year, filterSum(YearMonthFilter(year, month), findex).total))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("ThisMonthOverTime_%s_%s" % (fname, monthName(month)), yaxis=2)
        plot.open()
        plot.addLine(gnuplot.Line(fname, data, lineColour='blue'))
        plot.addLine(gnuplot.Line('linear', lineFit, lineColour='green'))
        plot.plot()
        plot.close()



def annualPlots(city, year):
    for field in [
            Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature"),
            FractionVal(daily.MAX_TEMP, "Max temp"),
            FractionVal(daily.MIN_TEMP, "Min temp"),
            FractionVal(daily.MEAN_TEMP, "Mean temp"),
            FractionVal(daily.MEAN_HUMIDITY, "Mean humidity"),
            FractionVal(daily.SNOW_ON_GRND_CM, "Snow-on-the-ground"),
            FractionVal(daily.AVG_WIND, "Wind"),
            FractionVal(daily.AVG_DEWPOINT, "Mean dewpoint"),
    ]:
        print(field.name)

        current = []
        average = []
        lowest = []
        highest = []
        stdLow = []
        stdHigh = []

        for month in range(1,13):
            thisyear = filterAverage(YearMonthFilter(year, month), field)
            normal = normalMonthlyAverage(year, YearMonthFilter(year=None, month=month), field)

            average.append("%d %.1f" % (month, normal.average))
            stdLow.append("%d %.1f" % (month, normal.average-normal.std))
            stdHigh.append("%d %.1f" % (month, normal.average+normal.std))
            lowest.append("%d %.1f" % (month, normal.minimum))
            highest.append("%d %.1f" % (month, normal.maximum))
            if thisyear != None and thisyear.count >= 15:
                current.append("%d %.1f" % (month, thisyear.average))

                units = field.units
                print("%10s-%10s: %+6.2f%s (%d: %+6.2f%s, normal: %+6.2f%s, extremeMin: %+6.2f%s %s, extremeMax: %+6.2f%s %s)" %
                      (monthName(month), field.name,
                       (thisyear.average-normal.average), units, year,
                       thisyear.average, units, normal.average, units,
                       normal.minimum, units, normal.minYear,
                       normal.maximum, units, normal.maxYear) )

        stdData = stdLow + list(reversed(stdHigh))
        plot = gnuplot.Plot("%s/svg/%d_%s" % (city, year, field.name.replace(' ', '_').replace('℃', 'C')), yaxis=2)
        plot.open(title="%s %s" % (city, field.title),
                  xtics=['"Jan" 1', '"Feb" 2', '"Mar" 3', '"Apr" 4', '"May" 5', '"Jun" 6',
                         '"Jul" 7', '"Aug" 8', '"Sep" 9', '"Oct" 10', '"Nov" 11', '"Dec" 12'])
        plot.addLine(gnuplot.Line('30-year std-dev',  stdData, lineColour='#e3e3e3', plot='filledcurves'))
        plot.addLine(gnuplot.Line("30-year normal", average, lineColour='#007700'))
        plot.addLine(gnuplot.Line("Record min", lowest, lineColour='blue'))
        plot.addLine(gnuplot.Line("Record max", highest, lineColour='red'))
        plot.addLine(gnuplot.Line("%d" % year, current, lineColour='purple'))
        plot.plot()
        plot.close()



    for field in (FractionVal(daily.TOTAL_SNOW_CM, "Snowfall"),
                  FractionVal(daily.TOTAL_RAIN_MM, "Rainfall"),
                  FractionVal(daily.TOTAL_PRECIP_MM, "Precip")):
        print(field.name)
        print("%s\t%s\t%s\t%s\t%s" % ("Month", "%d" % year, "Average", "Record max", "Record min"))

        current = []
        average = []
        lowest = []
        highest = []
        stdLow = []
        stdHigh = []


        for month in range(1,13):
            thisyear = filterSum(YearMonthFilter(year, month), field)
            normal = normalMonthlySum(year, YearMonthFilter(year, month), field)
            if normal != None:
                average.append((month, normal.average))
                stdLow.append("%d %.1f" % (month, normal.average-normal.std))
                stdHigh.append("%d %.1f" % (month, normal.average+normal.std))
                lowest.append((month, normal.minimum))
                highest.append((month, normal.maximum))

                if thisyear.count > 13:
                    current.append((month, thisyear.total))
                    units = field.units
                    print("%10s-%10s: %+6.1f%s (%d: %+6.1f%s, normal: %+6.1f%s, extremeMin: %+6.1f%s %s, extremeMax: %+6.1f%s %s)" %
                          (monthName(month), field.name,
                           (thisyear.total-normal.average), units, year,
                           thisyear.total, units, normal.average, units,
                           normal.minimum, units, normal.minYear,
                           normal.maximum, units, normal.maxYear) )

        if ( len(current) > 0 and
             len(average) > 0 and
             len(lowest) > 0 and
             len(highest) > 0 ):

            stdData = stdLow + list(reversed(stdHigh))
            plot = gnuplot.Plot("%s/svg/%d_%s" % (city, year, field.name.replace(' ', '_').replace('℃', 'C')), yaxis=2)
            plot.open(title="%s %s" % (city, field.title),
                      xtics=['"Jan" 1', '"Feb" 2', '"Mar" 3', '"Apr" 4', '"May" 5', '"Jun" 6',
                             '"Jul" 7', '"Aug" 8', '"Sep" 9', '"Oct" 10', '"Nov" 11', '"Dec" 12'])
            plot.addLine(gnuplot.Line('30-year std-dev',  stdData, lineColour='#e3e3e3', plot='filledcurves'))
            plot.addLine(gnuplot.Line("30-year normal", average, lineColour='#007700'))
            plot.addLine(gnuplot.Line("Record min", lowest, lineColour='blue'))
            plot.addLine(gnuplot.Line("Record max", highest, lineColour='red'))
            plot.addLine(gnuplot.Line("%d" % year, current, lineColour='purple'))
            plot.plot()
            plot.close()


def annualOrderedByMonth(city, monthFilter, field, cumulative):
    valByYears = yearDatas(monthFilter, field, now.year, cumulative)
    plotDataOtherYears = []
    plotDataThisYear = []
    plotTics = []
    plotIndex = 0

    divider = 1
    ylabel = field.units
    if max(valByYears.values()) > 10000:
        divider = 1000.0
        ylabel = '1000s of %s' % field.units

    valByYears = makeFit(valByYears, 75)
    plotIndex = 0
    last30Years = []

    yearsByVal = reverseDict(valByYears)
    print(yearsByVal)

    for val in sorted(yearsByVal.keys()):
        yearsWithThisVal = yearsByVal[val]
        for plotYear in yearsWithThisVal:
            if now.year == plotYear:
                plotDataThisYear.append((plotIndex, val/divider))
            else:
                plotDataOtherYears.append((plotIndex, val/divider))
            plotTics.append('"%s" %d' % (plotYear, plotIndex))
            plotIndex += 1
            if (plotYear > now.year - 31) and (plotYear < now.year):
                last30Years.append(val/divider)

    avg = sum(last30Years) / len(last30Years)
    std = numpy.std(last30Years)
    #print
    if len(yearsByVal.keys()) > 0:
        plot = gnuplot.Plot('%s/svg/yearOrdering.%s.%s' % (city,
                                                           monthFilter.filenamePart,
                                                           field.title.replace(' ', '_').replace('℃', 'C')),
                            yaxis=2)
        legend='on left'
        if max(yearsByVal.keys()) < 0:
            legend='bottom right'
        ymin = None
        if cumulative:
            ymin = 0
        plot.open(xtics=plotTics, xticsRotate=90, xticsFont='Arial,10', legend=legend,
                  ymin=ymin,
                  title='%s %s for %s' % (city.capitalize(),
                                          field.title.lower(),
                                          monthFilter.chartTitle),
                  margins=[6,8,2,3],
                  ylabel=ylabel
                  )
        plot.addLine(gnuplot.Line('30-year std-dev',  ((-1, avg-std), (plotIndex, avg-std), (plotIndex, avg+std), (-1, avg+std)), lineColour='#e3e3e3', plot='filledcurves'))
        plot.addLine(gnuplot.Line('Other years', plotDataOtherYears, plot='boxes'))
        plot.addLine(gnuplot.Line('This year', plotDataThisYear, plot='boxes'))
        plot.addLine(gnuplot.Line('30-Year Average', ((0, avg), (plotIndex-1, avg))))
        plot.plot()
        plot.close()

if __name__ == "__main__":
    now = datetime.date.today() - datetime.timedelta(3)


    parser = argparse.ArgumentParser(description='Calculate monthly average and charts.')
    parser.add_argument('--first', help='First year of data to consider.')
    parser.add_argument('--year', help='Year for annual plots.', default=now.year)
    parser.add_argument('--city', default='ottawa')
    args = parser.parse_args()

    cityData = daily.load(args.city)
    #forecast = forecast.getForecastData(args.city)
    #for day, v in forecast.items():
    #    if day not in cityData:
    #        cityData[day] = v
    firstYear = args.first

    if firstYear != None:
        firstYear = int(firstYear)
        keys = tuple(cityData.keys())
        for key in keys:
            if key.year < firstYear:
                del cityData[key]

    annualPlots(args.city, int(args.year))

    monFilter = YearMonthFilter(year = now.year, month = 11)
    #annualOrderedByMonth(args.city, monFilter, FractionVal(daily.TOTAL_PRECIP_MM, "Precip"), cumulative=True)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.TOTAL_RAIN_MM, "Rain"), cumulative=True)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.TOTAL_SNOW_CM, "Snow"), cumulative=True)
    #annualOrderedByMonth(monFilter, FreezingDegreeDaysSnowDepth(), cumulative=False)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.SNOW_ON_GRND_CM, "Snow-on-the-ground"), cumulative=False)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.AVG_WIND, "Wind"), cumulative=False)
    annualOrderedByMonth(
        args.city, monFilter, Avg(daily.MIN_TEMP, daily.MAX_TEMP, "Temperature"), cumulative=False)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.MAX_TEMP, "MaxTemp"), cumulative=False)
    annualOrderedByMonth(
        args.city, monFilter, FractionVal(daily.MEAN_HUMIDITY, "Humidity"), cumulative=False)

    #for year in range(cityData.minYear, cityData.maxYear+1):
    #    print(year, filterData(BeforeDateFilter(now.tm_mon, now.tm_mday, year), Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature")))

    SoFarThisYearFilter = BeforeDateFilter(datetime.date.today().month, datetime.date.today().day, datetime.date.today().year)
    print(filterAverage(SoFarThisYearFilter, Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature")))
    print(normalMonthlyAverage(now.year, SoFarThisYearFilter, Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature")))

    annualOrderedByMonth(SoFarThisYearFilter, Avg(daily.MIN_TEMP, daily.MAX_TEMP, "Temperature"), cumulative=False)
    #annualOrderedByMonth(SoFarThisYearFilter, FractionVal(daily.TOTAL_RAIN_MM, "Rain"), cumulative=True)
