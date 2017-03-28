#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, datetime, posix, daily, forecast, sys, gnuplot, numpy
from enum import Enum
from decimal import Decimal
from namedList import *
from collections import namedtuple
from makefit import makeFit
import fieldOperators
import dailyFilters

def uniq(fromList):
    toDict = {}
    for i in fromList:
        toDict[i] = None
    return toDict.keys()

def dayRangeYear(startDate, step=1):
    endDate = datetime.date(startDate.year + 1, startDate.month, startDate.day)
    return daily.dayRange(startDate, endDate, step)

def dayRangeDays(startDate, days):
    endDate = startDate + datetime.timedelta(days)
    return daily.dayRange(startDate, endDate)


GeneratorResult = namedStruct('GeneratorResult', 'value year=None')
now = forecast.now
class Progress(Enum):
    none = 1
    cumulative = 2
    average = 3

class AverageGenerator():
    def __init__(self):
        self.sum = 0
        self.count = 0
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.sum += val
            self.count += 1
    #
    def result(self):
        if self.count > 0:
            return GeneratorResult(self.sum / self.count)
        return None

class MaxGenerator():
    def __init__(self):
        self.max = None
        self.maxYear = None
    #
    def process(self, val, year):
        if self.max == None or val > self.max:
            self.max = val
            self.maxYear = year
    #
    def result(self):
        return GeneratorResult(self.max, self.maxYear)

class MinGenerator():
    def __init__(self):
        self.min = None
        self.minYear = None
    #
    def process(self, val, year):
        if self.min == None or val < self.min:
            self.min = val
            self.minYear = year
    #
    def result(self):
        return GeneratorResult(self.min, self.minYear)

class MedianGenerator():
    def __init__(self):
        self.values = []
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.values.append(val)
    #
    def result(self):
        if len(self.values) > 0:
            self.values.sort()
            return GeneratorResult(self.values[len(self.values)//2])
        return None

class PercentileGenerator():
    def __init__(self, percentile):
        self.percentile = percentile
        self.values = []
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.values.append(val)
    #
    def result(self):
        if len(self.values) == 0:
            return GeneratorResult(None)
        self.values.sort()
        extra = 0
        if self.percentile > 50:
            extra = -1
        return GeneratorResult(self.values[len(self.values)*self.percentile//100+extra])

class PercentileFactory():
    def __init__(self, percentile):
        self.percentile = percentile

    def __call__(self):
        return PercentileGenerator(self.percentile)

class StdHighGenerator():
    def __init__(self):
        self.values = []
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.values.append(val)
    #
    def result(self):
        if len(self.values) == 0:
            return GeneratorResult(None)
        return GeneratorResult(sum(self.values)/len(self.values)
                               + numpy.std(self.values))

class StdLowGenerator():
    def __init__(self, minValue):
        self.minValue = minValue
        self.values = []
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.values.append(val)
    #
    def result(self):
        if len(self.values) == 0:
            return GeneratorResult(None)
        avg = sum(self.values)/len(self.values)
        std = numpy.std(self.values)
        v = avg - std
        if self.minValue != None:
            v = max(self.minValue, v)
        return GeneratorResult(v)

class StdLowFactory():
    def __init__(self, minValue):
        self.minValue = minValue

    def __call__(self):
        return StdLowGenerator(self.minValue)

class StdGenerator():
    def __init__(self):
        self.values = []
    #
    def process(self, val, year):
        if year >= now.year - 30 and year != now.year:
            self.values.append(val)
    #
    def result(self):
        assert len(self.values)
        avg = sum(self.values)/len(self.values)
        std = numpy.std(self.values)
        return GeneratorResult( (avg - std, avg + std) )

def zeroIfNone(val):
    if val == None:
        return 0
    return val

class Point():
    def __init__(self, x, y, date1, date2=None):
        self.x = x
        self.y = y
        self.date1 = date1
        self.date2 = date2
    def datestr(self):
        ret = str(self.date1)
        if isinstance(self.date1, tuple):
            ret = '/'.join([str(a) for a in self.date1])
        if self.date2 != None:
            ret = ret + ' ' + '/'.join([str(a) for a in self.date2])
        return ret
    def __str__(self):
        if isinstance(self.y, tuple):
            return '{x} {y} {date}'.format(x=self.x,
                                           y=' '.join(['%.1f' % y for y in self.y]),
                                           date=self.datestr())
        if self.y is None:
            return ''
        return '{x} {y:.1f} {date}'.format(x=self.x,
                                           y=float(self.y),
                                           date=self.datestr())
    #
    def __repr__(self):
        if isinstance(self.y, tuple):
            return '%d,%s,%s' % (self.x, ','.join(['%.1f' % y for y in self.y]), self.datestr())
        if self.y is None:
            return '%s,%s,%s' % (datetime.date.fromordinal(self.x), self.y, self.datestr())
        return '%s,%.1f,%s' % (datetime.date.fromordinal(self.x), self.y, self.datestr())



colours = ['violet', 'cyan', 'pink', 'green']

def yearFromSeason(season, month, useSeasons):
    if useSeasons and month < 7:
        return season + 1
    return season

def dateFromSeasonMonthDay(season, month, day, useSeasons):
    return datetime.date(yearFromSeason(season, month, useSeasons), month, day)

def seasonFromDate(date, useSeasons):
    if not useSeasons or date.month >= 7:
        return date.year
    return date.year - 1

def yearLessEqualMore(plotData, day, useSeasons):
    less = []
    equal = []
    more = []
    cval = plotData[day]
    for date in plotData:
        if date.year != day.year and date.month == day.month and date.day == day.day:
            v = plotData[date]
            #
            season = seasonFromDate(date, useSeasons)
            #
            if v == cval:
                equal.append(season)
            elif v < cval:
                less.append(season)
            else:
                more.append(season)
    return namedStruct('LessEqualMore', 'less equal more')(less, equal, more)

def annualData(rawData, field, startDate, endDate, cumulative):
    dataByDate = {}
    yearDelta = endDate.year - startDate.year
    #
    for year in range(rawData.minYear, rawData.maxYear+1):
        yearValues = {}
        yearDayCount = 0
        #
        runningValue = 0
        #
        thisYearStartDate = datetime.date(year, startDate.month, startDate.day)
        thisYearEndDate = datetime.date(year+yearDelta, endDate.month, endDate.day)
        #
        for day in daily.dayRange(thisYearStartDate, thisYearEndDate):
            dayValue = None
            yearDayCount += 1
            if day in rawData:
                if isinstance(field, dailyFilters.DayFilter):
                    dayValue = field(rawData[day])
                elif callable(field):
                    dayValue = field(rawData[day])[0]
                else:
                    dayValue = rawData[day][field.index]
            if dayValue != None:
                runningValue += dayValue
                yearValues[day] = dayValue
                if cumulative:
                    yearValues[day] = runningValue
        #
        if ( cumulative is False
             or len(yearValues) > yearDayCount*95/100
             or ( now > thisYearStartDate and now < thisYearEndDate )
        ):
            #Only count years with at least 95% of days reported
            #print('Found %d values for %d: max=%s' % (yearDayCount, year, max(yearValues.keys())))
            dataByDate.update(yearValues)
        else:
            print('Discarding year(%d) because of incomplete data' % year)
    #
    return dataByDate

def getForecast(index, city, plotData, cumulative, useSeasons, plotDateRange):
    pdata = []
    count = 0
    forecastDays = forecast.getForecastDataEnvCan(city)
    #print(forecastDays)
    fval = 0
    #
    lastDay = max(plotData.keys())
    basevalue = Decimal(0)
    if (now - lastDay).days < 30:
        basevalue = plotData[lastDay]
    #
    lessEqualMore = yearLessEqualMore(plotData, lastDay, useSeasons)
    #print(lessEqualMore)
    #
    interestingSeasons = tuple()
    #
    for date in daily.dayRange(now - datetime.timedelta(1), now + datetime.timedelta(30)):
        if (date < plotDateRange[0]) or (date >= plotDateRange[1]):
            continue
        if (date == now - datetime.timedelta(1)):
            fval = 0
        elif (date not in forecastDays):
            continue
        elif forecastDays[date].TOTAL_SNOW_CM:
            value = forecastDays[date].TOTAL_SNOW_CM
            if cumulative:
                fval += value
            else:
                fval = value
        #
        dataValue = fval
        if cumulative:
            dataValue += basevalue
        pdata.append(Point(date.toordinal(), dataValue, (date.month, date.day)))
    #
    return pdata, interestingSeasons

def getForecastTemperature(field, city, plotData, cumulative, useSeasons, plotDateRange):
    #
    lastDay = now - datetime.timedelta(2)
    if lastDay > max(plotData.keys()):
        # the entire forecast is outside the plot date range
        return []

    pdata = []
    forecastDays = forecast.getForecastDataEnvCan(city)
    for i in range(10):
        try:
            cumulativeValue = plotData[lastDay-datetime.timedelta(days=i)]
        except KeyError:
            pass
    assert(cumulativeValue is not None)
    #
    for date in daily.dayRange(now - datetime.timedelta(1), now + datetime.timedelta(7)):
        if ( (date < plotDateRange[0]) or (date >= plotDateRange[1]) ):
            # If we are beyond the requested plot range, don't even bother.
            continue

        tempFields = [
            'MAX_TEMP',
            'MAX_TEMPop',
            'MIN_TEMP',
            'MIN_TEMPop',
            'MEAN_TEMP',
            'TOTAL_RAIN_MM',
        ]
        #print(field.name)
        curValue = None
        if ( (date in forecastDays) and field.name in tempFields ):
            thisDay = forecastDays[date]
            if callable(field):
                curValue = field(thisDay)
            elif thisDay[field.index+1] != 'M' and thisDay[field.index] is not None:
                curValue = thisDay[field.index]

        if curValue is None:
            lastDate = max(plotData.keys())
            try:
                curValue = plotData[lastDate]
            except KeyError:
                print(lastDate, field.name)
                raise
            cumulativeValue = curValue
        else:
            cumulativeValue += curValue


        dataValue = curValue
        if cumulative:
            dataValue = cumulativeValue
        #
        pdata.append(Point(date.toordinal(), dataValue, (date.month, date.day)))
    #
    return pdata


def manyYearsAgo(rawData, startDate):
    yearDiff = 0

    oldestDate = min(rawData.keys())
    while startDate.year-yearDiff >= oldestDate.year:
        yearDiff += 1
        try:
            pastDate = datetime.date(startDate.year-yearDiff, startDate.month, startDate.day)
        except ValueError:
            # This must be February 29th in some non-leap-year, skip
            continue
        yield pastDate

def cullLabels(labelLine):
    retLine = []
    for i in range(len(labelLine)):
        if i == 0 or i == len(labelLine) - 1:
            retLine.append(labelLine[i])
            continue
        if ( labelLine[i].date1 != labelLine[i-1].date1
             or labelLine[i].date1 != labelLine[i+1].date1 ):
            retLine.append(labelLine[i])
            continue
    return retLine


def createPlot(city, running, field, otheryears, name,
               dataStartDay, plotStartDay, plotEndDay, plotDate = None,
               plotZeros = True, plotYMin = 0, labelMinRecords = True,
               legendLocation=None):
    units = field.units
    FUTURE_DAYS = (plotEndDay - now).days
    PAST_DAYS = (now - plotStartDay).days
    useSeasons = plotEndDay.year != dataStartDay.year
    #
    seasonBySnow = {}
    snowBySeason = {}
    #
    rawData = daily.load(city)
    nowSeason = seasonFromDate(now, useSeasons)
    print('nowSeason', nowSeason)
    #
    nowDaysOffset = now - dataStartDay
    #
    #print( 'annualData(..., field = %s, startDate = %s, endDate = %s, cumulative = %s)' %
    #       (field, dataStartDay,
    #        plotEndDay,
    #        running) )
    if legendLocation is None:
        if running is True:
            legendLocation="on left top"
        else:
            legendLocation="on right top"

    plotData = annualData(rawData = rawData, field = field,
                          startDate = dataStartDay,
                          endDate = plotEndDay,
                          cumulative = running)
    #
    if plotDate == None:
        # if no date was provided, use the last date for which data is available
        plotDate = max(plotData.keys())
        print('Maximum date in plot =', plotDate)

    #
    for year in range(rawData.minYear, rawData.maxYear+1):
        #
        try:
            thisYearPlotDate = datetime.date(year, plotDate.month, plotDate.day)
        except ValueError:
            if plotDate.month == 2 and plotDate.day == 29:
                continue
            raise
        if thisYearPlotDate not in plotData:
            print("skipping %d because %s is out-of-bounds" % (year, thisYearPlotDate))
            continue
        #
        season = seasonFromDate(thisYearPlotDate, useSeasons)
        snow = plotData[thisYearPlotDate]
        if snow == None:
            snow = 0
        if (snow not in seasonBySnow):
            seasonBySnow[snow] = []
        seasonBySnow[snow].append(season)
        snowBySeason[season] = snow
        print(year, snow)

    snowTotals = sorted(seasonBySnow.keys())
    significantSnowBySeason = snowBySeason #makeFit(snowBySeason, 75)
    #
    print()
    print(name)
    print()
    #
    chartTicks = []
    chartDataOtherYears = []
    chartDataThisYear = []
    histogramBuckets = {1:{}, 2:{}, 5:{}, 10:{}, 20:{}}

    chartIndex = 0
    count = 0
    #sum = 0
    totalyears = (nowSeason - rawData.minYear)
    for snowTotal in snowTotals:
        # number of years with this amount of snow
        thiscount = len(seasonBySnow[snowTotal])
        #
        print("%d) %.1f%s, %s" % (count, snowTotal, units, seasonBySnow[snowTotal]), ["","*** median"][(count <= totalyears/2) and (count + thiscount > totalyears/2)])
        #sum += thiscount * snowTotal
        count += thiscount
        #
        if plotZeros == False and snowTotal == 0:
            # We've been told to skip zeros, so we don't plot them
            continue
        for i in range(thiscount):
            season = seasonBySnow[snowTotal][i]
            if season in significantSnowBySeason:
                chartTicks.append('"%d" %d' % (season, chartIndex))
                if season != dataStartDay.year:
                    chartDataOtherYears.append((chartIndex, snowTotal))
                else:
                    chartDataThisYear.append((chartIndex, snowTotal))
                chartIndex += 1

        for i in histogramBuckets.keys():
            snowTotalBucket = int(round(snowTotal/i)*i)
            if snowTotalBucket not in histogramBuckets[i]:
                histogramBuckets[i][snowTotalBucket] = 0
            histogramBuckets[i][snowTotalBucket] += thiscount
            if dataStartDay.year in seasonBySnow[snowTotal]:
                histogramBuckets[i][snowTotalBucket] += 1000

    #
    plot = gnuplot.Plot('%s/svg/%s.yearOrdering' % (city, name), yaxis=2)
    cumulative = "cumulative"
    if not running:
        cumulative = 'daily'
    #
    fieldFileName = field.englishName.replace(' ', '_').replace('℃', 'C')
    plot.open(title='%s %s %s as of %s' % (city.title(),
                                           cumulative,
                                           fieldFileName,
                                           max(plotData.keys())),
              xtics=chartTicks, xticsRotate=90, xticsFont='Arial,10', legend='on left',
              ylabel='%s (%s)' % (name, units), ymin=plotYMin,
              xmin=-1, xmax=chartIndex)
#              xmin=None, xmax=None)
    plot.addLine(gnuplot.Line('Other years', chartDataOtherYears, plot='boxes'))
    plot.addLine(gnuplot.Line('This year', chartDataThisYear, plot='boxes'))
    plot.plot()
    plot.close()

    for bucketSize in histogramBuckets.keys():
        plot = gnuplot.Plot('%s/svg/histogram/%s.histogram.%d' % (city, name, bucketSize), yaxis=2)
        cumulative = "cumulative"
        if not running:
            cumulative = 'daily'
        #
        histMin = min(histogramBuckets[bucketSize].keys())
        histMax = max(histogramBuckets[bucketSize].keys())
        plot.open(title='%s %s %s histogram as of %s' % (city.title(), cumulative, fieldFileName, max(plotData.keys())),
                  xticsFont='Arial,10', legend='on left',
                  ymin=0, ylabel='Number of years',
                  xmin=histMin-bucketSize, xmax=histMax+bucketSize, xlabel='%s (%s)' % (name, units),
                  boxWidth=bucketSize*.75)
        histogramLine = []
        histogramLineThisYear = []
        for i in range(histMin, histMax+1, bucketSize):
            v = histogramBuckets[bucketSize].get(i,0)
            if v < 1000:
                histogramLine.append((i, v))
            else:
                histogramLineThisYear.append((i, v-1000))

        plot.addLine(gnuplot.Line('Other years', histogramLine, plot='boxes'))
        plot.addLine(gnuplot.Line('This year', histogramLineThisYear, plot='boxes'))
        plot.plot()
        plot.close()

    #
    avgYears = list(filter(lambda t: t in snowBySeason, range(nowSeason-30, nowSeason)))
    avgYearVals = [snowBySeason[a] for a in avgYears]
    avg = 0
    if len(avgYearVals) > 0:
        avg = sum(avgYearVals)/len(avgYearVals)

    print("Average is %.1f%s" % (avg, units))
    #
    #print(snowBySeason)
    currentVariance = ("%.1f%s %s average"
                       % (abs(snowBySeason.get(nowSeason,0) - avg),
                          units,
                          ["below", "above"][snowBySeason.get(nowSeason,0) > avg]))
    print("%d is %s" % (nowSeason, currentVariance))
    print( "%d of past %d years had more"
           % (len(tuple(filter(lambda t: snowBySeason[t] > snowBySeason.get(nowSeason,0), avgYears))),
              len(avgYears)),
           tuple(filter(lambda t: snowBySeason[t] > snowBySeason.get(nowSeason,0), avgYears)) )

    print( "%d of past %d years had less"
           % (len(list(filter(lambda t: snowBySeason[t] < snowBySeason.get(nowSeason,0), avgYears))),
              len(avgYears)),
           tuple(filter(lambda t: snowBySeason[t] < snowBySeason.get(nowSeason,0), avgYears)) )
    #
    data = []
    #
    def genDates():
        dates = []
        skip = 7

        for dayDate in dayRangeYear(plotStartDay, step=7):
            dates.append('"%s" %d' % (time.strftime('%b/%d', dayDate.timetuple()), dayDate.toordinal()))
        return dates

    dates = genDates()

    def genYear(season):
        year = season
        if useSeasons and dataStartDay.month < 7:
            year += 1

        pdata = []
        curSeasonStart = plotStartDay
        yearDiff = dataStartDay.year-year
        print('genYear(season = %d) year = %d, curSeasonStart = %s, yearDiff = %d'
              % (season, year, curSeasonStart, yearDiff) )

        for dayDate in dayRangeDays(curSeasonStart, PAST_DAYS+FUTURE_DAYS):
            try:
                dataDate = datetime.date(dayDate.year-yearDiff, dayDate.month, dayDate.day)
            except ValueError:
                # the current date must be February 29th, and 'year' wasn't a leap year.
                continue

            #if season == nowSeason and dayDate == now:
            #    return pdata
            if (dayDate.month, dayDate.day) == (now + datetime.timedelta(FUTURE_DAYS)).timetuple()[1:3]:
                return pdata

            s = plotData.get(dataDate, None)
            if s != None:
                pdata.append(Point(dayDate.toordinal(), s, (dataDate.year, dataDate.month, dataDate.day)))
            else:
                pdata.append(None)
            if season == nowSeason and dayDate == now:
                return pdata
        return pdata

    def genWithGen(Generator):
        pdata = []

        for dayDate in dayRangeDays(plotStartDay, PAST_DAYS+FUTURE_DAYS):
            generator = Generator()
            resultCount = 0

            for pastDate in manyYearsAgo(rawData, dayDate):
                try:
                    data = plotData[pastDate]
                except KeyError:
                    continue
                if data != None:
                    generator.process(data, pastDate.year)
                    resultCount += 1

            result = generator.result()

            if result != None:
                if result.year == None:
                    date = (str(dayDate.month), str(dayDate.day))
                    pdata.append(Point(dayDate.toordinal(), result.value, '#'+'/'.join(date)))
                else:
                    date = (result.year, dayDate.month, dayDate.day)
                    pdata.append(Point(dayDate.toordinal(), result.value, date[0], date[1:]))

        return pdata

    def genAverage():
        return genWithGen(AverageGenerator)

    def genMax():
        return genWithGen(MaxGenerator)

    def genMedian():
        return genWithGen(MedianGenerator)

    plot = gnuplot.Plot("%s/svg/%s" % (city, name), yaxis=2, output='svg')
    plot.open(xtics=dates, ylabel='%s (%s)' % (name, units), legend=legendLocation, margins=[6,8,3,3])

    #stdData = ( genWithGen(StdLowFactory(field.minValue))
    #            + list(zip(reversed(genWithGen(StdHighGenerator)))) )
    #plot.addLine(
    #    gnuplot.Line(
    #        '30-year std-dev', stdData, lineColour='#e3e3e3', plot='filledcurves'))

    ciData        =         (        genWithGen(PercentileFactory(10))        +
                                     list(zip(reversed(genWithGen(PercentileFactory(90))))) )
    plot.addLine(
        gnuplot.Line(
            'Normal (80% CI)', ciData, lineColour='#e3e3e3', plot='filledcurves'))

    plot.addLine(gnuplot.Line('30-year average', genAverage(), lineColour='#008800'))
    #plot.addLine(gnuplot.Line('30-year median',  genMedian(), lineColour='blue', lineWidth=2))

    recordMax=genMax()
    RecordLabels = cullLabels(recordMax)
    plot.addLine(gnuplot.Line('max',     recordMax, lineColour='orange', lineWidth=2))
    plot.addLine(gnuplot.Line(title=None,     lineData=RecordLabels,
                              pointType=None, plot="labels notitle rotate left offset 0,1"))


    recordMin = genWithGen(MinGenerator)
    plot.addLine(gnuplot.Line('min',     recordMin, lineColour='purple', lineWidth=2))
    if labelMinRecords:
        recordMinLabels = cullLabels(recordMin)
        plot.addLine(gnuplot.Line(title=None,     lineData=recordMinLabels,
                                  pointType=None, plot="labels notitle rotate right offset 0,-1"))


    #print('nowSeason', nowSeason)
    CURRENT=genYear(nowSeason)
    currentLabel = '%d' % nowSeason
    if useSeasons:
        currentLabel = '%d/%d' % (nowSeason, nowSeason+1)
    plot.addLine(gnuplot.Line(currentLabel, CURRENT, lineColour='red', lineWidth=2))

    crossMin = tuple()
    crossMax = tuple()

    if field.name == 'TOTAL_SNOW_CM':
        #forecastMin, crossMin = getForecast(0, city, plotData, running, useSeasons, (plotStartDay, plotEndDay) )
        #forecastMax, crossMax = getForecast(1, city, plotData, running, useSeasons, (plotStartDay, plotEndDay) )
        #plot.addLine(gnuplot.Line('forecast', forecastMin, 'red', 1, lineType='2'))
        #plot.addLine(gnuplot.Line('forecast', forecastMax, 'red', 1, lineType='2'))
        pass
    elif field.name in ('MAX_TEMP', 'MIN_TEMP', 'MAX_TEMPop', 'MIN_TEMPop', 'MEAN_TEMP'):
        forecastTemp = getForecastTemperature(field, city, plotData, running, useSeasons, (plotStartDay, plotEndDay) )
        plot.addLine(gnuplot.Line('forecast', forecastTemp, 'red', 1, lineType='2'))
    elif field.name in ('TOTAL_RAIN_MM'):
        forecastTemp = getForecastTemperature(field, city, plotData, running, useSeasons, (plotStartDay, plotEndDay) )
        plot.addLine(gnuplot.Line('forecast', forecastTemp, 'red', 1, lineType='2'))

    cindex = 0

    oyears = otheryears
    if running:
        oyears = oyears + crossMin + crossMax

    for year in sorted(uniq(oyears)):
        c = None
        if cindex < len(colours):
            c = colours[cindex]
        yearLabel = '%d' % year
        if useSeasons:
            yearLabel = '%d/%d' % (year, year+1)

        plot.addLine(gnuplot.Line(yearLabel, genYear(year),
                                  lineColour=c, plot='lines', lineWidth=2))
        cindex+=1

    plot.plot()
    plot.close()
    ret = plot.fname

    #print(len(CURRENT), len(recordMax))
    for vi in range(len(CURRENT)):
        if ( CURRENT[vi] != None
             and recordMax[vi] != None
             and ( recordMax[vi].y is None
                   or CURRENT[vi].y > recordMax[vi].y )
        ):
            recordVal = recordMax[vi].y
            if recordVal == None:
                recordVal = str(recordVal)
            else:
                recordVal = '%.1f' % recordVal
            print( CURRENT[vi].datestr(),
                   CURRENT[vi].y,
                   units,
                   recordMax[vi].datestr(),
                   recordVal,
                   file=sys.stderr)
            print("Record {date} {val:.1f}{units} beats {prevRecordDate} {prevRecordVal}{units}"
                  .format(
                      date=CURRENT[vi].datestr(),
                      val=CURRENT[vi].y,
                      units=units,
                      prevRecordDate=recordMax[vi].datestr(),
                      prevRecordVal=recordVal) )
    return ret

if __name__ == '__main__':
    (city, output, otherYears, plotDate) = (sys.argv[1:] + [None])[:4]
    if plotDate != None:
        plotDate = tuple(map(int, plotDate.split('-')))
        plotDate = datetime.date(plotDate[0],plotDate[1],plotDate[2])
        print(plotDate)

    ChartDescription = namedtuple('ChartDescription', 'field cumulative plotZeros labelMinRecords')

    fieldByOutput = {
        "DailySnowfall":      ChartDescription(daily.TOTAL_SNOW_CM,   cumulative=False, plotZeros=True,  labelMinRecords=False),
        "CumulativeSnowfall": ChartDescription(daily.TOTAL_SNOW_CM,   cumulative=True,  plotZeros=True, labelMinRecords=True),
        "SnowOnTheGround":    ChartDescription(daily.SNOW_ON_GRND_CM, cumulative=False, plotZeros=True,  labelMinRecords=False),
        "DailyRainfall":      ChartDescription(daily.TOTAL_RAIN_MM,   cumulative=False, plotZeros=True,  labelMinRecords=False)}

    #(field, cumulative, plotZeros) = fieldByOutput[output]
    chart = fieldByOutput[output]

    dataStartDay = datetime.date(now.year, 7, 1)
    if now.month < 7:
        dataStartDay = datetime.date(now.year-1, 7, 1)

    createPlot(city,
               running=chart.cumulative,
               field=chart.field,
               otheryears=tuple(int(a) for a in otherYears.split(',')),
               name=output,
               dataStartDay = dataStartDay,
               plotStartDay = now - datetime.timedelta(21),
               plotEndDay = now + datetime.timedelta(60),
               plotDate = plotDate,
               plotZeros = chart.plotZeros,
               labelMinRecords = chart.labelMinRecords
    )
