#!/usr/bin/python
from __future__ import print_function
import daily, time

field = daily.SPD_OF_MAX_GUST_KPH

data = daily.load('ottawa')

count = 0
countAbove = {50: 0, 
              60: 0, 
              70: 0, 
              72: 0, 
              80: 0, 
              82: 0, 
              90: 0, 
              91: 0, 
              92: 0, 
              93: 0, 
              94: 0, 
              95: 0, 
              100: 0}

for date in data:
    #if date.year < 1984:
    #    continue
    wind = 0
    windStr = data[date].SPD_OF_MAX_GUST_KPH
    if len(windStr):
        wind = int(float(data[date].SPD_OF_MAX_GUST_KPH))
    count += 1
    for key in countAbove:
        if wind > key:
            countAbove[key] += 1

for key in sorted(countAbove.keys()):
    print key, count / countAbove[key]
#print count, countAbove
