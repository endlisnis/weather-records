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


def checkMaxRise(city, name):
    offsets = tuple(range(2))
    maxDiff = [0.0 for o in offsets]
    maxDiffValue = [None for o in offsets]
    maxDiffD = [None for o in offsets]
    lastV = deque([None for o in offsets])
    lastD = deque([None for o in offsets])
    done = [False for o in offsets]
    for utcTime, vals in fillReverseSortedGapsWithNone(data):
        if sum(done) == len(done):
            break
        if vals is None:
            lastV.insert(0, None)
            lastD.insert(0, None)
            continue
        localTime = utcTime.astimezone(stations.city[city].timezone)
        #print dateTime
        date = localTime.date()
        v = vals.TEMP
        if v is None:
            lastV.insert(0, None)
            lastD.insert(0, None)
            continue
        #print v
        for offset in offsets:
            if lastV[offset] == None or done[offset]:
                continue
            diff = lastV[offset] - v
            if diff >= maxDiff[offset]:
                if (dt.date.today() - date).days > 180:
                    dayName = dayOfWeek(maxDiffD[offset][1].date())
                    if (dt.date.today() - maxDiffD[offset][0].date()).days == 1:
                        dayName = 'Yesterday'
                    elif (dt.date.today() - maxDiffD[offset][0].date()).days == 0:
                        dayName = 'Today'
                    #import pudb; pu.db
                    since = sinceWhen.sinceWhen(
                        city,
                        daily.MAX_TEMP.index,
                        date)
                    text = ("{} between {} and {},"
                            " the temp jumped from {:.1f}℃➜{:.1f}℃"
                            " which was #{}'s largest {}-hour jump {}"
                            .format(dayName,
                                    clock12(city, 'H{}'.format(maxDiffD[offset][0].hour)),
                                    clock12(city, 'H{}'.format(maxDiffD[offset][1].hour)),
                                    float(maxDiffValue[offset][0]),
                                    float(maxDiffValue[offset][1]),
                                    stations.city[city].name,
                                    offset+1,
                                    since))
                    (use, tweet) = shouldTweetSuffix(
                        city, text)
                    if use:
                        delayedTweets.addToListForCity(city, tweet, urgent=True)
                        print('ok')
                    else:
                        print('skipping')
                    done[offset] = True
                if ( utcTime.timestamp() <= lastdatetimestamp.get(name, 0)
                     or (dt.date.today() - date).days >= 7
                ):
                    done[offset] = True
                maxDiff[offset] = diff
                maxDiffValue[offset] = v, lastV[offset]
                maxDiffD[offset] = localTime, lastD[offset]
        lastV.insert(0, v)
        lastD.insert(0, localTime)
    lastdatetimestamp[name] = int(sorted(data.keys())[-1].timestamp())

def genReverseTemperatures():
    utcTimes = tuple(sorted(data.keys(), reverse=True))
    for utcTime in hourly.hourrange(utcTimes[0], utcTimes[-1], -1):
        values = date.get(utcTime, None)
        if values is None:
            yield utcTime, None
        yield utcTime, v.TEMP

def checkMaxDrop(city, name, recentLimit=180):
    maxDiff = 0.0
    maxDiffD = None
    lastV = None
    lastD = None
    lastUtcTime = None
    for utcTime in sorted(data.keys(), reverse=True):
        localTime = utcTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        v = data[utcTime].TEMP
        if v is None:
            lastV = None
            continue
        if lastV != None and (lastUtcTime - utcTime) == dt.timedelta(hours=1):
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
                if ( utcTime.timestamp() <= lastdatetimestamp.get(name, 0)
                     or (dt.date.today() - date).days >= 7
                ):
                    break
                maxDiff = diff
                maxDiffValue = v, lastV
                maxDiffD = localTime, lastD
        lastV = v
        lastD = localTime
        lastUtcTime = utcTime
    lastdatetimestamp[name] = int(sorted(data.keys())[-1].timestamp())

def checkMaxWind(city, name):
    maxWind = 0.0
    maxWindD = None
    for utcTime in reversed(sorted(data.keys())):
        localTime = utcTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        v = data[utcTime].WIND_SPD
        if ( v is not None
             and ( (type(v) is str and len(v) > 0)
                   or type(v) is not str)
        ):
            wind = int(v)
            if wind >= maxWind:
                if (dt.date.today() - date).days > 180:
                    dayName = dayOfWeek(maxWindD.date())
                    if (dt.date.today() - maxWindD.date()).days == 1:
                        dayName = 'Yesterday'
                    elif (dt.date.today() - maxWindD.date()).days == 0:
                        dayName = 'Today'
                    since = sinceWhen.sinceWhen(
                        city,
                        daily.AVG_WIND.index,
                        date)
                    text = ("{} at {}, the wind was {}km/h"
                            " which made it #{}'s windiest hour {}"
                            .format(dayName,
                                    clock12(city, 'H{}'.format(maxWindD.hour)),
                                    maxWindValue,
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
                if ( utcTime.timestamp() <= lastdatetimestamp.get(name, 0)
                     or (dt.date.today() - date).days >= 7
                ):
                    break
                maxWind = wind
                maxWindValue = wind
                maxWindD = localTime
    lastdatetimestamp[name] = int(sorted(data.keys())[-1].timestamp())

def checkMaxHumidity(city, name):
    if 'MEAN_HUMIDITY' in stations.city[city].skipDailyFields:
        return None
    maxHumidity = 0
    maxHumidityD = None
    for utcTime in reversed(sorted(data.keys())):
        localTime = utcTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        v = data[utcTime].REL_HUM
        if ( v is not None
             and ( (type(v) is str and len(v) > 0)
                   or type(v) is not str)
        ):
            humidity = int(v)
            if humidity >= maxHumidity:
                if (dt.date.today() - date).days > 180:
                    dayName = dayOfWeek(maxHumidityD.date())
                    if (dt.date.today() - maxHumidityD.date()).days == 1:
                        dayName = 'Yesterday'
                    elif (dt.date.today() - maxHumidityD.date()).days == 0:
                        dayName = 'Today'
                    since = sinceWhen.sinceWhen(
                        city,
                        daily.AVG_WIND.index,
                        date)
                    text = ("{} at {}, the humidity was {}%"
                            " which made it #{}'s moistest hour {}"
                            .format(dayName,
                                    clock12(city, 'H{}'.format(maxHumidityD.hour)),
                                    maxHumidity,
                                    stations.city[city].name,
                                    since))
                    #import pudb; pu.db
                    (use, tweet) = shouldTweetSuffix(
                        city, text)
                    if use:
                        delayedTweets.addToListForCity(city, tweet, urgent=True)
                        print('ok')
                    else:
                        print('skipping')
                    break
                if ( utcTime.timestamp() <= lastdatetimestamp.get(name, 0)
                     or (dt.date.today() - date).days >= 7
                ):
                    break
                maxHumidity = humidity
                maxHumidityD = localTime
    lastdatetimestamp[name] = int(sorted(data.keys())[-1].timestamp())

def checkMinWindchill(city, name):
    #import pudb; pu.db
    if 'MIN_WINDCHILL' in stations.city[city].skipDailyFields:
        return None
    minWindchill = 99.0
    minWindchillD = None
    for utcTime in reversed(sorted(data.keys())):
        localTime = utcTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        windchill = data[utcTime].windchill
        if windchill is not None:
            if windchill <= minWindchill:
                if (dt.date.today() - date).days > 180:
                    dayName = dayOfWeek(minWindchillD.date())
                    if (dt.date.today() - minWindchillD.date()).days == 1:
                        dayName = 'Yesterday'
                    elif (dt.date.today() - minWindchillD.date()).days == 0:
                        dayName = 'Today'
                    since = sinceWhen.sinceWhen(
                        city,
                        daily.MIN_WINDCHILL.index,
                        date)
                    text = ("{} at {}, the windchill was {:.1f}"
                            " which made it #{}'s windchilliest hour {}"
                            .format(dayName,
                                    clock12(city, 'H{}'.format(minWindchillD.hour)),
                                    float(minWindchill),
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
                if ( utcTime.timestamp() <= lastdatetimestamp.get(name, 0)
                     or (dt.date.today() - date).days >= 7
                ):
                    break
                minWindchill = windchill
                minWindchillD = localTime
    lastdatetimestamp[name] = int(sorted(data.keys())[-1].timestamp())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Determine the last time has changed this much in an hour.')
    parser.add_argument('-f', help='Field')
    parser.add_argument('--city', default='ottawa')
    args = parser.parse_args()

    data = hourly.load(args.city)
    try:
        lastdatetimestamp = eval(open('{}/hourAlertMarkers.py'.format(args.city)).read())
        if type(lastdatetimestamp) == int:
            lastdatetimestamp = {'maxRise': lastdatetimestamp}
    except FileNotFoundError:
        lastdatetimestamp = {}
    checkMinWindchill(args.city, 'windchill')
    checkMaxRise(args.city, 'maxRise')
    checkMaxDrop(args.city, 'maxDrop')
    checkMaxHumidity(args.city, 'moistest')
    if 'AVG_WIND' not in stations.city[args.city].skipDailyFields:
        checkMaxWind(args.city, 'maxWind')

    open('{}/hourAlertMarkers.py'.format(args.city), 'w').write(
        PrettyPrinter().pformat(lastdatetimestamp))
