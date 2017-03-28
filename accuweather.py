#!/usr/bin/python3
import datetime
import sys
from collections import namedtuple
from html.parser import HTMLParser
import daily
import decimal
D = decimal.Decimal

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
        #print("Encountered some data  :", data)
        self.data.append(data)

def forecast(fname):
    a = open(fname).read()
    parser = MyHTMLParser()
    parser.feed(a)
    days = {}
    data = parser.data
    year = None

    for index, text in enumerate(data):
        tokens = text.split(' ', 5)
        if ( year is None
             and tokens[0].lower() == 'ottawa'
             and tokens[2] == 'Weather'
             and tokens[4] == '-'
        ):
            year = int(tokens[3])

        if text.strip() in ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'):
            month, day = map(int, data[index+1].strip().split('/'))
            high, low = map(lambda t: int(t.strip('°')), data[index+3].split('/'))
            rain = D(data[index+5].strip())
            snow = D(data[index+8].strip())
            conditions = parser.data[index+13].strip()
            date = datetime.date(year, month, day)
            days[date] = daily.DayData(
                MAX_TEMP=high,
                MAX_TEMP_FLAG='F',
                MIN_TEMP=low,
                MIN_TEMP_FLAG='F',
                TOTAL_RAIN_MM=rain,
                TOTAL_RAIN_FLAG='F',
                TOTAL_SNOW_CM=snow,
                TOTAL_SNOW_FLAG='F',
                MEAN_TEMP=str((float(low)+float(high))/2),
                MEAN_TEMP_FLAG='F',
                #conditions,
            )
            #print(date, days[date], '\n')
    return days

if __name__ == '__main__':
    f = forecast(sys.argv[1])
    total = 0
    for date, data in sorted(f.items()):
        if date > datetime.date.today():
            print('{} {:4.1f}cm'.format(date, data.TOTAL_SNOW_CM))
            total += data.TOTAL_SNOW_CM
    print('Total: {}cm'.format(total))
