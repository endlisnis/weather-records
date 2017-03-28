#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, time, datetime, sys, csv, numpy
from extraData import ExtraData, ValWithFlag
import bz2
import collections
import decimal
import io
import stations
import hoursPerDay
import todayXmlParse
from namedtuplewithdefaults import namedtuple_with_defaults
D = decimal.Decimal

def hourCount(city, date):
    return hoursPerDay.data[city].get(date,24)

def keyOfMinMaxFloatValue(data):
    minKey = None
    maxKey = None
    #
    for (key, value) in data.items():
        if value == None:
            continue
        if minKey == None:
            minKey = [key]
            maxKey = [key]
        #
        elif value < data[minKey[0]]:
            minKey = [key]
        elif value == data[minKey[0]]:
            minKey.append(key)
        elif value > data[maxKey[0]]:
            maxKey = [key]
        elif value == data[maxKey[0]]:
            maxKey.append(key)
    #
    return (minKey, maxKey)

def timeIsDuringToday(utcTimestamp):
    utctoday = datetime.datetime.utcnow().date()
    utcToday6 = datetime.datetime(utctoday.year,
                                  utctoday.month,
                                  utctoday.day,
                                  hour=6)
    utcTomorrow6 = utcToday6 + datetime.timedelta(days=1)
    if (utcTimestamp >= utcToday6) and (utcTimestamp < utcTomorrow6 ):
        return True
    return False

def envCanToday():
    utcnow = datetime.datetime.utcnow()
    if utcnow.hour >= 6:
        return utcnow.date()
    return (utcnow - datetime.timedelta(days=1)).date()

HourlyDailyData = namedtuple_with_defaults(
    'HourlyDailyData',
    ( 'maxTemp', 'maxTempFlag',
      'maxHumidex', 'maxHumidexFlag',
      'minTemp', 'minTempFlag',
      'minWindchill', 'minWindchillFlag',
      'avgTemp', 'avgTempFlag',
      'avgWindchill', 'avgWindchillFlag',
      'avgWind', 'avgWindFlag',
      'avgHumidity', 'avgHumidityFlag',
      'avgDewpoint', 'avgDewpointFlag',
      'maxGust', 'maxGustFlag')
)

multiplier = HourlyDailyData(
    maxTemp=10,
    maxHumidex=10,
    minTemp=10,
    minWindchill=10,
    avgTemp=10,
    avgWindchill=10,
    avgWind=10,
    avgHumidity=1,
    avgDewpoint=10,
    maxGust=1)

def prepForDb(data):
    ret = {}
    for i, name in enumerate(HourlyDailyData._fields):
        if multiplier[i] is None or data[i] is None:
            ret[name] = data[i]
        else:
            ret[name] = int(data[i]*multiplier[i])
    return HourlyDailyData(**ret)

nameMap = {
    'TEMP' : 'Temp',
    'TEMP_FLAG' : 'TempFlag',
    'DEW_POINT_TEMP' : 'Dewpoint',
    'DEW_POINT_TEMP_FLAG' : 'DewpointFlag',
    'REL_HUM' : 'Humidity',
    'REL_HUM_FLAG' : 'HumidityFlag',
    'WIND_DIR' : 'WindDir',
    'WIND_DIR_FLAG' : 'WindDirFlag',
    'WIND_SPD' : 'Wind',
    'WIND_SPD_FLAG' : 'WindFlag',
    'VISIBILITY' : 'Visibility',
    'VISIBILITY_FLAG' : 'VisibilityFlag',
    'STN_PRESS' : 'Pressure',
    'STN_PRESS_FLAG' : 'PressureFlag',
    'WEATHER' : 'Weather'}

def main(city, year):
    data = hourly.load(city,
                       ( datetime.datetime(year, 1, 1),
                         datetime.datetime(year+1, 1, 1) ) )
    statsByDay = {}

    for dateTime in sorted(data.keys()):
        info = data[dateTime]
        localTime = dateTime.astimezone(stations.city[city].timezone)
        date = localTime.date()
        #if (datetime.date.today() - date).days < 3:
        #print(dateTime, info)
        try:
            thisDayStats = statsByDay[date]
        except KeyError:
            statsByDay[date] = {}
            thisDayStats = statsByDay[date]

        for hourFieldName, val in info._asdict().items():
            fieldName = nameMap[hourFieldName]
            if val is None or (type(val) is str and len(val) == 0):
                # Skip empty fields and textual weather field
                continue
            try:
                thisDayStats[fieldName][localTime.hour] = val
            except KeyError:
                thisDayStats[fieldName] = {localTime.hour : val}
            #print('hourFieldName, val,', repr(hourFieldName), repr(val), repr(thisDayStats[hourFieldName]))

        val = info.humidex
        if val != None:
            fname = 'Humidex'
            try:
                thisDayStats[fname][localTime.hour] = val
            except KeyError:
                thisDayStats[fname] = {localTime.hour : val}

        val = info.windchill
        if val != None:
            fname = 'Windchill'
            try:
                thisDayStats[fname][localTime.hour] = val
            except KeyError:
                thisDayStats[fname] = {localTime.hour : val}

    fname = "{city}/data/{year}.dailyextra-csv.bz2".format(**locals())
    #print(fname)
    csvWriter = csv.writer(io.TextIOWrapper(bz2.BZ2File(fname, 'w')))

    flagMap = {'Humidex' : 'Temp',
               'Windchill' : 'Temp'}

    for date in sorted(statsByDay.keys()):
        infodict = statsByDay[date]
        #print(date, infodict)
        info = {}
        if date == envCanToday():
            _, _, summaryMaxGust = todayXmlParse.getMinMax(city)
            info['maxGust'] = summaryMaxGust
            info['maxGustFlag'] = 'H'
        for maxName in ('Temp', 'Humidex'):
            maxVal = None
            maxFlag = ''
            lenVals = 0
            if maxName in infodict:
                valByHour = infodict[maxName]
                lenVals = len(valByHour)
                minKey, maxKey = keyOfMinMaxFloatValue(valByHour)
                if maxKey is not None:
                    maxHourlyHour = maxKey[0]
                    maxHourlyValue = valByHour[maxHourlyHour]
                    maxVal = maxHourlyValue
                    maxFlag = 'H' + str(maxHourlyHour)
            info['max' + maxName] = maxVal
            #print(infodict)
            flagName = flagMap.get(maxName,maxName) + 'Flag'
            try:
                flagSet = set(infodict[flagName].values())
            except KeyError:
                flagSet = set()

            if len(maxFlag) > 0:
                # MAX_Temp should always be marked as HOURLY to avoid
                # confusion with official daytime highs
                if 'H' in flagSet:
                    flagSet.remove('H')
                flagSet.add(maxFlag)
            if 'M' in flagSet and len(flagSet) > 1:
                flagSet.remove('M')
            if lenVals > 0 and lenVals < hourCount(city, date):
                flagSet.add('I')
            info['max' + maxName + 'Flag'] = '+'.join(sorted(flagSet))

        for minName in ('Temp', 'Windchill'):
            #if minName == 'Windchill' and date == datetime.date(1972,1,26):
            #    import pudb; pu.db
            minVal = None
            minFlag = ''
            lenVals = 0
            if minName in infodict:
                valByHour = infodict[minName]
                lenVals = len(valByHour)
                minKey, maxKey = keyOfMinMaxFloatValue(valByHour)
                if minKey is not None:
                    minHourlyHour = minKey[0]
                    minHourlyValue = valByHour[minHourlyHour]
                    minVal = minHourlyValue
                    minFlag = 'H' + str(minHourlyHour)
            flagName = flagMap.get(minName,minName) + 'Flag'
            try:
                flagSet = set(infodict[flagName].values())
            except KeyError:
                flagSet = set()
            if len(minFlag) > 0:
                # minTemp should always be marked as HOURLY to avoid
                # confusion with official daytime lows
                if 'H' in flagSet:
                    flagSet.remove('H')
                flagSet.add(minFlag)
            if 'M' in flagSet and len(flagSet) > 1:
                flagSet.remove('M')
            if lenVals > 0 and lenVals < hourCount(city, date):
                flagSet.add('I')
            info['min' + minName] = minVal
            info['min' + minName + 'Flag'] = '+'.join(sorted(flagSet))

        for avgName in ('Temp', 'Windchill', 'Wind', 'Humidity', 'Dewpoint'):
            avgVal = None
            lenVals = 0
            if avgName in infodict:
                valByHour = infodict[avgName].values()
                floatVals = tuple(filter(lambda t: t is not None, valByHour) )
                if len(floatVals) > 0:
                    avgVal = numpy.average( tuple(map(float, floatVals)) )
                    if floatVals[0] is int:
                        avgVal = int(avgVal)
                    else:
                        avgVal = D(avgVal).quantize(floatVals[0], decimal.ROUND_HALF_UP)
                lenVals = len(floatVals)
            flagName = flagMap.get(avgName,avgName) + 'Flag'
            try:
                flagSet = set(infodict[flagName].values())
            except KeyError:
                flagSet = set()
            if 'M' in flagSet and avgVal is not None:
                flagSet.remove('M')
            #print(date, avgName, lenVals)
            if lenVals > 0 and lenVals < hourCount(city, date):
                flagSet.add('I')
            # All averages should always be marked as HOURLY to avoid
            # confusion with official MEAN_Temp
            if avgVal is not None:
                flagSet.add('H')
            info['avg' + avgName] = avgVal
            info['avg' + avgName + 'Flag'] = '+'.join(sorted(flagSet))

        info = HourlyDailyData(**info)
        intInfo = prepForDb(info)

        csvWriter.writerow( (date.year, date.month, date.day) + intInfo )
        if (datetime.date.today() - date).days < 3:
            print(date, intInfo)

if __name__ == '__main__':
    city, year = sys.argv[1:]
    main(city, int(year) )
