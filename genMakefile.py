#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, datetime, time, os
from collections import namedtuple
import stations, genHourlyUrls, weatherstats

now = datetime.datetime.now().date()
nowM = now.year * 12 + now.month - 1

city = sys.argv[1]

MINYEAR = tuple(stations.city[city].dayStations.values())[-1][0]
MAXYEAR = now.year

def monthString(month):
    return '%04d-%02d' % (int(month/12), (month % 12) + 1)

def refreshMonthStation(month, city, station):
    threeDaysAgoDT = now - datetime.timedelta(3)
    tdam = threeDaysAgoDT.year * 12 + threeDaysAgoDT.month - 1
    if month >= tdam:
        print("# month=%d future" % (month, ))
        return True

    mstr=monthString(month)
    fname = "{city}/{station}/{mstr}.mcsv.bz2".format(**locals())
    if not os.path.exists(fname):
        print("# fname=%s doesn't exist" % (fname, ))
        return True
    mdays = (time.time() - os.stat(fname).st_mtime) // 3600 // 24
    print("# fname=%s mdays=%d" % (fname, mdays))
    dy = month//12
    dm = month%12 + 1
    if month >= nowM - 12:
        return mdays > 7
    if month >= nowM - 12*10:
        return mdays > 28
    return mdays > 365

def refreshMonthCity(month):
    year = month//12
    ret = []
    for station in stations.city[city].hourStations.keys():
        if ( year >= stations.city[city].hourStations[station][0]
             and year <= stations.city[city].hourStations[station][1]
             and refreshMonthStation(month, city, station) ):
            ret.append(station)
    return ret


def refreshYearStation(year, city, station):
    threeDaysAgo = now - datetime.timedelta(3)
    if year == now.year or year == threeDaysAgo.year:
        return True
    fname = "{city}/{station}/{year}.csv.bz2".format(**locals())
    if not os.path.exists(fname):
        print("# fname=%s DOES_NOT_EXIST" % (fname, ))
        return True
    days = (time.time() - os.stat(fname).st_mtime) // 3600 // 24
    print("# fname=%s days=%d" % (fname, days))
    if year == now.year-1:
        return days > 30
    return days > 365

def refreshYearCity(year):
    ret = []
    for station in stations.city[city].dayStations.keys():
        if ( year >= stations.city[city].dayStations[station][0]
             and year <= stations.city[city].dayStations[station][1]
             and refreshYearStation(year, city, station) ):
            ret.append(station)
    return ret

years = {}
months = []
monthYears = set()

allStations = ( set(stations.city[city].dayStations.keys())
                .union(stations.city[city].hourStations.keys()) )

for station in allStations:
    print("{city}/{station}:".format(**locals()))
    print("\tmkdir -p $@")
    print

thisYear = datetime.date.today().year

for year in range(thisYear-1, thisYear+2):
    print("{city}/data/{year}.dailyextra-csv.bz2".format(city=city, year=year), end=' ')
print(':  city:={city}'.format(city=city))

for year in range(thisYear-1, thisYear+2):
    print("{city}/data/{year}.dailyextra-csv.bz2".format(**locals()), end=' ')
curMonth = now.month
lastMonth = now.month - 1 if now.month > 1 else 12
print("{city}/data/{year}-{curMonth}.mcsv.touch".format(**locals()), end=' ')
print("{city}/data/{year}-{lastMonth}.mcsv.touch".format(**locals()), end=' ')

print(':  {city}/environmentCanada.html'
      ' {city}/data/metar.db.touch'
      .format(city=city))

if len(stations.city[city].hourStations) > 0:
    MINMONTH = tuple(stations.city[city].hourStations.values())[-1][0] * 12
    MAXMONTH = nowM
    for month in range(MINMONTH, MAXMONTH+1):
        stationsToRefresh = refreshMonthCity(month)
        dy = month//12
        dm = month%12 + 1
        months.append(monthString(month))
        monthYears.add(dy)
        mstr=monthString(month)
        for station in stations.city[city].hourStations:
            if ( dy < stations.city[city].hourStations[station][0]
                 or dy > stations.city[city].hourStations[station][1]):
                continue
            target = "{city}/{station}/{mstr}.mcsv.bz2".format(**locals())
            touchTarget = "{city}/data/{mstr}.mcsv.touch".format(**locals())
            dailyExtraTarget = "{city}/data/{dy}.dailyextra-csv.bz2".format(**locals())
            print("{target}: | {city}/{station}".format(**locals()))
            print("{target}: YEAR:={dy}".format(**locals()))
            print("{target}: MONTH:={dm}".format(**locals()))
            print("{target}: STATION_ID:={station}".format(**locals()))
            print("{target}: city:={city}".format(**locals()))
            print("{touchTarget}: city:={city}".format(**locals()))
            print("{touchTarget}: YEAR:={dy}".format(**locals()))
            print("{touchTarget}: MONTH:={dm}".format(**locals()))
            print("{touchTarget}: {target}".format(**locals()))
            print("{dailyExtraTarget}: {touchTarget}".format(**locals()))
            print("all: {dailyExtraTarget}".format(**locals()))

for year in range(MINYEAR, MAXYEAR+1):
    stationsToRefresh = refreshYearCity(year)
    for station in stationsToRefresh:
        target = "{city}/{station}/{year}.csv.bz2".format(**locals())
        print("{target}: | {city}/{station}".format(**locals()))
        print("{target}: YEAR:={year}".format(**locals()))
        print("{target}: STATION_ID:={station}".format(**locals()))
        print("{target}: city:={city}".format(**locals()))
        print("{city}/data/all.fcsv.bz2: {city}/{station}/{year}.csv.bz2".format(**locals()))

print('YEARS:=%s' % ' '.join(map(str, sorted(years.keys()))))
print('MONTHS:=%s' % ' '.join(months))
print('MONTH_YEARS:=%s' % ' '.join([str(a) for a in monthYears]))
print('city_label:=%s' % stations.city[city].label)
