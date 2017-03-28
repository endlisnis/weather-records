#!/usr/bin/python3

from collections import namedtuple

import hourDataTuple
import bz2
import csv
import datetime
import decimal
import gatherSwob
import glob
import io
import os
import recentWeather
import forecastXml
import pytz
import sqlite3
import stations
import sys
import time

D = decimal.Decimal
HourData = hourDataTuple.HourData

def hourrange(start, end):
    v = start
    if end >= start:
        while v < end:
            yield v
            v += datetime.timedelta(hours=1)
    else:
        while v > end:
            yield v
            v -= datetime.timedelta(hours=1)

def utcHourRange(city, start, end):
    for hour in hourrange(start, end):
        localHour = stations.city[city].timezone.localize(hour)
        utcHour = localHour.astimezone(pytz.utc)
        yield utcHour

def utcHour(city, hour):
    if hour.tzinfo is None:
        localHour = stations.city[city].timezone.localize(hour)
    else:
        localHour = hour
    utcHour = localHour.astimezone(pytz.utc)
    return utcHour

def _toStr(val):
    if val is None:
        return ''
    return str(val)

def _toStr10(val):
    if val is None:
        return ''
    return str(val/10)

def _toStr100(val):
    if val is None:
        return ''
    return str(val/100)

def _div10MaybeNone(val):
    if val is None:
        return None
    return D(val) / 10

def _div100MaybeNone(val):
    if val is None:
        return None
    return D(val) / 100


class Field(namedtuple('Field', 'name index')):
    def __call__(self, hourvalues):
        return hourvalues[self.index]

TEMP=Field('TEMP', 0)
TEMP_FLAG=Field('TEMP_FLAG', 1)
DEW_POINT_TEMP=Field('DEW_POINT_TEMP', 2)
DEW_POINT_TEMP_FLAG=Field('DEW_POINT_TEMP_FLAG', 3)
REL_HUM=Field('REL_HUM', 4)
REL_HUM_FLAG=Field('REL_HUM_FLAG', 5)
WIND_DIR=Field('WIND_DIR', 6)
WIND_DIR_FLAG=Field('WIND_DIR_FLAG', 7)
WIND_SPD=Field('WIND_SPD', 8)
WIND_SPD_FLAG=Field('WIND_SPD_FLAG', 9)
VISIBILITY=Field('VISIBILITY', 10)
VISIBILITY_FLAG=Field('VISIBILITY_FLAG', 11)
STN_PRESS=Field('STN_PRESS', 12)
STN_PRESS_FLAG=Field('STN_PRESS_FLAG', 13)
WEATHER=Field('WEATHER', 14)
class WindchillClass(Field):
    def __call__(self, hourvalues):
        return hourvalues.windchill

WINDCHILL=WindchillClass('WINDCHILL', -1)

#stationsByCity = {'ottawa': (49568, 4337)}
dataByStation = {}

def decimalOrNone(val):
    if type(val) is str:
        if len(val) == 0:
            return None
        return D(val)
    assert(val is None)
    return None

def intOrNone(val):
    if type(val) is str:
        if len(val) == 0:
            return None
        return int(val)
    if type(val) is int:
        return val
    assert(val is None)
    return None

def loadStation(city, station, globPattern = '*'):
    all = {}
    ltime = 0

    for fname in glob.glob('{city}/{station}/{globPattern}.mcsv.bz2'.format(**locals())):
        ctime = time.time()
        if ctime - ltime > 1:
            print(station, fname)
            ltime = ctime

        content = bz2.open(fname, 'rt').read()
        if "The database is currently unavailable." in content:
            # Skip this month
            continue
        for tokens in csv.reader(content.split('\n')):
            if len(tokens) == 25:
                tokens.pop(5)
            if len(tokens) < 5 or tokens[0][0] not in ('1', '2'):
                # skip entries without date
                #print("Skipping because of invalid year %s" % tokens)
                continue
            dateTime = datetime.datetime(
                year=int(tokens[1], 10), #YEAR
                month=int(tokens[2], 10), #MONTH
                day=int(tokens[3], 10), #DAY
                hour=int(tokens[4].split(':')[0], 10), #HOUR
                tzinfo=datetime.timezone.utc,
            )
            dateTime += stations.city[city].hourlyDataTimeOffset

            if len(tokens) != 24:
                #print("Skipping because invalid token count %s" % tokens)
                continue
            hourData = HourData(
                TEMP=decimalOrNone(tokens[5]),
                TEMP_FLAG=tokens[6],
                DEW_POINT_TEMP=decimalOrNone(tokens[7]),
                DEW_POINT_TEMP_FLAG=tokens[8],
                REL_HUM=intOrNone(tokens[9]),
                REL_HUM_FLAG=tokens[10],
                WIND_DIR=intOrNone(tokens[11]),
                WIND_DIR_FLAG=tokens[12],
                WIND_SPD=intOrNone(tokens[13]),
                WIND_SPD_FLAG=tokens[14],
                VISIBILITY=decimalOrNone(tokens[15]),
                VISIBILITY_FLAG=tokens[16],
                STN_PRESS=decimalOrNone(tokens[17]),
                STN_PRESS_FLAG=tokens[17],
                WEATHER=tokens[-1])
            all[dateTime] = hourData
    return all

def hourRange(start, end, step=1):
    date = start
    while date != end:
        yield date
        date += datetime.timedelta(hours=1)

class Data(dict):
    @property
    def minYear(self):
        return min(self.keys()).year

    @property
    def maxYear(self):
        return max(self.keys()).year

def dataComplete(city, year, month, cityData):
    #import pudb; pu.db
    if year is None or len(cityData) == 0:
        return False
    if ( month is None
         and max(cityData.keys()) == datetime.datetime(year, 12, 31, 23, 0)
    ):
        return True
    if month is not None:
        lastHourOfMonth = (
            datetime.datetime(
                year if month < 12 else year + 1,
                month+1 if month < 12 else 1,
                1,
                23,
                0,
                tzinfo=datetime.timezone.utc)
            - datetime.timedelta(days=1) )
        lastHourOfMonth += stations.city[city].hourlyDataTimeOffset
        if max(cityData.keys()) == lastHourOfMonth:
            return True
    return False


def fixSaintJohn(data):
    assert(data.TEMP == D('17.7'))
    return data._replace(TEMP=D('-17.7'))

def fixEdmonton(data):
    if data.TEMP != D('25.7'):
        print(data.TEMP)
        assert(False)
    return data._replace(TEMP=D('-25.7'))

dataCorrections = {
    "ottawa": {},
    'stjohn': {
        datetime.datetime(2017,1,9,0,0): fixSaintJohn,
    },
    'edmonton-airport': {
        datetime.datetime(2017,2,5,20,0): fixEdmonton,
    },
}

def loadEnvCan(city, year = None, month = None):
    dataByStation = {}
    allTimes = set()
    #print(year, type(year))
    assert( year is None or type(year) is int)
    assert( month is None or type(month) is int)
    globPattern = '*'
    if year is not None:
        globPattern = '{}-*'.format(year)
        if month is not None:
            globPattern = '{}-{:02}'.format(year, month)

    for station in stations.city[city].hourStations.keys():
        dataByStation[station] = loadStation(city, station, globPattern)
        allTimes.update( set(dataByStation[station].keys()) )

    cityData = Data()
    cityCorrection = dataCorrections.get(city, {})

    for time in allTimes:
        for station in stations.city[city].hourStations.keys():
            if time in dataByStation[station]:
                cityData[time] = dataByStation[station][time]
                break

    if city in dataCorrections:
        for time in dataCorrections[city]:
            utcTime = time.replace(tzinfo=datetime.timezone.utc)
            utcTime += stations.city[city].hourlyDataTimeOffset
            hourData = cityData.get(utcTime, None)
            if hourData is not None:
                cityData[utcTime] = dataCorrections[city][time](hourData)

    fetchRecent = not dataComplete(city, year, month, cityData)

    if fetchRecent:
        swobData = gatherSwob.parseHourly(city)
        for timestamp, values in swobData.items():
            matchesFilter = ( year is None or timestamp.year == year
                              and month is None or timestamp.month == month)
            if not matchesFilter:
                continue
            cityData[timestamp] = cityData.get(timestamp, HourData()).merge(values)

    sys.stderr.write('\n')
    return cityData

def save_OLD(data, city):
    fname = city+"/data/hourly.fcsv.bz2"
    stream = io.TextIOWrapper(bz2.BZ2File(fname, 'w'), encoding='cp437')
    csvWriter = csv.writer(stream)

    for time in sorted(data.keys()):
        csvWriter.writerow(
            ('{:x}'
             .format(int(time.replace(tzinfo=datetime.timezone.utc).timestamp())),)
            + data[time])

def saveSql(data, city):
    dbname = city+"/data/weather.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlFields = ['{} {}'
                 .format(a,
                         getattr(hourDataTuple.sqlTypes,a)) for a in HourData._fields]
    c.execute('CREATE TABLE IF NOT EXISTS hourly (date int PRIMARY KEY, {})'
              .format(','.join(sqlFields)))
    for time in data.keys():
        utctimestamp = time.replace(tzinfo=datetime.timezone.utc).timestamp()
        utctimestamp = int(utctimestamp)
        sqlRow =  (utctimestamp,) + data[time].dumpAsSql()
        sqlCmd = 'REPLACE INTO hourly VALUES ({})'.format(','.join(['?']*len(sqlRow)))
        try:
            c.execute(sqlCmd, sqlRow)
        except sqlite3.OperationalError:
            print(sqlCmd)
            raise
    conn.commit()
    conn.close()

def quickLoad_OLD(city):
    fname = city+"/data/hourly.fcsv.bz2"
    stream = io.TextIOWrapper(bz2.BZ2File(fname, 'r'), encoding='cp437')
    ret = {}

    for row in csv.reader(stream):
        datestamp = datetime.datetime.utcfromtimestamp(int(row[0], 16))
        datestamp = datestamp.replace(tzinfo=datetime.timezone.utc)
        ret[datestamp] = HourData._make(row[1:])
    return ret

def load(city, dateRange=None):
    dbname = city+"/data/weather.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT * FROM hourly'
    if dateRange is not None:
        sqlCmd = ( 'SELECT * FROM hourly where date >= {} and date < {}'
                   .format(int(utcHour(city, dateRange[0]).timestamp()),
                           int(utcHour(city, dateRange[1]).timestamp())) )
    ret = {}

    for row in c.execute(sqlCmd):
        datestamp = datetime.datetime.fromtimestamp(row[0], datetime.timezone.utc)
        try:
            ret[datestamp] = HourData(
                TEMP=_div10MaybeNone(row[1]),
                TEMP_FLAG=row[2],
                DEW_POINT_TEMP=_div10MaybeNone(row[3]),
                DEW_POINT_TEMP_FLAG=row[4],
                REL_HUM=row[5],
                REL_HUM_FLAG=row[6],
                WIND_DIR=row[7],
                WIND_DIR_FLAG=row[8],
                WIND_SPD=row[9],
                WIND_SPD_FLAG=row[10],
                VISIBILITY=_div10MaybeNone(row[11]),
                VISIBILITY_FLAG=row[12],
                STN_PRESS=_div100MaybeNone(row[13]),
                STN_PRESS_FLAG=row[14],
                WEATHER=row[15])
        except KeyError:
            print(repr(row))
            raise

    return ret

if __name__ == '__main__':
    cityData = loadCity('ottawa')
    csvWriter = csv.writer(open('%s/data/allHours.csv' % 'ottawa', 'w'))
    for date in sorted(cityData.keys()):
        values = cityData[date]
        csvWriter.writerow([date.year, date.month, date.day, date.hour] + list(values))
