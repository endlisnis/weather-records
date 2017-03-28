#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import hourly, time, datetime
from namedList import *
from collections import namedtuple

data = hourly.load("ottawa")

dateByHmdx = {}
maxHmdxByDate = {}

for (dateTime, info) in data.iteritems():
    humidex = info.humidex
    if humidex != None:
        if humidex not in dateByHmdx:
            dateByHmdx[humidex] = []
        dateByHmdx[humidex].append(dateTime)
        #
        date = dateTime.date()
        #
        maxHmdxByDate[date] = max(maxHmdxByDate.get(date,0), humidex)
        

for hmdx in sorted(dateByHmdx.keys()):
    if hmdx > 44:
        print '%.1f' % hmdx, sorted(dateByHmdx[hmdx])
#for a in dateByHmdx[46]:
#    print time.ctime(a), data[a]

Day = namedtuple('Day', 'month day')
Record = namedtuple('Record', 'val year')
recordByDay = {}

for dateTime in sorted(maxHmdxByDate.keys()):
    day = Day(dateTime.month, dateTime.day)
    #
    if day not in recordByDay:
        recordByDay[day] = None
    val = Record(maxHmdxByDate[dateTime], dateTime.year)
    #
    oldRecord = recordByDay[day]
    if oldRecord == None:
        print "%04d/%02d/%02d: Humidex of %.1fC beats previous record of ... well, there was no previous recorded humidex." % (dateTime.year, day.month, day.day, val.val)
        recordByDay[day] = val
    elif val.val > oldRecord.val:
        print( "%04d/%02d/%02d: Humidex of %.1fC beats previous record of %.1fC from %04d/%02d/%02d." 
               % (dateTime.year, day.month, day.day, val.val, oldRecord.val, oldRecord.year, day.month, day.day) )
        recordByDay[day] = val
    elif day.month == 6 and day.day == 8:
        print "%04d/%02d/%02d: Humidex of %.1fC." % (dateTime.year, day.month, day.day, val.val)
    #print dateTime
    #print time.localtime(day*24*60*60)[:3], '%.1f' % maxHmdxByDate[day]
