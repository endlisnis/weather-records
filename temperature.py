#!/usr/bin/python
from __future__ import print_function
import sys, datetime, daily, ps, forecast, sys, dailyRecords
from collections import namedtuple

city = sys.argv[1]
historyDays = int(sys.argv[2])
now = forecast.now

daily.load(city)

Temp_MinMax = namedtuple('Temp_MinMax', 'min max')

def getTempData():
    history = Temp_MinMax({}, {})

    for daysOffset in range(-historyDays, 8+1):
	date = now+datetime.timedelta(daysOffset)

        history.min[date] = dailyRecords.getInfo(city, date, daily.MIN_TEMP)
        history.max[date] = dailyRecords.getInfo(city, date, daily.MAX_TEMP)

    return history

class COLDER():
    __slots__ = ()

class WARMER():
    __slots__ = ()

def getValue(date, findex):
    try:
	value = daily.dataByCity[city][date][findex]
	if len(value):
	    return Fraction(value)
    except KeyError:
        pass
    return None

def daysSince(state, field, temperature):
    findex = field.index
    for days in range(1,8000):
	val = getValue(now-datetime.timedelta(days), findex)
	if val != None:
	    if (state == COLDER and temperature > val) or (state == WARMER and temperature < val):
		return days
    return None

def historyLine(history, tag):
    ret = []

    for key in sorted(history.keys()):
	if tag == 'avg':
	    ret.append((key.toordinal(), history[key].normal))
	elif tag == 'min':
	    ret.append((key.toordinal(), history[key].min.value))
	elif tag == 'max':
	    ret.append((key.toordinal(), history[key].max.value))
	elif tag == 'recent':
	    ret.append((key.toordinal(), history[key].recent))

    return ret


def plotForecastData():

    days = forecast.getForecastData(city)

    ps.header(title = city+"/forecast.ps", creator = "forecast3.py")

    colour = {'low': "0 0 1", 'high': "1 0 0"}

    history = getTempData()
    #print history
    ps.plotline(historyLine(history.min, 'avg'), colour="1 1 0")  #avg low
    ps.plotline(historyLine(history.min, 'min'), colour="0 1 1")  #min low
    ps.plotline(historyLine(history.min, 'max'), colour="0 1 1", dash="[0.2 0.5] 0")  #max low

    ps.plotline(historyLine(history.max, 'avg'), colour="0 1 0")  #avg high
    ps.plotline(historyLine(history.max, 'max'), colour="1 0 1")  #max high
    ps.plotline(historyLine(history.max, 'min'), colour="1 0 1", dash="[0.2 0.5] 0")  #min high

    ps.plotline(historyLine(history.min, 'recent'), colour="0 0 1")
    ps.plotline(historyLine(history.max, 'recent'), colour="1 0 0")

    itemnames = {0:'low', 1:'high'}
    for i in range(len(history)):
	item = history[i]
	for day in item:
	    if item[day].recent != None:
		if item[day].recent > item[day].max.value:
		    print "%s: Record maximum %s %s, beats %s in %d" % (day, itemnames[i], float(item[day].recent), float(item[day].max.value), item[day].max.year)
		if item[day].recent < item[day].min.value:
		    print "%s: Record minimum %s %s, beats %s in %d" % (day, itemnames[i], float(item[day].recent), float(item[day].min.value), item[day].min.year)

    indexFromTag = {'low':0, 'high':1}

    for tag in ('low', 'high'):
	line = []
	for day in sorted(days.keys()):
	    if tag in days[day] and days[day][tag] != None:
		if days[day][tag] > history[indexFromTag[tag]][day].max.value:
		    print("%s: Forecast record maximum %s %s, would beat %s in %d" %
                          (day, tag, float(days[day][tag]), float(history[indexFromTag[tag]][day].max.value), history[indexFromTag[tag]][day].max.year) )
		if days[day][tag] < history[indexFromTag[tag]][day].min.value:
		    print("%s: Forecast record minimum %s %s, would beat %s in %d" %
                          (day, tag, float(days[day][tag]), float(history[indexFromTag[tag]][day].min.value), history[indexFromTag[tag]][day].min.year) )

		line.append((day.toordinal(), days[day][tag]))

	ps.plotline(line, colour[tag], dash="[1] 0")

    for tag in ('low', 'high'):
	mod = 1
	if tag == 'low':
	    mod = -1

	for day in days:
	    if tag in days[day]:
		ps.printText(day.toordinal(), days[day][tag]+mod, '%.1f' % days[day][tag])

		recordDays = 0
		if tag == 'low':
		    recordDays = max(daysSince(COLDER, daily.MIN_TEMP, days[day][tag]), daysSince(WARMER, daily.MIN_TEMP, days[day][tag]))
		else:
		    recordDays = max(daysSince(WARMER, daily.MAX_TEMP, days[day][tag]), daysSince(COLDER, daily.MAX_TEMP, days[day][tag]))

		if recordDays > historyDays:
		    print recordDays, days[day][tag], str(now-datetime.timedelta(recordDays))
		    ps.printText(day.toordinal(), days[day][tag]+2*mod, str(now-datetime.timedelta(recordDays)))

    ps.showPage()
    ps.trailer()

plotForecastData()
