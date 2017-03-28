#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import daily, sys, fnmatch, math
import datetime as dt
import holidays
import hourly
import stations
import parseWeatherStatsRealtime
from fieldOperators import SpecialNone, Value, ValueNoFlag, ValueDiff, ValueEmptyZero

from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from io import BytesIO
from collections import deque, Counter
import metarParse

def winterFromDate(date):
    if date.month < 7:
        return date.year - 1
    return date.year

def today():
    return dt.date.today()

def thisYear():
    return today().year

def thisWinter():
    return winterFromDate(today())

def yearsAgo(years):
    ret = dt.date.today()
    ret = dt.date(ret.year-years, ret.month, ret.day)
    return ret

def first(it):
    for i in it:
        return i

def pythonWords(expr):
    words = set()
    tokens = tokenize(BytesIO(expr.encode('utf-8')).readline)
    for token in tokens:
        if token.type == NAME:
            words.add(token.string)
    return sorted(words)

def base10int(a):
    return int(a,10)

def parseBetween(betweenStr):
    if betweenStr != None:
        return tuple(map(lambda t: tuple(map(base10int, t.split('-'))), betweenStr.split(',')))
    return None

def matchDate(date, dateFilter, between, holiday):
    if holiday != None:
        return holidays.Canada(state='ON',
                               years=date.year,
                               observed=False).get(date,'') == holiday
    if between != None:
        betweenStart = dt.date(date.year, between[0][0], between[0][1])
        betweenEnd = dt.date(date.year, between[1][0], between[1][1])
        if date < betweenStart or date > betweenEnd:
            return False
    return any(map(lambda d:fnmatch.fnmatch(str(date), d), dateFilter))

def dateDateStr(dates):
    ret = ''
    if len(dates) == 1:
        ret += dates[0].strftime('%Y-%m-%d')
    elif dates[0].year == dates[-1].year:
        if dates[0].month == dates[-1].month:
            ret += (dates[0].strftime('%Y-%m-%d')
                    + '➜'
                    + dates[-1].strftime('%d'))
        else:
            ret += (dates[0].strftime('%Y-%m-%d')
                    + '➜'
                    + dates[-1].strftime('%m-%d'))
    else: #Spans years
        ret += (dates[0].strftime('%Y-%m-%d')
                + '➜'
                + dates[-1].strftime('%Y-%m-%d'))
    return ret

def printDateDate(dates):
    print(dateDateStr(dates), end='')

def printDateTime(dates):
    if len(dates) == 1:
        print(dates[0].strftime('%Y/%m/%d@%H:%M'), end='')
    elif dates[0].year == dates[-1].year:
        if dates[0].month == dates[-1].month:
            print(dates[0].strftime('%Y/%m/%d')
                  + '-'
                  + dates[-1].strftime('%d'),
                  end='')
        else:
            print(dates[0].strftime('%Y/%m/%d')
                  + '-'
                  + dates[-1].strftime('%m/%d'),
                  end='')
    else: #Spans years
        print(dates[0].strftime('%Y/%m/%d')
              + '-'
              + dates[-1].strftime('%Y/%m/%d'),
              end='')

def printDate(dates):
    if type(dates[0]) is dt.datetime:
        printDateTime(dates)
    else:
        printDateDate(dates)
    print(end=' ')

def main():
    HISTORY=10

    parser = argparse.ArgumentParser(description='Determine how often some weather occurs.')
    parser.add_argument('expr', help='Which observation to check')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--run', type=int, default=1)
    parser.add_argument('-m', help='Mask', default=['*'], nargs='*')
    parser.add_argument('--between', help='Only consider dates between these two. Comma separated like 05-15,07-01')
    parser.add_argument('--holiday', help='The name of a holiday')
    parser.add_argument('--hour', help='Use hourly data instead of daily.', action='store_true', default=False)
    parser.add_argument('--winters', help='Count by winter instead of by year.', action='store_true', default=False)
    parser.add_argument('--group-by-year', action='store_true', default=False)
    args = parser.parse_args()

    run = args.run
    city = args.city

    fieldDict = {
        'min': Value(daily.MIN_TEMP),
        'max': Value(daily.MAX_TEMP),
        'meanTemp': Value(daily.MEAN_TEMP),
        'tempSpan': ValueDiff(daily.MAX_TEMP, daily.MIN_TEMP),
        'rain': Value(daily.TOTAL_RAIN_MM),
        'precip': Value(daily.TOTAL_PRECIP_MM),
        'humidex': Value(daily.MAX_HUMIDEX),
        'snow': Value(daily.TOTAL_SNOW_CM),
        'snowpack': ValueEmptyZero(daily.SNOW_ON_GRND_CM),
        'windgust': Value(daily.SPD_OF_MAX_GUST_KPH),
        'wind': Value(daily.AVG_WIND),
        'windchill': Value(daily.MIN_WINDCHILL),
        'avgWindchill': Value(daily.MIN_WINDCHILL),
    }
    if args.hour:
        fieldDict = {
            'temp': Value(hourly.TEMP),
            'dewpoint': Value(hourly.DEW_POINT_TEMP),
            'humidity': Value(hourly.REL_HUM),
            'windDir': Value(hourly.WIND_DIR),
            'wind': Value(hourly.WIND_SPD),
            'visibility': Value(hourly.VISIBILITY),
            'pressure': Value(hourly.STN_PRESS),
            'weather': ValueNoFlag(hourly.WEATHER),
            'windchill': ValueNoFlag(hourly.WINDCHILL),
        }

    def allFieldNames():
        return fieldDict.keys()

    dateFilter = args.m
    between = parseBetween(args.between)
    if args.hour:
        data = hourly.load(city)
        for time, conditions in parseWeatherStatsRealtime.parse(city).items():
            if time.minute == 0:
                values = data.get(time,None)
                if values is None:
                    data[time] = hourly.HourData(WEATHER=conditions)
                else:
                    data[time] = values._replace(WEATHER=conditions)
        for time, metarWeather in metarParse.genHourlyWeather(city):
            if time.minute != 0:
                continue
            #if time.date() == dt.date(2017,3,27):
            #    import pudb; pu.db
            values = data.get(time,None)
            if values is None:
                data[time] = hourly.HourData(WEATHER=metarWeather)
            elif ( values.WEATHER is None
                   or values.WEATHER == 'NA'
            ):
                data[time] = values._replace(WEATHER=metarWeather)
    else:
        data = daily.load(city)

    maxVal = None

    curRun = deque()
    curDates = deque()

    fieldValues = fieldDict.values()
    firstDate = None
    matches = []

    referencedValues=set()
    compiledExpr = compile(args.expr, filename='.', mode='eval')
    exprWords = pythonWords(args.expr)
    for fieldName in fieldDict.keys():
        if fieldName in exprWords:
            referencedValues.add(fieldName)

    #print(referencedValues)
    #print(tuple(allFieldNames()))

    class refCountedList(deque):
        def __init__(self):
            self.indexSet = set()
        def __getitem__(self, ind):
            if type(ind) != slice: #print('[{ind}]'.format(**locals()))
                self.indexSet.add(ind)
                return deque.__getitem__(self, ind)
            return list(self)[ind]
        def clearIndexSet(self):
            self.indexSet.clear()

    historyDates=deque([])
    history=refCountedList()
    class History():
        pass

    expectedDiff = dt.timedelta(days=1)
    if args.hour:
        expectedDiff = dt.timedelta(hours=1)
    mytimezone = stations.city[args.city].timezone

    for date in sorted(data.keys()):

        if args.hour:
            utchour = date
            localhour = utchour.astimezone(mytimezone)
            date = localhour

        if ( len(historyDates)>0
             and date - historyDates[0] != expectedDiff
         ):
            historyDates.clear()
            history.clear()

        if matchDate(date, args.m, between, args.holiday):
            #if date.year == 2016 and date.month == 11 and date.day == 30:
            #    import pudb; pu.db
            vals = {'history': history, "__builtins__":__builtins__, 'time': date}
            history.appendleft(History())
            historyDates.appendleft(date)
            for fieldName, fieldCall in fieldDict.items():
                vals[fieldName] = fieldCall(data[date], date)
                flagValue = fieldCall.getFlag(data[date])
                if flagValue is not None:
                    vals[fieldName+'Flag'] = flagValue
                if type(vals[fieldName]) is not SpecialNone:
                    history[0].__setattr__(fieldName, vals[fieldName])
                    if flagValue is not None:
                        history[0].__setattr__(fieldName+'Flag', flagValue)

            skip=False
            usedVals={}
            for fieldName in referencedValues:
                if type(vals[fieldName]) is SpecialNone:
                    #print('Skipping {} because {} is None'.format(date, fieldName))
                    skip=True
                    break
                #print(fieldName, type(vals[fieldName]) is SpecialNone)
                usedVals[fieldName] = vals[fieldName]
            if skip:
                continue

            if firstDate is None:
                firstDate = date
            lastDate = date

            #expr = args.expr.format(**vals)
            #print(date, args.expr, usedVals, vals)
            history.clearIndexSet()
            try:
                val = eval(compiledExpr, vals)
            except IndexError:
                val = False
            except AttributeError:
                val = False
            except TypeError:
                for offset, date in enumerate(historyDates):
                    print(date)
                    for name in allFieldNames():
                        if hasattr(history[offset], name):
                            print(name, history[offset].__getattribute__(name))
                raise
            #print(val)
            if val is True or type(val) is tuple and val[0] is True:
                #print('+++')
                #for offset, date in enumerate(historyDates):
                #    print(date)
                #    for name in allFieldNames():
                #        if name in dir(history[offset]):
                #            print(name, history[offset].__getattribute__(name))
                #print('---')
                for i in history.indexSet:
                    for fieldName in referencedValues:
                        usedVals['history[{}].{}'.format(i, fieldName)] = (
                            history[i].__getattribute__(fieldName) )
                #print(history.indexSet)

                expectedDate = date
                if len(curDates) > 0:
                    expectedDate = curDates[-1] + expectedDiff
                if date != expectedDate:
                    #print('Clearing run', date, curDates[-1])
                    curDates = deque([date])
                    curRun = deque([usedVals])
                    if type(val) is tuple:
                        curRun = deque([{'expr': val[1]}])
                else:
                    curDates.append(date)
                    if type(val) is tuple:
                        curRun.append({'expr': val[1]})
                    else:
                        curRun.append(usedVals)
                    if len(curRun) > run:
                        curRun.popleft()
                        curDates.popleft()

                #print(date, len(curRun), run)
                if len(curRun) == run:
                    printDate(curDates)

                    if len(curRun[0]) == 1:
                        print(' '.join([str(first(a.values())) for a in curRun]))
                    else:
                        print(curRun)
                    matches.append(curDates)

    if args.winters:
        grouping = tuple([winterFromDate(a[0]) for a in matches])
        group = 'winter'
    else:
        grouping = tuple([a[0].year for a in matches])
        group = 'year'
    if args.group_by_year:
        print(tuple(enumerate(Counter(grouping).most_common(30))))
    print('Total count: {}'.format(len(grouping)))
    print('Occurance: ', end='')
    yearSpan = lastDate.year - firstDate.year + 1
    if len(matches) < yearSpan:
        print('once every {:.1f} {}s'
              .format(yearSpan/len(matches),
                      group))
    else:
        print('{:.1f} times per {}'
              .format(len(matches)/yearSpan,
                      group))

    print('Yearly Occurance:', end=' ')
    uniqGrouping = sorted(list(set(grouping)))
    if len(uniqGrouping) < yearSpan:
        occurance = yearSpan/len(uniqGrouping)
        print('once every {occurance:.1f} {group}s,'.format(**locals()), end=' ')
    else:
        occurance = len(uniqGrouping)/yearSpan
        print('{occurance:.1f} times per {group},'.format(**locals()), end=' ')

    recentFilter = lambda t: t>=today().year-30 and t<today().year
    if args.winters:
        recentFilter = lambda t: t>=thisWinter()-30 and t<thisWinter()
    recentOccursYears = tuple(filter(recentFilter, grouping))
    recentUniqYears = tuple(sorted(set(recentOccursYears)))
    print('{} out of the past 30 years: {}'
          .format(len(recentUniqYears), str(recentUniqYears)))

    recentYears = range(thisYear()-30, thisYear())
    if args.winters:
        recentYears = range(thisWinter()-30, thisWinter())
    recentLen = len(recentUniqYears)
    recentYearCounter = Counter(recentOccursYears)
    recentLens = sorted(recentYearCounter[a] for a in recentYears)
    print('{} during the past 30 years'.format(recentLen))
    if True: #recentLen > 30:
        print('Average is {:.1f}/year during the past 30 years'
              .format(len(recentOccursYears)/30))
        print('Median is {},{}/year during the past 30 years'.format(recentLens[int(len(recentLens)/2)], recentLens[int((len(recentLens)+1)/2)]))
        print('80% CI is {},{}'.format(recentLens[len(recentLens)//10], recentLens[len(recentLens)-(len(recentLens)//10)-1]), recentLens)
        #print(sorted([(len(o),y) for y,o in recentByYear.items()]))
    else:
        print('Every {:.1f} years during the past 30 years'.format(30/recentLen))
    occurDays = '∞'
    if recentLen > 0:
        occurDays = (dt.date.today()-yearsAgo(30)).days/recentLen
    print('Every {} days during the past 30 years'.format(occurDays))
    if recentLen > 0:
        print('Every {} months, {:.1f} days during the past 30 years'.format(int(occurDays//30), occurDays%30))

    if args.hour:
        recentOccur = tuple(filter(lambda t: t[0].date()>=yearsAgo(1), matches))
    else:
        recentOccur = tuple(filter(lambda t: t[0]>=yearsAgo(1), matches))
    print('{} during the past year'.format(len(recentOccur)))
    if args.winters:
        thisWinterCount = grouping.count(thisWinter())
        print('{} so far this winter'.format(thisWinterCount))
    else:
        thisYearCount = grouping.count(thisYear())
        print('{} so far this year'.format(thisYearCount))

if __name__ == '__main__':
    main()
