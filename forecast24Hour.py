#!/usr/bin/python3
import datetime as dt
from hourDataTuple import HourData
from pprint import PrettyPrinter
import requests
import stations
session = requests.Session()

from html.parser import HTMLParser
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.data = []
        self.row = False
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = True
            print("Encountered a start tag:", tag)
            self.data.append([])
        #pass
    def handle_endtag(self, tag):
        if self.row == True and tag == 'tr':
            self.row = False
            print("Encountered an end tag :", tag)
        #pass
    def handle_data(self, data):
        if self.row:
            data = data.strip()
            if len(data):
                print("Encountered some data  :", repr(data))
                self.data[-1].append(data)

def getAndParse(city):
    data = {}
    if city != 'ottawa':
        return data
    response = session.get("http://weather.gc.ca/forecast/hourly/on-118_metric_e.html")
    assert(response.status_code == 200)
    html = response.text
    parser = MyHTMLParser()
    parser.feed(html)

    tz = stations.city[city].timezone

    tz.localize

    currDate = None

    for row in parser.data:
        if len(row) == 1:
            currDate = dt.datetime.strptime(row[0], '%d %B %Y')
            currDate = tz.localize(currDate)
            utcDate = currDate.astimezone(dt.timezone.utc)
        elif row[0] != "Date/Time":
            hour = int(row[0].split(':')[0])
            temp = int(row[1])
            wind = int(row[5][1:])
            data[utcDate+dt.timedelta(hours=hour)] = HourData(
                TEMP=temp,
                TEMP_FLAG='F',
                WIND_SPD=wind,
                WIND_SPD_FLAG='F')
    return data

if __name__ == '__main__':
    data = getAndParse('ottawa')

    for time, vals in sorted(data.items()):
        print(time, vals.TEMP, vals.WIND_SPD)
