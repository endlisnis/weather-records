#!/usr/bin/python3
import daily, time, hourly

data = daily.load('ottawa')

def variance(stableDict, extra=None):
    stableMin = min(stableDict.values())
    stableMax = max(stableDict.values())

    if extra != None:
        if extra < stableMin:
            stableMin = extra
        if extra > stableMax:
            stableMax = extra

    return stableMax - stableMin

stableDays = {}

for date in sorted(data.keys()):
    value = data[date]

    if len(value.MAX_TEMP) > 0:
        high = float(value.MAX_TEMP)

        stableDays[date] = high
        while variance(stableDays) > 1:
            stableDays.pop(min(stableDays.keys()))

        if len(stableDays) > 5:
            print(len(stableDays))
            for i in sorted(stableDays.keys()):
                print("%s: %.1f" % (i, stableDays[i]))
            print
