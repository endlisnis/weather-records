#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, sys, copy, fnmatch
import argparse
import datetime
import stations

def base10int(a):
    return int(a,10)

def recordSince(city, mask, after, before):
    print(mask)
    timeMatch = mask.split(',')
    #
    lowestVal = 999
    highestVal = -999
    highestVals = []
    lowestVals = []
    if after is not None:
        after = tuple(map(base10int, after.split('-')))
    if before is not None:
        before = tuple(map(base10int, before.split('-')))

    #
    for utcdate in reversed(sorted(data.keys())):
        date = utcdate.astimezone(stations.city[city].timezone)
        if after is not None:
            afterDay = datetime.date(date.year, after[0], after[1])
            if before != None:
                beforeDay = datetime.date(date.year, before[0], before[1])
                if date.date() <= afterDay and date.date() >= beforeDay:
                    continue
            elif date.date() <= afterDay:
                continue
        elif before != None:
            beforeDay = datetime.date(date.year, before[0], before[1])
            if date.date() >= beforeDay:
                continue
        if not any(map(lambda t: fnmatch.fnmatch(str(date), t), timeMatch)):
            continue
        #
        extraData = None
        val = None
        if field == 'temp':
            val = data[date].TEMP
        elif field == 'dewpoint':
            val = data[date].DEW_POINT_TEMP
        elif field == 'visibility':
            val = data[date].VISIBILITY
        elif field == 'windchill':
            val = data[date].windchill
        elif field == 'wind':
            val = data[date].WIND_SPD
        elif field == 'humidity':
            val = data[date].REL_HUM
        elif field == 'humidex':
            val = data[date].humidex
        elif field == 'dewpoint':
            val = data[date].DEW_POINT_TEMP
        elif field == 'coldheavysnow':
            conditions = data[date].WEATHER
            conditions = filter(lambda t: t!='Blowing Snow', conditions.split(','))
            val = None
            if 'Snow' in ','.join(conditions):
                vis = data[date].VISIBILITY
                if val == None or len(val) != 0:
                    vis = float(vis)
                    if vis <= 2:
                        extraData = vis
                        val = data[date].TEMP
                        if len(val) == 0:
                            val = None
                        else:
                            val = float(val)
        elif field == 'coldsnow':
            conditions = data[date].WEATHER
            conditions = filter(lambda t: t!='Blowing Snow', conditions.split(','))
            val = None
            if 'Snow' in ','.join(conditions):
                val = data[date].TEMP
                if len(val) == 0:
                    val = None
                else:
                    val = float(val)
        elif field == 'warmsnow':
            conditions = data[date].WEATHER
            conditions = filter(lambda t: t!='Blowing Snow', conditions.split(','))
            val = None
            if 'Snow' in ','.join(conditions):
                val = data[date].TEMP
                if len(val) == 0:
                    val = None
                else:
                    val = float(val)
                    if val <= 3:
                        val = None
                    else:
                        print(date, val)
        else:
            assert(false)
        #
        #
        #
        if val != None:
            if val <= lowestVal:
                if field not in ('wind', 'warmsnow'):
                    #print(date, val, ["", extraData][extraData != None])
                    lowestVals.append((date, val, ["", extraData][extraData != None]))
                    if args.min is True and args.recent is True and len(lowestVals) >= 2:
                        break
                lowestVal = val
            if val >= highestVal:
                highestVals.append((date, val, ["", extraData][extraData != None]))
                highestVal = val
                if args.min is False and args.recent is True and len(highestVals) >= 2:
                    break
    #
    if args.recent:
        array = highestVals
        if args.min:
            array = lowestVals
        if len(array) > 1:
            print( '{recent}: {val:3.1f}, {diff:5}, {old}: {oldVal:3.1f}'
                   .format(diff=(array[0][0] - array[1][0]).days,
                           recent=array[0][0],
                           old=array[1][0],
                           oldVal=array[1][1],
                           val=array[0][1] ) )
        else:
            print( '{recent}: {val:3.1f}, ever!'
                   .format(recent=array[0][0],
                           val=array[0][1], ) )

    else:
        for lv in lowestVals:
            print(lv)
        print('---')
        for hv in highestVals:
            print(hv)

parser = argparse.ArgumentParser(description='Determine the last time a field has been this high/low.')
parser.add_argument('-f', help='Field')
parser.add_argument('--city', default='ottawa')
parser.add_argument('-m', help='Mask', default=['*-*-* *:00:00-*'], nargs='*')
parser.add_argument('--min', help='Look for minimum values.', action='store_true')
parser.add_argument('--recent', help='Only print out the duration of the most recent record.', action='store_true')
parser.add_argument('--after', help='Only consider dates after this one.')
parser.add_argument('--before', help='Only consider dates before this one.')
args = parser.parse_args()

field = args.f
print(args.m)

data = hourly.load(args.city)
masks = args.m

for mask in masks:
    recordSince(args.city, mask, args.after, args.before)
