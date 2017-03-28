#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import daily, annualAverages, sets, gnuplot

def getValuesByYear(cityName, field, cumulative):
    cityData = daily.load(cityName)
    cityYearValues = annualAverages.getAnnualValues(cityData, field, cumulative)
    cityValuesByYear = {}
    for year, value in cityYearValues:
        cityValuesByYear[year] = value
    return cityValuesByYear

def plotDifference(city1Name, city2Name, field, cumulative):
    city1ByYear = getValuesByYear(city1Name, field, cumulative)
    city2ByYear = getValuesByYear(city2Name, field, cumulative)
    #
    bothYears = sorted(list(sets.Set(city1ByYear.keys()) & sets.Set(city2ByYear.keys())))
    #
    plotData = []
    for year in bothYears:
        diff = city2ByYear[year] - city1ByYear[year]
        print "%d: %.1f" % (year, diff)
        plotData.append((year, diff))
    #
    plot = gnuplot.Plot("%s_minus_%s_Annual_%s" % ('farm', 'ottawa', daily.fields[field].name), yaxis=2)
    plot.open()
    plot.addLine(gnuplot.Line("Temp", plotData, lineColour='purple', plot='boxes'))
    plot.plot()
    plot.close()

plotDifference('ottawa', 'farm', daily.MEAN_TEMP, False)
plotDifference('ottawa', 'farm', daily.MAX_TEMP, False)
plotDifference('ottawa', 'farm', daily.MIN_TEMP, False)
plotDifference('ottawa', 'farm', daily.TOTAL_SNOW_CM, True)
plotDifference('ottawa', 'farm', daily.TOTAL_RAINFALL_MM, True)
