#!/usr/bin/python
# -*- coding: utf-8 -*-
import hourly, datetime, sys, gnuplot, linear, time, getopt
from fieldOperators import *
from plotdict import plotdict
from makefit import makeFit, reverseDictionary
from monthName import monthName

now = datetime.datetime.now().date()

START_MONTH=7
START_DAY=1
END_MONTH=7
END_DAY=1
def YEAR_CROSS():
    if ( END_MONTH < START_MONTH
         or ( END_MONTH == START_MONTH
              and END_DAY == START_DAY ) ):
       return 1
    return 0


data = None

def lastDay():
    if END_MONTH == 3 and END_DAY == 1:
        return 'Feb 28,29'
    lastDate = datetime.datetime(now.year, END_MONTH, END_DAY)-datetime.timedelta(1)
    return '%s %u' % (monthName(lastDate.month), lastDate.day)

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

def count(cityName, data, expr, name, verbose=True, skipIncomplete=False, lineChart=False):
    countByYear = {}
    thisYearCount = 0

    for baseyear in range(data.minYear, data.maxYear-YEAR_CROSS()+1):
        countByYear[baseyear] = None
        countThisYear = 0

        starttime = datetime.datetime(baseyear, START_MONTH, START_DAY)
        endtime = datetime.datetime(baseyear+YEAR_CROSS(), END_MONTH, END_DAY)
        hourdiff = (endtime-starttime).days*24
        hoursWithObservations = 0

        thisRunLen = 0
        #print baseyear
        for day in hourly.hourRange(starttime, endtime):
            dayValues = data.get(day, None)

            val = None
            flag = ''
            if dayValues != None:
                #print day, dayValues
                val, flag = expr(dayValues)

            if val != None:
                hoursWithObservations += 1
                if val and not (skipIncomplete and 'I' in flag):
                    countThisYear += 1
                    if baseyear + YEAR_CROSS() == now.year:
                        if verbose:
                            print "Count: %s" % day, float(val), flag
                        if ( day.date() == min(endtime.date() - datetime.timedelta(1), datetime.date.today())):
                            # We only care about this year's count if the final day of
                            # this year actually met the criteria
                            thisYearCount = countThisYear
                else:
                    #if baseyear == 2014:
                    #    print "Skip: %s" % day
                    thisRunLen = 0

        if (hoursWithObservations >= hourdiff * 85 / 100):# or baseyear + YEAR_CROSS() == now.year:
            countByYear[baseyear] = countThisYear
            if verbose:
                print baseyear, countThisYear, hoursWithObservations
        else:
            # skip years with fewer than 90% of days recorded
            if verbose:
                print ("Skipping %d because it has only %u/%u records"
                       % (baseyear, hoursWithObservations, hourdiff) )


    #del countByYear[now.year]

    (fewest, most) = keyOfMinMaxValue(countByYear)

    if verbose:
        print "fewest %s was %s (%d)" % (name, fewest, countByYear[fewest[0]])
        print "most %s was %s (%d)" % (name, most, countByYear[most[0]])

    eThisYear = now.year
    if YEAR_CROSS():
        eThisYear -= 1

    avgKeys = filter(lambda t: t in countByYear, range(eThisYear-30, eThisYear))

    counts = [countByYear[a] for a in avgKeys]

    counts = filter(lambda t: t!=None, counts)

    avg = float(sum(counts)) / len(counts)

    if verbose:
        print "average %s is %f" % (name, avg)

    #print thisYearCount
    mostSince = None
    prevRecordYears = []
    prevRecord = 0
    if eThisYear in countByYear:
        #thisYearCount = countByYear[eThisYear]
        if thisYearCount > 0:
            for year in reversed(sorted(countByYear.keys())):
                if mostSince == None and year != eThisYear and countByYear[year] >= thisYearCount:
                    mostSince = year
                if year != eThisYear:
                    if countByYear[year] > prevRecord:
                        prevRecord = countByYear[year]
                        prevRecordYears = [year]
                    elif countByYear[year] == prevRecord:
                        prevRecordYears.append(year)

        if verbose:
            print now.year, name, "was", countByYear[eThisYear]
            if mostSince != None:
                print "Most since %d." % (mostSince)
            print ( "%d of past %d years had more %s"
                    % (len(filter(lambda t: countByYear[t] > thisYearCount, avgKeys)),
                       len(avgKeys),
                       name),
                    filter(lambda t: countByYear[t] > thisYearCount, avgKeys) )
            print ( "%d of past %d years had equal %s"
                    % (len(filter(lambda t: countByYear[t] == thisYearCount, avgKeys)),
                       len(avgKeys),
                       name),
                    filter(lambda t: countByYear[t] == thisYearCount, avgKeys) )
            print ( "%d of past %d years had fewer %s"
                    % (len(filter(lambda t: countByYear[t] < thisYearCount, avgKeys)),
                       len(avgKeys),
                       name),
                    filter(lambda t: countByYear[t] < thisYearCount, avgKeys) )
            print

    if lineChart:
        plotdata = []
        for (year, plotCount) in countByYear.iteritems():
            if plotCount != None:
                plotdata.append((year, plotCount))

        lineFit = linear.linearTrend(plotdata)

        plot = gnuplot.Plot("%s/svg/%s_count_%s-%u_before_%s"
                            % (cityName, name.replace(' ', '_'),
                               monthName(START_MONTH), START_DAY,
                               lastDay().replace(' ', '-') ),
                            yaxis=2)
        plot.open(title='%s number of %s between %s %u and %s'
                  % (cityName.capitalize(), name,
                     monthName(START_MONTH), START_DAY,
                     lastDay() ) )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Count", plotdata, lineColour='purple'))
        plot.plot()
        plot.close()
    else:
        barPlotData = makeFit(countByYear, 75)
        filename = ( "%s/svg/%s_count_%s-%u_to_%s_bar"
                     % (cityName, name.replace(' ', '_'),
                        monthName(START_MONTH), START_DAY,
                        lastDay().replace(' ', '-') ) )

        plotdict(barPlotData,
                 filename = filename,
                 chartTitle = ( '%s number of %s between %s %u and %s'
                                % (cityName.capitalize(), name,
                                   monthName(START_MONTH), START_DAY,
                                   lastDay() ) ),
                 yaxisLabel='',
                 thisYear = eThisYear,
                 ymin=0)
    return (filename, thisYearCount, mostSince, prevRecord, prevRecordYears)


def dispatch(cityName, firstYear,
             startMonth, startDay,
             endMonth, endDay,
             expression, verbose=True,
             skipIncomplete=False,
             lineChart=False):

    data = hourly.load(cityName)
    global START_MONTH, START_DAY, END_MONTH, END_DAY
    START_MONTH = startMonth
    START_DAY = startDay
    END_MONTH = endMonth
    END_DAY = endDay

    checkList = {
        '>=30' :   [GreaterThanOrEqualToWithFlag(hourly.TEMP,   30), "hours above or at 30"],
        '<10':   [LessThanOrEqualToWithFlag(hourly.TEMP,   10),  "hours below 10"],
        '<=-20':   [LessThanOrEqualToWithFlag(hourly.TEMP,   -20),  "hours below or at -20"],
    }


    args=checkList[expression]
    return count(cityName, data, args[0], args[1], verbose, skipIncomplete=skipIncomplete, lineChart=lineChart)

if __name__ == '__main__':
    cityName = 'ottawa'
    firstYear = None
    startMonth=7
    startDay=1
    endMonth=7
    endDay=1
    skipIncomplete=False
    lineChart=False
    verbose=False

    opts, args = getopt.getopt(sys.argv[1:],
                               'ibvc:f:s:l:e:x:',
                               ['city=',
                                'firstYear=',
                                'start=',
                                'last=',
                                'end=',
                                'exp=',
                                'line'])

    for opt, arg in opts:
        if opt in ('-c','--city'):
            cityName = arg
        elif opt in ('-f','--firstYear'):
            firstYear = int(arg)
        elif opt in ('-s','--start'):
            (startMonth, startDay) = map(int, arg.split(','))
        elif opt in ('-e','--end'):
            (endMonth, endDay) = map(int, arg.split(','))
        elif opt in ('-l','--last'):
            (lastMonthArg, lastDayArg) = map(int, arg.split(','))
            endDate = datetime.datetime(now.year, lastMonthArg, lastDayArg)+datetime.timedelta(1)
            (endMonth, endDay) = (endDate.month, endDate.day)
        elif opt in ('-x','--exp'):
            expression = arg
        elif opt == '-i':
            skipIncomplete=True
        elif opt == '--line':
            lineChart=True
        elif opt == '-v':
            verbose = True

    dispatch(cityName, firstYear,
             startMonth, startDay,
             endMonth, endDay,
             expression,
             skipIncomplete=skipIncomplete,
             lineChart=lineChart,
             verbose=verbose)
