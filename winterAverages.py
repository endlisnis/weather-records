#!/usr/bin/python3
import time, posix, daily, gnuplot, linear, sys, datetime
from dailyFilters import *
from monthName import monthName

START_MONTH=7
START_DAY=1
END_MONTH=7
END_DAY=1

def START_DATE(year):
    return datetime.date(year,START_MONTH,START_DAY)

def END_DATE(year):
    return datetime.date(year+1,END_MONTH,END_DAY)

TOTAL_COUNT = 30

def yearlySum(cityData, year, field):
    sum = 0
    count = 0
    fakeCount = 0
    for date in daily.dayRange(START_DATE(year), END_DATE(year)):
        #print date
        try:
            val = field(cityData[date])
            if val != None:
                sum += val
                count += 1
            elif cityData[date].MAX_TEMP is not None:
                fakeCount += 1
        except KeyError:
            pass

    if count > 30:
        count += fakeCount
    return (sum, count)

def yearlyAverage(cityData, year, field):
    (sum, count) = yearlySum(cityData, year, field)

    avg = None
    if count:
        avg = sum/count
    return avg

def normalYearlyAverage(cityData, beforeYear, field):
    sum = 0
    count = 0
    for year in range(beforeYear-31, beforeYear):
        (ysum, ycount) = yearlySum(cityData, year, field)
        sum += ysum
        count += ycount

    avg = None
    if count:
        avg = sum/count

    #print 'debug: m=%d, f=%d, s=%d, c=%d, a=%d' % (month, field, sum, count, avg)
    return avg

def normalYearlySum(cityData, beforeYear, field):
    sum = 0
    count = 0
    for year in range(beforeYear-31, beforeYear):
        (ysum, ycount) = yearlySum(cityData, year, field)
        sum += ysum
        count += 1

    avg = None
    if count:
        avg = sum/count
    return avg

def getAnnualValues(cityData, field, cumulative):
    data = []
    for year in range(cityData.minYear, cityData.maxYear+1):
        thisYearSum, thisYearCount = yearlySum(cityData, year, field)

        if thisYearCount >= TOTAL_COUNT*8/10:
            v = thisYearSum
            if not cumulative:
                v /= thisYearCount
            data.append((year, v))
    return data


if __name__=="__main__":
    city=sys.argv[1]

    for arg in sys.argv[2:]:
        if arg.startswith('-start='):
            (START_MONTH, START_DAY) = map(int, arg.split('=')[1].split(','))
        if arg.startswith('-end='):
            (END_MONTH, END_DAY) = map(int, arg.split('=')[1].split(','))

    print(START_MONTH, START_DAY, END_MONTH, END_DAY)
    cityData = daily.load(city)

    for field in [
            #FractionVal(daily.MIN_WINDCHILL, "windchill"),
            Avg(daily.MAX_TEMP, daily.MIN_TEMP, 'average temperature'),
            FractionVal(daily.AVG_WIND, 'wind'),
            #FractionVal(daily.SNOW_ON_GRND_CM, 'average snow depth'),
    ]:
        fname = field.name
        print(fname)
        data = getAnnualValues(cityData, field, False)
        assert len(data)
        for year, val in data:
            print('%u: %.1f' % (year, val))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("%s/svg/Winter_%s" % (city, fname), yaxis=2)
        plot.open(title='%s %s per winter (%s %u to %s %u)'
                  % (city.capitalize(), field.title,
                     monthName(START_MONTH), START_DAY,
                     monthName(END_MONTH), END_DAY) )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Temp", data, lineColour='purple'))
        plot.plot()
        plot.close()
        print('30-year average: %.1f' % normalYearlyAverage(cityData, 2014, field))

    for field in [FractionVal(daily.TOTAL_SNOW_CM, 'snow')]:
        fname = field.name
        print(fname)
        data = getAnnualValues(cityData, field, True)
        assert len(data)
        for year, val in data:
            print('%u: %8.1f' % (year, val))

        lineFit = linear.linearTrend(data)

        plot = gnuplot.Plot("%s/svg/Winter_%s" % (city, fname), yaxis=2)
        plot.open(title='%s %s per winter (%s %u to %s %u)'
                  % (city.capitalize(), field.title,
                     monthName(START_MONTH), START_DAY,
                     monthName(END_MONTH), END_DAY),
                  ymin=0 )
        plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
        plot.addLine(gnuplot.Line("Amount", data, lineColour='purple'))
        plot.plot()
        plot.close()
        print('30-year average: %.1f' % normalYearlySum(cityData, 2014, field))
