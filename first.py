#!/usr/bin/python3
# -*- coding: utf-8 -*-
import daily, datetime, sys, gnuplot, linear, time, getopt
import datacache
from fieldOperators import *
from plotdict import plotdict
from makefit import makeFit
from reversedict import reverseDict
import argparse
from monthName import monthName

now = datetime.datetime.now().date()

class DateRange():
    def __init__(self, start, last=None, end=None):
        assert( last != None or end != None )
        self.startMonth, self.startDay = map(int, start.split(','))
        if last is None:
            self.endMonth, self.endDay = map(int, end.split(','))
            print('Using end: {}/{}'.format(self.endMonth, self.endDay))
        else:
            (lastMonth, lastDay) = map(int, args.last.split(','))
            print('Using last: {}/{}'.format(lastMonth, lastDay))
            endDate = datetime.date(now.year, lastMonth, lastDay)+datetime.timedelta(1)
            self.endMonth, self.endDay = (endDate.month, endDate.day)
    def yearCross(self):
        if ( self.endMonth < self.startMonth
             or ( self.endMonth == self.startMonth
                  and self.endDay == self.startDay )
        ):
            return 1
        return 0
    def todayIsYearCross(self):
        return ( now.month < self.startMonth
                 or ( now.month == self.startMonth
                      and now.day <= self.startDay ) )
    def lastDay(self):
        if self.endMonth == 3 and self.endDay == 1:
            return 'Feb 28,29'
        lastDate = datetime.date(now.year, self.endMonth, self.endDay)-datetime.timedelta(1)
        return '%s %u' % (monthName(lastDate.month), lastDate.day)

    def __str__(self):
        return '{}/{}-{}/{}'.format(self.startMonth, self.startDay, self.endMonth, self.endDay)


def keyOfMinMaxValue(data):
    minKey = None
    maxKey = None

    for (key, value) in data.iteritems():
        if value == None:
            continue
        if minKey == None:
            minKey = [key]
            maxKey = [key]

        elif value < data[minKey[0]]:
            minKey = [key]
        elif value == data[minKey[0]]:
            minKey.append(key)
        elif value > data[maxKey[0]]:
            maxKey = [key]
        elif value == data[maxKey[0]]:
            maxKey.append(key)

    return (minKey, maxKey)

def valuesFromKeyList(db, keyList):
    return filter(lambda t: t!=None, [db.get(c,None) for c in keyList])

def lookupEmptyListIfNone(db, key):
    if key == None:
        return []
    return db[key]

def calcAvg(data):
    if len(data) == 0:
        return None
    return sum(data) / len(data)

def calcMedian(data):
    if len(data) == 0:
        return None
    return data[len(data)//2]

def calcDate(year, month, day, offset):
    if offset == None:
        return None
    return datetime.date(year, month, day) + datetime.timedelta(offset)

def showRecords(name, position, years, firstByYear, dateRange):
    dates = [datetime.date(e, dateRange.startMonth, dateRange.startDay) + datetime.timedelta(firstByYear[e]) for e in years]
    print("{} {} was ".format(position, name), end='')
    if len(years) > 1:
        print('a tie between ', end='')
    print('%s.' % (', '.join(map(str, dates))))
    return dates


def first(cityName,
          expr,
          name,
          dateRange,
          excludeThisYear=False,
          order="first",
          yaxisLabel=None,
          run=1,
          limitToMostRecentYears=None,
          verboseIfInDateRange=None,
):
    data = daily.load(cityName)
    if limitToMostRecentYears != None:
        ndata = daily.Data()
        yearsAgo = datetime.date(now.year-limitToMostRecentYears, now.month, now.day)
        for key in data:
            if key >= yearsAgo:
                ndata[key] = data[key]
        data = ndata
    fieldDict = {
        'min': Value(daily.MIN_TEMP),
        'max': Value(daily.MAX_TEMP),
        'tempSpan': ValueDiff(daily.MAX_TEMP, daily.MIN_TEMP),
        'rain': Value(daily.TOTAL_RAIN_MM),
        'humidex': Value(daily.MAX_HUMIDEX),
        'snow': Value(daily.TOTAL_SNOW_CM),
        'snowpack': ValueEmptyZero(daily.SNOW_ON_GRND_CM),
        'windgust': Value(daily.SPD_OF_MAX_GUST_KPH),
        'wind': Value(daily.AVG_WIND),
        'windchill': Value(daily.MIN_WINDCHILL),
        'avgWindchill': Value(daily.MIN_WINDCHILL),
    }
    fieldValues = fieldDict.values()
    referencedValues=[]
    for fieldName in fieldDict.keys():
        if '{'+fieldName+'}' in expr:
            referencedValues.append(fieldName)

    firstByYear = {}
    eThisYear = now.year
    endTimeThisYear = datetime.date(now.year, dateRange.endMonth, dateRange.endDay)
    if dateRange.yearCross() and now < endTimeThisYear:
        eThisYear -= 1


    for baseyear in range(data.minYear, data.maxYear-dateRange.todayIsYearCross()+1):

        try:
            dayOffset = datacache.readCache(cityName, baseyear,
                                            '{}.{}.{}.{}'.format(name,order,str(dateRange),expr))
            if dayOffset != None:
                firstByYear[baseyear] = dayOffset
            continue
        except datacache.NotInCache:
            pass
        starttime = datetime.date(baseyear, dateRange.startMonth, dateRange.startDay)
        endtime = datetime.date(baseyear+dateRange.yearCross(), dateRange.endMonth, dateRange.endDay)

        #print baseyear, starttime, endtime
        dayRange = daily.dayRange(starttime,endtime)
        if order=="last":
            dayRange = daily.dayRange(endtime-datetime.timedelta(1), starttime-datetime.timedelta(1), -1)
            if excludeThisYear and baseyear == now.year-dateRange.yearCross():
                # don't consider this year when looking for records for last event, because this year is not over
                continue

        expectedDayCount = 0
        observedDayCount = 0
        for day in dayRange:
            expectedDayCount += 1
            if day in data:
                observedDayCount += 1
            else:
                continue

            if baseyear in firstByYear:
                # We already figured out which day was first
                continue

            vals = {}
            for fieldName, fieldCall in fieldDict.items():
                try:
                    vals[fieldName] = fieldCall(data[day], day)
                    vals[fieldName+'Flag'] = '"' + fieldCall.getFlag(data[day]) + '"'
                except KeyError:
                    #print day, 'KeyError'
                    vals[fieldName] = None
            skip=False
            usedVals={}
            for fieldName in fieldDict.keys():
                if fieldName in referencedValues:
                    if vals[fieldName] is None:
                        #print 'Skipping {} because {} is None'.format(day, fieldName)
                        skip=True
                        break
                    usedVals[fieldName] = vals[fieldName]
            if skip:
                continue

            #resolvedExpr = expr.format(**vals)
            #print(vals)
            #val = eval(expr)
            val = eval(expr, vals)

            #if True: #day == datetime.date(2015,10,17):
            #print day, resolvedExpr, val

            if val is True:
                dayOffset = (day - starttime).days
                firstByYear[baseyear] = dayOffset
                break

        observedPercent = observedDayCount * 100 / expectedDayCount
        if observedPercent < 85 and baseyear != eThisYear:
            print('Skipping {baseyear} because it only had {observedPercent:.1f}% of the days'.format(**locals()))
            if baseyear in firstByYear:
                firstByYear.pop(baseyear)
        elif baseyear not in firstByYear and baseyear != eThisYear:
            print('Event did not happen during {}.'.format(baseyear))
        datacache.cacheThis(cityName, baseyear,
                            '{}.{}.{}.{}'.format(name,order,str(dateRange),expr),
                            firstByYear.get(baseyear, None))


    yearByFirst = reverseDict(firstByYear)
    #for offset in sorted(yearByFirst.keys()):
    #    for year in yearByFirst[offset]:
    #        print datetime.date(year, dateRange.startMonth, dateRange.startDay) + datetime.timedelta(offset)
    #print yearByFirst

    verbose = False
    if verboseIfInDateRange == None:
        verbose = True
    elif eThisYear in firstByYear:
        thisYearFirstDayOffset = firstByYear[eThisYear]
        firstThisYearDate = (
            datetime.date(eThisYear, dateRange.startMonth, dateRange.startDay)
            + datetime.timedelta(thisYearFirstDayOffset) )
        if ( firstThisYearDate >= verboseIfInDateRange[0]
             and firstThisYearDate <= verboseIfInDateRange[1] ):
            verbose = True

    (earliest, secondEarliest, *ignore) = sorted(filter(lambda y: y!=now.year-dateRange.yearCross(), yearByFirst.keys()))[:2] + [None,None]
    (secondLatest, latest, *ignore) = sorted(filter(lambda y: y!=now.year-dateRange.yearCross(), yearByFirst.keys()))[-2:] + [None,None]

    earliestYears = lookupEmptyListIfNone(yearByFirst, earliest)
    secondEarliestYears = lookupEmptyListIfNone(yearByFirst, secondEarliest)

    latestYears = lookupEmptyListIfNone(yearByFirst, latest)
    secondLatestYears = lookupEmptyListIfNone(yearByFirst, secondLatest)

    earliestDates=[]
    latestDates=[]
    if verbose:
        earliestDates=showRecords(name, 'earliest', earliestYears, firstByYear, dateRange)
        showRecords(name, '2nd earliest', secondEarliestYears, firstByYear, dateRange)
        showRecords(name, '2nd latest', secondLatestYears, firstByYear, dateRange)
        latestDates=showRecords(name, 'latest', latestYears, firstByYear, dateRange)

    avgKeys = filter(lambda t: t in firstByYear, range(eThisYear-30, eThisYear))

    offsets = sorted([firstByYear[a] for a in avgKeys])
    avg = calcAvg(offsets)
    median = calcMedian(offsets)

    avgFirst = calcDate(eThisYear, dateRange.startMonth, dateRange.startDay, avg)
    medianFirst = calcDate(eThisYear, dateRange.startMonth, dateRange.startDay, median)
    if verbose:
        print("average {name} is {avgFirst}".format(**locals()))
        print("median {name} is {medianFirst}".format(**locals()))

    ret = None
    if eThisYear in firstByYear:
        thisYearFirst = firstByYear[eThisYear]
        countEarlier = 0
        countEqual = 0
        countLater = 0
        recentCountEarlier = []
        recentCountEqual = []
        recentCountLater = []

        for first in sorted(yearByFirst.keys()):
            if first < thisYearFirst:
                countEarlier += len(yearByFirst[first])
                recentCountEarlier += filter(lambda y: y<eThisYear and y > eThisYear-31, yearByFirst[first])
            elif first == thisYearFirst:
                countEqual += len(yearByFirst[first]) - 1 #Subtract the current year
                recentCountEqual += filter(lambda y: y<eThisYear and y > eThisYear-31, yearByFirst[first])
            else:
                countLater += len(yearByFirst[first])
                recentCountLater += filter(lambda y: y<eThisYear and y > eThisYear-31, yearByFirst[first])

        totalCount = countEarlier + countEqual + countLater
        totalRecentCount = len(recentCountEarlier) + len(recentCountEqual) + len(recentCountLater)

        firstThisYear = ( datetime.date(eThisYear, dateRange.startMonth, dateRange.startDay)
                          + datetime.timedelta(thisYearFirst) )
        if verbose:
            print('%s %s was %s' % (now.year, name, firstThisYear ))
            print('%d%% of last %d years were earlier.'
                  % (round(countEarlier * 100.0 / totalCount), totalCount))
            print('%d%% of last %d years were the same.'
                  % (round(countEqual * 100.0 / totalCount), totalCount))
            print('%d%% of last %d years were later.'
                  % (round(countLater * 100.0 / totalCount), totalCount))
            print('%d of last %d years were earlier.'
                  % (len(recentCountEarlier), totalRecentCount), sorted(recentCountEarlier))
            print('%d of last %d years were the same.'
                  % (len(recentCountEqual), totalRecentCount), sorted(recentCountEqual))
            print('%d of last %d years were later.'
                  % (len(recentCountLater), totalRecentCount), sorted(recentCountLater))
        ret = firstThisYear, medianFirst, earliestDates, latestDates
    else:
        print('Not showing this year because eThisYear="{}" and firstByYear="{}"'.format(eThisYear, firstByYear))

    if len(yearByFirst) == 0:
        # There's nothing to plot, so don't even bother trying
        return ret
    plotDataOtherYears = []
    plotDataThisYear = []
    dateLabels = []
    for key in sorted(yearByFirst.keys()):
        if eThisYear in yearByFirst[key]:
            plotDataThisYear.append((key, len(yearByFirst[key]), '#%s' % ','.join(map(str, yearByFirst[key])) ))
        else:
            plotDataOtherYears.append((key, len(yearByFirst[key]), '#%s' % ','.join(map(str, yearByFirst[key]))))
    histogramFname = '%s/svg/%s' % (cityName, name.replace(' ', '_'))
    if ret != None:
        ret = ret + (histogramFname,)
    plot = gnuplot.Plot(histogramFname)
    dateMin = min(yearByFirst.keys())
    dateMax = max(yearByFirst.keys())
    plotDateMin = dateMin-1 #int(dateMin - (dateMax - dateMin)*.25)
    plotDateMax = dateMax+1 #int(dateMax + (dateMax - dateMin)*.25)

    for dayOffset in range(plotDateMin, plotDateMax+1, 1):
        date = datetime.date(now.year, dateRange.startMonth, dateRange.startDay) + datetime.timedelta(dayOffset)
        if date.day % 5 == 1 and date.day != 31:
            dateLabels.append('"%s" %d' % (date.strftime('%b/%d'), dayOffset))

    ylabel = 'Number of years when %s happened on this day' % name
    if yaxisLabel != None:
        ylabel = yaxisLabel
    plot.open(title='%s in %s' % (name, cityName.capitalize()),
              ylabel=ylabel,
              xmin=plotDateMin,
              xmax=plotDateMax,
              ymin=0,
              ymax=max(len(a) for a in yearByFirst.values())+1,
              xtics=dateLabels, xticsRotate=45,
              margins=[7,8,2,5])
    plot.addLine(gnuplot.Line('Other years', plotDataOtherYears, plot='boxes'))
    plot.addLine(gnuplot.Line('This year', plotDataThisYear, plot='boxes'))
    plot.plot()
    plot.close()

    print('')

    plotdata = []
    for (year, plotCount) in firstByYear.items():
        if plotCount != None:
            plotdata.append(
                (year, plotCount,
                 ( '#'
                   +str(datetime.date(year, dateRange.startMonth, dateRange.startDay)
                        + datetime.timedelta(plotCount)))))

    ytics = []
    for m in range(1,13):
        for d in (1,10,20):
            thisDate = datetime.date(2015,m,d)
            dayOffset = (thisDate - datetime.date(2015, dateRange.startMonth, dateRange.startDay)).days
            ytics.append('"%s" %d' % (thisDate.strftime('%b %d'), dayOffset))

    #print(tuple(t[:2] for t in plotdata))
    lineFit = linear.linearTrend(tuple(t[:2] for t in plotdata))

    plot = gnuplot.Plot("%s/svg/%s_%s-%u_%s.line"
                        % (cityName, name.replace(' ', '_'),
                           monthName(dateRange.startMonth), dateRange.startDay,
                           dateRange.lastDay().replace(' ', '-') ),
                        yaxis=2)
    plot.open(title='%s %s between %s %u and %s'
              % (cityName.capitalize(), name,
                 monthName(dateRange.startMonth), dateRange.startDay,
                 dateRange.lastDay() ),
              ytics=ytics)
    plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
    plot.addLine(gnuplot.Line("Date", plotdata, lineColour='purple'))
    plot.plot()
    plot.close()
    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determine the first/last time some expression was true.')
    parser.add_argument('expr', help='Which observation to check')
    parser.add_argument('--name', '-n', required=True)
    parser.add_argument('--city', '-c', default='ottawa')
    parser.add_argument('--start', '-s', default='7,1')
    parser.add_argument('--end', '-e', default='7,1')
    parser.add_argument('--last', '-l')
    parser.add_argument('--excludeThisYear', action='store_true')
    parser.add_argument('--latest', action='store_true')
    parser.add_argument('--recentNYears', type=int, help='Limit the results to the most recent N years')

    #parser.add_argument('--run', type=int, default=1)
    #parser.add_argument('-m', help='Mask', default=['*-*-*'], nargs='*')
    args = parser.parse_args()


    dateRange = DateRange(args.start, args.last, args.end)

    order='first'
    if args.latest:
        order='last'

    print(dateRange, order)

    ret = first(args.city,
                args.expr, name=args.name,
                dateRange=dateRange,
                excludeThisYear=args.excludeThisYear,
                limitToMostRecentYears=args.recentNYears,
                order=order)
    print(ret)
