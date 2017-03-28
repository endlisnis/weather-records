# -*- coding: utf-8 -*-
from __future__ import print_function
from math import sqrt
def linreg(X, Y):
    """
    Summary
        Linear regression of y = ax + b
    Usage
        real, real, real = linreg(list, list)
    Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value
    """
    if len(X) != len(Y):  raise ValueError('unequal length')
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det
    meanerror = residual = 0.0
    for x, y in zip(X, Y):
        meanerror = meanerror + (y - Sy/N)**2
        residual = residual + (y - a * x - b)**2

    RR = None
    if meanerror != 0:
        RR = 1 - residual/meanerror
    #ss = residual / (N-2)
    #Var_a, Var_b = ss * N / det, ss * Sxx / det
    #print "y=ax+b"
    #print "N= %d" % N
    #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, sqrt(Var_a))
    #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, sqrt(Var_b))
    #print "R^2= %g" % RR
    #print "s^2= %g" % ss
    return a, b, RR

def movingAverage(data, distance):
    ret = []
    for i in range(len(data) - distance + 1):
        total = 0
        for j in range(i, i+distance):
            total += data[j][1]
        ret.append((data[i+distance-1][0], total/distance))
    return ret

def linearTrend(data):
    linearX = [d[0] for d in data]
    linearY = [float(d[1]) for d in data]
    (m,b,RR) = linreg(linearX, linearY)

    lineFit = []
    for x,y in data:
        lineFit.append((x,m*x+b))

    return lineFit

def linearExtra(data):
    linearX = [d[0] for d in data]
    linearY = [d[1] for d in data]
    (m,b,RR) = linreg(linearX, linearY)
    return m * (linearX[-1]+1) + b
