#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime, time, sys
from monthName import monthName
import argparse
from dailyFilters import *

import snow, daily, fieldOperators

class AvgTemp(fieldOperators.OpWithFlag):
    def __init__(self):
        fieldOperators.OpWithFlag.__init__(self, daily.MAX_TEMP, None)
    def __call__(self, data):
        if ( data.MIN_TEMP_FLAG == 'M'
             or data.MAX_TEMP_FLAG == 'M'
             or len(data.MIN_TEMP) == 0
             or len(data.MAX_TEMP) == 0
         ):
            return None, 'M'
        return (float(data.MIN_TEMP) + float(data.MAX_TEMP))/2,
    @property
    def englishName(self):
        return 'Average temperature'
    @property
    def name(self):
        return 'AVG_TEMP'

# day-before-yesterday's month and year
defaultMonth = (datetime.date.today()-datetime.timedelta(2)).month
defaultYear = (datetime.date.today()-datetime.timedelta(2)).year
city = 'ottawa'

from collections import namedtuple

parser = argparse.ArgumentParser(description='Determine the last time a field has been this high/low.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--year', type=int, default=defaultYear)
parser.add_argument('--month', type=int, default=defaultMonth)
parser.add_argument('--meantemp', action='store_true')
parser.add_argument('--avgtemp', action='store_true')
parser.add_argument('--maxtemp', action='store_true')
parser.add_argument('--maxtempcum', action='store_true')
parser.add_argument('--mintemp', action='store_true')
parser.add_argument('--mintempcum', action='store_true')
parser.add_argument('--maxhumidex', action='store_true')
parser.add_argument('--forecast', action='store_true')
parser.add_argument('--rain', action='store_true')
parser.add_argument('--snow', action='store_true')
parser.add_argument('--snowpack', action='store_true')
parser.add_argument('--windchill', action='store_true')
parser.add_argument('--humidity', action='store_true')
parser.add_argument('--wind', action='store_true')

args = parser.parse_args()

month = args.month
year = args.year
city = args.city

nextMonthYear = (year*12+month)//12
nextMonthMonth = month%12+1

print(year, month, nextMonthYear, nextMonthMonth)

if args.humidity:
    snow.createPlot(city,
                    running=False,
                    field=daily.MEAN_HUMIDITY,
                    otheryears=(),
                    name = monthName(month) + "MeanHumidity",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=daily.MEAN_HUMIDITY,
                    otheryears=(),
                    name = monthName(month) + "MeanHumidityCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    exit(0)

if args.wind:
    snow.createPlot(city,
                    running=False,
                    field=daily.AVG_WIND,
                    otheryears=(),
                    name = monthName(month) + "AvgWind",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    snow.createPlot(city,
                    running=True,
                    field=daily.AVG_WIND,
                    otheryears=(),
                    name = monthName(month) + "AvgWindCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    exit(0)

if args.maxtempcum:
    snow.createPlot(city,
                    running=True,
                    field=daily.MAX_TEMP,
                    otheryears=(),
                    name = monthName(month) + "MaxTempCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.meantemp:
    snow.createPlot(city,
                    running=True,
                    field=ExprVal('meanTemp'
                                  ' if ("M" not in meanTempFlag and "I" not in meanTempFlag)'
                                  ' else ((max+min)/2'
                                  '  if ("M" not in minFlag and "I" not in minFlag'
                                  '      and "M" not in maxFlag and "I" not in maxFlag)'
                                  '  else None)',
                                  name="Mean temperature",
                                  title="Mean temperature",
                                  units="℃",
                                  unit="℃",
                                  precision=2,
                                  field=daily.MEAN_TEMP,
                                  description='avg. hourly temp'),
                    otheryears=(),
                    name = monthName(month) + "MeanTempCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    snow.createPlot(city,
                    running=False,
                    field=ExprVal('meanTemp'
                                  ' if ("M" not in meanTempFlag and "I" not in meanTempFlag)'
                                  ' else ((max+min)/2'
                                  '  if ("M" not in minFlag and "I" not in minFlag'
                                  '      and "M" not in maxFlag and "I" not in maxFlag)'
                                  '  else None)',
                                  name="Mean temperature",
                                  title="Mean temperature",
                                  units="℃",
                                  unit="℃",
                                  precision=2,
                                  field=daily.MEAN_TEMP,
                                  description='avg. hourly temp'),
                    otheryears=(),
                    name = monthName(month) + "MeanTemp",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.avgtemp:
    snow.createPlot(city,
                    running=True,
                    field=AvgTemp(),
                    otheryears=(),
                    name = monthName(month) + "AvgTempCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    snow.createPlot(city,
                    running=False,
                    field=AvgTemp(),
                    otheryears=(),
                    name = monthName(month) + "AvgTemp",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.maxtemp:
    snow.createPlot(city,
                    running=False,
                    field=daily.MAX_TEMP,
                    otheryears=(),
                    name = monthName(month) + "MaxTemp",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

    for t in range(15,35):
        snow.createPlot(city,
                        running=True,
                        field=fieldOperators.AtLeastWithFlagBoolean(daily.MAX_TEMP, t),
                        otheryears=(),
                        name = monthName(month) + "MaxTempAtLeast{:02}".format(t),
                        dataStartDay = datetime.date(year, month,   1),
                        plotStartDay = datetime.date(year, month,   1),
                        plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                        plotYMin = None)

if args.maxhumidex:
    snow.createPlot(city,
                    running=False,
                    field=daily.MAX_HUMIDEX,
                    otheryears=(),
                    name = monthName(month) + "MaxHumidex",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.mintempcum:
    snow.createPlot(city,
                    running=True,
                    field=daily.MIN_TEMP,
                    otheryears=(),
                    name = monthName(month) + "MinTempCumulative",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.mintemp:
    snow.createPlot(city,
                    running=False,
                    field=daily.MIN_TEMP,
                    otheryears=(),
                    name = monthName(month) + "MinTemp",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)
    for t in range(-20, 1):
        snow.createPlot(city,
                        running=True,
                        field=fieldOperators.AtMostWithFlagBoolean(daily.MIN_TEMP, t),
                        otheryears=(),
                        name = monthName(month) + "MinTempAtMost{:-02}".format(t),
                        dataStartDay = datetime.date(year, month,   1),
                        plotStartDay = datetime.date(year, month,   1),
                        plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                        plotYMin = None)

if args.windchill:
    snow.createPlot(city,
                    running=False,
                    field=daily.MIN_WINDCHILL,
                    otheryears=(),
                    name = monthName(month) + "MinWindchill",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    plotYMin = None)

if args.rain:
    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_RAIN_MM,
                    otheryears=(),
                    name = monthName(month) + "Rain",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    legendLocation = "on top left")

    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_PRECIP_MM,
                    otheryears=(),
                    name = monthName(month) + "Precip",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    legendLocation = "on top left")

    snow.createPlot(city,
                    running=True,
                    field=fieldOperators.GreaterThanWithFlagBoolean(daily.TOTAL_RAIN_MM,10),
                    otheryears=(),
                    name = monthName(month) + "RainAbove10mm",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1),
                    legendLocation = "on top left")


if args.snow:
    snow.createPlot(city,
                    running=True,
                    field=daily.TOTAL_SNOW_CM,
                    otheryears=(),
                    name = monthName(month) + "Snow",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1))
    #plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1))

if args.snowpack:
    snow.createPlot(city,
                    running=False,
                    field=daily.SNOW_ON_GRND_CM,
                    otheryears=(),
                    name = monthName(month) + "SnowDepth",
                    dataStartDay = datetime.date(year, month,   1),
                    plotStartDay = datetime.date(year, month,   1),
                    plotEndDay   = datetime.date(nextMonthYear, nextMonthMonth, 1))

if args.forecast:
    snow.createPlot(city,
                    running=False,
                    field=daily.MAX_TEMP,
                    otheryears=(),
                    name = "ForecastMaxTemp",
                    dataStartDay = datetime.date.today() - datetime.timedelta(20),
                    plotStartDay = datetime.date.today() - datetime.timedelta(20),
                    plotEndDay   = datetime.date.today() + datetime.timedelta(8),
                    plotYMin = None)
    snow.createPlot(city,
                    running=False,
                    field=daily.MIN_TEMP,
                    otheryears=(),
                    name = "ForecastMinTemp",
                    dataStartDay = datetime.date.today() - datetime.timedelta(20),
                    plotStartDay = datetime.date.today() - datetime.timedelta(20),
                    plotEndDay   = datetime.date.today() + datetime.timedelta(8),
                    plotYMin = None)
