#!/usr/bin/python3
import hourly
import fnmatch, time, sys
import argparse

parser = argparse.ArgumentParser(description='Determine the last time has changed this much in an hour.')
parser.add_argument('-f', help='Field')
parser.add_argument('--city', default='ottawa')
parser.add_argument('-m', help='Mask', default=['*'], nargs='*')
parser.add_argument('--mindrop')
args = parser.parse_args()

data = hourly.load(args.city)

dropThresh = args.mindrop
if dropThresh != None:
    dropThresh = float(dropThresh)

masks = args.m
maxDrop = 0.0
maxRise = 0.0
lastV = None
for dateTime in reversed(sorted(data.keys())):
    #print dateTime
    date = dateTime.date()
    if ( len(data[dateTime].TEMP) > 0
         and any(map(lambda d:fnmatch.fnmatch(str(date), d), masks)) ):
        v = Fraction(data[dateTime].TEMP)
        #print v
        if lastV != None:
            diff = lastV - v
            if diff >= maxRise:
                maxRise = diff
                if dropThresh == None:
                    print('%s: %+5.1f, %+5.1f: %+5.1f' % (dateTime, v, lastV, diff))
            if diff <= maxDrop:
                maxDrop = diff
                if dropThresh == None:
                    print('%s: %+5.1f, %+5.1f: %+5.1f' % (dateTime, v, lastV, diff))
            if dropThresh != None and abs(diff) >= dropThresh:
                print('%s: %+5.1f, %+5.1f: %+5.1f' % (dateTime, v, lastV, diff))

        lastV = v
    else:
        lastV = None
