#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import hourly, datetime
import stations

def hourrange(start, end):
    v = start
    while v < end:
        yield v
        v += datetime.timedelta(hours=1)

def addTo(runs, allRuns, run):
    if len(run) > 1:
        if len(run) not in runs:
            runs[len(run)] = [run]
        else:
            runs[len(run)].append(run)
        allRuns.insert(0, run)
        return run

def consecutiveHours(city, expr):
    data = hourly.load(city)
    tz = stations.city[city].timezone

    runs = {}
    allRuns = []
    curRun = []
    mostRecentRun = None
    #
    timestamps = sorted(data.keys())
    #
    for utc in hourrange(timestamps[0], timestamps[-1]):
        hourdata = data.get(utc)
        ltime = utc.astimezone(tz)
        v = None
        if hourdata is not None:
            v = hourdata.eval(expr, {'time':ltime} )
        if v is not None and v is not False:
            curRun.append((ltime, v))
        else:
            r = addTo(runs, allRuns, curRun)
            if r is not None:
                mostRecentRun = r
            curRun = []
    r = addTo(runs, allRuns, curRun)
    if r is not None:
        mostRecentRun = r
    return runs, allRuns, mostRecentRun

parser = argparse.ArgumentParser(description='Determine how often some weather occurs.')
parser.add_argument('expr', help='Which observation to check')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--nth', type=int, default=30)
parser.add_argument('-m', help='Mask', default=['*-*-*'], nargs='*')
parser.add_argument('--between', help='Only consider dates between these two. Comma separated like 05-15,07-01')
parser.add_argument('--holiday', help='The name of a holiday')
args = parser.parse_args()

city = args.city

a, allRuns, mostRecentRun = consecutiveHours(city, args.expr)

nth = 1
for runlen in reversed(sorted(a.keys())):
    for run in a[runlen]:
        if nth <= args.nth or run is mostRecentRun:
            print('{},{},{:02}-{:02}-{:02}'.format(nth, len(run), run[0][0].year, run[0][0].month, run[0][0].day))
    nth += len(a[runlen])

print('---')

longest = 1
for i in allRuns:
    if len(i) >= longest:
        print(len(i), i[0])
        longest = len(i)
