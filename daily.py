#/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from extraData import ExtraData
from daydata import DayData

import bz2
import convertHourlyToDaily
import csv
import datetime
import decimal
import gatherSwob
import glob
import io
import metarParse
import os
import parseHtmlForecast
import sqlite3
import stations
import time

D = decimal.Decimal

def calcScore(dayData):
    score = 0
    for v in dayData:
        if v is not None and v != "M":
            score += 1
    return score


class Field():
    def __init__(self,
                 name, englishName, units, htmlunits, monthlyPrecision, minValue,
                 sqlType='string'):
        self.name = name
        self.englishName = englishName
        self.units = units
        self.htmlunits = htmlunits
        self.monthlyPrecision = monthlyPrecision
        self.minValue = minValue
        self.sqlType = sqlType
    @property
    def index(self):
        return DayData._fields.index(self.name)


fields = DayData(
    MAX_TEMP = Field(
        name="MAX_TEMP",
        englishName='maximum temperature',
        units="℃",
        htmlunits='&deg;C',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    MAX_TEMP_FLAG = Field(
        name="MAX_TEMP_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    MIN_TEMP = Field(
        name="MIN_TEMP",
        englishName='minimum temperature',
        units="℃",
        htmlunits='&deg;C',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    MIN_TEMP_FLAG = Field(
        name="MIN_TEMP_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    TOTAL_RAIN_MM = Field(
        name="TOTAL_RAIN_MM",
        englishName='rain',
        units='mm',
        htmlunits='mm',
        monthlyPrecision=1,
        minValue=0,
        sqlType='integer'),
    TOTAL_RAIN_FLAG = Field(
        name="TOTAL_RAIN_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    TOTAL_SNOW_CM = Field(
        name="TOTAL_SNOW_CM",
        englishName='snow',
        units='cm',
        htmlunits='cm',
        monthlyPrecision=1,
        minValue=0,
        sqlType='integer'),
    TOTAL_SNOW_FLAG = Field(
        name="TOTAL_SNOW_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    TOTAL_PRECIP_MM = Field(
        name="TOTAL_PRECIP_MM",
        englishName='precipitation',
        units='mm',
        htmlunits='mm',
        monthlyPrecision=1,
        minValue=0,
        sqlType='integer'),
    TOTAL_PRECIP_FLAG = Field(
        name="TOTAL_PRECIP_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    SNOW_ON_GRND_CM = Field(
        name="SNOW_ON_GRND_CM",
        englishName='snow on the ground',
        units='cm',
        htmlunits='cm',
        monthlyPrecision=0,
        minValue=0,
        sqlType='integer'),
    SNOW_ON_GRND_FLAG = Field(
        name="SNOW_ON_GRND_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    DIR_OF_MAX_GUST_10S_DEG = Field(
        name="DIR_OF_MAX_GUST_10S_DEG",
        englishName='direction of max wind',
        units='10°',
        htmlunits='10&deg;',
        monthlyPrecision=0,
        minValue=0,
        sqlType='integer'),
    DIR_OF_MAX_GUST_FLAG = Field(
        name="DIR_OF_MAX_GUST_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    SPD_OF_MAX_GUST_KPH = Field(
        name="SPD_OF_MAX_GUST_KPH",
        englishName='speed of max wind',
        units='km/h',
        htmlunits='km/h',
        monthlyPrecision=0,
        minValue=0,
        sqlType='integer'),
    SPD_OF_MAX_GUST_FLAG = Field(
        name="SPD_OF_MAX_GUST_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    MAX_HUMIDEX = Field(
        name='MAX_HUMIDEX',
        englishName='maximum humidex',
        units="",
        htmlunits='',
        monthlyPrecision=1,
        minValue=23,
        sqlType='integer'),
    MAX_HUMIDEX_FLAG = Field(
        name='MAX_HUMIDEX_FLAG',
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    MIN_WINDCHILL = Field(
        name='MIN_WINDCHILL',
        englishName='minimum windchill',
        units="",
        htmlunits='',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    MIN_WINDCHILL_FLAG = Field(
        name='MIN_WINDCHILL_FLAG',
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    AVG_WINDCHILL = Field(
        name='AVG_WINDCHILL',
        englishName='average windchill',
        units="",
        htmlunits='',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    AVG_WINDCHILL_FLAG = Field(
        name='AVG_WINDCHILL_FLAG',
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    AVG_WIND = Field(
        name='AVG_WIND',
        englishName='average wind',
        units="km/h",
        htmlunits='km/h',
        monthlyPrecision=1,
        minValue=0,
        sqlType='integer'),
    AVG_WIND_FLAG = Field(
        name='AVG_WIND_FLAG',
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    MEAN_TEMP = Field(
        name="MEAN_TEMP",
        englishName='mean temperature',
        units="℃",
        htmlunits='&deg;C',
        monthlyPrecision=2,
        minValue=None,
        sqlType='integer'),
    MEAN_TEMP_FLAG = Field(
        name="MEAN_TEMP_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    MIN_HUMIDITY = Field(
        name="MIN_HUMIDITY",
        englishName='min humidity',
        units='%',
        htmlunits='%',
        monthlyPrecision=0,
        minValue=None,
        sqlType='integer'),
    MIN_HUMIDITY_FLAG = Field(
        name="MIN_HUMIDITY_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None,
        sqlType='integer'),
    MEAN_HUMIDITY = Field(
        name="MEAN_HUMIDITY",
        englishName='mean humidity',
        units='%',
        htmlunits='%',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    MEAN_HUMIDITY_FLAG = Field(
        name="MEAN_HUMIDITY_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
    AVG_DEWPOINT = Field(
        name="AVG_DEWPOINT",
        englishName='average dewpoint',
        units='℃',
        htmlunits='&deg;C',
        monthlyPrecision=1,
        minValue=None,
        sqlType='integer'),
    AVG_DEWPOINT_FLAG = Field(
        name="AVG_DEWPOINT_FLAG",
        englishName='',
        units='',
        htmlunits='',
        monthlyPrecision=0,
        minValue=None),
)


MAX_TEMP = fields.MAX_TEMP
MAX_TEMP_FLAG = fields.MAX_TEMP_FLAG
MIN_TEMP = fields.MIN_TEMP
MIN_TEMP_FLAG = fields.MIN_TEMP_FLAG
TOTAL_RAIN_MM = fields.TOTAL_RAIN_MM
TOTAL_RAIN_FLAG = fields.TOTAL_RAIN_FLAG
TOTAL_SNOW_CM = fields.TOTAL_SNOW_CM
TOTAL_SNOW_FLAG = fields.TOTAL_SNOW_FLAG
TOTAL_PRECIP_MM = fields.TOTAL_PRECIP_MM
TOTAL_PRECIP_FLAG = fields.TOTAL_PRECIP_FLAG
SNOW_ON_GRND_CM = fields.SNOW_ON_GRND_CM
SNOW_ON_GRND_FLAG = fields.SNOW_ON_GRND_FLAG
DIR_OF_MAX_GUST_10S_DEG = fields.DIR_OF_MAX_GUST_10S_DEG
DIR_OF_MAX_GUST_FLAG = fields.DIR_OF_MAX_GUST_FLAG
SPD_OF_MAX_GUST_KPH = fields.SPD_OF_MAX_GUST_KPH
SPD_OF_MAX_GUST_FLAG = fields.SPD_OF_MAX_GUST_FLAG
MAX_HUMIDEX = fields.MAX_HUMIDEX
MAX_HUMIDEX_FLAG = fields.MAX_HUMIDEX_FLAG
MIN_WINDCHILL = fields.MIN_WINDCHILL
MIN_WINDCHILL_FLAG = fields.MIN_WINDCHILL_FLAG
AVG_WINDCHILL = fields.AVG_WINDCHILL
AVG_WINDCHILL_FLAG = fields.AVG_WINDCHILL_FLAG
AVG_WIND = fields.AVG_WIND
AVG_WIND_FLAG = fields.AVG_WIND_FLAG
MEAN_TEMP = fields.MEAN_TEMP
MEAN_TEMP_FLAG = fields.MEAN_TEMP_FLAG
MIN_HUMIDITY = fields.MIN_HUMIDITY
MIN_HUMIDITY_FLAG = fields.MIN_HUMIDITY_FLAG
MEAN_HUMIDITY = fields.MEAN_HUMIDITY
MEAN_HUMIDITY_FLAG = fields.MEAN_HUMIDITY_FLAG
AVG_DEWPOINT = fields.AVG_DEWPOINT
AVG_DEWPOINT_FLAG = fields.AVG_DEWPOINT_FLAG

thisyear = time.localtime()[0]

def _noneOrInt(strVal):
    if len(strVal) == 0:
        return None
    return int(strVal)

def _noneOrInt10(val):
    if type(val) is str:
        if len(val) == 0:
            return None
        return int(D(val)*10)
    if val is None:
        return None
    return int(val*10)

def _noneOrInt100(strVal):
    if len(strVal) == 0:
        return None
    return int(D(strVal)*100)

def _noneOrFloat10(strVal):
    if len(strVal) == 0:
        return None
    return D(strVal)/10

def _noneOrDecimal(strVal):
    if len(strVal) == 0:
        return None
    return D(strVal)


class Data(dict):
    @property
    def minYear(self):
        return min(self.keys()).year

    @property
    def maxYear(self):
        return max(self.keys()).year

    def firstDateWithValue(self, valueIndex, monthMask=None, dayMask=None):
        for date in sorted(self.keys()):
            if monthMask != None and date.month != monthMask:
                continue
            if dayMask != None and date.day != dayMask:
                continue
            vals = self.get(date, None)
            if vals is not None and vals[valueIndex] is not None:
                return date


dataByCity = {}
timeByCity = {}

def fixOttawa(data):
    assert(data.SNOW_ON_GRND_CM is None)
    return data._replace(SNOW_ON_GRND_CM=77)

dataCorrections = {
    #"ottawa": {datetime.date(2017,2,17): fixOttawa},
    #'stjohn': {datetime.date(2017,1,8): fixSaintJohn},
}

def loadDailyWeatherForYear(data, fname):
    content = bz2.open(fname, 'rt').read()
    if "The database is currently unavailable." in content:
        return
    for tokens in csv.reader(content.split('\n')):
        if len(tokens) != 27 or tokens[0][0] not in ('1', '2'):
            #print "Skipping %s" % line, tokens
            continue

        (lyear, lmonth, lday) = [int(a) for a in tokens[0].split('-')]

        date = datetime.date(lyear, #year
                             lmonth, #month
                             lday) #day

        if tokens[25] == '<31':
            tokens[25] = ''

        dayValues = DayData(
            MAX_TEMP = _noneOrDecimal(tokens[5]),
            MAX_TEMP_FLAG = tokens[6],
            MIN_TEMP = _noneOrDecimal(tokens[7]),
            MIN_TEMP_FLAG = tokens[8],
            TOTAL_RAIN_MM = _noneOrDecimal(tokens[15]),
            TOTAL_RAIN_FLAG = tokens[16],
            TOTAL_SNOW_CM = _noneOrDecimal(tokens[17]),
            TOTAL_SNOW_FLAG = tokens[18],
            TOTAL_PRECIP_MM = _noneOrDecimal(tokens[19]),
            TOTAL_PRECIP_FLAG = tokens[20],
            SNOW_ON_GRND_CM = _noneOrInt(tokens[21]),
            SNOW_ON_GRND_FLAG = tokens[22],
            DIR_OF_MAX_GUST_10S_DEG = _noneOrInt(tokens[23]),
            DIR_OF_MAX_GUST_FLAG = tokens[24],
            SPD_OF_MAX_GUST_KPH = _noneOrInt(tokens[25]),
            SPD_OF_MAX_GUST_FLAG = tokens[26],
        )

        #if date == datetime.date(2016,12,31):
        #    import pudb; pu.db
        if ( ( dayValues.count(None)
               + dayValues.count('')
               + dayValues.count('M')
               + dayValues.count('‡') ) < len(dayValues)
        ):
            # don't even create the day entry if there are no values to report
            data[date] = dayValues

def addForecastYesterdayData(city, data):
    yesterdayDataFromForecastPage = parseHtmlForecast.load(city)
    for yesterdayForecastDate, d in yesterdayDataFromForecastPage.items():
        data[yesterdayForecastDate] = data[yesterdayForecastDate].merge(d)


#Feels = convertHourlyHumidexToDaily.Feels
def addHumidex(data, fyear, city):
    fname = '%s/data/%s.dailyextra-csv.bz2' % (city, fyear)
    if not os.path.exists(fname):
        return

    extraData = csv.reader(io.TextIOWrapper(bz2.BZ2File(fname, 'r'), encoding='cp437'))
    for tokens in extraData:
        ( dateYear, dateMonth, dateDay, *vals ) = tokens
        vals = convertHourlyToDaily.HourlyDailyData(*vals)
        date = datetime.date(int(dateYear), int(dateMonth), int(dateDay) )
        dvals = DayData(
            MAX_TEMP = _noneOrFloat10(vals.maxTemp),
            MAX_TEMP_FLAG = vals.maxTempFlag,
            MIN_TEMP = _noneOrFloat10(vals.minTemp),
            MIN_TEMP_FLAG = vals.minTempFlag,
            SPD_OF_MAX_GUST_KPH = _noneOrInt(vals.maxGust),
            SPD_OF_MAX_GUST_FLAG = vals.maxGustFlag,
            MAX_HUMIDEX = _noneOrFloat10(vals.maxHumidex),
            MAX_HUMIDEX_FLAG = vals.maxHumidexFlag,
            MIN_WINDCHILL = _noneOrFloat10(vals.minWindchill),
            MIN_WINDCHILL_FLAG = vals.minWindchillFlag,
            AVG_WINDCHILL = _noneOrFloat10(vals.avgWindchill),
            AVG_WINDCHILL_FLAG = vals.avgWindchillFlag,
            AVG_WIND = _noneOrInt(vals.avgWind),
            AVG_WIND_FLAG = vals.avgWindFlag,
            MEAN_TEMP = _noneOrFloat10(vals.avgTemp),
            MEAN_TEMP_FLAG = vals.avgTempFlag,
            AVG_DEWPOINT = _noneOrFloat10(vals.avgDewpoint),
            AVG_DEWPOINT_FLAG = vals.avgDewpointFlag,
        )
        try:
            #if date == datetime.date(2017,1,24):
            #    import pudb; pu.db
            data[date] = data[date].merge(dvals)
        except KeyError:
            data[date] = dvals


        v = data[date]
        if v.MIN_TEMP is not None:
            if ( len(vals.minWindchill) > 0
                 and _noneOrInt(vals.minWindchill) > v.MIN_TEMP
             ):
                data[date] = v._replace(
                    MIN_WINDCHILL = v.MIN_TEMP,
                    MIN_WINDCHILL_FLAG = "E")



def load0(city):
    if city not in dataByCity:
        dataByStation = {}
        allTimes = set()
        for station in stations.city[city].dayStations:
            dataByStation[station] = {}
            for fname in glob.glob("{city}/{station}/*.csv.bz2".format(**locals())):
                loadDailyWeatherForYear(dataByStation[station], fname)
            allTimes.update( set(dataByStation[station].keys()) )

        # Merge all of the station data into city data
        dataByCity[city] = Data()
        data = dataByCity[city]

        for time in allTimes:
            for station in stations.city[city].dayStations:
                if time in dataByStation[station]:
                    if time not in data:
                        data[time] = dataByStation[station][time]
                    else:
                        s1 = calcScore(data[time])
                        s2 = calcScore(dataByStation[station][time])
                        if s2 > s1:
                            data[time] = dataByStation[station][time]

        # Include all of the converted hourly data
        for fname in glob.glob("%s/data/*.dailyextra-csv.bz2" % city):
            fyear = fname.split('/')[-1].split('.')[0]
            addHumidex(data, fyear, city)

        if city in dataCorrections:
            for date in dataCorrections[city]:
                data[date] = dataCorrections[city][date](data[date])

        if city == 'ottawa':
            #import pudb; pu.db
            for date in data:
                # before 1955, the snow-on-the-ground data is missing but not
                # labelled as missing
                if date.year < 1955 and data[date].SNOW_ON_GRND_CM is None:
                    data[date] = data[date]._replace(SNOW_ON_GRND_FLAG = 'M')
        if stations.city[city].airportCode is not None:
            metarSnowPerDay = metarParse.loadSnowWithHour(city)
            for date, vals in metarSnowPerDay.items():
                snowAmount, hour = vals
                if data[date].TOTAL_SNOW_CM is None or data[date].TOTAL_SNOW_FLAG == 'M':
                    data[date] = data[date]._replace(
                        TOTAL_SNOW_CM = snowAmount,
                        TOTAL_SNOW_FLAG = 'H'+str(hour))
            swobDayData = gatherSwob.parseDaily(city)
            for date, vals in swobDayData.items():
                data[date] = data.get(date, DayData()).merge(vals)
        addForecastYesterdayData(city, data)
    else:
        data = dataByCity[city]

    return data

def quickSave(city):
    fname = city+"/data/all.fcsv.bz2"
    stream = bz2.open(fname, 'wt')
    csvWriter = csv.writer(stream)
    for date in sorted(dataByCity[city].keys()):
        values = dataByCity[city][date]
        #print(repr(values))
        meaningfulValueCount = sum(
            map(lambda v: v not in ('', 'ç', 'M', '‡'),
                values))
        if meaningfulValueCount > 0:
            csvWriter.writerow((date.year, date.month, date.day) + values.dumpCsv())

def saveSql(data, city):
    dbname = city+"/data/weather.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlFields = ['{} {}'.format(a.name, a.sqlType) for a in fields]
    c.execute('CREATE TABLE IF NOT EXISTS daily (date int PRIMARY KEY, {})'
              .format(','.join(sqlFields)))
    for date, values in data.items():
        ordinal = date.toordinal()
        sqlRow =  (ordinal,) + values.dumpCsv()
        sqlCmd = ( 'REPLACE INTO daily VALUES (?,{})'
                   .format( ','.join(['?']*len(values)) ) )
        try:
            c.execute(sqlCmd, sqlRow)
        except sqlite3.OperationalError:
            print(sqlCmd)
            print(tuple(enumerate(sqlFields)))
            print(tuple(enumerate(sqlRow)))
            raise
        except sqlite3.InterfaceError:
            print(sqlCmd)
            print(tuple(enumerate(sqlFields)))
            print(tuple(enumerate(sqlRow)))
            raise
    conn.commit()
    conn.close()

def load(city):
    if city in dataByCity:
        return dataByCity[city]
    utcTime = datetime.datetime.now(tz=datetime.timezone.utc)
    cityTimezone = stations.city[city].timezone
    timeByCity[city] = utcTime.astimezone(cityTimezone)

    dataByCity[city] = Data()
    data = dataByCity[city]
    fname = city+"/data/all.fcsv.bz2"
    stream = bz2.open(fname, 'rt')

    for tokens in csv.reader(stream):

        date = datetime.date(int(tokens[0]), #year
                             int(tokens[1]), #month
                             int(tokens[2])) #day

        dayValues = DayData(
            MAX_TEMP      = _noneOrFloat10(tokens[3]),
            MAX_TEMP_FLAG = tokens[4],
            MIN_TEMP      = _noneOrFloat10(tokens[5]),
            MIN_TEMP_FLAG  = tokens[6],
            TOTAL_RAIN_MM   = _noneOrFloat10(tokens[7]),
            TOTAL_RAIN_FLAG  = tokens[8],
            TOTAL_SNOW_CM     = _noneOrFloat10(tokens[9]),
            TOTAL_SNOW_FLAG    = tokens[10],
            TOTAL_PRECIP_MM     = _noneOrFloat10(tokens[11]),
            TOTAL_PRECIP_FLAG    = tokens[12],
            SNOW_ON_GRND_CM       = _noneOrInt(tokens[13]),
            SNOW_ON_GRND_FLAG      = tokens[14],
            DIR_OF_MAX_GUST_10S_DEG = _noneOrInt(tokens[15]),
            DIR_OF_MAX_GUST_FLAG    = tokens[16],
            SPD_OF_MAX_GUST_KPH     = _noneOrInt(tokens[17]),
            SPD_OF_MAX_GUST_FLAG    = tokens[18],
            MAX_HUMIDEX            = _noneOrFloat10(tokens[19]),
            MAX_HUMIDEX_FLAG      = tokens[20],
            MIN_WINDCHILL        = _noneOrFloat10(tokens[21]),
            MIN_WINDCHILL_FLAG  = tokens[22],
            AVG_WINDCHILL      = _noneOrFloat10(tokens[23]),
            AVG_WINDCHILL_FLAG = tokens[24],
            AVG_WIND           = _noneOrFloat10(tokens[25]),
            AVG_WIND_FLAG      = tokens[26],
            MEAN_TEMP          = _noneOrFloat10(tokens[27]),
            MEAN_TEMP_FLAG     = tokens[28],
            MIN_HUMIDITY       = _noneOrFloat10(tokens[29]),
            MIN_HUMIDITY_FLAG  = tokens[30],
            MEAN_HUMIDITY      = _noneOrFloat10(tokens[31]),
            MEAN_HUMIDITY_FLAG = tokens[32],
            AVG_DEWPOINT       = _noneOrFloat10(tokens[33]),
            AVG_DEWPOINT_FLAG  = tokens[34])


        data[date] = dayValues

    return data

def dayRange(start, end, step=1):
    for i in range(start.toordinal(), end.toordinal(), step):
        yield datetime.date.fromordinal(i)


if False and __name__ == '__main__':
    #import daily, time
    time1 = time.time()
    a = load('ottawa')
    time2 = time.time()
    a = quickSaveC('ottawa')
    time3 = time.time()

    print(time2 - time1, time3-time2)

    #daily.quickSave('ottawa')

if True and __name__ == '__main__':
    #import daily, time
    time1 = time.time()
    a = load('ottawa')
    #a = load('ottawa')
    time2 = time.time()

    print( time2 - time1 )

    #daily.quickSave('ottawa')
