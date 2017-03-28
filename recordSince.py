#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import daily, sys, fnmatch, math, datetime
from fieldOperators import Value, ValueDiff, ValueEmptyZero, ValueNearRecordMin
import holidays
from howOften import matchDate, parseBetween
import collections

parser = argparse.ArgumentParser(description='Determine historical max/min for some weather.')
parser.add_argument('expr', help='Which observation to check')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--run', type=int, default=1)
parser.add_argument('-m', help='Mask', default='*')
parser.add_argument('--between', help='Only consider dates between these two. Comma separated like 05-15,07-01')
parser.add_argument('--holiday', help='The name of a holiday')
args = parser.parse_args()

fieldName = args.expr
run = args.run

city = args.city
MAX_TIE_COUNT=10

field = {'min': Value(daily.MIN_TEMP),
         'max': Value(daily.MAX_TEMP),
         'mean': Value(daily.MEAN_TEMP),
         'tempSpan': ValueDiff(daily.MAX_TEMP, daily.MIN_TEMP),
         'rain': Value(daily.TOTAL_RAIN_MM),
         'humidex': Value(daily.MAX_HUMIDEX),
         'snow': Value(daily.TOTAL_SNOW_CM),
         'snowpack': ValueEmptyZero(daily.SNOW_ON_GRND_CM),
         'windgust': Value(daily.SPD_OF_MAX_GUST_KPH),
         'wind': Value(daily.AVG_WIND),
         'windchill': Value(daily.MIN_WINDCHILL),
         'avgWindchill': Value(daily.AVG_WINDCHILL),
         'meanHumidity': Value(daily.MEAN_HUMIDITY),
         'minHumidity': Value(daily.MIN_HUMIDITY),
         'minRec': ValueNearRecordMin(daily.MIN_TEMP),
} [fieldName]

dateFilter = args.m
between = parseBetween(args.between)

data = daily.load(city)

maxVal = -999

curRun = collections.deque([-999] * run, run)
curDates = collections.deque([datetime.date(1800,1,1)] * run, run)

rawData = open('recordSince.csv','w')

for date in reversed(sorted(data.keys())):
    if matchDate(date, [dateFilter], between, args.holiday):
        flag = field.getFlag(data[date])
        if 'H' in flag and field.getName() in ('MIN_TEMP', 'MIN_WINDCHILL'):
            continue
        val = field(data[date], date)
        if val != None:
            if date != curDates[-1] - datetime.timedelta(1):
                curDates.clear()
                curRun.clear()
            curDates.append(date)
            curRun.append(val)

            curRunVal = sum(curRun)
            if curRunVal >= maxVal:
                print(curDates[0],
                      curRunVal,
                      [ (str(curDates[i]) + ': ' + str(curRun[i]))
                        for i in range(len(curRun)) ])
                maxVal = curRunVal
            rawData.write('{val:.1f}, {year}, {dates}, {values}\n'
                          .format(val=curRunVal/10,
                                  year=curDates[0].year,
                                  dates='+'.join([str(a) for a in curDates]),
                                  values=curRun) )

print('---')

minVal = 99999999
tieCounter = 0
for date in reversed(sorted(data.keys())):
    if matchDate(date, [dateFilter], between, args.holiday):
        flag = field.getFlag(data[date])
        if ( 'H' in flag
             and field.getName() in ('MAX_TEMP', 'MAX_HUMIDEX', 'MAX_TEMP-MIN_TEMP' )
        ):
            curDates.clear()
            curRun.clear()
            continue
        val = field(data[date], date)
        if val != None:
            val = int(round(float(val)*10))
            if len(curDates) and date != curDates[-1] - datetime.timedelta(1):
                curDates.clear()
                curRun.clear()
            curDates.append(date)
            curRun.append(val)

            curRunVal = sum(curRun)
            #print(curRunVal)
            if len(curRun) == run and curRunVal <= minVal:
                if tieCounter < MAX_TIE_COUNT:
                    print([str(a) for a in curDates], '%.1f' % (curRunVal/10.0), curRun)
                if curRunVal == minVal:
                    tieCounter += 1
                else:
                    if tieCounter >= MAX_TIE_COUNT:
                        print('Skipped {tieCounter} other ties'.format(**locals()))
                    tieCounter = 0
                minVal = curRunVal
if tieCounter >= MAX_TIE_COUNT:
    print('Skipped {tieCounter} other ties'.format(**locals()))
