#!/usr/bin/python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from fieldOperators import *
from howOften import dateDateStr, winterFromDate
from makefit import makeFit
from monthName import monthName
from plotdict import plotdict
from reversedict import reverseDict
import daily, sys, gnuplot, linear, time, getopt, argparse, fnmatch
import datetime as dt

now = dt.datetime.now().date()

data = None

def keyOfMinMaxValue(data):
    minKey = None
    maxKey = None

    for (key, value) in data.items():
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


def count(cityName, data, expr, name, endDate,
          minRunLen,
          showNth,
          verbose=True,
          skipIncomplete=False,
):
    runByStartDate = {}
    currentRunStartDate = None
    currentRun = []
    todaysRun = 0

    for sampleDate in daily.dayRange(min(data.keys()), endDate):
        dayValues = data.get(sampleDate, None)

        val = None
        flag = ''
        if dayValues != None:
            #print day, dayValues
            try:
                val = dayValues.eval(expr, {'time': sampleDate})
            except AttributeError:
                print(dayValues)
                raise

        if val is not None:
            if ( val is False
                 or ( type(val) is tuple and val[0] is False )
                 or skipIncomplete and 'I' in flag
            ):
                if len(currentRun) >= minRunLen:
                    #print currentRunStartDate, len(currentRun), ['%.1f' % a for a in currentRun]
                    runByStartDate[currentRunStartDate] = currentRun
                if sampleDate == endDate - dt.timedelta(1):
                    print('today breaks a run of %d, starting on %s' % (len(currentRun), currentRunStartDate))
                currentRun = []
                currentRunStartDate = None
            else:
                if len(currentRun) == 0:
                    currentRunStartDate = sampleDate
                if type(val) is tuple:
                    currentRun.append(val[1])
                else:
                    currentRun.append(val)
                if sampleDate == endDate - dt.timedelta(1):
                    todaysRun = len(currentRun)
        else:
            if len(currentRun) >= minRunLen:
                runByStartDate[currentRunStartDate] = currentRun
            currentRun = []
            currentRunStartDate = None
    if len(currentRun) >= minRunLen:
        runByStartDate[currentRunStartDate] = currentRun

    #print runByStartDate
    startDateByRunLen = defaultdict(list)
    longestRunByWinter = defaultdict(int)
    for startDate, run in sorted(runByStartDate.items()):
        runlen = len(run)
        winter = winterFromDate(startDate)
        longestRunByWinter[winter] = max(runlen, longestRunByWinter[winter])
        ds = dateDateStr( (startDate, startDate+dt.timedelta(days=runlen-1)) )
        print(ds, len(run), run) #, startDateByRunLen
        startDateByRunLen[runlen] = list(reversed(sorted(startDateByRunLen[runlen]+[startDate])))

    lengths = sorted(startDateByRunLen.keys())
    most = lengths[-1]
    lastStartDate = max(runByStartDate.keys())
    print('lastStartDate', lastStartDate)

    if verbose:
        print("most %s was %d (%s)" % (name, most, startDateByRunLen[most]))
        nth = 1
        for l in reversed(lengths):
            for d in startDateByRunLen[l]:
                if nth <= showNth or d == lastStartDate:
                    print('%d) %s (%d)' % (nth, dateDateStr( (d, d+dt.timedelta(days=l-1)) ), l), tuple(runByStartDate[d]))
            nth += len(startDateByRunLen[l])
        print("today's run was %d" % todaysRun, currentRun)
        maxLengthPerModernWinter = tuple(
            longestRunByWinter[x] for x in filter(
                lambda t: t in range(winterFromDate(now)-30,
                                     winterFromDate(now)),
                longestRunByWinter.keys()))
        print('30-year average: {:.1f}'
              .format(sum(maxLengthPerModernWinter)/len(maxLengthPerModernWinter)))

        #for winter, runlen in sorted(longestRunByWinter.items()):
        #    print(winter, runlen)


def dispatch(cityName, firstYear,
             endDate,
             expression,
             minRunLen,
             showNth,
             verbose=True,
             skipIncomplete=False):

    data = daily.load(cityName)

    if firstYear != None:
        for key in tuple(data.keys()):
            if key.year < firstYear:
                del data[key]

    return count(cityName, data, expression, '??', endDate,
                 minRunLen,
                 showNth,
                 verbose, skipIncomplete=skipIncomplete)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Determine the longest number of days some condition has been true.')
    parser.add_argument('-x', '--exp', help='Expression', required=True)
    parser.add_argument('-c', '--city', default='ottawa')
    parser.add_argument('-f', '--firstYear', help='Ignore years before this value', type=int)
    parser.add_argument('-e', '--end', default=str(now + dt.timedelta(1)))
    parser.add_argument('-l', '--last')
    parser.add_argument('--nth', type=int, default=20)
    parser.add_argument('-i', help='Skip incomplete.', action='store_true', default=False)
    parser.add_argument('-r', help='Minimum run', type=int, default=3)
    args = parser.parse_args()

    if args.end != None:
        (y,m,d) = map(int, args.end.split('-'))
        endDate = dt.date(y,m,d)
    if args.last != None:
        (y,m,d) = map(int, args.last.split('-'))
        endDate = dt.date(y,m,d)+dt.timedelta(1)

    dispatch(args.city, args.firstYear,
             endDate,
             args.exp,
             showNth=args.nth,
             skipIncomplete=args.i,
             minRunLen=args.r)
