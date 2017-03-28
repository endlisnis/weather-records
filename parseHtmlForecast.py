#!/usr/bin/python3
import datetime
import sys
from collections import namedtuple
from html.parser import HTMLParser
import daily
import decimal
Decimal = decimal.Decimal
import sqlite3

def _toSql10(val):
    if val is None:
        return 'NULL'
    return str(int(val*10))

def _div10MaybeNone(val):
    if val is None:
        return None
    return Decimal(val) / 10

def save(city, data):
    dbname = city+"/data/weather.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    #c.execute('DROP TABLE IF EXISTS hourly')
    sqlFields = ( 'MAX_TEMP int', 'MAX_TEMP_FLAG text',
                  'MIN_TEMP int', 'MIN_TEMP_FLAG text',
                  'TOTAL_PRECIP_MM int', 'TOTAL_PRECIP_FLAG text',
                  'TOTAL_RAIN_MM int', 'TOTAL_RAIN_FLAG text',
                  'TOTAL_SNOW_CM int', 'TOTAL_SNOW_FLAG text',
                  'MEAN_TEMP int', 'MEAN_TEMP_FLAG text' )

    c.execute('CREATE TABLE IF NOT EXISTS forecastYesterday (date text PRIMARY KEY, {})'
              .format(','.join(sqlFields)))
    for date, v in data.items():
        maxTemp = _toSql10(v.MAX_TEMP)
        minTemp = _toSql10(v.MIN_TEMP)
        precip = _toSql10(v.TOTAL_PRECIP_MM)
        rain = _toSql10(v.TOTAL_RAIN_MM)
        snow = _toSql10(v.TOTAL_SNOW_CM)
        mean = _toSql10(v.MEAN_TEMP)
        sqlRow = ( '"{date}",'
                   '{maxTemp},"{v.MAX_TEMP_FLAG}",'
                   '{minTemp},"{v.MIN_TEMP_FLAG}",'
                   '{precip},"{v.TOTAL_PRECIP_FLAG}",'
                   '{rain},"{v.TOTAL_RAIN_FLAG}",'
                   '{snow},"{v.TOTAL_SNOW_FLAG}",'
                   '{mean},"{v.MEAN_TEMP_FLAG}"'.format(**locals()) )
        sqlCmd = 'REPLACE INTO forecastYesterday VALUES ({})'.format(sqlRow)
        try:
            c.execute(sqlCmd)
        except sqlite3.OperationalError:
            print(sqlCmd)
            raise
    conn.commit()
    conn.close()

def load(city):
    dbname = city+"/data/weather.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT * FROM forecastYesterday'
    ret = {}

    for row in c.execute(sqlCmd):
        date = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
        try:
            ret[date] = daily.DayData(
                MAX_TEMP=_div10MaybeNone(row[1]),
                MAX_TEMP_FLAG=row[2],
                MIN_TEMP=_div10MaybeNone(row[3]),
                MIN_TEMP_FLAG=row[4],
                TOTAL_PRECIP_MM=_div10MaybeNone(row[5]),
                TOTAL_PRECIP_FLAG=row[6],
                TOTAL_RAIN_MM=_div10MaybeNone(row[7]),
                TOTAL_RAIN_FLAG=row[8],
                TOTAL_SNOW_CM=_div10MaybeNone(row[9]),
                TOTAL_SNOW_FLAG=row[10],
                MEAN_TEMP=_div10MaybeNone(row[11]),
                MEAN_TEMP_FLAG=row[12])
        except KeyError:
            print(repr(row))
            raise

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

def parseAndSave(city, fname):
    a = open(fname).read()
    parser = MyHTMLParser()
    parser.feed(a)
    days = {}
    MAX_TEMP = None
    MAX_TEMP_FLAG = 'M'
    MIN_TEMP = None
    MIN_TEMP_FLAG = 'M'
    TOTAL_PRECIP_MM = None
    TOTAL_PRECIP_FLAG = 'M'
    TOTAL_RAIN_MM = None
    TOTAL_RAIN_FLAG = 'M'
    TOTAL_SNOW_CM = None
    TOTAL_SNOW_FLAG = 'M'
    MEAN_TEMP = None
    MEAN_TEMP_FLAG = 'M'
    yesterdaysData = False
    for index, data in enumerate(parser.data):
        if data == 'Date:':
            today = parser.data[index+1].strip().split()
            ampm = today[1]
            hour = int(today[0].split(':')[0])
            if ( ( ampm == 'AM' and hour < 6 )
                 or ( ampm == 'PM' and hour > 9 )
            ):
                # I don't trust that "yesterday" is really yesterday
                # between 10pm and 6am.
                return {}
            today = ' '.join(today[-3:])
            today = datetime.datetime.strptime(today, '%d %B %Y').date()
        elif data == 'Yesterday\'s Data':
            yesterdaysData = True
        elif yesterdaysData:
            if data == 'Max:':
                MAX_TEMP = Decimal(parser.data[index+1].strip('°'))
                MAX_TEMP_FLAG = 'Y'
            elif data == 'Min':
                strVal = parser.data[index+2].strip('°')
                try:
                    MIN_TEMP = Decimal(strVal)
                except decimal.InvalidOperation:
                    print(strVal)
                    raise
                MIN_TEMP_FLAG = 'Y'
            elif data == 'Total Precipitation':
                v = parser.data[index+2]
                if v == "Trace":
                    TOTAL_PRECIP_MM = Decimal(0)
                    TOTAL_PRECIP_FLAG = 'T'
                else:
                    TOTAL_PRECIP_MM = Decimal(v)
                    TOTAL_PRECIP_FLAG = 'Y'
            elif data == 'Rainfall':
                v = parser.data[index+2]
                if v == "Trace":
                    TOTAL_RAIN_MM = Decimal(0)
                    TOTAL_RAIN_FLAG = 'T'
                else:
                    TOTAL_RAIN_MM = Decimal(v)
                    TOTAL_RAIN_FLAG = 'Y'
            elif data == 'Snowfall':
                v = parser.data[index+2]
                if v == "Trace":
                    TOTAL_SNOW_CM = Decimal(0)
                    TOTAL_SNOW_FLAG = 'T'
                else:
                    TOTAL_SNOW_CM = Decimal(v)
                    TOTAL_SNOW_FLAG = 'Y'
    if MAX_TEMP is not None and MIN_TEMP is not None:
        MEAN_TEMP = (MAX_TEMP+MIN_TEMP)/2
        MEAN_TEMP_FLAG = ''
    days[today-datetime.timedelta(days=1)] = daily.DayData(
        MAX_TEMP=MAX_TEMP,
        MAX_TEMP_FLAG=MAX_TEMP_FLAG,
        MIN_TEMP=MIN_TEMP,
        MIN_TEMP_FLAG=MIN_TEMP_FLAG,
        TOTAL_PRECIP_MM=TOTAL_PRECIP_MM,
        TOTAL_PRECIP_FLAG=TOTAL_PRECIP_FLAG,
        TOTAL_RAIN_MM=TOTAL_RAIN_MM,
        TOTAL_RAIN_FLAG=TOTAL_RAIN_FLAG,
        TOTAL_SNOW_CM=TOTAL_SNOW_CM,
        TOTAL_SNOW_FLAG=TOTAL_SNOW_FLAG,
        MEAN_TEMP=MEAN_TEMP,
        MEAN_TEMP_FLAG=MEAN_TEMP_FLAG,
    )
        #print(date, days[date], '\n')
    save(city, days)

def main(city, fname):
    parseAndSave(city, fname)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
