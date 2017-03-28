#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import decimal
import metarParse
import pathlib
import pprint
import re
import requests
import sqlite3
import stations

from lxml import etree
from hourDataTuple import HourDataTuple
from daydata import DayData
from namedtuplewithdefaults import namedtuple_with_defaults
from collections import defaultdict

D = decimal.Decimal

#import random
#def testDA0():
#    da = {}
#    for i in range(2400):
#        v = random.randint(0,23)
#        cv = da.get(v, None)
#        if cv is None:
#            cv = [None]*24
#            da[v] = cv
#        cv[v] = i

#def testDA1():
#    da = defaultdict(lambda: [None]*24)
#    for i in range(2400):
#        v = random.randint(0,23)
#        da[v][v] = i
#timeit.timeit('testDA0()', globals=globals())

def synopticDay(currTimeUtc):
    if currTimeUtc.hour < 6:
        return (currTimeUtc-dt.timedelta(days=1)).date()
    return currTimeUtc.date()

def synopticDayPastHour(currTimeUtc):
    if currTimeUtc.hour*60 + currTimeUtc.minute <= 6*60:
        return (currTimeUtc-dt.timedelta(days=1)).date()
    return currTimeUtc.date()

def linksWithName(dirListHtml):
    links = []
    for match in re.findall('<a href="(.*?)">\\1', dirListHtml):
        links.append(match)
    return links

class Db():
    def __init__(self, city):
        self.dbname = city+"/data/metar.db"
        self.conn = sqlite3.connect(self.dbname)

    def createTable(self):
        c = self.conn.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS swob (fname text PRIMARY KEY, swob text)')
        self.conn.commit()

    def loadRawKeys(self):
        c = self.conn.cursor()
        sqlCmd = 'SELECT name FROM sqlite_master WHERE type="table"'
        for tableDesc in c.execute(sqlCmd):
            if 'swob' in tableDesc:
                break
        else:
            return set()
        sqlCmd = 'SELECT fname FROM swob'
        ret = set()

        for row in c.execute(sqlCmd):
            ret.add(row[0])
        return ret

    def load(self):
        c = self.conn.cursor()
        sqlCmd = 'SELECT name FROM sqlite_master WHERE type="table"'
        for tableDesc in c.execute(sqlCmd):
            if 'swob' in tableDesc:
                break
        else:
            return {}
        sqlCmd = 'SELECT * FROM swob'
        ret = {}

        for fname, swobXml in c.execute(sqlCmd):
            ret[fname] = swobXml
        return ret

    def showAndSave(self, fname, swobXml):
        print(fname)
        sqlCmd = 'REPLACE INTO swob VALUES (?,?)'
        c = self.conn.cursor()
        try:
            c.execute(sqlCmd, (fname, swobXml))
        except sqlite3.OperationalError:
            print(sqlCmd)
            raise
        self.conn.commit()
        pathlib.Path(self.dbname+'.touch').touch()


def gather(city):
    airportCode = stations.city[city].airportCode
    if airportCode is None:
        return

    db = Db(city)
    db.createTable()

    session = requests.Session()

    dayList = []

    response = session.get('http://dd.weather.gc.ca/observations/swob-ml/')
    for dirname in linksWithName(response.text):
        if dirname[0] != '2':
            #print('Skipping', dirname)
            continue
        #print(dirname)
        dayyear = int(dirname[0:4])
        daymonth = int(dirname[4:6])
        dayday = int(dirname[6:8])
        #print(dayyear, daymonth, dayday)
        daydate = dt.date(dayyear, daymonth, dayday)
        dayList.append(daydate)

    rawKeys = db.loadRawKeys()
    for date in dayList:
        url = ( 'http://dd.weather.gc.ca/observations/swob-ml'
                '/{date.year}{date.month:02}{date.day:02}'
                '/C{airportCode}'
                .format(**locals()))
        response = session.get(url)
        if response.status_code == 404: # File not found
            print("Skipping missing day {date}".format(**locals()))
            continue
        for hourlyEntryFname in linksWithName(response.text):
            if hourlyEntryFname in rawKeys:
                continue
            url = ( 'http://dd.weather.gc.ca/observations/swob-ml'
                    '/{date.year}{date.month:02}{date.day:02}'
                    '/C{airportCode}/{hourlyEntryFname}'
                    .format(**locals()))
            response = session.get(url)
            if response.status_code == 404: # File not found
                print("Skipping missing entry {date}:{url}".format(**locals()))
                continue

            xmlText = response.content
            db.showAndSave(hourlyEntryFname, xmlText.decode())

def parse(city):
    if stations.city[city].airportCode is None:
        return
    db = Db(city)
    swobData = db.load()
    lastHourObs = {'time': None,
                   'cc': None}
    for fname in sorted(swobData.keys()):
        swobXml = swobData[fname]
        root = etree.XML(swobXml.encode())
        ns = {
            'om': 'http://www.opengis.net/om/1.0',
            'po': 'http://dms.ec.gc.ca/schema/point-observation/2.0',
        }

        correctionCounter = root.xpath(
            '/om:ObservationCollection/om:member/om:Observation'
            '/om:metadata/po:set/po:identification-elements'
            '/po:element[@name="cor"]/@value',
            namespaces=ns)
        if len(correctionCounter) == 0:
            correctionCounter = 0
        else:
            correctionCounter = ord(correctionCounter[0][2]) - ord('a') + 1
        timestampstr, = root.xpath(
            '/om:ObservationCollection/om:member/om:Observation'
            '/om:metadata/po:set/po:identification-elements'
            '/po:element[@name="date_tm"]/@value',
            namespaces=ns)
        #if city == 'fredericton' and timestampstr == "2017-03-15T12:00:00.000Z":
        #    import pudb; pu.db
        timestamp = ( dt.datetime.strptime(timestampstr, '%Y-%m-%dT%H:%M:%S.%fZ')
                      .replace(tzinfo=dt.timezone.utc) )

        observations = {
            'time': timestamp,
            'cc': correctionCounter,
            'air_temp' : None,
            'dwpt_temp' : None,
            'rel_hum' : None,
            'max_air_temp_pst1hr' : None,
            'min_air_temp_pst1hr' : None,
            'max_air_temp_pst6hrs' : None,
            'min_air_temp_pst6hrs' : None,
            'max_air_temp_pst24hrs' : None,
            'min_air_temp_pst24hrs' : None,
            'vis' : None,
            'avg_wnd_spd_10m_mt58-60' : None,
            'pcpn_amt_pst6hrs' : None,
            'snw_dpth' : None,
            'rmk' : None,
        }
        for ob in observations.keys():
            obQaXpath = ( '/om:ObservationCollection/om:member/om:Observation'
                          '/om:result/po:elements/po:element[@name="{}"]'
                          '/po:qualifier/@value'
                           .format(ob) )
            obQa = root.xpath(obQaXpath, namespaces=ns)
            assert(len(obQa) <= 1)
            obValXpath = ( '/om:ObservationCollection/om:member/om:Observation'
                           '/om:result/po:elements/po:element[@name="{}"]/@value'
                           .format(ob) )
            obVal = root.xpath(obValXpath, namespaces=ns)
            if len(obQa) == 1:
                obQa = int(obQa[0])
                if obQa not in (-10,-1,0,10,100):
                    print(ob, obQa, obVal, observations)
                    assert(False)
                if int(obQa) < 0:
                    #The QA value was not 100. Skip.
                    continue
            assert(len(obVal) <= 1)
            if len(obVal) == 1:
                obVal = obVal[0]
                if obVal != 'MSNG':
                    observations[ob] = obVal
        if lastHourObs['time'] != observations['time']:
            if lastHourObs['time'] is not None:
                yield lastHourObs
            lastHourObs = observations
        elif observations['cc'] > lastHourObs['cc']:
            lastHourObs = observations
    yield lastHourObs


def parseHourly(city):
    ret = {}
    for observations in parse(city):
        if observations['time'].minute == 0:
            intFromFloat = lambda t: int(D(t).quantize(D(0), decimal.ROUND_HALF_UP))
            hourFieldByObservation = {
                'air_temp' : ('TEMP', D),
                'dwpt_temp' : ('DEW_POINT_TEMP', D),
                'rel_hum' : ('REL_HUM', int),
                'vis' : ('VISIBILITY', D),
                'avg_wnd_spd_10m_mt58-60' : ('WIND_SPD', intFromFloat),
            }

            v = HourDataTuple()
            for ob, t in hourFieldByObservation.items():
                hourFieldName, cast = t
                if observations[ob] is not None:
                    #print(hourFieldName)
                    v = v._replace(**{hourFieldName: cast(observations[ob]),
                                      hourFieldName+'_FLAG': 'S',
                    })
            ret[observations['time']] = v
    return ret

ValAndHour = namedtuple_with_defaults('ValAndHour', ['val', 'hour'])

def parseDaily(city):
    ltimezone = stations.city[city].timezone
    ret = defaultdict(dict)
    maxInterHour = defaultdict(lambda: [None]*24)
    minInterHour = defaultdict(lambda: [None]*24)
    precipByDay = defaultdict(D)
    for observations in parse(city):
        utctime = observations['time']
        if utctime.minute != 0:
            continue
        day = synopticDay(utctime)
        dayPastHour = synopticDayPastHour(utctime)
        l = utctime.astimezone(ltimezone)
        if observations['max_air_temp_pst1hr'] is not None:
            currVal = D(observations['max_air_temp_pst1hr'])
            maxInterHour[dayPastHour][l.hour] = currVal
        if observations['min_air_temp_pst1hr'] is not None:
            currVal = D(observations['min_air_temp_pst1hr'])
            minInterHour[dayPastHour][l.hour] = currVal
        if ( utctime.hour == 12
             and utctime.minute == 0
             and observations['snw_dpth'] is not None
        ):
            ret[day] = {
                'SNOW_ON_GRND_CM': int(observations['snw_dpth']),
                'SNOW_ON_GRND_FLAG': 'S' + str(l.hour) }
        if observations['pcpn_amt_pst6hrs'] is not None and utctime.hour % 6 == 0:
            sd = synopticDayPastHour(utctime)
            #if sd == dt.date(2017,3,15):
            #    import pudb; pu.db
            precip = D(observations['pcpn_amt_pst6hrs'])
            precipByDay[sd] += precip
    for day, info in maxInterHour.items():
        nz = tuple(filter(lambda t: t is not None, info))
        m = max(nz)
        mi = info.index(m)
        flags = 'S' + str(mi)
        if len(nz) != 24: #Incomplete
            flags += '+I'
        ret[day].update({'MAX_TEMP': m,
                         'MAX_TEMP_FLAG': flags})
    for day, info in minInterHour.items():
        nz = tuple(filter(lambda t: t is not None, info))
        m = min(nz)
        mi = info.index(m)
        flags = 'S' + str(mi)
        if len(nz) != 24: #Incomplete
            flags += '+I'
        ret[day].update({'MIN_TEMP': m,
                         'MIN_TEMP_FLAG': flags})
    for day, info in precipByDay.items():
        ret[day].update({'TOTAL_PRECIP_MM': info,
                         'TOTAL_PRECIP_FLAG': 'S'})

    for k,v in tuple(ret.items()):
        ret[k] = DayData(**v)
    return ret

def parseDepth(city):
    ltimezone = stations.city[city].timezone
    for observations in parse(city):
        if observations['snw_dpth'] is not None:
            utctime = observations['time']
            l = utctime.astimezone(ltimezone)
            print( l, observations['snw_dpth'], 'cm')

def parseSnow(city):
    ltimezone = stations.city[city].timezone
    for observations in parse(city):
        rmk = observations['rmk']
        if rmk is None:
            continue
        snow = metarParse.parseMetarForSnow(rmk)
        if snow is None:
            continue
        utctime = observations['time']
        l = utctime.astimezone(ltimezone)
        print( l, snow, 'cm')

def parseRain(city):
    ltimezone = stations.city[city].timezone
    precipByDay = defaultdict(D)
    for observations in parse(city):
        utctime = observations['time']
        if observations['pcpn_amt_pst6hrs'] is not None and utctime.hour % 6 == 0:
            sd = synopticDayPastHour(utctime)
            l = utctime.astimezone(ltimezone)
            precip = D(observations['pcpn_amt_pst6hrs'])
            precipByDay[sd] += precip
            print( l, precip, 'mm', observations['cc'])
    for day, precip in sorted(precipByDay.items()):
        print(day, precip, 'mm')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, save and load metar data.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--gather', action='store_true')
    parser.add_argument('--daily', action='store_true')
    parser.add_argument('--hourly', action='store_true')
    parser.add_argument('--snow-depth', action='store_true')
    parser.add_argument('--snow', action='store_true')
    parser.add_argument('--rain', action='store_true')
    args = parser.parse_args()

    if args.gather:
        gather(args.city)

    if args.daily:
        pprint.PrettyPrinter().pprint(parseDaily(args.city))

    if args.hourly:
        pprint.PrettyPrinter().pprint(parseHourly(args.city))

    if args.snow_depth:
        parseDepth(args.city)

    if args.snow:
        parseSnow(args.city)

    if args.rain:
        parseRain(args.city)
