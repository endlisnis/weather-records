#!/usr/bin/python3
import argparse
import daily
import datetime
import metar
import pygal
import stations
import tabulate

from collections import namedtuple, deque

ValueDateLabel = namedtuple('ValueDateLabel', [ 'val', 'date', 'label'] )


def test_date():
    """Test a simple dateline"""
    from pygal import DateLine
    from datetime import date, timedelta
    import random
    style=pygal.style.Style(label_font_size=15, major_label_font_size=20)
    date_chart = DateLine(style=style, truncate_label=1000, x_label_rotation=80)
    d = tuple(map(lambda t: ( date(2017,1,1)+timedelta(days=t),
                              random.randint(t,t+100)),
                  range(3000)))
    date_chart.add('dates', d, show_dots=False)
    date_chart.render_to_png('test.png', width=1024, height=768)

test_date()

def daysRecently(data, compareDay, field):
    recordDays = []
    for day, values in reversed(sorted(data.items())):
        if day > compareDay:
            continue
        v = values[field.index]
        if ( v is not None
             and ( len(recordDays) == 0
                   or v > recordDays[-1].val)
        ):
            recordDays.append(
                ValueDateLabel(v,
                               day,
                               '{} -- {}{}'.format(day, v, field.units)))
    return recordDays

def daysToday(data, compareDay, field):
    recordDays = []
    for day, values in reversed(sorted(data.items())):
        if day > compareDay or day.month != compareDay.month or day.day != compareDay.day:
            continue
        v = values[field.index]
        if ( v is not None
             and ( len(recordDays) == 0
                   or v > recordDays[-1].val)
        ):
            recordDays.append(
                ValueDateLabel(v,
                               day,
                               '{} -- {}{}'.format(day, v, field.units)))
    if len(recordDays) == 1:
        oldMax = None
        for day, values in reversed(sorted(data.items())):
            if ( day >= compareDay
                 or day.month != compareDay.month
                 or day.day != compareDay.day
            ):
                continue
            v = values[field.index]
            if ( v is not None
                 and ( oldMax is None
                       or v > oldMax.val)
            ):
                oldMax = ValueDateLabel(v,
                                        day,
                                        '{} -- {}{}'.format(day, v, field.units))
        recordDays.append(oldMax)
    return recordDays

def dailyDataClean(data):
    for year in range(data.minYear, data.maxYear+1):
        for day in daily.dayRange( datetime.date(year, 7, 1),
                                   datetime.date(year, 1, 1),
                                   -1):
            if day not in data:
                continue
            vals = data[day]
            if vals.SNOW_ON_GRND_CM is not None and vals.SNOW_ON_GRND_CM > 0:
                break
            vals = vals._replace(SNOW_ON_GRND_CM = 0)
            #print('Replacing missing data {day} with zero'.format(**locals()))
            data[day] = vals
        for day in daily.dayRange( datetime.date(year, 7, 1),
                                   datetime.date(year, 12, 31),
                                   1):
            if day not in data:
                continue
            vals = data[day]
            if vals.SNOW_ON_GRND_CM is not None and vals.SNOW_ON_GRND_CM > 0:
                break
            vals = vals._replace(SNOW_ON_GRND_CM = 0)
            #print('Replacing missing data {day} with zero'.format(**locals()))
            data[day] = vals

def main(city, dayToPlot, recently, thisDayInHistory, field):
    dailyData = daily.load(city)
    dailyDataClean(dailyData)
    if dayToPlot is None:
        dayToPlot = datetime.date.today()
    if recently:
        historyLines = daysRecently(dailyData, dayToPlot, field)
    else:
        historyLines = daysToday(dailyData, dayToPlot, field)

    if len(historyLines) == 1: #Most ever
        startDate = dailyData.firstDateWithValue(field.index)
    else:
        startDate = historyLines[1].date
        # - datetime.timedelta(days=(historyLines[0].date - historyLines[1].date).days * .1)
    endDate = historyLines[0].date + datetime.timedelta(days=1)
    plotData = []
    for date in daily.dayRange(startDate,
                               endDate):
        values = dailyData.get(date, None)
        if values is None:
            continue
        plotData.append( (date, values[field.index]) )
    style=pygal.style.Style(label_font_size=15, major_label_font_size=20)
    date_chart = pygal.DateLine(style=style,
                                print_values=True,
                                #truncate_label=1000,
                                x_label_rotation=80)
    date_chart.y_title = '{} ({})'.format(field.englishName,
                                          field.units)
    if field.minValue == 0:
        date_chart.add(None, plotData, show_dots=False, fill=True)
    else:
        date_chart.add(None, plotData, show_dots=False)

    labelByValue = {}
    for history in historyLines[0:2]:
        labelByValue[float(history.val)] = history.label
        date_chart.add(None,
                       ( ( startDate, history.val ),
                         ( historyLines[0].date, history.val ) ),
                       formatter = lambda t: labelByValue[t[1]] )

    historyType = ''
    if thisDayInHistory:
        historyType = 'thisDayInHistory'
    if recently:
        historyType = 'recently'
    fname = '{city}/{dayToPlot}.recordSince.{historyType}.png'.format(**locals())
    date_chart.render_to_png(fname,
                             width=1024, height=768)
    return fname

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Chart intra-day snowfall.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--today')
    parser.add_argument('--thisDayInHistory', action='store_true')
    parser.add_argument('--recently', action='store_true')
    args = parser.parse_args()
    today = args.today
    if today is not None:
        today = datetime.date(*map(int, today.split('-')))
    main(args.city, today, args.recently, args.thisDayInHistory, field=daily.MAX_TEMP)
