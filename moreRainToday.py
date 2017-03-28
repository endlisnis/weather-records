#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import daily
import datetime
import stations
import sys

parser = argparse.ArgumentParser(description='Determine how many days of rain we got today (or yesterday).')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--today', type=float)
args = parser.parse_args()

data = daily.load(args.city)

k = sorted(data.keys())

yesterday = daily.timeByCity[args.city].date() - datetime.timedelta(days=1)

value = int(float(data[yesterday].TOTAL_PRECIP_MM)*10)
dayStr = "yesterday"
end = -2
rangeStart = 3
if args.today is not None:
    dayStr = "today"
    value = int(args.today*10)
    end = -1
    rangeStart = 2


for i in range(rangeStart, 101):
    start = -i
    valSlice = k[start:end]
    cum = sum([int(float(data[a].TOTAL_PRECIP_MM)*10) for a in valSlice])
    if cum < value:
        print(len(valSlice), valSlice[0], valSlice[-1], cum/10)
    else:
        print('-'*80)
        print(len(valSlice), valSlice[0], valSlice[-1], cum/10)
        dayCount = len(valSlice)-1
        if dayCount >= 20:
            cityName = stations.city[args.city].name
            print('#{cityName} had more rain {dayStr} ({value}) than in the past'
                  ' {dayCount} days combined.'
                  .format(**locals()))
        break
