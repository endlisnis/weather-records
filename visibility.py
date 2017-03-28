#!/usr/bin/python
from __future__ import print_function
import hourly

data = hourly.load("ottawa")

hours = []

for hour,hourdata in data.iteritems():
    visibility = hourdata[hourly.VISIBILITY]
    if len(visibility):
        visibility = float(visibility)
        #if visibility <= 0.2 and 'fog' in hourdata[hourly.WEATHER].lower():
        if visibility <= 1 and 'fog' in hourdata[hourly.WEATHER].lower():
            hours.append(hour)
            #print hour

hours.sort()
for hour in hours:
    print hour
exit(0)

days = {}

for hour in hours:
    day = hour[:-1]
    if day not in days:
        days[day] = 0

    days[day] += 1

daykeys = days.keys()
daykeys.sort()

for day in daykeys:
    print day, days[day]
