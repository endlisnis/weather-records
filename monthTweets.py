#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import monthlyAverages
import daily
import dailyRecords
import datetime
import argparse
import alertTweets
import alert
import stations
import snow
import os
import pprint
from monthName import monthName
from dailyFilters import *
from reversedict import topNValuesLists, inListOfLists, reverseDict
import decimal
D = decimal.Decimal

def formatWithUnits(val, field, precision=None, skipUnits=None):
    #print ((val, field, precision, skipUnits))
    if precision is None:
        precision = field.precision
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

def confidenceInterval80(valByYear, now):
    vals = []
    for y in range(now.year-30, now.year):
        if y in valByYear:
            vals.append(valByYear[y])
    vals.sort()
    ret = (vals[len(vals)//10], vals[len(vals)-(len(vals)//10)-1])
    return ret

def confidenceInterval50(valByYear, now):
    vals = []
    for y in range(now.year-30, now.year):
        if y in valByYear:
            vals.append(valByYear[y])
    vals.sort()
    ret = (vals[len(vals)//4], vals[len(vals)-(len(vals)//4)-1])
    return ret

def roundAwayFromZero(val):
    return int(val+val/(2*abs(val)))

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
    if hasattr(field, 'description'):
        return field.description
    ret = {
        "MEAN_TEMP": 'avg. hourly temp',
        "MEAN_HUMIDITY": 'avg. hourly humidity',
        "AVG_WIND": 'avg. wind',
        "AVG[MIN_TEMP,MAX_TEMP]": 'avg. temp',
        "TOTAL_SNOW_CM": None,
    }
    return ret[field.name]

def tweetTopN(city, db, monthStr, field, thisYear, daysLeftThisYear):
    #import pudb; pu.db
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
    tweetText = '#{cityName}\'s {totalCount} {adjective} {monthStr}s'.format(**locals())
    if description is not None:
        tweetText += '(by {description})'.format(**locals())
    for key in reversed(sorted(db.keys())):
        for year in reversed(sorted(db[key])):
            #val = '{:.{}f}'.format(key, field.precision+1)
            #print(field.precision, D('.'+'0'*(field.precision)+'1'))
            #val = key.quantize(D('.'+'0'*(field.precision)+'1'))
            val = key
            nth = top10.get(place,'*')
            if year == thisYear:
                nth = top10Double.get(place, '*')
                if place == 1 and daysLeftThisYear <= 0:
                    tweetText = f'#{cityName} just had its {adjective} {monthStr} ever'
                    if description is not None:
                        tweetText += f' (by {description})'
            nextLine = "\n{nth} {year}: {val}{units}".format(**locals())
            if year == thisYear and daysLeftThisYear > 0:
                if daysLeftThisYear > 1:
                    nextLine += ' ({daysLeftThisYear} days left)'.format(**locals())
                else:
                    nextLine += ' (1 day left)'.format(**locals())
            if len(tweetText) + len(nextLine) > 140:
                tweetText += '...'
                break
            tweetText += nextLine
        place += len(db[key])
    #print(tweetText); input()
    alertTweets.maybeTweetWithSuffix(city, tweetText)

def deviationDescription(val, average):
    #import pudb; pu.db
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
    aboveBelow = 'above'
    if val < average:
        aboveBelow = 'below'
    deviation = "∞%" + ' ' + aboveBelow
    average = D(average).quantize(D('.1'), decimal.ROUND_HALF_UP)
    if average != 0:
        percent=int(100*(val-average)/average)
        absPercent=abs(percent)
        deviation = '{absPercent}% {aboveBelow}'.format(**locals())
        if percent >= 75:
            moreThanDescription = moreThan[(percent + 25)//100]
            percentMod = percent % 100
            if percentMod >= 75:
                deviation = 'almost {moreThanDescription}'.format(**locals())
            elif percentMod == 0:
                deviation = '{moreThanDescription}'.format(**locals())
            else:
                deviation = 'more than {moreThanDescription}'.format(**locals())
    return deviation

#deviationDescription(175, 100)

def maybeTweetTop5(
        city, valByYear,
        nextMonthYear, nextMonthMonth,
        monthStr, field, monthDate
):
    yearByVal = reverseDict(valByYear)
    top5 = topNValuesLists(yearByVal, 5)
    if inListOfLists(top5.values(), monthDate.year):
        daysLeft = datetime.date(nextMonthYear, nextMonthMonth, 1) - datetime.date.today()
        tweetTopN(city, top5, monthStr, field, monthDate.year, daysLeft.days)

def filterDict(dictInput, filterFunction):
    return {
        k:v for k,v in dictInput.items() if filterFunction(k,v) }

def maybeTweetMaxSince(
        city, valByYear,
        field, monthDate,
        monthStr, maxSince,
        cumulative
):
    if maxSince is None:
        return
    if monthDate.year - maxSince < 8:
        return
    if len(tuple(filter(lambda t: t in range(maxSince,monthDate.year), valByYear.keys()))) < 8:
        return
    thisYearVal = valByYear[monthDate.year]
    cityName = stations.city[city].name

    monthAdjective = fieldAdjective(field)[0]
    amount = formatWithUnits(thisYearVal, field)
    aggregate = "Total" if cumulative else "Average"
    #import pudb; pu.db
    tweet = ( '#{cityName} just had its {monthAdjective} {monthStr}'
              ' since {maxSince}. {aggregate} {field.englishName} was {amount}.'
              .format(**locals()))
    if field.units == 'days':
        tweet = ( '#{cityName} had 7 {monthStr} {field.englishName} days;'
                  ' more than any year since {maxSince}.'
                  .format(**locals()))

    #pprint.PrettyPrinter().pprint(valByYear)
    #print(tweet)
    #input()
    alertTweets.maybeTweetWithSuffix(city, tweet)

def maybeTweetMinSince(
        city, valByYear,
        field, monthDate,
        monthStr, minSince,
        cumulative
):
    if minSince is None:
        return
    if monthDate.year - minSince < 8:
        return
    thisYearVal = valByYear[monthDate.year]
    cityName = stations.city[city].name

    monthAdjective = fieldAdjective(field)[1]
    amount = formatWithUnits(thisYearVal, field)
    aggregate = "Total" if cumulative else "Average"
    #import pudb; pu.db
    tweet = ( '#{cityName} just had its {monthAdjective} {monthStr}'
              ' since {minSince}. {aggregate} {field.englishName} was just {amount}.'
              .format(**locals()))
    alertTweets.maybeTweetWithSuffix(city, tweet)

def main(city, args,
         lastCheckedValue=None, today=None):
    #import pdb; pdb.set_trace()
    monthlyAverages.cityData = daily.load(city)
    if today is None:
        today = daily.timeByCity[city].date()
    monthDate = today - datetime.timedelta(7)
    nextMonthStart = datetime.date(
        monthDate.year if monthDate.month < 12 else monthDate.year + 1,
        monthDate.month + 1 if monthDate.month < 12 else 1,
        1)
    daysLeft = (nextMonthStart - today).days
    monthlyAverages.now = monthDate
    tomorrow = today + datetime.timedelta(days=1)

    fieldList = []
    if args.daysAbove:
        fieldList += [
            ( ExprVal('max>=' + str(t),
                      title=str(t) + "℃",
                      name="max>=" + str(t),
                      units="days",
                      unit="day",
                      precision=0,
                      field=daily.MAX_TEMP,
                      description=str(t) + "℃ days"),
              True ) for t in range(20, 29+1) ]
    if args.daysBelow:
        fieldList += [
            ( ExprVal('min<=' + str(t),
                      title=str(t) + "℃",
                      name="min<=" + str(t),
                      units="days",
                      unit="day",
                      precision=0,
                      field=daily.MIN_TEMP,
                      description=str(t) + "℃ nights"),
              True ) for t in range(-10, 1) ]
        #[ ( ExprVal('maxHumidex>max and maxHumidex>=' + str(t),
        #              title=str(t) + " humidex",
        #              name="humidex>=" + str(t),
        #              units="days",
        #              unit="day",
        #              precision=0),
        #      True ) for t in range(30, 51) ]
    if args.rain:
        if 'TOTAL_RAIN_MM' not in stations.city[args.city].skipDailyFields:
            fieldList += [
                ( FractionVal(daily.TOTAL_RAIN_MM, "Rain"), True ) ]
    if args.snow:
        fieldList += [
            ( FractionVal(daily.TOTAL_SNOW_CM, "snow"), True ) ]
    if args.snowDays:
        fieldList += (
            [ ( ExprVal('snow>0',
                        title="snow",
                        name="snow",
                        units="days",
                        unit="day",
                        precision=0,
                        field=daily.TOTAL_SNOW_CM,
                        description="snow days"), True ) ]
            +
            [ ( ExprVal('snow>=' + str(t),
                        title=str(t) + "cm snow",
                        name="snow>=" + str(t),
                        units="days",
                        unit="day",
                        precision=0,
                        field=daily.TOTAL_SNOW_CM,
                        description=str(t) + "cm snow days"),
                True ) for t in range(5, 41, 5) ]
        )
    if args.wind:
        fieldList += [
            ( FractionVal(daily.AVG_WIND, "wind"), False ) ]
    if args.meanTemp:
        fieldList += [
            ( ExprVal('meanTemp'
                      ' if ("M" not in meanTempFlag and "I" not in meanTempFlag)'
                      ' else ((max+min)/2'
                      '  if ("M" not in minFlag and "I" not in minFlag'
                      '      and "M" not in maxFlag and "I" not in maxFlag)'
                      '  else None)',
                      name="Mean temperature",
                      title="Mean temperature",
                      units="℃",
                      unit="℃",
                      precision=2,
                      field=daily.MEAN_TEMP,
                      description='avg. hourly temp'), False ) ]
    if args.avgTemp:
        fieldList += [
            ( Avg(daily.MIN_TEMP, daily.MAX_TEMP, "Temperature"), False ) ]
    if args.humidity:
        fieldList += [
            ( FractionVal(daily.MEAN_HUMIDITY, "Humidity"), False ) ]

    monthStr = monthName(monthDate.month, long=True)
    monFilter = monthlyAverages.MonthFilter(month = monthDate.month)
    nextMonthYear = (monthDate.year*12+monthDate.month)//12
    nextMonthMonth = monthDate.month%12+1

    #import pudb; pu.db
    for field, cumulative in fieldList:
        valByYear = monthlyAverages.yearDatas(
            monFilter, field=field,
            lastYear=monthDate.year, cumulative=cumulative)
        normalVal = monthlyAverages.normalMonthlyDatas(
            monthDate.year, monFilter, field, cumulative=cumulative)
        if monthDate.year not in valByYear:
            continue
        ci80 = confidenceInterval80(valByYear, monthDate)
        ci50 = confidenceInterval50(valByYear, monthDate)

        thisYearVal = valByYear[monthDate.year]
        maxSince = None
        minSince = None
        for year in reversed(sorted(valByYear.keys())):
            if year != monthDate.year:
                val = valByYear[year]
                if maxSince is None and val >= thisYearVal:
                    maxSince = year
                if minSince is None and val <= thisYearVal:
                    minSince = year
        del val

        maybeTweetTop5(
            city, valByYear,
            nextMonthYear, nextMonthMonth,
            monthStr, field, monthDate)
        maybeTweetMaxSince(
            city, valByYear, field,
            monthDate, monthStr,
            maxSince, cumulative)
        maybeTweetMinSince(
            city, valByYear, field,
            monthDate, monthStr,
            minSince, cumulative)

        insideCi80 = (thisYearVal >= ci80[0] and thisYearVal <= ci80[1])
        insideCi50 = (thisYearVal >= ci50[0] and thisYearVal <= ci50[1])

        amountDescription=''
        if thisYearVal < ci50[0] and ( field.units != 'days' or thisYearVal != 0 ):
            amountDescription='just '
        if daysLeft > 5 and thisYearVal > ci50[0]:
            amountDescription='already '
        amount = formatWithUnits(thisYearVal, field)
        if field.units == 'days':
            amount = formatWithUnits(thisYearVal, field, 0, skipUnits=True)
            if thisYearVal == 0:
                amount = "no"

        aboveBelow = 'above'
        if thisYearVal < normalVal.average:
            aboveBelow = 'below'

        if cumulative:
            deviation = deviationDescription(thisYearVal, normalVal.average)
        else:
            diff = abs(float(thisYearVal-normalVal.average))
            deviation = formatWithUnits(diff, field) + ' ' + aboveBelow
        start='average'
        if cumulative:
            start='total'
        title=field.title.lower()
        ci80Low = formatWithUnits(ci80[0], field, skipUnits=True)
        ci80High = formatWithUnits(ci80[1], field)
        insideOutside = 'outside'
        if insideCi80:
            insideOutside = 'inside'
        cityName = stations.city[city].name
        average = formatWithUnits(normalVal.average, field,
                                  precision=max(field.precision, 1))
        tweetText = (
            '#{cityName}\'s {start} {title} this {monthStr} was'
            ' {amountDescription}{amount},'
            ' {deviation} the average of {average}.'.format(**locals()))
        if daysLeft > 0:
            tweetText = (
                f'With {daysLeft} days left, #{cityName}\'s {start} {title} this {monthStr} is'
                f' {amountDescription}{amount},'
                f' {deviation} the average of {average}.')
        if field.units == 'days':
            units = field.unit
            if thisYearVal != 1:
                units = field.units
            tweetText = (
                '#{cityName} had'
                ' {amountDescription}{amount} {title} {units} this {monthStr},'
                ' {deviation} the average of {average}.'.format(**locals()))
        print(tweetText)
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
        elif monthDate.year - maxSince > 10:
            maxSinceVal = float(valByYear[maxSince])
            print('***Max since {maxSince}:{maxSinceVal}{field.units}'.format(**locals()))
            plotIt = True
        if minSince is None:
            print('***Min since records began in {}.'.format(min(valByYear.keys())))
            plotIt = True
        elif monthDate.year - minSince > 10:
            minSinceVal = float(valByYear[minSince])
            print('***Min since {minSince}:{minSinceVal}{field.units}'.format(**locals()))
            plotIt = True
        if plotIt:
            monthlyAverages.annualOrderedByMonth(
                city, monFilter, field, cumulative=cumulative)
            plotFname = snow.createPlot(
                city,
                running=cumulative,
                field=field,
                otheryears=(),
                name = monthName(monthDate.month) + title.replace(' ', '_').replace('℃', 'C'),
                dataStartDay = datetime.date(monthDate.year, monthDate.month,   1),
                plotStartDay = datetime.date(monthDate.year, monthDate.month,   1),
                plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                plotYMin = None)
            pngname = plotFname.replace('/svg/','/')+'.png'
            command='rsvg-convert -o {pngname} --background-color=white {plotFname}'.format(**locals())
            print(command)
            assert os.system(command) == 0
            alertTweets.maybeTweetWithSuffix(city, tweetText, fname=pngname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate monthly tweets.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--lastCheckedValue', type=int)
    parser.add_argument('--today')
    parser.add_argument('--rain', action='store_true')
    parser.add_argument('--snow', action='store_true')
    parser.add_argument('--snowDays', action='store_true')
    parser.add_argument('--wind', action='store_true')
    parser.add_argument('--meanTemp', action='store_true')
    parser.add_argument('--avgTemp', action='store_true')
    parser.add_argument('--humidity', action='store_true')
    parser.add_argument('--daysAbove', action='store_true')
    parser.add_argument('--daysBelow', action='store_true')
    parser.add_argument('--force', action='store_true')


    args = parser.parse_args()
    city = args.city
    today = None
    if args.today is not None:
        today = datetime.date(*map(lambda t: int(t, 10), args.today.split('-')))
    main(city, args, args.lastCheckedValue, today)
