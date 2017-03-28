#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time, posix, daily, gnuplot, linear, sys, datetime, numpy
from dailyFilters import *

def yearlySum(cityData, year, field):
    sum = 0
    count = 0
    fakeCount = 0
    for date in daily.dayRange(datetime.date(year,1,1), datetime.date(year+1,1,1)):
        try:
            val = field(cityData[date])
            if val != None:
                sum += val
                count += 1
            elif len(cityData[date].MAX_TEMP) > 0:
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
    for year in range(cityData.minYear, beforeYear):
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
    for year in range(cityData.minYear, beforeYear):
        (ysum, ycount) = yearlySum(cityData, year, field)
        sum += ysum
        count += 1

    avg = None
    if count:
        avg = sum/count
    return avg

def getAnnualValues(cityData, field, cumulative):
    data = []
    for year in range(1959, cityData.maxYear+1):
        thisYearSum, thisYearCount = yearlySum(cityData, year, field)

        if thisYearCount > 300:
            v = thisYearSum
            if not cumulative:
                v /= thisYearCount
            data.append((year, v))
    return data

co2 = [315.9741666667,       316.9075,       317.6375,       318.4508333333,       318.9941666667,       319.2044444444,
       319.985,       321.3833333333,       322.1575,       323.045,       324.6241666667,       325.68,
       326.32,       327.4533333333,       329.6766666667,       330.1775,       331.1290909091,       332.0533333333,
       333.7816666667,       335.4091666667,       336.7816666667,       338.6791666667,       340.1,       341.4366666667,
       343.025,       344.3809090909,       346.0416666667,       347.3841666667,       349.1608333333,       351.5633333333,
       353.0675,       354.3475,       355.5666666667,       356.3825,       357.0675,       358.8225,       360.7958333333,
       362.5875,       363.705,       366.6525,       368.3258333333,       369.525,       371.13,       373.215,
       375.7741666667,       377.4908333333,       379.8,       381.9041666667,       383.7641666667,       385.585,
       387.3666666667,       389.845,       391.6258333333,       393.8191666667,       396.4816666667]

def co2Error(tempData, m, b):
    totalError = []
    for i in range(1, len(tempData)):
        year, val = data[i]
        co2fv = co2[i]*m+b
        totalError.append( (co2fv - val)**2 )
    return numpy.average(totalError) ** .5


if __name__=="__main__":
    city='ottawa'

    cityData = daily.load(city)

    field = Avg(daily.MAX_TEMP, daily.MIN_TEMP, 'average temperature')
    fname = field.name
    print fname
    data = getAnnualValues(cityData, field, False)
    lineFit = linear.linearTrend(data)

    co2Fit = []
    co2FitError = []
    progressiveLineFit = []
    progressiveError = []
    lineFitError = []
    sameError = [] # each year is the same as the last

    for i in range(len(data)):
        year, val = data[i]
        lfitv = lineFit[i][1]
        co2fv = co2[i]*0.021310-1.300000 #minErr: m=0.021310, b=-1.300000, err=5.263987
        co2Fit.append( (year, co2fv) )
        if i > 0:
            progressivePrediction = linear.linearExtra(data[:(i+1)])
            progressiveLineFit.append( (year+1, progressivePrediction) )
            progressiveError.append( abs(progressivePrediction - val) )
            lineFitError.append( abs(lfitv - val) )
            sameError.append( abs(float(data[i-1][1] - val)) )
            co2FitError.append( abs(co2fv - val) )
        print year, float(val), lfitv


    co2ErrorBarSize = sorted(co2FitError)[len(co2FitError)*95/100]
    co2ErrorBarPlot = []
    for year, val in co2Fit:
        co2ErrorBarPlot.append( (year, val, co2ErrorBarSize) )

    plot = gnuplot.Plot("%s/Annual_Prediction_%s" % (city, fname), yaxis=2)
    plot.open(title='%s %s per year' % (city.capitalize(), field.title),
              ylabel = '%s in %s' % (field.title, field.units) )
    plot.addLine(gnuplot.Line("Linear", lineFit, lineColour='green', plot='lines'))
    plot.addLine(gnuplot.Line("Extrapolation", progressiveLineFit,
                              lineColour='red', plot='lines'))
    plot.addLine(gnuplot.Line("Co2", co2Fit, lineColour='blue'))
    plot.addLine(gnuplot.Line("Co2 Error", co2ErrorBarPlot, lineColour='blue', plot='errorbars'))
    plot.addLine(gnuplot.Line("Temp", data, lineColour='purple'))
    plot.plot()
    plot.close()

    for label, errors in (('progressive', progressiveError),
                          ('lineFit', lineFitError),
                          ('same', sameError),
                          ('co2Fit', co2FitError)):
        print ( '%sError: %.2f +/- %.2f'
                % ( label,
                    numpy.average([e*e for e in errors]) ** .5,
                    numpy.average(errors) ) )

    bmin=-20
    bmax=-10
    minErr = 99

    sys.stdout.write('        ')
    for bi in range(bmin,bmax):
        b = bi/10.0
        sys.stdout.write('| %5.1f ' % b)
    sys.stdout.write('\n')
    sys.stdout.write('       ')
    for bi in range(bmin,bmax):
        sys.stdout.write('--------')
    sys.stdout.write('\n')
    for mi in range(2099, 2191, 1):
        m = mi / 100000.0
        sys.stdout.write(' %7.5f ' % m)
        for bi in range(bmin,bmax):
            b = bi/10.0
            err = co2Error(data, m, b)
            if err < minErr:
                minErr = err
                minErrM = m
                minErrB = b
            sys.stdout.write('| %7.4f ' % err)
        sys.stdout.write('\n')
    print 'minErr: m=%f, b=%f, err=%f' % (minErrM, minErrB, minErr)
