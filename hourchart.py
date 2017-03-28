#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, sys, copy, fnmatch
import argparse, datetime
import stations

parser = argparse.ArgumentParser(
    description='Determine the last time a field has been this high/low.')
parser.add_argument('-f', help='Field')
parser.add_argument('--city', default='ottawa')
parser.add_argument('-d', help='Mask', nargs='*')

args = parser.parse_args()

field = args.f

data = hourly.load(args.city)
days = args.d

tz = stations.city[args.city].timezone

for d in days:
    dayStart = datetime.datetime.strptime(d, "%Y-%m-%d").date()
    print('---', dayStart)
    for utc in sorted(data.keys()):
        ltime = utc.astimezone(tz)
        if ltime.date() != dayStart:
            continue
        if utc in data:
            windchill = data[utc].windchill
            if windchill is not None:
                windchill = '{:.1f}'.format(windchill)
            humidex = data[utc].humidex
            if humidex is not None:
                humidex = '{:.1f}'.format(humidex)
            hourStr = str(ltime)
            temp = float(data[utc].TEMP)
            print('{hourStr} {temp:.1f} {windchill} {humidex}'.format(**locals()))
