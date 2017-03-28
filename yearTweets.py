#!/usr/bin/python3
# -*- coding: utf-8 -*-
import monthlyAverages
import daily
import dailyRecords
import datetime as dt
import argparse
import alertTweets
import alert
import stations
import snow
import operator
import os
from monthName import monthName
from dailyFilters import *
from reversedict import topNValuesLists, inListOfLists, reverseDict
from collections import namedtuple

class WinterFilter():
    def __call__(self, year):
        if type(year) is int:
            year = year,
        for y in year:
            yield from daily.dayRange(
                dt.date(y, 7, 1),
                dt.date(y+1, 7, 1))

def formatWithUnits(val, field, precision, skipUnits=None):
    #print ((val, field, precision, skipUnits))
    ret = '{val:.{precision}f}'.format(**locals())
    if skipUnits is not None:
        return ret
    units = field.units
    if field.units == 'days':
        units = ' days'
    if val == 1:
        units = field.unit
        if field.unit == 'day':
            units = ' day'
    return ret + units

LowHigh = namedtuple('LowHigh', ['low', 'high'])

def confidenceInterval80(valByYear, thisyear):
    vals = []
    for y in range(thisyear-30, thisyear):
        if y in valByYear:
            vals.append(valByYear[y])
    vals.sort()
    ret = LowHigh(vals[len(vals)//10], vals[len(vals)-(len(vals)//10)-1])
    return ret

def confidenceInterval50(valByYear, thisyear):
    vals = []
    for y in range(thisyear-30, thisyear):
        if y in valByYear:
            vals.append(valByYear[y])
    vals.sort()
    ret = LowHigh(vals[len(vals)//4], vals[len(vals)-(len(vals)//4)-1])
    return ret

def roundAwayFromZero(val):
    return int(val+val/(2*abs(val)))

def adjective(field):
    ret = {
        "MAX_TEMP": ( 'warmest', 'coldest' ),
        "MEAN_TEMP": ( 'warmest', 'coldest' ),
        "MIN_TEMP": ( 'warmest', 'coldest' ),
        "TOTAL_RAIN_MM": ( 'wetest', 'driest' ),
        "TOTAL_SNOW_CM": ( 'snowiest', 'greenest' ),
        "TOTAL_PRECIP_MM": ( 'wetest', 'driest' ),
        "SNOW_ON_GRND_CM": ( 'deepest', 'shallowest' ),
        "SPD_OF_MAX_GUST_KPH": ( 'windiest', 'calmest' ),
        "MAX_HUMIDEX": ( 'muggiest', 'crispest' ),
        "MIN_WINDCHILL": ( '', 'windchilliest' ),
        "AVG_WIND": ( 'windiest', 'calmest' ),
        "AVG_WINDCHILL": ( '', 'windchilliest' ),
        "MIN_HUMIDITY": ( 'moistest', 'driest' ),
        "MEAN_HUMIDITY": ( 'moistest', 'driest' ),
        "AVG_DEWPOINT": ( 'moistest', 'driest' ),
    }

def deviationDescription(val, average, field):
    #import pdb; pdb.set_trace()
    moreThan = {
        1: 'double',
        2: 'triple',
        3: 'quadruple',
        4: "5x",
        5: "6x",
        6: "7x",
        7: "8x",
        8: "9x",
        9: "10x",
        10: "11x",
    }
    lessThan = {2: 'half',
                3: 'a third',
                4: 'a quarter',
                10: 'a tenth',
                100: 'one hundredth'
    }
    aboveBelow = 'above'
    if val < average:
        aboveBelow = 'below'
    deviation = "∞%" + ' ' + aboveBelow
    if average != 0:
        percent=100*(val-average)/average
        absPercent=abs(int(percent))
        deviation = '{absPercent}% {aboveBelow}'.format(**locals())
        if percent < -99:
            return "less than one hundredth"
        if percent < -90:
            return "less than a tenth"
        if percent < -75:
            return "less than a quarter"
        if percent < -67:
            return "less than a third"
        if percent < -50:
            return "less than half"
        if percent < -40:
            return "barely half"
        if percent >= 75:
            moreThanDescription = moreThan[(percent + 25)//100]
            percentMod = percent % 100
            if percentMod >= 75:
                deviation = 'almost {moreThanDescription}'.format(**locals())
            elif percentMod == 0:
                deviation = '{moreThanDescription}'.format(**locals())
            else:
                deviation = 'more than {moreThanDescription}'.format(**locals())
        elif percent < 50:
            diff = abs(int(val-average))
            diffWithUnits = formatWithUnits(diff, field, 0)
            deviation = '{diffWithUnits} {aboveBelow}'.format(**locals())
    return deviation

def fieldAdjective(field):
    ret = {
        "MAX_TEMP": ( 'warmest', 'coldest' ),
        "MEAN_TEMP": ( 'warmest', 'coldest' ),
        "AVG[MIN_TEMP,MAX_TEMP]": ( 'warmest', 'coldest' ),
        "MIN_TEMP": ( 'warmest', 'coldest' ),
        "TOTAL_RAIN_MM": ( 'wetest', 'driest' ),
        "TOTAL_SNOW_CM": ( 'snowiest', 'least snowy' ),
        "TOTAL_PRECIP_MM": ( 'wetest', 'driest' ),
        "SNOW_ON_GRND_CM": ( 'deepest', 'shallowest' ),
        "SPD_OF_MAX_GUST_KPH": ( 'windiest', 'calmest' ),
        "MAX_HUMIDEX": ( 'muggiest', 'crispest' ),
        "MIN_WINDCHILL": ( '', 'windchilliest' ),
        "AVG_WIND": ( 'windiest', 'calmest' ),
        "AVG_WINDCHILL": ( '', 'windchilliest' ),
        "MIN_HUMIDITY": ( 'moistest', 'driest' ),
        "MEAN_HUMIDITY": ( 'moistest', 'driest' ),
        "AVG_DEWPOINT": ( 'moistest', 'driest' ),
    }
    if hasattr(field, 'field'):
        return ret[field.field.name]
    return ret[field.name]

def fieldDescription(field):
    ret = {
        "MEAN_TEMP": 'avg. hourly temp',
        "MEAN_HUMIDITY": 'avg. hourly humidity',
        "AVG_WIND": 'avg. wind',
        "AVG[MIN_TEMP,MAX_TEMP]": 'avg. temp',
        'TOTAL_SNOW_CM': 'cumulative snowfall',
    }
    return ret[field.name]

def tweetTopN(city, db, field, thisYear):
    top10 = {
        1:'❶',
        2:'❷',
        3:'❸',
        4:'❹',
        5:'❺',
        6:'❻',
        7:'❼',
        8:'❽',
        9:'❾',
        10:'❿',
    }
    top10Double = {
        1: '⓵',
        2: '⓶',
        3: '⓷',
        4: '⓸',
        5: '⓹',
        6: '⓺',
        7: '⓻',
        8: '⓼',
        9: '⓽',
        10: '⓾'
    }
    place = 1
    totalCount = sum(len(a) for a in db.values())
    adjective = fieldAdjective(field)[0]
    description = fieldDescription(field)
    cityName = stations.city[city].name
    units = field.units
    tweetText = (
        '#{cityName}\'s 5 {adjective} years (by {description}):'
        .format(**locals()))
    for key in reversed(sorted(db.keys())):
        count = place
        for year in reversed(sorted(db[key])):
            nth = top10[place]
            if year == thisYear:
                nth = top10Double.get(place, '*')
            if count > 5:
                break
            val = key
            tweetText += "\n{nth} {year}: {val} {units}".format(**locals())
            count += 1
        place += len(db[key])
    alertTweets.maybeTweetWithSuffix(city, tweetText)

def nearestDiv(a,b):
    if a > 0:
        return int(a/b+1)*b
    return int(a/b)*b

def main(city,
         force=False,
         lastCheckedValue=None,
         today=None,
         maxValueToCheck=None,
         allYear=False,
         allWinter=False,
         justTop5=False,
         dataSinceDay=None,
):
    #import pdb; pdb.set_trace()
    data = daily.load(city)
    if dataSinceDay is not None:
        for day in tuple(data.keys()):
            if day < dataSinceDay:
                del data[day]
    monthlyAverages.cityData = data
    if today is None:
        today = daily.timeByCity[city].date()
        #if allYear:
        #    today = dt.date(daily.timeByCity[city].date().year, 12, 31)
    yearToCheck = (today - dt.timedelta(7)).year
    if yearToCheck != today.year:
        today = dt.date(yearToCheck, 12, 31)
    monthlyAverages.now = today
    tomorrow = today + dt.timedelta(days=1)

    todayMaxInfo = dailyRecords.getInfo(city, today, daily.MAX_TEMP)

    todayAverageMax = roundAwayFromZero( todayMaxInfo.normal )
    todayMax = None
    if todayMaxInfo.recent is not None:
        todayMax = int( todayMaxInfo.recent )

    if lastCheckedValue is None:
        minValueToCheck = int(todayAverageMax) + 2
    else:
        minValueToCheck = int(lastCheckedValue) + 1

    if maxValueToCheck is None:
        maxValueToCheck = todayMax
        if todayMax is None:
            maxValueToCheck = 35

    maxValuesToCheck = filter(lambda t: t%10==0, range(minValueToCheck, maxValueToCheck+1))

    fieldList = [
        #*[ ( ExprVal('max>={} if max is not None else None'.format(t),
        #             title=str(t) + "℃",
        #             name="max>=" + str(t),
        #             units="days",
        #             unit="day",
        #             precision=0,
        #             field=daily.MAX_TEMP,
        #             description=str(t)+"℃ days"),
        #     True ) for t in maxValuesToCheck ],
        #[ ( ExprVal('maxHumidex>max and maxHumidex>=' + str(t),
        #              title=str(t) + " humidex",
        #              name="humidex>=" + str(t),
        #              units="days",
        #              unit="day",
        #              precision=0),
        #      True ) for t in range(30, 51) ]
        #( FractionVal(daily.TOTAL_RAIN_MM, "Rain"), True ),
        ( FractionVal(daily.TOTAL_SNOW_CM, "snow"), True ),
        #( FractionVal(daily.TOTAL_PRECIP_MM, "precipitation"), True ),
        #( FractionVal(daily.AVG_WIND, "Wind"), False ),
        #( Avg(daily.MIN_TEMP, daily.MAX_TEMP, "temperature"), False ),
        #( FractionVal(daily.MEAN_HUMIDITY, "Humidity"), False ),
    ]

    monFilter = monthlyAverages.BeforeDateFilter(month = tomorrow.month,
                                                 day = tomorrow.day)
    if allYear:
        monFilter = monthlyAverages.BeforeDateFilter(month = 1, day = 1)
    if allWinter:
        monFilter = WinterFilter()
    todayFilter = monthlyAverages.OneDayFilter(month = today.month,
                                               day = today.day)

    #import pudb; pu.db
    for field, cumulative in fieldList:
        thisyear = today.year
        if allWinter:
            thisyear = today.year if today.month >= 7 else today.year - 1
        valByYear = monthlyAverages.yearDatas(
            monFilter, field=field,
            lastYear=thisyear, cumulative=cumulative)
        normalVal = monthlyAverages.normalMonthlyDatas(
            today.year, monFilter, field, cumulative=cumulative)
        if thisyear not in valByYear:
            continue
        ci80 = confidenceInterval80(valByYear, thisyear)
        ci50 = confidenceInterval50(valByYear, thisyear)

        thisYearVal = valByYear[thisyear]
        maxSince = None
        minSince = None
        for year in reversed(sorted(valByYear.keys())):
            if year != thisyear:
                val = valByYear[year]
                if maxSince is None and val >= thisYearVal:
                    maxSince = year
                if minSince is None and val <= thisYearVal:
                    minSince = year
        del val
        insideCi80 = (thisYearVal >= ci80.low and thisYearVal <= ci80.high)
        insideCi50 = (thisYearVal >= ci50.low and thisYearVal <= ci50.high)

        if field.units == 'days': # and False:
            todayValByYear = monthlyAverages.yearDatas(
                todayFilter, field=field,
                lastYear=today.year, cumulative=cumulative)
            if todayValByYear[today.year] == 0:
                #The countable event did not occur today, so skip.
                continue
            #import pdb; pdb.set_trace()

        yearByVal = reverseDict(valByYear)
        top5 = topNValuesLists(yearByVal, 5)
        if ( (allYear or allWinter)
             and ( inListOfLists(top5.values(), thisyear)
                   or args.force)
        ):
            tweetTopN(city, top5, field, thisyear)
        if justTop5:
            continue

        amountDescription=''
        if thisYearVal < ci50[0] and ( field.units != 'days' or thisYearVal != 0 ):
            amountDescription='just '
        amount = formatWithUnits(thisYearVal, field, field.precision)
        if field.units == 'days':
            amount = formatWithUnits(thisYearVal, field, 0, skipUnits=True)
            if thisYearVal == 0:
                amount = "no"

        aboveBelow = 'above'
        if thisYearVal < normalVal.average:
            aboveBelow = 'below'

        if cumulative:
            deviation = deviationDescription(thisYearVal, normalVal.average, field)
        else:
            diff = abs(thisYearVal-normalVal.average)
            deviation = formatWithUnits(diff, field, field.precision) + ' ' + aboveBelow
        start='average'
        if cumulative:
            start='total'
        title=field.title.lower()
        ci80Low = formatWithUnits(ci80[0], field, field.precision, skipUnits=True)
        ci80High = formatWithUnits(ci80[1], field, field.precision)
        insideOutside = 'outside'
        if insideCi80:
            insideOutside = 'inside'
        cityName = stations.city[city].name
        avgWithUnits = formatWithUnits(normalVal.average, field, field.precision)
        #tweetText = (
        #    '#{cityName}\'s {start} {title} so far this year was'
        #    ' {amountDescription}{amount},'
        #    ' {deviation} {aboveBelow} average; {insideOutside} the normal range of'
        #    ' {ci80Low} to {ci80High}'.format(**locals()))
        tweetText = (
            '#{cityName}\'s {start} {title} so far this year was'
            ' {amountDescription}{amount},'
            ' {deviation} the average of'
            ' {avgWithUnits}'.format(**locals()))
        if allYear:
            tweetText = (
                '#{cityName}\'s {start} {title} during {today.year} was'
                ' {amountDescription}{amount},'
                ' {deviation} the average of'
                ' {avgWithUnits}'.format(**locals()))
        if field.units == 'days':
            units = field.unit
            if thisYearVal != 1:
                units = field.units
            nth = alert.nth(thisYearVal)
            #import pdb; pdb.set_trace()
            average = formatWithUnits(normalVal.average, field, precision=1)
            todayString = 'Today is'
            if today != daily.timeByCity[city].date():
                todayString = 'Yesterday was'
            tweetText = (
                '{todayString} #{cityName}\'s {nth} {title} day so far this year,'
                ' {deviation} the average of {average}.'
                .format(**locals()))
        #alertTweets.maybeTweetWithSuffix(city, tweetText)
        recordMin = normalVal.minimum
        recordMax = normalVal.maximum
        print('Record minimum was {recordMin}{field.units} in {normalVal.minYear}'
              .format(**locals()))
        print('Record maximum was {recordMax}{field.units} in {normalVal.maxYear}'
              .format(**locals()))
        plotIt = not insideCi80 or args.force
        if maxSince is None:
            print('***Max since records began in {}.'.format(min(valByYear.keys())))
            plotIt = True
        elif today.year - maxSince > 10:
            maxSinceVal = valByYear[maxSince]
            print('***Max since {maxSince}:{maxSinceVal}{field.units}'.format(**locals()))
            plotIt = True
        if minSince is None:
            print('***Min since records began in {}.'.format(min(valByYear.keys())))
            plotIt = True
        elif today.year - minSince > 10:
            minSinceVal = valByYear[minSince]
            print('***Min since {minSince}:{minSinceVal}{field.units}'.format(**locals()))
            plotIt = True
        if plotIt:
            fname = field.name
            pngname = "%s/Annual_%s.png" % (city, fname)
            alertTweets.maybeTweetWithSuffix(city, tweetText, fname=pngname)
    if todayMax is None:
        return todayAverageMax + 2
    return max(todayMax, todayAverageMax + 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate monthly tweets.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--lastCheckedValue', type=int)
    parser.add_argument('--maxValueToCheck', type=int)
    parser.add_argument('--rangeToCheck', nargs=2)
    parser.add_argument('--today')
    parser.add_argument('--only-since-date')
    parser.add_argument('--all-year', action='store_true')
    parser.add_argument('--all-winter', action='store_true')
    parser.add_argument('--top5', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    city = args.city
    today = None
    if args.today is not None:
        today = dt.date(*map(lambda t: int(t), args.today.split('-')))
    onlySinceDate = None
    if args.only_since_date is not None:
        onlySinceDate = dt.date(*map(lambda t: int(t),
                                     args.only_since_date.split('-')))
    lastCheckedValue = args.lastCheckedValue
    maxValueToCheck = args.maxValueToCheck
    if args.rangeToCheck is not None:
        rangeToCheck = tuple(map(int, map(float, args.rangeToCheck)))
        lastCheckedValue = rangeToCheck[0]
        maxValueToCheck = rangeToCheck[1]
    main(city, args.force,
         lastCheckedValue, today,
         maxValueToCheck,
         args.all_year, args.all_winter,
         args.top5,
         dataSinceDay = onlySinceDate)
