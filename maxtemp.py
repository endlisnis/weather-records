#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time, posix, daily

data = daily.load("ottawa")

class FloatValue():
    __slots__ = ()
    def __init__(self, field):
        self.fieldIndex = field.index
    def __call__(self, fields):
        r = fields[self.fieldIndex]
        if len(r) == 0:
            return None
        return float(r)

class IntValue():
    __slots__ = ()
    def __init__(self, field):
        self.fieldIndex = field.index
    def __call__(self, fields):
        r = fields[self.fieldIndex]
        if len(r) == 0:
            return None
        return int(float(r)+.5)


class IntDiff():
    __slots__ = ()
    def __init__(self, field1, field2):
        self.field1Index = field1.index
        self.field2Index = field2.index
    def __call__(self, fields):
        r1 = fields[self.field1Index]
        r2 = fields[self.field2Index]
        if len(r1) == 0 or len(r2) == 0:
            return None
        return int(float(r1) - float(r2) +.5)


class Max():
    __slots__ = ()
    def __init__(self, field):
        self.fieldIndex = field.index
    #
    def __call__(self, fields):
        r = fields[self.fieldIndex]
        if len(r) == 0:
            return -99
        return float(r)
    #
    def better(self, one, two):
        return self(one) > self(two)


class MaxDiff():
    __slots__ = ()
    def __init__(self, field1, field2):
        self.field1Index = field1.index
        self.field2Index = field2.index
    #
    def __call__(self, fields):
        r1 = fields[self.field1Index]
        r2 = fields[self.field2Index]
        if len(r1) == 0 or len(r2) == 0:
            return 0
        return float(r1) - float(r2)
    #
    def better(self, one, two):
        return self(one) > self(two)

class MinDiff():
    __slots__ = ()
    def __init__(self, field1, field2):
        self.field1Index = field1.index
        self.field2Index = field2.index
    #
    def __call__(self, fields):
        r1 = fields[self.field1Index]
        r2 = fields[self.field2Index]
        if len(r1) == 0 or len(r2) == 0:
            return 100
        return float(r1) - float(r2)
    #
    def better(self, one, two):
        return self(one) < self(two)

def findBest(proc):
    bv = None
    date = None
    #
    for year in data:
        yd = data[year]
        for month in yd:
            md = yd[month]
            for day in md:
                f = md[day]
                if bv == None or proc.better(f, bv):
                    bv = f
                    date = (year,month,day)
    #
    return date, bv

def histogram(proc):
    hist = {}
    #
    for year in data:
        yd = data[year]
        for month in yd:
            md = yd[month]
            for day in md:
                f = proc(md[day])
                if f != None:
                    if f not in hist:
                        hist[f] = 0
                    hist[f] += 1
    return hist

#findBest(Max(daily.MAX_TEMP))
#findBest(Max(daily.MAX_TEMP))
#findBest(Max(daily.TOTAL_RAIN_MM))
#findBest(Max(daily.TOTAL_SNOW_CM))
#findBest(MaxDiff(daily.MAX_TEMP, daily.MIN_TEMP))
#findBest(MinDiff(daily.MAX_TEMP, daily.MIN_TEMP))

mth = histogram(IntValue(daily.TOTAL_SNOW_CM))

for mt in sorted(mth.keys()):
    print '%s\t%s' % (mt, mth[mt])

