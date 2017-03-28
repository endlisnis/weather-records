#!/usr/bin/python
from __future__ import print_function
import daily, datetime

def windchill(temp, wind):
    if temp < 10:
        return 13.12 + .6215*temp - 11.37*wind**.16 + 0.3965*temp*wind**.16
    return None

field = daily.MIN_WINDCHILL

data = daily.load('ottawa')

for year in range(data.minYear, data.maxYear+1):
    try:
        print year, data[datetime.date(year, 12, 1)].MIN_WINDCHILL
    except KeyError:
        pass
