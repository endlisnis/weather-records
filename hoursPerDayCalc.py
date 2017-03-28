#!/usr/bin/python3
# -*- coding: utf-8 -*-
import stations
import pytz
import datetime
import hourly
import sys

countPerDay = {}
for city in sorted(stations.city):
    print(city,file=sys.stderr)
    countPerDay[city] = {}
    tz = stations.city[city].timezone
    lstart = tz.localize(datetime.datetime(1953,1,1,0,0)).astimezone(pytz.utc)
    lend = tz.localize(datetime.datetime(2030,1,1,0,0)).astimezone(pytz.utc)
    for hour in hourly.hourrange(lstart,lend):
        lhour = hour.astimezone(tz)
        lday = lhour.date()
        countPerDay[city][lday] = countPerDay[city].get(lday, 0) + 1

    for lday in sorted(countPerDay[city].keys()):
        v = countPerDay[city][lday]
        if v == 24:
            del countPerDay[city][lday]

    for lday in sorted(countPerDay[city].keys()):
        v = countPerDay[city][lday]
        #print(lday, v)

print(repr(countPerDay))
