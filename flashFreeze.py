#!/usr/bin/python3
# -*- coding: utf-8 -*-
import hourly, sys, copy, datetime
from collections import deque

data = hourly.load('ottawa')

records = []
recordNames = []

def main(field, duration, drop, maxAbove=None, minBelow=None):
    record = 0
    recordVal = None
    lastDate = None
    temps = deque()
    for date in sorted(data.keys()):
        if field == 'temp':
            val = data[date].TEMP
        elif field == 'windchill':
            val = data[date].windchill
        temps.append(val)
        if len(temps) > duration:
            temps.popleft()
        if val != None:
            maxV = max(filter(lambda t: t!=None, temps))
            minV = min(filter(lambda t: t!=None, temps))
            #indexOfMin = temps.index(minV)
            indexOfMax = temps.index(maxV)
            thisDrop = maxV - minV

            #if maxV > 0 and val < 0 and thisDrop >= drop: # and lastDate != date.date():
            if (indexOfMax == 0 #len(temps)-1
                and (maxAbove == None or maxV >= maxAbove)
                and (minBelow == None or val <= minBelow)
                and thisDrop >= drop
            ):
                #and thisDrop < drop and len(temps) == duration and None not in temps):
                print('Flash freeze: ', date, maxV, val, thisDrop, temps)
                records.append(copy.copy(temps))
                recordNames.append(date)
                if thisDrop > record:
                    record = thisDrop
                    recordVal = (date, maxV, val, thisDrop)
                #lastDate = date.date()
    print(recordVal)

    print('---')

    i = 0
    while i < len(recordNames):
        if i < len(recordNames)-1:
            if recordNames[i+1] - recordNames[i] < datetime.timedelta(hours=duration):
                firstMin = min(filter(lambda t: t!=None, records[i]))
                firstMax = max(filter(lambda t: t!=None, records[i]))
                secondMin = min(filter(lambda t: t!=None, records[i+1]))
                secondMax = max(filter(lambda t: t!=None, records[i+1]))
                firstDiff = firstMax - firstMin
                secondDiff = secondMax - secondMin
                if firstDiff < secondDiff:
                    print("Skipping %d" % i, recordNames[i])
                    del recordNames[i]
                    del records[i]
                    i = 0
                    continue
        if i > 0:
            if recordNames[i] - recordNames[i-1] < datetime.timedelta(hours=duration):
                firstMin = min(filter(lambda t: t!=None, records[i-1]))
                firstMax = max(filter(lambda t: t!=None, records[i-1]))
                secondMin = min(filter(lambda t: t!=None, records[i]))
                secondMax = max(filter(lambda t: t!=None, records[i]))
                firstDiff = firstMax - firstMin
                secondDiff = secondMax - secondMin
                if firstDiff >= secondDiff:
                    print("Skipping %d" % i, recordNames[i])
                    del recordNames[i]
                    del records[i]
                    i = 0
                    continue
        i += 1

    for name in recordNames:
        sys.stdout.write(str(name).replace(' ', '_')+'\t')
    print()
    for i in range(len(records[0])):
        for j in range(len(records)):
            if records[j][i] is None:
                sys.stdout.write('"None"\t')
            else:
                maxV = max(filter(lambda t: t is not None, records[j]))
                sys.stdout.write('%f\t' % (records[j][i]-maxV) )
        print()

if __name__ == '__main__':
    #field = sys.argv[1]
    #field = {'temp': hourly.TEMP, 'windchill': hourly.weather.daily.MAX_TEMP}[sys.argv[3]]

    #main('temp', 37, 31, None, None)
    main('windchill', duration=13, drop=29.7)

#main('temp', 5, 11.4)

#import flashFreeze
#flashFreeze.main('temp', 36, 30.0, None, None)
