#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, sys, copy, fnmatch
import argparse, datetime
import stations

from pytz import timezone
import pytz

parser = argparse.ArgumentParser(
    description='Determine the last time a field has been this high/low.')
parser.add_argument('--temp', help='Show temperature', action='store_true', default=False)
parser.add_argument('--windchill', help='Show windchill', action='store_true', default=False)
parser.add_argument('--wind', help='Show wind', action='store_true', default=False)
parser.add_argument('--weather', help='Show weather', action='store_true', default=False)
parser.add_argument('--city', default='ottawa')

args = parser.parse_args()

data = hourly.load(args.city)
#data = hourly.load(args.city)

mytimezone = stations.city[args.city].timezone

lastDay = None
lastDayVal = []
for h in sorted(data.keys()):
    l = h.astimezone(mytimezone)
    print(l, end='')
    if args.temp:
        print(' ', data[h].TEMP, end='')
    if args.wind:
        print(' ', data[h].WIND_SPD, end='')
    if args.windchill:
        print(' ', data[h].windchill, end='')
    if args.weather:
        print(' ', data[h].WEATHER, end='')
    print()
