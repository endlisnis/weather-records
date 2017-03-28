#!/usr/bin/python3
import argparse
import datetime as dt
import liststations
from metar import Metar
import pygal
import re
import sqlite3
import stations
import tabulate
import termcolor
import requests

from html.parser import HTMLParser
from collections import namedtuple, defaultdict

session = requests.Session()
extraMetarCities = {
    'gagetown': 'CYCX',
    'moncton': 'CYQM',
    'gatineau': 'CYND',
    'Sault Ste. Marie': 'CYAM',
    'Geraldton': 'CYGQ',
    'Buttonville': 'CYKZ',
    'Chapleau': 'CYLD',
    'Pickle Lake': 'CYPL',
    'Windsor': 'CYQG',
    'Kenora': 'CYQK',
    'Red Lake': 'CYRL',
    'Sudbury': 'CYSB',
    'St. Catharines/Niagara': 'CYSN',
    'Marathon': 'CYSP',
    'Trenton': 'CYTR',
    'Timmins': 'CYTS',
    'Wiarton': 'CYVV',
    'Sioux Lookout': 'CYXL',
    'Wawa': 'CYXZ',
    'Kapuskasing': 'CYYU',
}

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.data = []
    def handle_starttag(self, tag, attrs):
        #attrsD = dict(attrs)
        #if tag == 'tr' and 'title' in attrsD:
        #    self.data.append(attrsD['title'])
        #    tokens = attrsD['title'].split()
        #    print("Encountered a title:", tokens)
        pass
    def handle_endtag(self, tag):
        pass
        #print("Encountered an end tag :", tag)
    def handle_data(self, data):
        d = data.strip().replace('\n  ', ' ')
        if len(d) > 0 and d[0] == 'C':
            #print("Encountered some data  :", d)
            self.data.append(d)
        pass

def parseTime(city, metarTimeString):
    utcDay = int(metarTimeString[0:2], 10)
    utcHour = int(metarTimeString[2:4], 10)
    utcMin = int(metarTimeString[4:6], 10)
    utcNow = dt.datetime.utcnow()
    #import pudb; pu.db
    if utcDay <= utcNow.day:
        metarDatestamp = dt.datetime(
            utcNow.year, utcNow.month, utcDay, utcHour, utcMin,
            tzinfo=dt.timezone.utc)
    else:
        metarDatestamp = dt.datetime(
            utcNow.year if utcNow.month > 1 else utcNow.year-1,
            utcNow.month-1 if utcNow.month > 1 else 12,
            utcDay, utcHour, utcMin,
            tzinfo=dt.timezone.utc)
    return metarDatestamp

def synopticPeriod(date):
    minutes = date.hour * 60 + date.minute
    sp = (minutes - 1) // (6*60)
    if sp < 1:
        return (date-dt.timedelta(days=1)).date(), sp+3
    return date.date(), sp-1

def loadNoaa(city):
    path = ( 'https://aviationweather.gov/metar/data?ids={}&format=raw&hours=250&taf=off'
             '&layout=off&date=0'.format(extraMetarCities[city]) )
    response = session.get(path)
    assert response.status_code == 200
    a = response.text
    parser = MyHTMLParser()
    parser.feed(a)
    data = {}
    for m in parser.data:
        tokens = m.split()
        h = parseTime(city, tokens[1])
        data[h] = m
    return data

def save(city, data):
    dbname = city+"/data/metar.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS metar (date int PRIMARY KEY, metar text)')
    for time, metar in data.items():
        utctimestamp = time.replace(tzinfo=dt.timezone.utc).timestamp()
        utctimestamp = int(utctimestamp)
        sqlRow =  '{utctimestamp},"{metar}"'.format(**locals())
        sqlCmd = 'REPLACE INTO metar VALUES ({})'.format(sqlRow)
        try:
            c.execute(sqlCmd)
        except sqlite3.OperationalError:
            print(sqlCmd)
            raise
    conn.commit()
    conn.close()

def score(val):
    if val is None:
        return -1
    m = re.match('.* CC(.)', val)
    if m is None:
        return 0
    return ord(m.groups()[0]) - ord('A') + 1

def best(one, two):
    s1 = score(one)
    s2 = score(two)
    if s1 < s2:
        # The existing metar is the newest correction, skip this older one
        return two
    elif s1 > s2:
        return one
    elif s1 == s2:
        return one
    else:
        # Correction numbers are the same and yet data is different?
        print(one, two)
        assert(False)

def merge(data0, data1):
    ret = data0.copy()
    for key, val1 in data1.items():
        val0 = data0.get(key, None)
        if val0 is not None and val0 != val1:
            bval = best(val0, val1)
            ret[key] = bval
    return ret

def load(city, sinceWhen=None, rawKeys=False):
    if stations.city[city].dayStations is None:
        return loadNoaa(city)
    dbname = city+"/data/metar.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT name FROM sqlite_master WHERE type="table"'
    for tableDesc in c.execute(sqlCmd):
        if 'metar' in tableDesc:
            break
    else:
        return {}
    sqlCmd = 'SELECT * FROM metar'
    if sinceWhen is not None:
        sqlCmd = 'SELECT * FROM metar WHERE date >= {sinceWhen}'.format(**locals())
    ret = {}

    try:
        for row in c.execute(sqlCmd):
            if rawKeys is True:
                datestamp = row[0]
            else:
                datestamp = dt.datetime.fromtimestamp(row[0], dt.timezone.utc)
            ret[datestamp] = row[1]
    except sqlite3.OperationalError:
        print(sqlCmd)
        raise
    return ret

def genHourlyWeather(city):
    mytimezone = stations.city[city].timezone
    for time, metarStr in sorted(load(city).items()):
        l = time.astimezone(mytimezone)
        m = Metar.Metar(metarStr, year=time.year, month=time.month)
        obs = m.present_weather()
        yield time, obs
        #if 'freezing' in obs:
        #    print(l, obs.replace('freezing', termcolor.colored('freezing', 'red')))

def loadRawKeys(city):
    dbname = city+"/data/metar.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlCmd = 'SELECT name FROM sqlite_master WHERE type="table"'
    for tableDesc in c.execute(sqlCmd):
        if 'metar' in tableDesc:
            break
    else:
        return set()
    sqlCmd = 'SELECT date FROM metar'
    ret = set()

    for row in c.execute(sqlCmd):
        ret.add(row[0])
    return ret

SnowAndHourly = namedtuple('SnowAndHourly', [ 'snow', 'snowByHour'] )
SnowAndHour = namedtuple('SnowAndHourly', [ 'snow', 'hour'] )

def parseMetarForSnow(metarText):
    m = re.search('/S[0-9O][0-9]/', metarText)
    #if '/S' in metar and m is None:
    #    print(repr(metar))
    #    assert(False)
    if m != None:
        tok = m.group()
        snow = tok[2:4].replace('O','0') #Humans can't type
        try:
            snow = int(snow)
        except ValueError:
            print(time, metar)
            if tok == '/SOG1/': # I have no idea ... skip
                return None
            raise
        return snow

def printSnowHours(city):
    data = load(city)
    mytimezone = stations.city[city].timezone
    for time, metar in sorted(data.items()):
        l = time.astimezone(mytimezone)
        snow = parseMetarForSnow(metar)
        if snow is None:
            continue
        print(l, snow, 'cm')


def loadSnowWithHours(city):
    data = load(city)
    snowPerSP = defaultdict(dict)
    cumulativeSnowByHour = defaultdict(dict)
    mytimezone = stations.city[city].timezone
    for time, metar in sorted(data.items()):
        synopticDay, sp = synopticPeriod(time)
        l = time.astimezone(mytimezone)
        snow = parseMetarForSnow(metar)
        if snow is not None:
            k = synopticDay, sp
            snowPerSP[synopticDay][sp] = snow
            cumulativeSnowByHour[synopticDay][l] = 0
            for synopticPeriodIndex, snowPerSynopticPeriod in snowPerSP[synopticDay].items():
                cumulativeSnowByHour[synopticDay][l] += snowPerSynopticPeriod
        #print(l, metar)
    snowPerDay = {}
    for spDay, snowByHour in cumulativeSnowByHour.items():
        maxHour = max(snowByHour.keys())
        totalSnow = snowByHour[maxHour]
        snowPerDay[spDay] = SnowAndHourly(totalSnow, snowByHour)
    return snowPerDay

def loadSnowWithHour(city):
    snowPerDay = loadSnowWithHours(city)
    ret = {}
    for spDay, snowInfo in snowPerDay.items():
        ret[spDay] = SnowAndHour(snowInfo.snow, max(snowInfo.snowByHour.keys()).hour)
    return ret

def loadSnow(city):
    snowWithHours = loadSnowWithHours(city)
    snow = {}
    for key, val in snowWithHours.items():
        snow[key] = val.snow
    return snow


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, save and load metar data.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--display', action='store_true')
    parser.add_argument('--hourly', action='store_true')
    parser.add_argument('--display-snow-hours', action='store_true')
    parser.add_argument('--today-table', action='store_true')
    parser.add_argument('--today')
    parser.add_argument('--days', default=1, type=int)
    args = parser.parse_args()

    if ( args.display is False
         and args.today_table is False
    ):
        #pdata = parse(args.city)
        #ldata = load(args.city)
        #data = merge(pdata, ldata)
        #save(args.city, data)
        pass
    if args.display_snow_hours:
        printSnowHours(args.city)
    if args.hourly is True:
        loadHourly(args.city)
    if args.display is True:
        snowPerDay = loadSnowWithHour(args.city)
        for day, snow in sorted(snowPerDay.items()):
            snowAmount, snowHour = snow
            print('{day}: {snowAmount}cm @ {snowHour}h'.format(**locals()))
    if args.today_table is True:
        rows = []
        today = dt.date.today()
        if type(args.today) is str:
            today = dt.date(*map(int, args.today.split('-')))
        for city in sorted(liststations.getMetarSnowCities()):
            snowPerDay = loadSnowWithHour(city)
            if args.days > 1:
                snowAmount = 0
                for daysAgo in range(args.days):
                    thisDay = today - dt.timedelta(days=daysAgo)
                    if thisDay in snowPerDay:
                        snowAmount += snowPerDay[thisDay][0]
                if snowAmount > 0:
                    rows.append((city, '{snowAmount}cm'.format(**locals())))
            elif today in snowPerDay:
                snowAmount, snowHour = snowPerDay[today]
                rows.append((city, '{snowAmount}cm @ {snowHour}h'.format(**locals())))
        print(tabulate.tabulate(rows,
                                headers=('City', 'Snow'),
                                tablefmt="fancy_grid"))
