#!/usr/bin/python3
import argparse
import daily
import datetime
import decimal
import forecast24Hour
import gatherSwob
import hourly
import metarParse
import pprint
import pygal
import reversedict
import stations
import tabulate

from collections import namedtuple, deque, defaultdict

D = decimal.Decimal
SnowDateLabel = namedtuple('SnowDateLabel', [ 'snow', 'date', 'label'] )

def snowiestDaysHistory(data, compareDay, field):
    recordSinceSnow = []
    for day, values in reversed(sorted(data.items())):
        if day >= compareDay:
            continue
        v = values[field.index]
        if ( v is not None
             and v > 0
             and ( len(recordSinceSnow) == 0
                   or v > recordSinceSnow[-1].snow)
        ):
            recordSinceSnow.append(
                SnowDateLabel(v,
                              day,
                              '{} -- {}{}'.format(day, v, field.units)))
    recordSinceSnow[-1] = (
        recordSinceSnow[-1]._replace(
            label=(
                recordSinceSnow[-1].label
                + ' all-time record')))
    return recordSinceSnow

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

def maxDaysToday(data, compareDay, field, maxValues=True):
    yearByVal = defaultdict(list)
    for day, values in data.items():
        if day >= compareDay or day.month != compareDay.month or day.day != compareDay.day:
            continue
        v = values[field.index]
        if v is not None:
            yearByVal[v].append(day.year)
    previousValues = []
    count = 1
    if maxValues is True:
        keyList = reversed(sorted(reversedict.topNValuesLists(yearByVal, 5).keys()))
    else:
        keyList = sorted(reversedict.topNValuesLists(yearByVal, 5, bottomN=True).keys())
    for v in keyList:
        years = yearByVal[v]
        label = ( '{}: {}{}'
                  .format('/'.join(map(str,years)),
                          v,
                          field.units) )
        if count == 1:
            label += ' record for {:%b %d}'.format(compareDay)
        previousValues.append(
            SnowDateLabel(v,
                          years,
                          label))
        count += len(years)
    return previousValues

def maxDaysMonth(data, compareDay, field, maxValues=True):
    yearByVal = defaultdict(list)
    for day, values in data.items():
        if day >= compareDay or day.month != compareDay.month:
            continue
        v = values[field.index]
        if v is not None:
            yearByVal[v].append(day.year)
    previousValues = []
    count = 1
    if maxValues is True:
        keyList = reversed(sorted(reversedict.topNValuesLists(yearByVal, 5).keys()))
    else:
        keyList = sorted(reversedict.topNValuesLists(yearByVal, 5, bottomN=True).keys())
    for v in keyList:
        years = yearByVal[v]
        label = ( '{}: {}{}'
                  .format('/'.join(map(str,years)),
                          v,
                          field.units) )
        if count == 1:
            label += ' record for {:%b}'.format(compareDay)
        previousValues.append(
            SnowDateLabel(v,
                          years,
                          label))
        count += len(years)
    return previousValues

def loadHourlyDataSwob(city, dayField, day):
    if dayField == daily.TOTAL_SNOW_CM:
        return metarParse.loadSnowWithHours(city)
    mytimezone = stations.city[city].timezone
    cityData = daily.load(city)
    utcDayStart = datetime.datetime(
        day.year, day.month, day.day, 6, tzinfo=datetime.timezone.utc)
    dayStart = utcDayStart.astimezone(mytimezone)
    dayEnd = dayStart + datetime.timedelta(days=1)
    cityHourData = gatherSwob.parse(city)
    hourly.load(
        city, dateRange=(dayStart, dayEnd) )

    valByHour = {}
    for valuesDict in cityHourData:
        ts = valuesDict['time']
        if ts < dayStart or ts >= dayEnd:
            continue
        if ts == utcDayStart:
            v = valuesDict['air_temp']
        elif dayField == daily.MAX_TEMP:
            v = valuesDict['max_air_temp_pst1hr']
        elif dayField == daily.MIN_TEMP:
            v = valuesDict['min_air_temp_pst1hr']
        else:
            assert(False)
        if v is None:
            continue
        v = D(v)
        l = ts.astimezone(mytimezone)
        valByHour[l] = v

    dayData = cityData.get(day, None)
    if dayData is not None:
        return {day: metarParse.SnowAndHourly(dayData[dayField.index], valByHour)}
    return {day: metarParse.SnowAndHourly(None, valByHour)}

def loadHourlyData(city, dayField, hourField, day):
    if dayField == daily.TOTAL_SNOW_CM:
        return metarParse.loadSnowWithHours(city)
    elif dayField in (daily.MAX_TEMP, daily.MIN_TEMP):
        return loadHourlyDataSwob(city, dayField, day)
    mytimezone = stations.city[city].timezone
    cityData = daily.load(city)
    utcDayStart = datetime.datetime(
        day.year, day.month, day.day, 6, tzinfo=datetime.timezone.utc)
    dayStart = utcDayStart.astimezone(mytimezone)
    dayEnd = dayStart + datetime.timedelta(days=1)
    cityHourData = hourly.load(
        city, dateRange=(dayStart, dayEnd) )

    valByHour = {}
    for utcHour, values in cityHourData.items():
        v = hourField(values)
        if v is None:
            continue
        l = utcHour.astimezone(mytimezone)
        valByHour[l] = v

    return {day: metarParse.SnowAndHourly(cityData[day][dayField.index], valByHour)}

FakeSnowHourField = hourly.Field('SNOW', -1)

hourlyFromDailyField = {
    daily.MAX_TEMP: hourly.TEMP,
    daily.MIN_TEMP: hourly.TEMP,
    daily.TOTAL_SNOW_CM: FakeSnowHourField,
    daily.MIN_WINDCHILL: hourly.WINDCHILL,
    daily.AVG_WIND: hourly.WIND_SPD,
}

def main(city, dayToPlot, recently, thisDayInHistory, thisMonthInHistory,
         days, field, checkMax=True):
    hourField = hourlyFromDailyField[field]
    rows = []
    plotData = [None] * 25
    if field.minValue == 0:
        plotData[0] = 0
    plotForecast = [None] * 25
    today, _ = metarParse.synopticPeriod(datetime.datetime.utcnow())
    if dayToPlot is not None:
        today = dayToPlot
        if type(dayToPlot) is str:
            today = datetime.date(*map(int, dayToPlot.split('-')))
    snowPerDay = loadHourlyData(city, field, hourField, today)
    yesterday = today - datetime.timedelta(days=1)
    dailyData = daily.load(city)
    forecastData = forecast24Hour.getAndParse(city)

    todayUtcMidnight = datetime.datetime(today.year,
                                         today.month,
                                         today.day,
                                         hour=6,
                                         tzinfo=datetime.timezone.utc)
    mtz = stations.city[city].timezone
    todayUtcMidnightLocal = todayUtcMidnight.astimezone(mtz)
    if today in snowPerDay:
        if days == 2:
            plotData[0] = dailyData[yesterday].TOTAL_SNOW_CM
        maxVal, snowHours = snowPerDay[today]
        for utctime, vals in forecastData.items():
            v = hourField(vals)
            if v is None:
                continue
            timediff = utctime - todayUtcMidnight
            index = timediff.days * 24 + timediff.seconds // 3600
            if index < 0 or index > 24:
                continue
            rows.append( ('{}h'.format(index), '{}{}'.format(v, field.units)) )
            plotForecast[index] = {'value': v,
                                   'node': {'r': 6}}
            if maxVal is None or v > maxVal:
                maxVal = v
        for hour, snow in sorted(snowHours.items()):
            totalSnow = snow
            if days == 2:
                totalSnow += dailyData[yesterday].TOTAL_SNOW_CM
            utcHour = hour.astimezone(datetime.timezone.utc)
            timediff = utcHour - todayUtcMidnight
            index = timediff.days * 24 + timediff.seconds // 3600
            rows.append( ('{}h'.format(hour), '{}{}'.format(snow, field.units)) )
            plotData[index] = {'value': totalSnow,
                               'node': {'r': 6}}
        print(tabulate.tabulate(rows,
                                headers=('Time', hourField.name),
                                tablefmt="fancy_grid"))

        style=pygal.style.Style(label_font_size=15, major_label_font_size=20)
        line_chart = pygal.Line(style=style, print_values=True,
                                x_label_rotation=80,
                                include_x_axis=field.minValue==0)
        cityName = stations.city[city].name
        line_chart.title = '{cityName} {field.name} on {today:%b %d, %Y}'.format(**locals())
        line_chart.y_title = '{hourField.name} ({field.units})'.format(**locals())
        line_chart.x_labels = map(
            lambda t: ( '{:%H:%M}'
                        .format( todayUtcMidnightLocal
                                 + datetime.timedelta(hours=t) ) ),
            range(25)
        )
        #print(plotData)
        line_chart.add('Observed', plotData,
                       stroke_style = {'width': 3},
                       formatter = lambda t: str(t)+field.units)
        if plotForecast.count(None) < len(plotForecast):
            line_chart.add('Forecast',
                           plotForecast,
                           stroke_style = {'width': 3})
        historyLines = []

        if recently:
            historyLines = snowiestDaysHistory(dailyData, today, field)
        if thisDayInHistory:
            historyLines = maxDaysToday(dailyData, today, field, maxValues=checkMax)
        if thisMonthInHistory:
            historyLines = maxDaysMonth(dailyData, today, field, maxValues=checkMax)

        labelByValue = {}
        for history in historyLines:
            fv = float(history.snow)
            labelByValue[fv] = labelByValue.get(fv,'') + history.label
            line_chart.add(history.label,
                           ( [ { 'value': history.snow, 'node': {'r': 1} } ]
                             + [ None ] *23
                             + [ history.snow ] ),
                           stroke_style = {'width': 3},
                           formatter = lambda t: '' )
        pprint.PrettyPrinter().pprint(labelByValue)

        historyType = ''
        if thisDayInHistory:
            historyType = 'thisDayInHistory'
        if recently:
            historyType = 'recently'
        if thisMonthInHistory:
            historyType = 'thisMonthInHistory'
        minMax = 'max' if checkMax else 'min'
        fname = '{city}/{today}.hour-{field.name}.{minMax}.{historyType}.png'.format(**locals())
        line_chart.render_to_png(fname,
                                 width=1024, height=768)
        return fname

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Chart intra-day snowfall.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--today')
    parser.add_argument('--thisDayInHistory', action='store_true')
    parser.add_argument('--thisMonthInHistory', action='store_true')
    parser.add_argument('--recently', action='store_true')
    parser.add_argument('--days', default=1, type=int)
    parser.add_argument('--field', choices=['snow', 'max', 'min', 'minWindchill', 'wind'], default='snow')
    parser.add_argument('--min', action='store_true')
    args = parser.parse_args()
    main(city=args.city,
         dayToPlot=args.today,
         recently=args.recently,
         thisDayInHistory=args.thisDayInHistory,
         thisMonthInHistory=args.thisMonthInHistory,
         days=args.days,
         field={ 'snow': daily.TOTAL_SNOW_CM,
                 'max': daily.MAX_TEMP,
                 'min': daily.MIN_TEMP,
                 'minWindchill': daily.MIN_WINDCHILL,
                 'wind': daily.AVG_WIND,
         }[args.field],
         checkMax=args.min is False)
