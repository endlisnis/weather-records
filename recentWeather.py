#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re, datetime
import glob, observationXml
import stations, weatherstats
import hourDataTuple
import decimal
import sqlite3
D = decimal.Decimal
HourData = hourDataTuple.HourData

def _div10MaybeNone(val):
    if val is None:
        return None
    return D(val) / 10

def _div100MaybeNone(val):
    if val is None:
        return None
    return D(val) / 100


class Snow():
    def __init__(self):
        self.snow = 0

    def handle(self, hour):
        hoursnow = 0
        if hour[1] in ('light snow', 'snow', 'heavy snow'):
            hoursnow = 1.0/float(hour[7])
        self.snow += hoursnow

def oldGet(city):
    returnData = {}
    if stations.city[city].station == None:
        # This station doesn't have any recent data
        return returnData
    prov = stations.city[city].province
    inputFiles = sorted(glob.glob(prov+'/hourly_*_e.xml'))
    for inputFile in inputFiles:
        observation = observationXml.getCurrentConditionsFromXmlFile(inputFile, city)
        returnData[observation['timestamp']] = HourData(
            TEMP=observation['air_temperature'],
            TEMP_FLAG='H',
            DEW_POINT_TEMP=observation['dew_point'],
            DEW_POINT_TEMP_FLAG='H',
            REL_HUM=observation['relative_humidity'],
            REL_HUM_FLAG='H',
            WIND_DIR=observation['wind_direction'],
            WIND_DIR_FLAG='H',
            WIND_SPD=observation['wind_speed'],
            WIND_SPD_FLAG='H',
            VISIBILITY=observation['horizontal_visibility'],
            VISIBILITY_FLAG='H',
            STN_PRESS=observation['mean_sea_level'],
            STN_PRESS_FLAG='H',
            WEATHER=observation['present_weather'])
    return returnData

def decimalUnlessNone(val):
    if type(val) is str or type(val) is int:
        return D(val)
    if type(val) is float:
        return D(str(val))
    assert(val is None)
    return None

def decimalDiv1000UnlessNone(val):
    if type(val) is str or type(val) is int:
        return D(val)/1000
    if type(val) is float:
        return D(str(val))/1000
    assert(val is None)
    return None

def strDiv1000UnlessNone(val):
    if val != None:
        return str(val/1000.0)
    return ''

def missingIfNone(val):
    if val != None:
        return 'H'
    return 'M'

def parse(city):
    returnData = {}
    obs = {}
    for ob in filter(lambda t: t not in stations.city[city].skipOb, weatherstats.allObs):
        observations = {}
        dayFilenamePattern = '{city}/data/{ob}-24hrs.*.json'.format(**locals())
        inputFiles = glob.glob(dayFilenamePattern)
        for dayFilename in inputFiles:
            observations.update(weatherstats.main(city, dayFilename))
        for timestamp, observation in observations.items():
            v = returnData.get(timestamp,
                               HourData(
                                   TEMP=None,
                                   TEMP_FLAG='M',
                                   DEW_POINT_TEMP=None,
                                   DEW_POINT_TEMP_FLAG='M',
                                   REL_HUM=None,
                                   REL_HUM_FLAG='M',
                                   WIND_DIR=None,
                                   WIND_DIR_FLAG='M',
                                   WIND_SPD=None,
                                   WIND_SPD_FLAG='M',
                                   VISIBILITY=None,
                                   VISIBILITY_FLAG='M',
                                   STN_PRESS=None,
                                   STN_PRESS_FLAG='M',
                                   WEATHER=None) )

            if ob == 'temperature':
                v = v._replace(TEMP=decimalUnlessNone(observation),
                               TEMP_FLAG=missingIfNone(observation))
            elif ob == 'relative_humidity':
                v = v._replace(REL_HUM=observation,
                               REL_HUM_FLAG=missingIfNone(observation))
            elif ob == 'dew_point':
                v = v._replace(DEW_POINT_TEMP=decimalUnlessNone(observation),
                               DEW_POINT_TEMP_FLAG=missingIfNone(observation))
            elif ob == 'wind_speed':
                v = v._replace(WIND_SPD=observation,
                               WIND_SPD_FLAG=missingIfNone(observation))
            elif ob == 'pressure_sea':
                v = v._replace(STN_PRESS=decimalUnlessNone(observation),
                               STN_PRESS_FLAG=missingIfNone(observation))
            elif ob == 'visibility':
                v = v._replace(VISIBILITY=decimalDiv1000UnlessNone(observation),
                               VISIBILITY_FLAG=missingIfNone(observation))
            returnData[timestamp]=v
    return returnData

def saveSql(data, city):
    dbname = city+"/data/weatherstats.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    #c.execute('DROP TABLE IF EXISTS hourly')
    sqlFields = ['{} {}'
                 .format(a,
                         getattr(hourDataTuple.sqlTypes,a)) for a in HourData._fields]
    c.execute('CREATE TABLE IF NOT EXISTS hourly (date int PRIMARY KEY, {})'
              .format(','.join(sqlFields)))
    for time in data.keys():
        utctimestamp = time.replace(tzinfo=datetime.timezone.utc).timestamp()
        utctimestamp = int(utctimestamp)
        sqlRow =  '{},'.format(utctimestamp) + data[time].dumpAsSql()
        sqlCmd = 'REPLACE INTO hourly VALUES ({})'.format(sqlRow)
        try:
            c.execute(sqlCmd)
        except sqlite3.OperationalError:
            print(sqlCmd)
            raise
    conn.commit()
    conn.close()

def load(city):
    dbname = city+"/data/weatherstats.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT * FROM hourly'
    ret = {}

    for row in c.execute(sqlCmd):
        datestamp = datetime.datetime.utcfromtimestamp(row[0])
        datestamp = datestamp.replace(tzinfo=datetime.timezone.utc)
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

def loadTimes(city):
    dbname = city+"/data/weatherstats.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT name FROM sqlite_master WHERE type="table"'
    for tableDesc in c.execute(sqlCmd):
        if 'hourly' in tableDesc:
            break
    else:
        #The 'hourly' table did not exist
        return set()

    sqlCmd = 'SELECT date FROM hourly'
    ret = set()

    for row in c.execute(sqlCmd):
        datestamp = datetime.datetime.utcfromtimestamp(row[0])
        datestamp = datestamp.replace(tzinfo=datetime.timezone.utc)
        ret.add(datestamp)
    return ret

def hourrange(start, end):
    v = start
    while v < end:
        yield v
        v += datetime.timedelta(hours=1)

def scan(city):
    mytimezone = stations.city[city].timezone
    utcTimes = loadTimes(city)
    utcNow = datetime.datetime.utcnow()
    utcNow = utcNow.replace(minute=0, second=0, microsecond=0,
                            tzinfo=datetime.timezone.utc)
    loadSuffixes = set()
    for utcTime in hourrange(
            utcNow-datetime.timedelta(days=3),
            utcNow+datetime.timedelta(hours=1)):
        if utcTime not in utcTimes:
            dayDelta = (utcNow - utcTime).days
            utcLoadTime = utcNow - datetime.timedelta(days=dayDelta)
            localLoadTime = utcLoadTime.astimezone(mytimezone)
            localLoadTimeStr = localLoadTime.strftime('date=%Y-%m-%d;time=%H:%M')
            #print(utcTime, ' MISSING', localLoadTimeStr)
            loadSuffixes.add(localLoadTimeStr)
    return enumerate(sorted(loadSuffixes))

if __name__ == '__main__':
    import argparse, stations
    parser = argparse.ArgumentParser(
        description='Import weatherstats data into a database.')
    parser.add_argument('--scan', help='Figure out how much data is missing',
                        action='store_true')
    parser.add_argument('--city', default='ottawa')
    args = parser.parse_args()
    if args.scan:
        print(tuple(scan(args.city)))
    else:
        data = parse(args.city)
        saveSql(data, args.city)
