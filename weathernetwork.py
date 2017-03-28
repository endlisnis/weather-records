#!python
import glob, re, datetime, daily, dailyRecords
from collections import namedtuple
from namedList import *

def getDateFromPath(path):
    (folder, fname) = path.split('/')
    (year, month, day, rest) = fname.split('.', 3)

    return datetime.date( int(year), int(month), int(day) )


def get14Days(startDate):
    ret = {}
    for date in daily.dayRange( startDate + datetime.timedelta(1),
                                startDate + datetime.timedelta(15) ):
        ret[date.strftime('<td class="date">%A<br />%b. ') + '%d</td>' % date.day] = date
    return ret

data = daily.load('ottawa')

LowHigh = namedStruct('LowHigh', 'forecastLow forecastHigh normalLow normalHigh')
deviationsByDay = []
for day in range(14):
    deviationsByDay.append( LowHigh(forecastLow=[], forecastHigh=[], normalLow=[], normalHigh=[] ) )

for fname in glob.glob('WeatherNetwork/*.html'):
    print fname
    forecastIssued = getDateFromPath(fname)
    futureDays = get14Days(forecastIssued)

    high = None
    low = None
    curDay = None

    for line in file(fname):
        strippedLine = line.strip()

        if strippedLine.startswith('<td class='):
            if strippedLine in futureDays:
                curDay = futureDays[strippedLine]
                #print "%s, %d" % (curDay, (curDay-forecastIssued).days)
                high = None
                low = None
            else:
                search = re.search('<td class="(.*)">([-0-9]*)</td>', strippedLine)
                if search != None:
                    (label, temperature) = search.groups()
                    if temperature != '-':
                        if label == 'high':
                            high = int(temperature)
                        elif label == 'low lbtext':
                            low = int(temperature)
        if strippedLine == '</tr>' and low != None and high != None:
            forecastOffset = (curDay-forecastIssued).days
            print "%s(%d): Low %d, High %d" % (curDay, forecastOffset, low, high)
            lowRec = dailyRecords.getInfo('ottawa', curDay, daily.MIN_TEMP)
            highRec = dailyRecords.getInfo('ottawa', curDay, daily.MAX_TEMP)

            if lowRec.recent != None and highRec.recent != None:
                actualLow = lowRec.recent
                actualHigh = highRec.recent
                deviation = LowHigh(low - actualLow, high - actualHigh, low - lowRec.avg, high - highRec.avg)

                deviationsByDay[forecastOffset-1].forecastLow.append(deviation.forecastLow)
                deviationsByDay[forecastOffset-1].forecastHigh.append(deviation.forecastHigh)
                deviationsByDay[forecastOffset-1].normalLow.append(deviation.normalLow)
                deviationsByDay[forecastOffset-1].normalHigh.append(deviation.normalHigh)

                print "actual: Low %s, High %s" % (data[curDay].MIN_TEMP, data[curDay].MAX_TEMP)
                print "forecast error(%d): Low %.1f, High %.1f" % (forecastOffset, low - actualLow, high - actualHigh)

def error(errors):
    if len(errors) == 0:
        return (0, 0)
    errorAvg = sum(errors) / len(errors)
    errorSquaredSum = 0
    for v in errors:
        errorSquaredSum += v*v
    stddev = (errorSquaredSum / len(errors)) ** .5

    return errorAvg, stddev

for (dayoffset, deviations) in enumerate(deviationsByDay):
    forecastErrorLow = error(deviations.forecastLow)
    forecastErrorHigh = error(deviations.forecastHigh)
    normalErrorLow = error(deviations.normalLow)
    normalErrorHigh = error(deviations.normalHigh)

    print('%d) low: %.1f (%.1f -- %.1f)  high: %.1f (%.1f -- %.1f)'
          % (dayoffset,
             forecastErrorLow[0], forecastErrorLow[1], normalErrorLow[1],
             forecastErrorHigh[0], forecastErrorHigh[1], normalErrorHigh[1]) )
