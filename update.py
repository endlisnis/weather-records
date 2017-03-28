#!/usr/bin/python3
# -*- coding: utf-8 -*-
import stations
import datetime
import random
import stations
import os
import updateCsv
import recentWeather

def mkdirExists(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def wgetVerify(city, url, local, verify=None):
    timeout = random.randint(8,12)
    if verify is not None:
        verify = '&& {verify}'.format(**locals())
    else:
        verify = ''
    print('for iteration in {{1..100}};'
          ' do'
          '  if [ $iteration -gt 1 ]; then'
          '   echo {city}#$iteration;'
          '  fi;'
          ' wget -q -T {timeout} -O {local} "{url}"'
          '  {verify}'
          '  && break;'
          ' done'.format(**locals()))

now = datetime.date.today()
yesterday = now-datetime.timedelta(1)
curMonth = datetime.date(now.year, now.month, 1)
nextMonth = datetime.date(now.year+curMonth.month//12, (now.month%12)+1, 1)

for city, info in stations.city.items():
    mkdirExists('{city}'.format(**locals()))
    mkdirExists('{city}/data'.format(**locals()))
    allStations = ( set(stations.city[city].dayStations.keys())
                    .union(stations.city[city].hourStations.keys()) )
    for station in allStations:
        mkdirExists("{city}/{station}".format(**locals()))


    if info.airportCode is not None:
        if info.skipMetar is False:
            print('./gatherMetarEc.py --days=1 --city {city}'.format(**locals()))
        print('./gatherSwob.py --gather --city {city}'.format(**locals()))
    wgetVerify(
        city,
        url='http://weather.gc.ca/rss/city/{info.label}_e.xml'.format(**locals()),
        local='{city}/environmentCanada.xml'.format(**locals()),
        verify=( 'python3 -c "from lxml import etree;'
                 ' etree.parse(open(\\"{city}/environmentCanada.xml\\", \\"r\\"))"'
                 .format(**locals())))
    wgetVerify(
        city,
        url='http://weather.gc.ca/city/pages/{info.label}_metric_e.html'.format(**locals()),
        local='{city}/environmentCanada.html'.format(**locals()))

    #weatherStatsPrefix = city
    #if info.weatherStatsSite != None:
    #    weatherStatsPrefix = info.weatherStatsSite
    #suffixes = tuple(recentWeather.scan(city))
    #fields = tuple(filter(
    #    lambda t: t not in info.skipOb,
    #    ('temperature', 'relative_humidity', 'dew_point', 'wind_speed', 'wind_gust_speed',
    #     'pressure_sea', 'visibility')) )
    #for field in fields:
    #    for fileSuffix, urlSuffix in suffixes:
    #        timeout = random.randint(8,12)
    #        print('for iteration in {{1..100}}; do'
    #              ' if [ $iteration -gt 1 ]; then'
    #              '  echo {city}#$iteration;'
    #              ' fi;'
    #              ' wget -q -t 1 -T {timeout} -O {city}/data/{field}-24hrs.{fileSuffix}.json "http://{weatherStatsPrefix}.weatherstats.ca/data/{field}-24hrs.json?{urlSuffix}" && break;'
    #              ' done'
    #              .format(**locals()))
    updateCsv.main(city)

    utcdate = (datetime.datetime.utcnow()
              - datetime.timedelta(minutes=15)).date()
    prov = info.label.split('-')[0]
    PROV = prov.upper()

    timeout = random.randint(8,12)
    localXmlFname = '{city}/data/today.xml.gzip'.format(**locals())
    print('for iteration in {{1..100}};'
          ' do'
          '  if [ $iteration -gt 1 ]; then'
          '   echo {city}#$iteration;'
          '  fi;'
          '  wget -q -T {timeout} --header="accept-encoding: gzip" -O {localXmlFname}'
          '   "http://dd.weather.gc.ca/observations/xml/{PROV}/today/today_{prov}_{utcdate.year}{utcdate.month:02}{utcdate.day:02}_e.xml"'
          '  && python3 -c "import gzip; from lxml import etree; etree.parse(gzip.open(\\"{localXmlFname}\\", \\"rt\\"))"'
          '  && break;'
          ' done;'.format(**locals()))
