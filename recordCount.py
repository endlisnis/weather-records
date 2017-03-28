#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import daily, time

data = daily.load("farm")

records = {}

consequtiveRecords = 0

def reportRecords(dateTime):
    global consequtiveRecords
    if consequtiveRecords >= 3:
        print dateTime, consequtiveRecords
    consequtiveRecords = 0
    

for dateTime in sorted(data.keys()):
    if len(data[dateTime].MAX_TEMP) > 0:
        v = float(data[dateTime].MAX_TEMP)
        monthDay = (dateTime.month, dateTime.day)
        if monthDay not in records:
            records[monthDay] = v
            reportRecords(dateTime)
        elif records[monthDay] <= v:
            #print "Record %d %s %.1fC" % (dateTime.year, monthDay, v)
            records[monthDay] = v
            consequtiveRecords += 1
        else:
            reportRecords(dateTime)

reportRecords(dateTime)
