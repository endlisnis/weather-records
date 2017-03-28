#!/usr/bin/python3
# -*- coding: utf-8 -*-
import daily
import datetime

field = daily.SNOW_ON_GRND_CM

data = daily.load('ottawa')

winterStartByYear = {}
winterEndByYear = {}

for year in range(data.minYear, data.maxYear+1):
    daysCount = 0
    missingDays = 0
    days = daily.dayRange(
        datetime.date(year, 7, 1),
        datetime.date(year+1, 7, 1) )

    for day in days:
        if day not in data or data[day].SNOW_ON_GRND_FLAG == 'M':
            if missingDays > 0:
                # Too many days missing, start from scratch
                daysCount = 0
                missingDays = 0
            else:
                missingDays += 1
                daysCount += 1
            continue
        if len(data[day].SNOW_ON_GRND_CM) > 0:
            depth = int(data[day].SNOW_ON_GRND_CM)
            if depth >= 1:
                daysCount += 1
                if daysCount >= 10:
                    firstWinterDay = day
                    break
    else:
        print(year, "Could not find winter")
        continue

    daysCount = 0
    missingDays = 0
    days = reversed(
        tuple(
            daily.dayRange(
                firstWinterDay,
                datetime.date(year+1, 7, 1) )))
    for day in days:
        if day not in data or data[day].SNOW_ON_GRND_FLAG == 'M':
            if missingDays > 0:
                # Too many days missing, start from scratch
                daysCount = 0
                missingDays = 0
            else:
                missingDays += 1
                daysCount += 1
            continue
        if len(data[day].SNOW_ON_GRND_CM) > 0:
            depth = int(data[day].SNOW_ON_GRND_CM)
            if depth >= 5:
                daysCount += 1
                if daysCount >= 10:
                    lastWinterDay = day+datetime.timedelta(days=20)
                    break
    print(year, firstWinterDay, lastWinterDay)
    winterStartByYear[year] = (firstWinterDay - datetime.date(year,1,1)).days
    winterEndByYear[year] = (lastWinterDay - datetime.date(year,1,1)).days

recentYears = sorted(winterStartByYear.keys())[-31:-1]
recentStarts = [winterStartByYear[a] for a in recentYears]
avgStart = sum(recentStarts)/len(recentStarts)
recentEnds = [winterEndByYear[a] for a in recentYears]
avgEnd = sum(recentEnds)/len(recentEnds)
print("Avg start:", datetime.date(year,1,1)+datetime.timedelta(avgStart))
print("Avg end:", datetime.date(year,1,1)+datetime.timedelta(avgEnd))
