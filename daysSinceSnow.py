#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather, sys

limit = float(sys.argv[1])

#field = weather.daily.TOTAL_RAIN_MM
#field = weather.daily.MAX_TEMP
field = weather.daily.MIN_TEMP
#field = weather.daily.SPD_OF_MAX_GUST_KPH
#field = weather.daily.MAX_HUMIDEX

def isSummer(date):
    return ( date.month == 7 
             or date.month == 8
             or (date.month == 6 and date.day >= 22)
             or (date.month == 9 and date.day < 20) );

data = weather.daily.load('ottawa')

dayBySnow = {}

for date in reversed(sorted(data.keys())):
    if not isSummer(date):
        continue
    val = data[date][field.index]
    if len(val):
        val = int(round(float(val)*10))
        if val <= limit*10:
            print date, '%d.%d' % (val/10, val%10)
