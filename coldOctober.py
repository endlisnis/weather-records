#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather, sys, copy

field = weather.daily.MAX_TEMP

data = weather.daily.load('ottawa')

coldestDate = None
coldestTemp = 100

for date in sorted(data.keys()):
    if date.month == 8:
        val = data[date].MIN_TEMP
        if len(val):
            val = float(val)
            if val < coldestTemp:
                print date, val
                coldestTemp = val
                coldestDate = date
