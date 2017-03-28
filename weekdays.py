#!/usr/bin/python3
import argparse
import datetime
import daily
import pygal
import stations

parser = argparse.ArgumentParser(description='Determine how weather distributes across weekdays.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--year', type=int, default=datetime.date.today().year-1)
args = parser.parse_args()

data = daily.load(args.city)
year = args.year

def yearlySum(wday, field):
    sum = 0
    count = 0

    for d, vals in data.items():
        if d < datetime.date(year,7,1) or d >= datetime.date(year+1,7,1):
            continue
        weekoffset = d.weekday()
        val = vals[field.index]
        if weekoffset == wday and val is not None:
            sum += val
            count += 1
    return (sum, count)

def yearlyAverage(wday, field):
    (sum, count) = yearlySum(wday, field)

    avg = None
    if count:
        avg = sum/count
    return avg


city = 'ottawa'
cityName = stations.city[city].name
wdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

#for field in [daily.MAX_TEMP, daily.MIN_TEMP, daily.MEAN_TEMP]:
#    print(field.name)
#    for wday in range(len(wdays)):
#        thisyear = yearlyAverage(wday, field)
#
#        print("%s %+5.1f" % (wdays[wday], thisyear))

style=pygal.style.Style(label_font_size=15, major_label_font_size=20)
for field in [daily.TOTAL_SNOW_CM, daily.TOTAL_RAIN_MM]:
    print(field.name)
    plotData = []
    for wday in range(len(wdays)):
        thisyear = yearlySum(wday, field)[0]
        print("%s %+5.1f" % (wdays[wday], thisyear))
        plotData.append(thisyear)
    line_chart = pygal.Bar(style=style, print_values=True)
    line_chart.title = '{cityName} {field.englishName} per day-of-week during winter {year}'.format(**locals())
    line_chart.y_title = '{} ({})'.format(field.englishName.title(), field.units)
    line_chart.x_labels = wdays
    line_chart.add(None, plotData)
    line_chart.render_to_png('{city}/weekday.{field.englishName}.png'.format(**locals()),
                             dpi=50,
                             width=1024, height=768)
