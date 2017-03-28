#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, sys, copy, fnmatch
import argparse, datetime
import stations
import daily

from pytz import timezone
import pytz

parser = argparse.ArgumentParser(
    description='Determine the last time a field has been this high/low.')
parser.add_argument('--temp', help='Show temperature', action='store_true', default=False)
parser.add_argument('--wind', help='Show wind', action='store_true', default=False)
parser.add_argument('--weather', help='Show weather', action='store_true', default=False)
parser.add_argument('--city', default='ottawa')

args = parser.parse_args()

data = hourly.load(args.city)
daydata = daily.load(args.city)
#data = hourly.load(args.city)

mytimezone = stations.city[args.city].timezone

lastH = None
lastHVal = None
for h in sorted(data.keys()):
    l = h.astimezone(mytimezone)
    if lastH is not None and l.utcoffset().total_seconds() != lastH.utcoffset().total_seconds():
        #print(lastH, lastHVal[0], lastHVal[1], l, data[h].TEMP, data[h].windchill)
        print(l.date(), daydata[l.date()].MIN_WINDCHILL)
    lastH = l
    lastHVal = (data[h].TEMP, data[h].windchill)
    #print(l.utcoffset().total_seconds())
