#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, datetime, time, os
from collections import namedtuple
import stations, genHourlyUrls, weatherstats
import random

now = datetime.datetime.now().date()
nowM = now.year * 12 + now.month - 1

MINMONTH = None
MAXMONTH = None
MINYEAR = None
MAXYEAR = None

def monthString(month):
    return '%04d-%02d' % (int(month/12), (month % 12) + 1)

def refreshMonthStation(month, city, station):
    threeDaysAgoDT = now - datetime.timedelta(3)
    tdam = threeDaysAgoDT.year * 12 + threeDaysAgoDT.month - 1
    if month >= tdam:
        #print("# month=%d future" % (month, ))
        return True

    mstr=monthString(month)
    fname = "{city}/{station}/{mstr}.mcsv.bz2".format(**locals())
    if not os.path.exists(fname):
        #print("# fname=%s doesn't exist" % (fname, ))
        return True
    mdays = (time.time() - os.stat(fname).st_mtime) // 3600 // 24
    #print("# fname=%s mdays=%d" % (fname, mdays))
    dy = month//12
    dm = month%12 + 1
    if month >= nowM - 12:
        return mdays > 7
    if month >= nowM - 12*10:
        return mdays > 28
    return mdays > 365

def refreshMonthCity(city, month):
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
    #print("# fname=%s days=%d" % (fname, days))
    if year == now.year-1:
        return days > 30
    return days > 365

def refreshYearCity(city, year):
    ret = []
    for station in stations.city[city].dayStations.keys():
        if ( year >= stations.city[city].dayStations[station][0]
             and year <= stations.city[city].dayStations[station][1]
             and refreshYearStation(year, city, station) ):
            ret.append(station)
    return ret

def main(city):
    global MINMONTH
    global MAXMONTH
    global MINYEAR
    global MAXYEAR
    if len(stations.city[city].hourStations) > 0:
        MINMONTH = tuple(stations.city[city].hourStations.values())[-1][0] * 12
        MAXMONTH = nowM
        for month in range(MINMONTH, MAXMONTH+1):
            stationsToRefresh = refreshMonthCity(city, month)
            dy = month//12
            dm = month%12 + 1
            mstr=monthString(month)
            for station in stationsToRefresh:
                timeout = random.randint(8,12)
                target = '{city}/{station}/{dy}-{dm:02}.mcsv'.format(**locals())
                print('for iteration in {{1..100}};'
                      ' do'
                      '  if [ $iteration -gt 1 ]; then'
                      '   echo {city}#$iteration;'
                      '  fi;'
                      '  wget -q -T {timeout} -O {target} \'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station}&Year={dy}&Month={dm:02}&Day=1&timeframe=1\' && break;'
                      ' done;'
                      ' if grep -e "The database is currently unavailable" {target}; then'
                      ' true;'
                      ' else'
                      '  bzdiff -N {target}.bz2 | sed s/^/{city}\|/;'
                      '  bzip2 -f {target};'
                      '  rm -f {city}/data/cache/{dy}.py;'
                      ' fi;'
                      .format(**locals()))

    MINYEAR = tuple(stations.city[city].dayStations.values())[-1][0]
    MAXYEAR = now.year
    for year in range(MINYEAR, MAXYEAR+1):
        stationsToRefresh = refreshYearCity(city, year)
        for station in stationsToRefresh:
            timeout = random.randint(8,12)
            target = '{city}/{station}/{year}.csv'.format(**locals())
            print("for iteration in {{1..100}};"
                  " do"
                  "  if [ $iteration -gt 1 ]; then"
                  "   echo {city}#$iteration;"
                  "  fi;"
                  "  wget -q -T {timeout} -O {target} 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station}&Year={year}&Month=1&Day=1&timeframe=2' && break;"
                  " done;"
                  #"if [ -r {target}.patch ]; then"
                  #" patch < {target}.patch {target};"
                  #"fi;"
                  "bzdiff -N {target}.bz2 | sed s/^/{city}\|/;"
                  "bzip2 -f {target};"
                  "rm -f {city}/data/cache/{year}.py".format(**locals()))

if __name__=='__main__':
    import sys
    city = 'ottawa'
    if len(sys.argv) > 1:
        city = sys.argv[1]
    main(city)
