#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, time, daily, datetime
data = daily.load('ottawa')

days = int(sys.argv[1])

maxloss = [1900,1,1,0]

for date in reversed(sorted(data.keys())):
    v1 = None
    yesterday = date-datetime.timedelta(days)
    try:
        v1 = data[yesterday].SNOW_ON_GRND_CM
    except KeyError:
        pass
    v2 = data[date].SNOW_ON_GRND_CM
    #print v1, v2
    if v1 is not None and v2 is not None:
        diff = v1 - v2

        if diff >= 20: #qmaxloss[3]:
            print("(%s)%.1f (%d - %d)," % (date, diff, v1, v2))
            maxloss = [date.year, date.month, date.day, diff]
