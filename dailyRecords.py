#!/usr/bin/python3
# -*- coding: utf-8 -*-
import daily, time, datetime
import hourly
from namedList import *

class Record(namedStruct('Record', ('value', 'year', 'month=None', 'day=None'))):
    def __str__(self):
        m = self.month
        if m == None:
            m = 'None'
        else:
            m = '%02d' % m

        d = self.day
        if d == None:
            d = 'None'
        else:
            d = '%02d' % d

        v = self.value
        if v != None:
            v = '%.1f' % float(v)
        return ( "{year}/{month}/{day}: {value}"
                 .format(year=self.year, month=m, day=d, value=v ) )

    def __repr__(self):
        return self.__str__()

DayInfo = namedStruct('DayInfo', ('max', 'min', 'avg',
                                  'recent', 'recentEstimated', 'recentEstimatedHour',
                                  'incomplete', 'normal', 'median',
                                  'maxSince', 'minSince'))

def getInfo(city, date, field, recentValOverride=None):
    if recentValOverride != None:
        recentValOverride = int(recentValOverride[field.index])
        #print('Using recentValOverride={}'.format(recentValOverride))
    ret = DayInfo(max=Record(-999, year=1900),
                  min=Record(+999, year=1900),
                  avg=None,
                  recent=recentValOverride,
                  recentEstimated=(recentValOverride==None),
                  recentEstimatedHour=-1,
                  incomplete=False,
                  normal=None,
                  median=None,
                  maxSince=Record(None, year=1800),
                  minSince=Record(None, year=1800) )
    vSum = 0
    vCount = 0
    cityData = daily.dataByCity[city]
    targetYear = date.year

    normalValues = []

    for year in range(cityData.maxYear, cityData.minYear-1, -1):
        try:
            iDateTime = datetime.date(year, date.month, date.day)
        except ValueError:
            assert(date.month == 2 and date.day == 29)
            # This is a leap day, but not a leap year, so just skip it
            continue

        try:
            val = cityData[iDateTime][field.index]
            valEstimated = False
            valEstimatedHour = None
            valIncomplete = False
            flagsText = cityData[iDateTime][field.index+1]
            flags = flagsText.split('+')
            if ( 'H' in flagsText
                 or 'I' in flagsText
                 or 'S' in flagsText
            ):
                valEstimated = True
                if year == targetYear and recentValOverride == None:
                    valEstimatedHour = None
                    if 'H' in flagsText:
                        valEstimatedTuple = tuple(filter(lambda t: t[0] == 'H', flags))
                        if len(valEstimatedTuple) > 0 and len(valEstimatedTuple[0]) > 1:
                            valEstimatedHour = valEstimatedTuple[0]
                    if 'S' in flagsText:
                        valEstimatedTuple = tuple(filter(lambda t: t[0] == 'S', flags))
                        if len(valEstimatedTuple) > 0 and len(valEstimatedTuple[0]) > 1:
                            valEstimatedHour = valEstimatedTuple[0]
            if 'I' in flagsText:
                valIncomplete = True
        except KeyError:
            continue

        if val is None:
            continue

        if year == targetYear and recentValOverride == None:
            #print val, Fraction(val)
            ret.recent = val
            ret.recentEstimated = valEstimated
            ret.recentEstimatedHour = valEstimatedHour
            ret.incomplete = valIncomplete
        else:
            if val > ret.max.value:
                ret.max = Record(val, year)
            if ret.recent is not None and val >= ret.recent and ret.maxSince.value is None:
                ret.maxSince = Record(val, year)
            if val < ret.min.value:
                ret.min = Record(val, year)
            if ret.recent is not None and val <= ret.recent and ret.minSince.value is None:
                ret.minSince = Record(val, year)
            vSum += val
            vCount += 1

            if year >= (targetYear - 30):
                normalValues.append(val)

    if vCount > 0:
        ret.avg = vSum/vCount

    if len(normalValues) > 0:
        ret.normal = sum(normalValues)/len(normalValues)
        ret.median = sorted(normalValues)[len(normalValues)//2]

    return ret

MaxMin = namedStruct('MaxMin', ('max','min'))

maxMinCache = {}

def cachedDailyMaxMin(city, date, field):
    key = (field, date.month, date.day)
    ret = maxMinCache.get(key, None)
    if ret != None:
        return ret

    dayInfo = getInfo(city, date, field)
    ret = MaxMin(dayInfo.max, dayInfo.min)
    maxMinCache[key] = ret
    return ret

def getMonthRecords(city, targetYear, field):
    ret = MaxMin(max=[], min=[])
    for i in range(12):
        ret.max.append(Record(-999, year=1900))
        ret.min.append(Record(+999, year=1900))
    cityData = daily.dataByCity[city]

    for date in sorted(cityData.keys()):
        if date.year == targetYear:
            break
        val = cityData[date][field.index]
        if val is not None:
            if val > ret.max[date.month-1].value:
                ret.max[date.month-1] = Record(val, date.year, date.month, date.day)
            if val < ret.min[date.month-1].value:
                ret.min[date.month-1] = Record(val, date.year, date.month, date.day)

    return ret

if __name__ == '__main__':
    daily.load("hamilton")
    print(getInfo('hamilton', datetime.date(2017,3,1), daily.AVG_WIND))
