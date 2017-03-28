#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import weather, sys, copy

data = weather.daily.load('ottawa')

month = 8

for date in data.keys():
    if date.month == month:
        val = data[date].MAX_TEMP
        if len(val):
            val = float(val)

            print val, date
