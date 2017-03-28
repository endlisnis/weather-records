#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, datetime, time, recentWeather, re, glob
from decimal import Decimal
from collections import namedtuple
import accuweather
import daily

now = datetime.datetime.now().date()

MinMax = namedtuple('MinMax', 'min max')

def valueAfter(list, word):
    val = None
    if word in list:
        val = list[list.index(word)+1]
        val = val.split('<')[0].strip('.')
    return val

def valueBefore(list, word):
    val = None
    if word in list:
        index = list.index(word)
        val = int(list[index-1])
        val = MinMax(val, val)
        if list[index-2] == "to":
            val = val._replace(min = int(list[index-3]))
    return val

def getSnowForecast(flist):
    val = valueBefore(flist, 'cm.')

    if val == None:
        val = MinMax(min=0, max=0)

        joined = " ".join(flist)
        if " periods of snow. " in joined:
            val = MinMax(3, 8)
        elif " periods of rain or snow. " in joined:
            val = MinMax(0, 8)
        elif " periods of light snow. " in joined:
            val = MinMax(1, 3)
        elif " freezing rain or snow. " in joined:
            val = MinMax(2.5, 7.5)
        elif " snow. blowing snow. windy. " in joined:
            val = MinMax(8, 20)
        #elif " flurries. " in joined:
        #    val = MinMax(1, 3)
        else:
            snowmatch = re.match(".* ([0-9]+) percent chance of snow", joined)
            flurriesmatch = re.match(".* ([0-9]+) percent chance of flurries", joined)

            if snowmatch != None:
                percent = int(snowmatch.groups()[0])
                val = MinMax(percent*5.0/100, percent*15.0/100)
            elif flurriesmatch != None:
                percent = int(flurriesmatch.groups()[0])
                val = MinMax(percent*1.0/100, percent*3.0/100)
            elif " rain or snow. " in joined or " snow or rain. " in joined:
                val = MinMax(0, 15)
            elif " snow. " in joined:
                val = MinMax(5, 15)

    return val

def getRainForecast(flist):
    val = valueBefore(flist, 'mm.')
    if val is None:
        val = MinMax(min=0, max=0)
    return val

def getForecastData(city):
    ret = {}
    for fname in (city+'/accuweather/thisMonth.html', city+'/accuweather/nextMonth.html'):
        ret.update(accuweather.forecast(fname))
    return ret

def getForecastDataEnvCan(city):
    localFilename = city+'/environmentCanada.xml'
    return getForecastFromLocalFile(localFilename)[1]

def getForecastFromLocalFile(filename):
    input = open(filename, 'r')

    xml = input.read().lower().replace("&nbsp;", " ")

    text = ( xml
             .replace(" wind chill minus ", " windchill -")
             .replace(" high plus ", " high +")
             .replace(" high minus ", " high -")
             .replace(" low plus ", " low +")
             .replace(" low minus ", " low -")
             .replace(" zero", ' 0')
             .replace(" steady near ", ' steadynear ')
             .replace(' steadynear plus ', ' steadynear +')
             .replace(' steadynear minus ', ' steadynear -')
             .replace(" falling to ", ' fallingto ')
             .replace(' fallingto plus ', ' fallingto +')
             .replace(' fallingto minus ', ' fallingto -')
             .replace(" temperature rising to ", ' risingto ')
             .replace(' risingto plus ', ' risingto +')
             .replace(' risingto minus ', ' risingto -')
             .replace(' low lying ', 'lowlying') )


    #print(text)
    datetimeMatch = re.search("forecast issued (.*? 20[0-9][0-9])", text)
    assert datetimeMatch != None
    issuedDatetimeStr = datetimeMatch.groups()[0]
    issuedDatetime = issuedDatetimeStr.split()
    issuedDatetime = issuedDatetime[:2] + issuedDatetime[3:] # Strip out the time zone
    issuedDatetime = ' '.join(issuedDatetime)
    #print(issuedDatetimeStr)
    issuedDatetime = datetime.datetime.strptime(issuedDatetime, '%I:%M %p %A %d %B %Y')
    #print(issuedDatetime #, text)

    keys = [("today ,", issuedDatetime.date()),
            ("tonight ,", issuedDatetime.date()+datetime.timedelta(1))]

    dates = {}
    for dayoff in range(0, 7):
        dateTime = issuedDatetime.date() + datetime.timedelta(dayoff)
        dates[time.strftime("%A: ", dateTime.timetuple())] = time.strftime("%Y-%m-%d", dateTime.timetuple())
        keys.append( (time.strftime("%A: ", dateTime.timetuple()).lower(), dateTime) )
        keys.append( (time.strftime("%A night: ", dateTime.timetuple()).lower(), dateTime+datetime.timedelta(1)) )

    days = {}

    for key in keys:
        (name, dateTime) = key
        nameoffset = text.find(name)

        val = [0,0]

        if(nameoffset != -1):
            offset = text.find('</summary>', nameoffset)

            if offset < nameoffset:
                # we didn't find a comma, so we wrapped around to -1.
                # Use "None" to make sure we capture the entire rest of the text
                offset = None

            forecast = text[nameoffset:offset]
            #print(key, repr(forecast))
            #forecast = forecast.replace('low:', 'low').replace('high:', 'high')

            flist = forecast.split()
            #print(flist, file=sys.stderr)

            dayTags = {}
            #import pudb; pu.db
            for tag in ('low', 'high', 'windchill', 'snow', 'rain'):
                val = None
                if tag == 'snow':
                    val = getSnowForecast(flist)

                    val = (val.min + val.max) / 2
                elif tag == 'rain':
                    val = getRainForecast(flist)

                    val = (val.min + val.max) / 2
                else:
                    val = valueAfter(flist, tag)
                    if val == None:
                        if tag == 'high':
                            val = valueAfter(flist, 'fallingto')
                        else:
                            val = valueAfter(flist, 'risingto')

                    if val == None:
                        #print(tag, flist)
                        val = valueAfter(flist, 'steadynear')

                        if ( (val != None) and (tag == 'low')
                             and (dateTime in days and tag in days[dateTime])
                         ):
                            val = None


                if val is not None:
                    if dateTime not in days:
                        days[dateTime] = {tag: Decimal(val)}
                    else:
                        if tag in ('rain', 'snow'):
                            days[dateTime][tag] = val + days[dateTime].get(tag, 0)
                        else:
                            if tag in days[dateTime]:
                                if tag in ('low', 'windchill'):
                                    # If a daytime windchill and a nighttime windchill
                                    # is listed, use the lowest value.
                                    val = min(days[dateTime][tag], Decimal(val))
                                elif tag == 'high':
                                    val = max(days[dateTime][tag], Decimal(val))
                                else:
                                    print("Unexpected duplicate: ", dateTime, tag, days[dateTime][tag], val)
                                    exit(1)
                            days[dateTime][tag] = Decimal(val)
    #print(days)
    for day in tuple(days.keys()):
        oldDayValue = days[day]
        MAX_TEMP=None
        MAX_TEMP_FLAG='M'
        MIN_TEMP=None
        MIN_TEMP_FLAG='M'
        TOTAL_RAIN_MM=None
        TOTAL_RAIN_FLAG='M'
        TOTAL_SNOW_CM=None
        TOTAL_SNOW_FLAG='M'
        MEAN_TEMP=None
        MEAN_TEMP_FLAG='M'
        MIN_WINDCHILL=None
        MIN_WINDCHILL_FLAG='M'
        if 'high' in oldDayValue:
            MAX_TEMP = oldDayValue['high']
            if 'low' in oldDayValue:
                MAX_TEMP = max(oldDayValue['high'], oldDayValue['low'])
            MAX_TEMP_FLAG = 'F'
        if 'low' in oldDayValue:
            MIN_TEMP = oldDayValue['low']
            if 'high' in oldDayValue:
                MIN_TEMP = min(oldDayValue['high'], oldDayValue['low'])
            MIN_TEMP_FLAG = 'F'
        if 'windchill' in oldDayValue:
            MIN_WINDCHILL = oldDayValue['windchill']
            MIN_WINDCHILL_FLAG = 'F'
        if 'snow' in oldDayValue:
            TOTAL_SNOW_CM = int(oldDayValue['snow'])
            TOTAL_SNOW_FLAG='F'
        if 'rain' in oldDayValue:
            TOTAL_RAIN_MM = int(oldDayValue['rain'])
            TOTAL_RAIN_FLAG='F'
        if MIN_TEMP is not None and MAX_TEMP is not None:
            MEAN_TEMP = (MAX_TEMP + MIN_TEMP)/2
            MEAN_TEMP_FLAG = 'F'
        days[day] = daily.DayData(
            MAX_TEMP=MAX_TEMP,
            MAX_TEMP_FLAG=MAX_TEMP_FLAG,
            MIN_TEMP=MIN_TEMP,
            MIN_TEMP_FLAG=MIN_TEMP_FLAG,
            MEAN_TEMP=MEAN_TEMP,
            MEAN_TEMP_FLAG=MEAN_TEMP_FLAG,
            MIN_WINDCHILL=MIN_WINDCHILL,
            MIN_WINDCHILL_FLAG=MIN_WINDCHILL_FLAG,
            TOTAL_RAIN_MM=TOTAL_RAIN_MM,
            TOTAL_RAIN_FLAG=TOTAL_RAIN_FLAG,
            TOTAL_SNOW_CM=TOTAL_SNOW_CM,
            TOTAL_SNOW_FLAG=TOTAL_SNOW_FLAG,
        )

        accum = [0,0]
        #if name == 'today:':
        #    accum = recentWeather.get(city)
        #    accum = (accum*0.75, accum*2)

        if sum(accum) > 0:
            if datetime not in days:
                days[datetime] = {}
            days[datetime]['snow'] = accum
    #print(days)
    return issuedDatetime, days

if __name__ == '__main__':
    f = getForecastDataEnvCan(sys.argv[1])
    for day in sorted(f.keys()):
        print(day, ':', end=' ')
        dv = f[day]
        for fieldName in dv._fields:
            v = dv.__getattribute__(fieldName)
            if v is not None:
                print('{} = {:>5},'.format(fieldName, repr(v)), end='')
        #print(f[day])
        #for (field, val) in f[day].items():
        #    if isinstance(val, Fraction):
        #        print('{%s: %.1f}' % (field, val), end='')
        #    else:
        #        print('{%s: %s}' % (field, val), end='')
        print()
