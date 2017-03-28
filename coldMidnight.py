#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import hourly, sys, copy

data = hourly.load('ottawa')

minByDate = {}

for date in reversed(sorted(data.keys())):
    val = data[date].TEMP
    if len(val) == 0:
        continue
    val = float(val)
    if date.hour == 0 and val < minByDate.get(date.date(), -999):
        print date.date()
    else:
        minByDate[date.date()] = min(minByDate.get(date.date(), 999), val)
