#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import daily, time

data = daily.load('ottawa')

dateByVariance = {}

for key in sorted(data.keys()):
    value = data[key]
    if len(value.MAX_TEMP) > 0 and len(value.MIN_TEMP) > 0:
        high = int(round(float(value.MAX_TEMP)*10))
        low = int(round(float(value.MIN_TEMP)*10))
        variance = high - low
        if variance >= 215:
            print variance/10.0, key
        if variance not in dateByVariance:
            dateByVariance[variance] = [key]
        else:
            dateByVariance[variance].append(key)

count = 0
for key in reversed(sorted(dateByVariance.keys())):
#for key in sorted(dateByVariance.keys()):
    print count+1, key/10.0, dateByVariance[key]
    count += len(dateByVariance[key])
