#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import hourly, sys, copy

length = 48
maxdiff = 2

data = hourly.load('ottawa')

values = []

results = {}

def handleValue(v):
    global values
    if len(v):
        v = float(v)
        #print "append(%f,%s)" % (v, values),
        values.append(v)
        #print " = ", values
        while max(values) - min(values) > maxdiff:
            values.pop(0)
    else:
        values = []
    #
    clen = len(values)
    if clen >= length:
        diff = max(values) - min(values)
        if clen in results:
            results[clen].append(date)
        else:
            results[clen] = [date]
        print date, min(values), max(values)

for date in sorted(data.keys()):
    handleValue(data[date].TEMP)

for runLength in reversed(sorted(results.keys())):
    print runLength, results[runLength]
