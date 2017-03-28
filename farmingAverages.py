#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time, datetime, posix, daily, gnuplot, linear, sys, copy, numpy, getopt
from types import *
from dailyFilters import *
from makefit import makeFit, reverseDictionary
from monthName import monthName

now = datetime.date.today() - datetime.timedelta(3)

cityName = 'ottawa'
firstYear = None

opts, args = getopt.getopt(sys.argv[1:], 'c:f:', ['city=', 'firstYear='])

for opt, arg in opts:
    if opt in ('-c','--city'):
        cityName = arg
    elif opt in ('-f','--firstYear'):
        firstYear = int(arg)

cityData = daily.load(cityName)

if firstYear != None:
    keys = cityData.keys()
    for key in keys:
        if key.year < firstYear:
            del cityData[key]

class YearMonthFilter():
    __slots__ = ()
    def __init__(self, year, month):
        self.year = year
        self.month = month
    #
    def __call__(self, year = None):
        if year != None:
            self.year = year
        if type(self.year) != TupleType:
            self.year = (self.year,)
        for year in self.year:
            baseDate = datetime.date(year, self.month, 1).toordinal()

            endYear = year
            endMonth = self.month+1
            if endMonth > 12:
                endMonth = 1
                endYear += 1

            endDate = datetime.date(endYear, endMonth, 1).toordinal()
            for date in range(baseDate, endDate):
                yield datetime.date.fromordinal(date)

    def __str__(self):
        return "YearMonthFilter(year=%s, month=%s)" % (self.year, self.month)

    @property
    def filenamePart(self):
        return '%02d' % self.month

    @property
    def chartTitle(self):
        return monthName(self.month)

class BeforeDateFilter():
    __slots__ = ()
    def __init__(self, month, day, year=None):
        self.year = year
        self.month = month
        self.day = day
    #
    def __call__(self, year = None):
        if year != None:
            self.year = year
        #
        if type(self.year) != TupleType:
            self.year = (self.year,)
        for year in self.year:
            baseDate = datetime.date(year, 1, 1).toordinal()
            endDateTime = datetime.date(year, self.month, self.day).toordinal()
            for date in range(baseDate, endDateTime):
                yield datetime.date.fromordinal(date)

    @property
    def filenamePart(self):
        return 'before-%02d-%02d' % (self.month, self.day)

    @property
    def chartTitle(self):
        return 'before %s %02d' % (monthName(self.month), self.day)

class MonthFilter():
    __slots__ = ()
    def __init__(self, month):
        self.month = month
    #
    def __call__(self, date):
        month = datetime.date.fromordinal(date).month
        return month == self.month


def filterData(dayFilter, field):
    data = []
    #
    for dateTime in dayFilter():
        if dateTime in cityData:
            val = field(cityData[dateTime])
            #print "'%s'" % strval
            if val != None:
                #data.append( (time.strftime('%Y-%m-%d', time.gmtime(dateTime)), val) )
                data.append(val)
    return data

class Sum:
    __slots__ = ()
    def __init__(self, total, count):
        self.total = total
        self.count = count

def filterSum(dayFilter, field):
    data = filterData(dayFilter, field)

    return Sum(total = sum(data), count = len(data))

class Monthly:
    __slots__ = ()
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

    df = copy.copy(dayFilter)
    maxCount = 0
    for year in range(cityData.minYear, lastYear+1):
        df.year = (year,)
        md = filterData(df, field)
        if len(md) > 0:
            if len(md) > maxCount:
                maxCount = len(md)
            v = sum(md)
            if not cumulative:
                v /= len(md)
                v = int(v*10+.5)/10.0

            yearCountVal.append( (year, len(md), v) )

    validCount = int(maxCount * 0.85)


    for (y,c,v) in yearCountVal:
        if c < validCount:
            print "Discarding %d because it only has %d/%d values" % (y, c, maxCount)
            continue
        dataByYear[y] = v
    return dataByYear


def normalMonthlyDatas(year, dayFilter, field, cumulative):
    valByYear = yearDatas(dayFilter, field, now.year-1, cumulative)

    if len(valByYear.keys()) == 0:
        return None
    dataSum = 0
    dataCount = 0
    recentVals = []

    minVal = 999999
    minYear = 0
    maxVal = -999999
    maxYear = 0

    for y, val in valByYear.iteritems():
        if y > year - 31 and y < year:
            recentVals.append(val)
            dataCount += 1
            dataSum += val
        if val < minVal:
            minVal = val
            minYear = y
        if val > maxVal:
            maxVal = val
            maxYear = y

    std = numpy.std([float(a) for a in recentVals])

    return Monthly(dataSum / dataCount, minVal, maxVal, dataCount, std, minYear, maxYear)

def oldNormalMonthlyDatas(year, dayFilter, field, cumulative):
    valByYear = yearDatas(dayFilter, field, now.year-1, cumulative)

    if len(valByYear.keys()) == 0:
        return None
    dataSum = 0
    dataCount = 0
    recentVals = []

    minVal = 999999
    minYear = 0
    maxVal = -999999
    maxYear = 0

    for y, val in valByYear.iteritems():
        if y > year - 61 and y < year - 30:
            recentVals.append(val)
            dataCount += 1
            dataSum += val
        if val < minVal:
            minVal = val
            minYear = y
        if val > maxVal:
            maxVal = val
            maxYear = y

    std = numpy.std([float(a) for a in recentVals])

    return Monthly(dataSum / dataCount, minVal, maxVal, dataCount, std, minYear, maxYear)

def normalMonthlyAverage(year, dayFilter, field):
    return normalMonthlyDatas(year, dayFilter, field, cumulative = False)

def normalMonthlySum(year, dayFilter, field):
    return normalMonthlyDatas(year, dayFilter, field, cumulative = True)

def oldNormalMonthlyAverage(year, dayFilter, field):
    return oldNormalMonthlyDatas(year, dayFilter, field, cumulative = False)

def oldNormalMonthlySum(year, dayFilter, field):
    return oldNormalMonthlyDatas(year, dayFilter, field, cumulative = True)

def thisMonthOverTime(month):
    for fname in ['MEAN_TEMP']:
        findex = daily.fields._fields.index(fname)
        data = []
        for year in range(min(cityData.keys()),2010):
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
        for year in range(min(cityData.keys()),2010):
            data.append((year, filterSum(YearMonthFilter(year, month), findex).total))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("ThisMonthOverTime_%s_%s" % (fname, monthName(month)), yaxis=2)
        plot.open()
        plot.addLine(gnuplot.Line(fname, data, lineColour='blue'))
        plot.addLine(gnuplot.Line('linear', lineFit, lineColour='green'))
        plot.plot()
        plot.close()



def annualPlots(year):
    for field in [Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature"),
                  FractionVal(daily.SNOW_ON_GRND_CM, "Snow-on-the-ground"),
                  FractionVal(daily.AVG_WIND, "Wind"),
                  FreezingDegreeDaysSnowDepth()]:
        print field.name

        current = []
        average = []
        oldAverage = []
        lowest = []
        highest = []
        stdLow = []
        stdHigh = []

	for month in range(1,13):
	    thisyear = filterAverage(YearMonthFilter(year, month), field)
	    normal = normalMonthlyAverage(year, YearMonthFilter(year=None, month=month), field)
            oldNormal = oldNormalMonthlyAverage(year, YearMonthFilter(year=None, month=month), field)

            average.append("%d %.1f" % (month, normal.average))
            oldAverage.append("%d %.1f" % (month, oldNormal.average))
            stdLow.append("%d %.1f" % (month, normal.average-normal.std))
            stdHigh.append("%d %.1f" % (month, normal.average+normal.std))
            lowest.append("%d %.1f" % (month, normal.minimum))
            highest.append("%d %.1f" % (month, normal.maximum))
            if thisyear != None and thisyear.count >= 15:
                current.append("%d %.1f" % (month, thisyear.average))

                units = field.units
                print("%10s-%10s: %+6.1f%s (%d: %+6.1f%s, normal: %+6.1f%s, extremeMin: %+6.1f%s %s, extremeMax: %+6.1f%s %s)" %
                      (monthName(month), field.name,
                       (thisyear.average-normal.average), units, year,
                       thisyear.average, units, normal.average, units,
                       normal.minimum, units, normal.minYear,
                       normal.maximum, units, normal.maxYear) )

        stdData = stdLow + list(reversed(stdHigh))
        plot = gnuplot.Plot("%s/svg/%d_%s" % (cityName, year, field.name), yaxis=2)
        plot.open(title="%s %s" % (cityName, field.title),
                  xtics=['"Jan" 1', '"Feb" 2', '"Mar" 3', '"Apr" 4', '"May" 5', '"Jun" 6',
                         '"Jul" 7', '"Aug" 8', '"Sep" 9', '"Oct" 10', '"Nov" 11', '"Dec" 12'])
        plot.addLine(gnuplot.Line('30-year std-dev',  stdData, lineColour='#e3e3e3', plot='filledcurves'))
        plot.addLine(gnuplot.Line("30-year normal", average, lineColour='#007700'))
        plot.addLine(gnuplot.Line("60 to 30 year normal", oldAverage, lineColour='#555500'))
        plot.addLine(gnuplot.Line("Record min", lowest, lineColour='blue'))
        plot.addLine(gnuplot.Line("Record max", highest, lineColour='red'))
        plot.addLine(gnuplot.Line("%d" % year, current, lineColour='purple'))
        plot.plot()
        plot.close()



    for field in (FractionVal(daily.TOTAL_SNOW_CM, "Snowfall"),
                  FractionVal(daily.TOTAL_RAIN_MM, "Rainfall"),
                  FractionVal(daily.TOTAL_PRECIP_MM, "Precip")):
        print field.name
        print "%s\t%s\t%s\t%s\t%s" % ("Month", "%d" % year, "Average", "Record max", "Record min")

        current = []
        average = []
        oldAverage = []
        lowest = []
        highest = []
        stdLow = []
        stdHigh = []


	for month in range(1,13):
	    thisyear = filterSum(YearMonthFilter(year, month), field)
	    normal = normalMonthlySum(year, YearMonthFilter(year, month), field)
            oldNormal = oldNormalMonthlySum(year, YearMonthFilter(year=None, month=month), field)
            if normal != None:
                average.append((month, normal.average))
                oldAverage.append((month, oldNormal.average))
                stdLow.append("%d %.1f" % (month, normal.average-normal.std))
                stdHigh.append("%d %.1f" % (month, normal.average+normal.std))
                lowest.append((month, normal.minimum))
                highest.append((month, normal.maximum))

                if thisyear.count > 14:
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
            plot = gnuplot.Plot("%s/svg/%d_%s" % (cityName, year, field.name), yaxis=2)
            plot.open(title="%s %s" % (cityName, field.title),
                      xtics=['"Jan" 1', '"Feb" 2', '"Mar" 3', '"Apr" 4', '"May" 5', '"Jun" 6',
                             '"Jul" 7', '"Aug" 8', '"Sep" 9', '"Oct" 10', '"Nov" 11', '"Dec" 12'])
            plot.addLine(gnuplot.Line('30-year std-dev',  stdData, lineColour='#e3e3e3', plot='filledcurves'))
            plot.addLine(gnuplot.Line("30-year normal", average, lineColour='#007700'))
            plot.addLine(gnuplot.Line("60 to 30 year normal", oldAverage, lineColour='#555500'))
            plot.addLine(gnuplot.Line("Record min", lowest, lineColour='blue'))
            plot.addLine(gnuplot.Line("Record max", highest, lineColour='red'))
            plot.addLine(gnuplot.Line("%d" % year, current, lineColour='purple'))
            plot.plot()
            plot.close()


def annualOrderedByMonth(monthFilter, field, cumulative):
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

    yearsByVal = reverseDictionary(valByYears)

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
    std = numpy.std([float(a) for a in last30Years])
    #print
    if len(yearsByVal.keys()) > 0:
        plot = gnuplot.Plot('%s/svg/yearOrdering.%s.%s' % (cityName,
                                                           monthFilter.filenamePart,
                                                           field.title),
                            yaxis=2)
        legend='on left'
        if max(yearsByVal.keys()) < 0:
            legend='bottom right'
        ymin = None
        if cumulative:
            ymin = 0
        plot.open(xtics=plotTics, xticsRotate=90, xticsFont='Arial,10', legend=legend,
                  ymin=ymin,
                  title='%s %s for %s' % (cityName.capitalize(),
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
    annualPlots(2015)

    monFilter = YearMonthFilter(year = now.year, month = 3)
    #annualOrderedByMonth(monFilter, FractionVal(daily.TOTAL_PRECIP_MM, "Precip"), cumulative=True)
    #annualOrderedByMonth(monFilter, FractionVal(daily.TOTAL_RAIN_MM, "Rain"), cumulative=True)
    annualOrderedByMonth(monFilter, FractionVal(daily.TOTAL_SNOW_CM, "Snow"), cumulative=True)
    #annualOrderedByMonth(monFilter, FreezingDegreeDaysSnowDepth(), cumulative=False)
    annualOrderedByMonth(monFilter, FractionVal(daily.SNOW_ON_GRND_CM, "Snow-on-the-ground"), cumulative=False)
    annualOrderedByMonth(monFilter, FractionVal(daily.AVG_WIND, "Wind"), cumulative=False)
    annualOrderedByMonth(monFilter, Avg(daily.MIN_TEMP, daily.MAX_TEMP, "Temperature"), cumulative=False)

    #for year in range(cityData.minYear, cityData.maxYear+1):
    #    print year, filterData(BeforeDateFilter(now.tm_mon, now.tm_mday, year), Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature"))

    SoFarThisYearFilter = BeforeDateFilter(datetime.date.today().month, datetime.date.today().day, datetime.date.today().year)
    print filterAverage(SoFarThisYearFilter, Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature"))
    print normalMonthlyAverage(now.year, SoFarThisYearFilter, Avg(daily.MAX_TEMP, daily.MIN_TEMP, "Temperature"))

    annualOrderedByMonth(SoFarThisYearFilter, Avg(daily.MIN_TEMP, daily.MAX_TEMP, "Temperature"), cumulative=False)
    #annualOrderedByMonth(SoFarThisYearFilter, FractionVal(daily.TOTAL_RAIN_MM, "Rain"), cumulative=True)
