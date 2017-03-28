#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly
import fnmatch, time, sys
import argparse
import datetime as dt
import delayedTweets
import stations
import sinceWhen
import daily

from alert import clock12, today, nth
from alertTweets import shouldTweetSuffix
from collections import deque
from pprint import PrettyPrinter

def dayOfWeek(day):
    return day.strftime('%A')




def fillReverseSortedGapsWithNone(data):
    r = tuple(reversed(sorted(data.items())))
    lastUtcTime = r[0][0] - dt.timedelta(hours=1)
    for utcTime, vals in reversed(sorted(data.items())):
        while lastUtcTime + dt.timedelta(hours=1) < utcTime:
            lastUtcTime += dt.timedelta(hours=1)
            yield lastUtcTime, None
        yield utcTime, vals
        lastUtcTime = utcTime



def genReverseTemperatures():
    utcTimes = tuple(sorted(data.keys(), reverse=True))
    print(utcTimes[0], utcTimes[-1])
    for utcTime in hourly.hourrange(utcTimes[0], utcTimes[-1]):
        print (utcTime)
        values = data.get(utcTime, None)
        if values is None:
            yield utcTime, None
        yield utcTime, values.TEMP

#checkMaxDrop2('ottawa', 'maxDrop', recentLimit=1)

def checkMaxDrop2(city, name, recentLimit=180):
    maxDiff = 0.0
    maxDiffD = None
    lastV = None
    lastD = None
    lastUtcTime = None
    for utcTime, v in genReverseTemperatures():
        localTime = utcTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        print(v)
        if v is None:
            lastV = None
            continue
        if lastV != None:
            diff = v - lastV
            if diff >= maxDiff:
                if (dt.date.today() - date).days > recentLimit:
                    dayName = dayOfWeek(maxDiffD[1].date())
                    if (dt.date.today() - maxDiffD[0].date()).days == 1:
                        dayName = 'Yesterday'
                    elif (dt.date.today() - maxDiffD[0].date()).days == 0:
                        dayName = 'Today'
                    since = sinceWhen.sinceWhen(
                        city,
                        daily.AVG_WIND.index,
                        date)
                    text = ("{} between {}➜{},"
                            " the temp dropped from {:.1f}℃➜{:.1f}℃"
                            " which was #{}'s largest 1-hour drop {}"
                            .format(dayName,
                                    clock12(city, 'H{}'.format(maxDiffD[0].hour)),
                                    clock12(city, 'H{}'.format(maxDiffD[1].hour)),
                                    float(maxDiffValue[0]),
                                    float(maxDiffValue[1]),
                                    stations.city[city].name,
                                    since))
                    (use, tweet) = shouldTweetSuffix(
                        city, text)
                    if use:
                        delayedTweets.addToListForCity(city, tweet, urgent=True)
                        print('ok')
                    else:
                        print('skipping')
                    break
                maxDiff = diff
                maxDiffValue = v, lastV
                maxDiffD = localTime, lastD
        lastV = v
        lastD = localTime
        lastUtcTime = utcTime



if __name__ == '__main__':
    data = hourly.load('ottawa')
    checkMaxDrop2('ottawa', 'maxDrop', recentLimit=1)
