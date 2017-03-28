#!/usr/bin/python3
import datetime, time, sys
from monthName import monthName
import snow, daily, fieldOperators
import argparse


# day-before-yesterday's month and year
defaultMonth = (datetime.date.today()-datetime.timedelta(2)).month
defaultYear = (datetime.date.today()-datetime.timedelta(2)).year
city = 'ottawa'

from collections import namedtuple

parser = argparse.ArgumentParser(description='Determine the last time a field has been this high/low.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--year', type=int, default=defaultYear)
parser.add_argument('--startmonth', type=int, default=1)
parser.add_argument('--startday', type=int, default=1)
parser.add_argument('--meantemp', action='store_true')
parser.add_argument('--maxtemp', action='store_true')
parser.add_argument('--maxtempcum', action='store_true')
parser.add_argument('--mintemp', action='store_true')
parser.add_argument('--mintempcum', action='store_true')
parser.add_argument('--maxhumidex', action='store_true')
parser.add_argument('--for', action='store_true')
parser.add_argument('--rain', action='store_true')
parser.add_argument('--precip', action='store_true')
parser.add_argument('--snow', action='store_true')
parser.add_argument('--snowpack', action='store_true')
parser.add_argument('--windchill', action='store_true')
parser.add_argument('--humidity', action='store_true')
parser.add_argument('--all', action='store_true')
parser.add_argument('--other-years')

args = parser.parse_args()

year = args.year
city = args.city
otherYears = args.other_years
if type(otherYears) is str:
    otherYears = tuple(map(int, otherYears.split(',')))

plotStartDay = datetime.date.today()-datetime.timedelta(20)
plotEndDay = datetime.date.today()+datetime.timedelta(8)
dataStartDay = datetime.date(year, args.startmonth, args.startday)

if args.maxtempcum or args.all:
    snow.createPlot(city,
                    running=True,
                    field=daily.MAX_TEMP,
                    otheryears=otherYears,
                    name = "{}MaxTempCumulative".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=daily.MEAN_TEMP,
                    otheryears=otherYears,
                    name = "{}MeanTempCumulative".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

if args.maxtemp or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.MAX_TEMP,
                    otheryears=(),
                    name = "{}MaxTemp".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

    for t in range(28,35):
        snow.createPlot(city,
                        running=True,
                        field=fieldOperators.AtLeastWithFlagBoolean(daily.MAX_TEMP, t),
                        otheryears=otherYears,
                        name = "{}MaxTempAtLeast{:02}".format(year, t),
                        dataStartDay = dataStartDay,
                        plotStartDay = plotStartDay,
                        plotEndDay   = plotEndDay,
                        plotYMin = None)

if args.meantemp or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.MEAN_TEMP,
                    otheryears=(),
                    name = "{}MeanTemp".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=daily.MEAN_TEMP,
                    otheryears=(),
                    name = "{}MeanTempCumulative".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

if args.maxhumidex or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.MAX_HUMIDEX,
                    otheryears=(),
                    name = "{}MaxHumidex".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=fieldOperators.AtLeastWithFlagBoolean(daily.MAX_HUMIDEX,40),
                    otheryears=(),
                    name = "{}MaxHumidexAtLeast40".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

if args.mintempcum or args.all:
    snow.createPlot(city,
                    running=True,
                    field=daily.MIN_TEMP,
                    otheryears=(),
                    name = "{}MinTempCumulative".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

if args.mintemp or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.MIN_TEMP,
                    otheryears=(),
                    name = "{}MinTemp".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=fieldOperators.AtMostWithFlagBoolean(daily.MIN_TEMP,-20),
                    otheryears=(),
                    name = "{}MinTempAtMost-20".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)
    for t in range(10,20):
        snow.createPlot(city,
                        running=True,
                        field=fieldOperators.AtMostWithFlagBoolean(daily.MIN_TEMP, t),
                        otheryears=(),
                        name = "{}MinTempAtMost{:02}".format(year, t),
                        dataStartDay = dataStartDay,
                        plotStartDay = plotStartDay,
                        plotEndDay   = plotEndDay,
                        plotYMin = None)

if args.windchill or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.MIN_WINDCHILL,
                    otheryears=(),
                    name = "{}MinWindchill".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay,
                    plotYMin = None)

if args.rain or args.all:
    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_RAIN_MM,
                    otheryears=otherYears,
                    name = "{}Rain".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay)
                    #plotDate = plotEndDay-datetime.timedelta(1))

    #snow.createPlot(city,
    #                running=True,
    #                field=fieldOperators.GreaterThanWithFlagBoolean(daily.TOTAL_RAIN_MM,10),
    #                otheryears=(),
    #                name = "{}RainAbove10mm".format(year),
    #                dataStartDay = dataStartDay,
    #                plotStartDay = plotStartDay,
    #                plotEndDay   = plotEndDay)

if args.precip or args.all:
    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_PRECIP_MM,
                    otheryears=(),
                    name = "{}Precip".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay)


if args.snow or args.all:
    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_SNOW_CM,
                    otheryears=(),
                    name = "{}Snow".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay)
    #plotEndDay   = plotEndDay)

if args.snowpack or args.all:
    snow.createPlot(city,
                    running=False,
                    field=daily.SNOW_ON_GRND_CM,
                    otheryears=(),
                    name = "{}SnowDepth".format(year),
                    dataStartDay = dataStartDay,
                    plotStartDay = plotStartDay,
                    plotEndDay   = plotEndDay)
