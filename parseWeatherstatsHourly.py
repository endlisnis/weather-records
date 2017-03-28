#!/usr/bin/python3
# -*- coding: utf-8 -*-

from html.parser import HTMLParser
import datetime
import json
import sys
import pprint
import sqlite3
import hourly
import stations
import pygal

def filterDict(db, keyFilter):
    ret = {}
    for key in db:
        if key in keyFilter:
            ret[key] = db[key]
    return ret

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.data = []
    def handle_starttag(self, tag, attrs):
        pass
        #print("Encountered a start tag:", tag)
    def handle_endtag(self, tag):
        pass
        #print("Encountered an end tag :", tag)
    def handle_data(self, data):
        s = data.strip()
        if len(s):
            #print("Encountered some data  :", s)
            self.data.append(s)

def javascriptDate(year,month,day,hour,minute,second):
    return datetime.datetime(year,month+1,day,hour,minute,second)

conditions = {
    'A Few Clouds',
    'Blowing Snow',
    'Blowing Snow',
    'Clear',
    'Cloudy',
    'Distant Precipitation',
    'Drifting Snow',
    'Drizzle',
    'Flurries',
    'Fog Depositing Ice',
    'Fog Patches',
    'Fog',
    'Freezing Fog',
    'Freezing Rain',
    'Haze',
    'Heavy Rain',
    'Heavy Rainshower',
    'Heavy Snow Pellets',
    'Heavy Snow',
    'Heavy Snowshower',
    'Heavy Thunderstorm with Rain',
    'Ice Crystals',
    'Ice Fog',
    'Ice Pellets',
    'Light Drizzle and Fog',
    'Light Drizzle',
    'Light Flurries',
    'Light Freezing Drizzle',
    'Light Freezing Rain',
    'Light Ice Pellets',
    'Light Rain Showers',
    'Light Rain and Drizzle',
    'Light Rain and Fog',
    'Light Rain and Snow',
    'Light Rain',
    'Light Rainshower',
    'Light Snow Grains',
    'Light Snow Pellets',
    'Light Snow and Blowing Snow',
    'Light Snow',
    'Light Snowshower',
    'Localized Showers',
    'Mainly Clear',
    'Mainly Cloudy',
    'Mainly Sunny',
    'Mist',
    'Mixed Rain and Snow Showers',
    'Moderate Rain',
    'Moderate Snow',
    'Mostly Cloudy',
    'Overcast',
    'Partial Fog Depositing Ice',
    'Partial Fog Lessening',
    'Partly Cloudy',
    'Partly Sunny',
    'Rain and Snow',
    'Rain',
    'Rainshower',
    'Recent Thunderstorm',
    'Severe Sand or Dust Storm',
    'Shallow Fog',
    'Smoke',
    'Snow Grains',
    'Snow Pellets',
    'Snow',
    'Snowshower',
    'Sunny',
    'Thunderstorm with Hail',
    'Thunderstorm with Heavy Rain',
    'Thunderstorm with Light Rain',
    'Thunderstorm with Rain',
    'Thunderstorm with heavy rainshowers',
    'Thunderstorm with light rainshowers',
    'Thunderstorm with rainshowers',
    'Thunderstorm without Precipitation',
    'Thunderstorm',
    'Tornado',
    'Variable Clouds',
    'Violent Rainshower',
}

ignore = {'WindChill'}

def parse(json):
    json = json.replace(');','')
    json = json.replace('google.visualization.Query.setResponse(','')
    json = json.replace('new Date','Date')
    #stuff = stuff.replace(', ', ',\n')
    stuff = eval(json, {'status':'status', 'Date':javascriptDate, 'null':None, 'table':'table', 'false': False})
    p = stuff['table']['p']
    html = p['html_content3']
    if len(html) == 0:
        html = p['html_content4'] + p['html_content5']
    parser = MyHTMLParser()
    parser.feed(html)
    if len(parser.data) == 0:
        return None, None
    conditionText = parser.data[-1]
    if conditionText[0] == ':':
        conditionText = None
    elif conditionText in ignore:
        conditionText = None
    elif conditionText not in conditions:
        print(repr(conditionText))
        print(repr(stuff))
        print()
        exit(1)
    i = parser.data.index('Last Observation')
    lastObservation = parser.data[i+1]
    if(lastObservation[0] != ':'):
        print(lastObservation)
        pprint.PrettyPrinter().pprint(stuff)
        return None, None
    timezonestr = lastObservation.split()[-1]
    lastObservation = datetime.datetime.strptime(lastObservation,
                                                 ': %A, %B %d %Y %H:%M %Z')
    if timezonestr == 'EST':
        utctime = lastObservation + datetime.timedelta(hours=5)
    else:
        utctime = lastObservation + datetime.timedelta(hours=4)
    utctime = utctime.replace(tzinfo=datetime.timezone.utc)
    return utctime, conditionText

if __name__ == '__main__':
    sunByYear = {i:0 for i in range(1952,2017)}
    countByYear = {i:0 for i in range(1952,2017)}
    obsByHour = {}

    mytimezone = stations.city['ottawa'].timezone
    data = hourly.load('ottawa')
    for utctime, values in sorted(data.items()):
        #l = utctime.astimezone(mytimezone)
        #season = l.year - (l.month < 6)
        #countByYear[season] += 1
        if values.WEATHER is not None:
            obsByHour[utctime] = values.WEATHER
        #if 'freezing' in values.WEATHER.lower():
        #    print(l.strftime('%Y/%m/%d@%H:%M'), values.WEATHER)
        #    sunByYear[season] += 1


    dbname = "ottawa/data/weatherstatshistory.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    lastYear = None

    for number, line in enumerate(c.execute('SELECT DISTINCT(json) FROM hourly ORDER BY date')):
        utcTime, conditionText = parse(line[0])
        if conditionText is None:
            continue
        if ( utctime not in obsByHour
             # and lastObservation.month == 1
             and utctime.minute == 0
        ):
            obsByHour[utctime] = conditionText
            if lastYear != utctime.year:
                print('{lastYear}->{utctime.year}'.format(**locals()))
            lastYear = utctime.year

    for utctime, conditions in obsByHour.items():
        l = utctime.astimezone(mytimezone)
        season = l.year - (l.month < 6)
        countByYear[season] += 1
        #if conditionText in (
        #        'Sunny', 'Mainly Sunny',
        #        'Clear', 'Mainly Clear',
        #        'Partly Cloudy'):
        if 'thunder' in conditions.lower() and l.month == 2:
            print(l.strftime('%Y/%m/%d@%H:%M'), conditions)
            sunByYear[season] += 1
    exit(0)

    for year in sorted(sunByYear.keys()):
        thisYearSun = sunByYear[year]
        thisYearCount = countByYear[year]
        print('{year}: {thisYearSun}/{thisYearCount}'.format(**locals()))
    #pprint.PrettyPrinter().pprint(sunByYear)

    plotData = filterDict(sunByYear, range(1987,2017))

    style=pygal.style.Style(label_font_size=15, major_label_font_size=20)
    bar_chart = pygal.Bar(style=style, print_values=True)
    bar_chart.title = 'Ottawa freezing precip per winter'
    bar_chart.y_title = 'Hours'
    bar_chart.x_labels = [str(a)+'/'+str(a+1) for a in sorted(plotData.keys())]
    bar_chart.x_label_rotation=270
    bar_chart.add(None, [plotData[a] for a in sorted(plotData.keys())])
    bar_chart.render_to_png('ottawa/freezingPrecip.png',
                            dpi=50,
                            width=1024, height=768)
