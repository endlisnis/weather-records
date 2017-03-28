#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime, copy, random
import daily, sendMail, dailyRecords, namedList, htmlday
from decimal import Decimal
from pprint import PrettyPrinter
import dayplot, os, delayedTweets, sys, stations
import first
from monthName import monthName
from alert import *
from dailyRecordAlert import DailyRecordAlert
from dailyForecastAlert import (DailyForecastAlert, DailyForecastAlertMaxMin)
from alertTweets import *
from previousReport import PreviousReport
import yearTweets
from recordsincealert import RecordSinceAlert, RecordSinceAlertSum, RecordSinceAlertAvg

def makedict(**args):
    return args

city = 'ottawa'
if len(sys.argv) > 1:
    city=sys.argv[1]

citydata = daily.load(city)
auto = False

def maybePostWarmMorningTweet(time, value, median):
    if value - median < 3:
        tweet = ( "@ %dAM, with a temperature of %.1f℃, #%s already exceeded the normal daytime high of %.1f%s. #Summer"
                  % (time.hour,
                     value,
                     stations.city[city].name,
                     median,
                     chr(0x2103) ) )
    else:
        tweet = ( "@ %dAM, with a temperature of %.1f%s, #%s is already well above the normal daytime high of %.1f%s. #Summer"
                  % (time.hour,
                     value,
                     chr(0x2103),
                     stations.city[city].name,
                     median,
                     chr(0x2103) ) )
    print(tweet)
    response = input('"n" to cancel this tweet: ').strip()
    if response == 'y':
        delayedTweets.addToEndOfListForCity(city, tweet)



def showList(days, units):
    print("{} consequtive days".format(len(days)))
    #
    for day in days:
        print("{year}/{month:02d}/{day:02d}: {val:.1f}{}" % (day.year, day.month, day.day, day.value, units))

DayValue = namedList.namedStruct('DayValue', 'value year month day')

def maxConsecutive(field, expr):
    firstYear = citydata.minYear
    #
    sampleDay = datetime.date(firstYear, 1, 1)
    #
    cur = []
    maxRun = []
    #
    while sampleDay < today(city):
        try:
            value = citydata[sampleDay][field]
            if value is not None and expr(value):
                cur.append( DayValue(value, sampleDay.year, sampleDay.month, sampleDay.day) )
                if len(cur) > len(maxRun):
                    maxRun = copy.deepcopy(cur)
            else:
                cur = []
        except KeyError:
            cur = []
        sampleDay += datetime.timedelta(days=1)
    return maxRun

#showList(maxConsecutive(daily.MAX_TEMP.index, lambda t: t>34), "C")

def consecutiveLonger(field, expr, minRun):
    sampleDay = today(city)-datetime.timedelta(days=31)

    cur = []
    ret = []

    while sampleDay < today(city):
        try:
            value = citydata[sampleDay][field.index]
            if value is not None:
                if expr(value):
                    cur.append( DayValue(value, sampleDay.year, sampleDay.month, sampleDay.day) )
                else:
                    if len(cur) >= minRun:
                        ret.append(copy.deepcopy(cur))
                    cur = []
            else:
                if len(cur) >= minRun:
                    ret.append(copy.deepcopy(cur))
                cur = []
        except KeyError:
            if len(cur) >= minRun:
                ret.append(copy.deepcopy(cur))
            cur = []
        sampleDay += datetime.timedelta(days=1)
    return ret

class ConsequtiveAlert(Alert):
    def __init__(self, title, address, field, expr, minLen, units):
        Alert.__init__(self, title, address, field)
        self.expr = expr
        self.minLen = minLen
        self.units = units

    def __call__(self, city):
        if self.field.name in stations.city[city].skipDailyFields:
            # This city doesn't keep track of this information in a useful way.
            return
        ret = []
        results = consecutiveLonger(self.field, self.expr, self.minLen)
        for span in results:
            datemarker = span[0]
            datemarker = (datemarker.year*100+datemarker.month)*100+datemarker.day

            if self.datemarker.get(datemarker,None) != len(span) :
                msg = "\n%d consequtive days\n" % (len(span), )
                for day in span:
                    dt = datetime.date(day.year, day.month, day.day)
                    msg += "%.1f%s %s\n" % (day.value, self.units, dt)
                self.datemarker[datemarker] = (len(span), msg)
                ret.append( Email(field=None, date=None, message=msg) )
        return ret

class WarmMorningAlert(Alert):
    def __call__(self, city):
        dInfo = dailyRecords.getInfo(city, today(city), self.field)
        msg = ''
        datemarker = dateMarkerFromDate(today(city))
        alreadyReportedRecord, oldTweet = self.datemarker.get(datemarker,(None,None))

        if ( dInfo.median != None
             and alreadyReportedRecord != dInfo.recent
             and daily.timeByCity[city].hour < 11
             and dInfo.recent > dInfo.median
        ):
            maybePostWarmMorningTweet(daily.timeByCity[city], dInfo.recent, dInfo.median)
            self.datemarker[datemarker] = dInfo.recent

class YearCountMaxTempAlert(Alert):
    def __call__(self, city):
        return
        datemarker = dateMarkerFromDate(today(city))
        alreadyReportedRecord, oldTweet = self.datemarker.get(datemarker,(None,None))

        print((city, alreadyReportedRecord))
        self.datemarker[datemarker] = (
            yearTweets.main(city, alreadyReportedRecord),
            '' )
        yearTweets.main(city, alreadyReportedRecord, allYear=True, justTop5=True)


class MonthlyRecordAlert(Alert):

    def __call__(self, city):
        if self.field.name in stations.city[city].skipDailyFields:
            # This city doesn't keep track of this information in a useful way.
            return
        ret = []
        startDate = today(city)-datetime.timedelta(days=7)
        lyear = 0

        for sampleDay in daily.dayRange(startDate, today(city)):
            if sampleDay.year != lyear:
                monthlyRecords = dailyRecords.getMonthRecords(city, sampleDay.year, self.field)
            lyear = sampleDay.year
            datemarker = dateMarkerFromDate(sampleDay)

            try:
                v = citydata[sampleDay][self.field.index]
                if v != None and self.datemarker.get(datemarker,None) != v:
                    maxr = monthlyRecords.max[sampleDay.month-1]
                    minr = monthlyRecords.min[sampleDay.month-1]
                    msg = ''
                    if v > maxr.value and self.datemarker.get(datemarker,None) != v:
                        print( {'date': sampleDay,
                                'month': monthName(sampleDay.month, long=True),
                                'field': self.field.name,
                                'value': v,
                                'units': self.field.htmlunits,
                                'recordValue': maxr.value,
                                'recordYear': maxr.year,
                                'recordMonth': maxr.month,
                                'recordDay': maxr.day} )
                        tweet = ( '{date}: {month} record high {field} of {value:.1f}{units} breaks previous record of {recordValue:.1f}{units} from {recordYear}/{recordMonth:02d}/{recordDay:02d}\n'
                                  .format(date=sampleDay,
                                          month=monthName(sampleDay.month, long=True),
                                          field=self.field.name,
                                          value=float(v),
                                          units=self.field.htmlunits,
                                          recordValue=float(maxr.value),
                                          recordYear=maxr.year,
                                          recordMonth=maxr.month,
                                          recordDay=maxr.day) )
                        msg += tweet
                        self.datemarker[datemarker] = v, tweet
                    elif v < minr.value and self.skipMinRecords is False:
                        print( {'date': sampleDay,
                                'month': monthName(sampleDay.month, long=True),
                                'field': self.field.name,
                                'value': v,
                                'units': self.field.htmlunits,
                                'recordValue': minr.value,
                                'recordYear': minr.year,
                                'recordMonth': minr.month,
                                'recordDay': minr.day} )
                        tweet = ( '{date}: {month} record low {field} of {value:.1f}{units} breaks previous record of {recordValue:.1f}{units} from {recordYear}/{recordMonth:02d}/{recordDay:02d}\n'
                                  .format(date=sampleDay,
                                          month=monthName(sampleDay.month, long=True),
                                          field=self.field.name,
                                          value=float(v),
                                          units=self.field.htmlunits,
                                          recordValue=float(minr.value),
                                          recordYear=minr.year,
                                          recordMonth=minr.month,
                                          recordDay=minr.day) )
                        msg += tweet
                        self.datemarker[datemarker] = v, tweet
                    if len(msg) > 0:
                        ret.append( Email(field=self.field, date=sampleDay, message=msg) )
            except KeyError:
                pass
        return ret

class FirstAlert(Alert):
    def __init__(self, title, address, expression,
                 tweetEvent,
                 skipMinRecords=False,
                 skipMaxRecords=False,
                 skipMinEstimated=False,
                 skipMaxEstimated=False,
                 skipIncomplete=False):
        Alert.__init__(self,
                       title, address, expression,
                       skipMinRecords, skipMaxRecords,
                       skipMinEstimated, skipMaxEstimated,
                       skipIncomplete)
        self.tweetEvent = tweetEvent

    def maybeTweetFirst(self, datemarker, firstThisYear, medianFirst, earliest, latest, histogramFname):
        print((datemarker, firstThisYear, medianFirst, earliest, latest))
        dayString = 'Today is'
        if firstThisYear == today(city)-datetime.timedelta(days=1):
            dayString = 'Yesterday was'
        elif firstThisYear != today(city):
            dayString = '%s %d was' % (monthName(firstThisYear.month),
                                       firstThisYear.day)
        #tweet = '{day} #{cityName} {event} of the season. Typical first is {medMonth} {medDay}. Record earliest is {earliest}; latest {latest}.'
        tweet = '{day} #{cityName} {event} of the season. Typical first is {medMonth} {medDay}.'
        tweet = tweet.format(day=dayString,
                             cityName=possessive(stations.city[city].name),
                             event=self.tweetEvent,
                             event2=self.title.lower(),
                             medMonth=monthName(medianFirst.month),
                             medDay=medianFirst.day,
                             earliest=str(earliest[-1]),
                             latest=str(latest[-1]),
                             )
        targetAccounts = accountsPerCity.get(city,nationalAccounts)
        (use, tweet) = shouldTweetSuffix(
            city, tweet, oldText=None)

        if use is True:
            pngname = histogramFname.replace('/svg/','/')+'.png'
            command='rsvg-convert -o %s --background-color=white %s.svg' % (pngname, histogramFname)
            print(command)
            assert os.system(command) == 0
            delayedTweets.addToEndOfListForCity(city, tweet, pngname)
            if city == 'ottawa':
                sendMail.sendMailConsole("thats.unpossible@gmail.com",
                                         alert.address,
                                         subject = alert.title,
                                         text = tweet,
                                         auto = True)
        self.datemarker[datemarker] = PreviousReport(1, tweet)

    def __call__(self, city):
        ret = []

        startDate = today(city)-datetime.timedelta(days=7)
        firstResults = first.first(city, self.field, self.title,
                                   dateRange=first.DateRange(start='7,1', end='7,1'),
                                   verboseIfInDateRange=(startDate, today(city)) )
        if firstResults == None:
            # This event hasn't occured yet
            return

        (firstThisYear, medianFirst, earliest, latest, histogramFname) = firstResults

        if firstThisYear < startDate:
            return

        datemarker = dateMarkerFromDate(firstThisYear)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)

        if alreadyReportedRecord != None and alreadyReportedRecord.value == 1:
            return

        flag = '' # fixme
        if self.skipIncomplete and 'I' in flag:
            return

        self.maybeTweetFirst(datemarker, firstThisYear, medianFirst, earliest, latest, histogramFname)

        return ret


class DayCountAlert(Alert):
    def __init__(self, title, address, expr, label, skipIncomplete=False):
        Alert.__init__(self, title, address, None)
        self.expr = expr
        self.label = label
        self.skipIncomplete = skipIncomplete

    def __call__(self, city):
        startDate = today(city)-datetime.timedelta(days=7)

        for sampleDay in daily.dayRange(startDate, today(city)+datetime.timedelta(1)):
            endDay = sampleDay+datetime.timedelta(1)
            startMonth, startDay = self.startMonthDay(sampleDay.month, sampleDay.day)

            (svgFname, result, mostSince, prevRecord, prevRecordYears) = (
                first.dispatch(city, firstYear=None,
                               startMonth = startMonth, startDay = startDay,
                               endMonth = endDay.month, endDay = endDay.day,
                               expression = self.expr,
                               verbose = False,
                               skipIncomplete = self.skipIncomplete) )
            datemarker = dateMarkerFromDate(sampleDay)
            alreadyReportedRecord = self.datemarker.get(datemarker,0)
            if result <= alreadyReportedRecord:
                try:
                    os.unlink(svgFname+'.svg')
                except OSError as err:
                    if err.errno != 2:
                        raise
            else:
                dayString = 'Today is'
                if sampleDay != today(city):
                    dayString = '%s %d was' % (monthName(sampleDay.month),
                                               sampleDay.day)

                context = '??'
                if mostSince != None:
                    hashtag = ''
                    if ( mostSince <= startDate.year - 20
                         and (today(city) - sampleDay).days < 2 ):
                        hashtag = {'ottawa':' #OttNews','toronto':' #ToNews'}[city]
                    context = 'Most since %d.%s' % (mostSince, hashtag)
                elif len(prevRecordYears) > 0:
                    context = ( 'Broke previous record of %d in %s. #%s'
                                % ( prevRecord,
                                    '/'.join(map(str, prevRecordYears)),
                                    {'ottawa':'OttNews','toronto':'ToNews'}[city]) )

                tweet = ('%s #%s\'s %s day with %s during %s. %s'
                         % (dayString,
                            stations.city[city].name,
                            nth(result),
                            self.label,
                            self.timeBinDescription(sampleDay),
                            context) )

                if len(tweet) > 117:
                    tweet = tweet.replace(' below ', ' < ')
                print(tweet)
                if (mostSince == None and len(prevRecordYears) > 0) or mostSince <= startDate.year - 10:
                    pngname = svgFname.replace('/svg/','/')+'.png'
                    command = 'rsvg-convert -o %s --background-color=white %s.svg' % (pngname, svgFname)
                    #print command
                    assert os.system(command) == 0
                    #print 'api.PostMedia(%s, %s)' % (repr(tweet), repr(pngname))
                    if auto:
                        response = 'y'
                    else:
                        response = input('"n" to cancel this tweet: ').strip()
                    if response == 'y':
                        delayedTweets.addToEndOfListForCity(city, tweet, pngname)
                    if response != 'c':
                        self.datemarker[datemarker] = result
                else:
                    self.datemarker[datemarker] = result
                    os.unlink(svgFname+'.svg')
                if ( city == 'ottawa'
                     and ( (mostSince == None and len(prevRecordYears) > 0)
                           or mostSince <= startDate.year - 20) ):
                    sendMail.sendMailConsole("thats.unpossible@gmail.com", alert.address,
                                             subject = alert.title,
                                             text = tweet,
                                             files = [pngname],
                                             auto = auto)

class MonthlyCountAlert(DayCountAlert):
    def startMonthDay(self, sampleMonth, sampleDay):
        return sampleMonth, 1

    def timeBinDescription(self, sampleDay):
        return monthName(sampleDay.month)

class AnnualCountAlert(DayCountAlert):
    def startMonthDay(self, sampleMonth, sampleDay):
        return 1, 1

    def timeBinDescription(self, sampleDay):
        return str(sampleDay.year)

def humidexNotAboveTemp(dayData):
    if dayData.MAX_TEMP is None:
        return True
    if dayData.MAX_HUMIDEX is None:
        return True
    return dayData.MAX_HUMIDEX <= dayData.MAX_TEMP

people = ['gilesni@hotmail.com', 'tmsmall@gmail.com', 'beerbeerbeer@gmail.com', 'will.hickie@gmail.com', 'celia@drmath.ca', 'michael.coire@gmail.com', 'nichola@gmail.com']

annualMinTempAlerts = [
    AnnualCountAlert('Days with min below %dC this year' % t,
                     people, 'min<%d' % t , ('min temp below %d' % t)+chr(0x2103)) for t in (-25,-20,-15,-10)]

monthlyMinTempAlerts = [
    MonthlyCountAlert('Days with min below %dC this month' % t,
                      people, 'min<%d' % t , ('min temp below %d' % t)+chr(0x2103)) for t in (-25,-20,-15,-10)]

annualMaxTempAlerts = [
    AnnualCountAlert('Days with max below %dC this year' % t,
                     people, 'max<%d' % t , ('max temp below %d' % t)+chr(0x2103)) for t in (-15,-10,-5,0)]

alerts = [ #annualMinTempAlerts + monthlyMinTempAlerts  + [
    RecordSinceAlertAvg('Record 5-day humidity since', people, daily.MEAN_HUMIDITY, dayCount=5, skipIncomplete=True),
    RecordSinceAlertSum('Record 5-day rain since', people, daily.TOTAL_RAIN_MM, dayCount=5),
    RecordSinceAlertSum('Record 5-day snow since', people, daily.TOTAL_SNOW_CM, dayCount=5),
    RecordSinceAlertAvg('Record 5-day wind since', people, daily.AVG_WIND, dayCount=5, skipIncomplete=True),
    YearCountMaxTempAlert('Day above so far this year', people, daily.MAX_TEMP),
    DailyForecastAlert('Record forecast daily high temperature alert',
                       people, daily.MAX_TEMP),
    DailyForecastAlert('Record forecast daily low temperature alert',
                       people, daily.MIN_TEMP, skipMaxRecords=True),
    DailyForecastAlert('Record forecast daily windchill alert',
                       people, daily.MIN_WINDCHILL, skipMaxRecords=True),
    #DailyForecastAlertMaxMin('Record forecast daily low temperature alert',
    #                         people, daily.MIN_TEMP),
    FirstAlert('First frost', people, 'min <= 0', tweetEvent='first #frost'),
    FirstAlert('First -20', people, 'min <= -20', tweetEvent='first -20'),
    FirstAlert('First -10', people, 'min <= -10', tweetEvent='first -10'),
    FirstAlert('First frozen day', people, 'max <= 0 and "I" not in maxFlag and "H" not in maxFlag',
               tweetEvent='first #frozen day'),
    FirstAlert('First -30 windchill', people, 'windchill <= -30', tweetEvent='first -30 windchill'),
    FirstAlert('First -20 windchill', people, 'windchill <= -20', tweetEvent='first -20 windchill'),
    FirstAlert('First -10 windchill', people, 'windchill <= -10', tweetEvent='first -10 windchill'),
    FirstAlert('First 10cm snow', people, 'snow > 10', tweetEvent='first 10cm'),
    FirstAlert('First 5cm snow', people, 'snow > 5', tweetEvent='first 5cm'),
    FirstAlert('First snow', people, 'snow > 0', tweetEvent='first #snow'),
    RecordSinceAlert('Record month daytime high since', people, daily.MAX_TEMP,
                     skipMinEstimated=True, skipMinIncomplete=True,
                     limitToThisMonth=True),
    RecordSinceAlert('Record month daytime low since', people, daily.MIN_TEMP,
                     skipMaxEstimated=True, skipMaxIncomplete=True,
                     limitToThisMonth=True),
    RecordSinceAlert('Record month humidex since', people, daily.MAX_HUMIDEX, limitToThisMonth=True,
                     skipFilter=humidexNotAboveTemp),
    RecordSinceAlert('Record month windchill since', people,
                     daily.MIN_WINDCHILL, limitToThisMonth=True,
                     skipMinEstimated=True, skipMaxEstimated=True),
    RecordSinceAlert('Record month snow since', people,
                     daily.TOTAL_SNOW_CM, limitToThisMonth=True,
                     skipMinRecords=True),
    RecordSinceAlert('Record month rain since', people,
                     daily.TOTAL_RAIN_MM, limitToThisMonth=True),
    RecordSinceAlert('Record month wind gust since', people,
                     daily.SPD_OF_MAX_GUST_KPH, limitToThisMonth=True),
    RecordSinceAlert('Record month wind since', people, daily.AVG_WIND,
                     skipIncomplete=True, limitToThisMonth=True, skipMinRecords=True),
    RecordSinceAlert('Record month min humidity since', people, daily.MIN_HUMIDITY,
                     skipIncomplete=True, limitToThisMonth=True),
    RecordSinceAlert('Record month mean humidity since', people, daily.MEAN_HUMIDITY,
                     skipIncomplete=True, limitToThisMonth=True),

    RecordSinceAlert('Record daytime high since', people, daily.MAX_TEMP,
                     skipMinEstimated=True, skipMinIncomplete=True),
    RecordSinceAlert('Record daytime low since', people, daily.MIN_TEMP,
                     skipMaxEstimated=True, skipMaxIncomplete=True),
    RecordSinceAlert('Record humidex since', people, daily.MAX_HUMIDEX,
                     skipFilter=humidexNotAboveTemp),
    RecordSinceAlert('Record windchill since', people,
                     daily.MIN_WINDCHILL,
                     skipMinEstimated=True, skipMaxEstimated=True),
    RecordSinceAlert('Record snow since', people, daily.TOTAL_SNOW_CM,
                     skipMinRecords=True),
    RecordSinceAlert('Record snowpack since', people, daily.SNOW_ON_GRND_CM),
    RecordSinceAlert('Record rain since', people, daily.TOTAL_RAIN_MM),
    RecordSinceAlert('Record wind gust since', people, daily.SPD_OF_MAX_GUST_KPH),
    RecordSinceAlert('Record wind since', people, daily.AVG_WIND,
                     skipIncomplete=True, skipMinRecords=True),
    RecordSinceAlert('Record min humidity since', people, daily.MIN_HUMIDITY,
                     skipIncomplete=True, skipMinRecords=True),
    RecordSinceAlert('Record mean humidity since', people, daily.MEAN_HUMIDITY,
                     skipIncomplete=True, skipMinRecords=True),
#    AnnualMax('Record warm low this year', people, daily.MIN_TEMP),
    #AnnualCountAlert('Days with at least 10cm of snow this year',
    #                 people, 'snow>=10', '10cm of snow'),
    #MonthlyCountAlert('Days with at least 10cm of snow this month',
    #                  people, 'snow>=10', '10cm of snow'),
    ConsequtiveAlert('At least 7 consecutive days of snow alert',
                     people, daily.TOTAL_SNOW_CM, lambda x: x>0, 7, 'cm'),
    DailyRecordAlert('Record daily high temperature alert',
                     people, daily.MAX_TEMP, skipMinIncomplete=True),
    DailyRecordAlert('Record daily low temperature alert',
                     people, daily.MIN_TEMP, skipMaxIncomplete=True),
    DailyRecordAlert('Record daily snowfall alert',
                     people, daily.TOTAL_SNOW_CM, skipMinRecords=True),
    DailyRecordAlert('Record daily snow on the ground alert',
                     people, daily.SNOW_ON_GRND_CM),
    DailyRecordAlert('Record daily rainfall alert',
                     people, daily.TOTAL_RAIN_MM, skipMinRecords=True),
    DailyRecordAlert('Record daily precipitation alert',
                     people, daily.TOTAL_PRECIP_MM, skipMinRecords=True),
    DailyRecordAlert('Record daily wind speed alert',
                     people, daily.SPD_OF_MAX_GUST_KPH, skipMinRecords=True),
    ConsequtiveAlert('At least 13 consecutive days of no precipitation alert',
                     people, daily.TOTAL_PRECIP_MM, lambda x: x<0.31, 13, 'mm'),
    DailyRecordAlert('Record daily humidex alert',
                     people, daily.MAX_HUMIDEX, skipMinRecords=True, skipBelowZero=True,
                     skipFilter=humidexNotAboveTemp),
    DailyRecordAlert('Record daily windchill alert',
                     people, daily.MIN_WINDCHILL, skipMaxRecords=True),
    DailyRecordAlert('Record daily average windchill alert',
                     people, daily.AVG_WINDCHILL, skipMaxRecords=True, skipIncomplete=True),
    DailyRecordAlert('Record daily average wind speed alert',
                     people, daily.AVG_WIND, skipIncomplete=True, skipMinRecords=True),
    DailyRecordAlert('Record daily mean humidity alert',
                     people, daily.MEAN_HUMIDITY, skipIncomplete=True),
    DailyRecordAlert('Record daily min humidity alert',
                     people, daily.MIN_HUMIDITY, skipMaxRecords=True),
    MonthlyRecordAlert('Record monthly high temperature alert',
                       people, daily.MAX_TEMP),
    MonthlyRecordAlert('Record monthly low temperature alert',
                       people, daily.MIN_TEMP),
    MonthlyRecordAlert('Record monthly snowfall-per-day alert',
                       people, daily.TOTAL_SNOW_CM),
    MonthlyRecordAlert('Record monthly rainfall-per-day alert',
                       people, daily.TOTAL_RAIN_MM),
    MonthlyRecordAlert('Record monthly precipitation-per-day alert',
                       people, daily.TOTAL_PRECIP_MM),
    MonthlyRecordAlert('Record monthly snow-on-ground alert',
                       people, daily.SNOW_ON_GRND_CM),
    MonthlyRecordAlert('Record monthly wind-speed alert',
                       people, daily.SPD_OF_MAX_GUST_KPH,
                       skipMinRecords=True),
]

alertTimeMarkers = {}
historyFname = "{}/alertTimeMarkers.py".format(city)
if os.path.exists(historyFname):
    alertTimeMarkers = eval(open(historyFname, 'rb').read().strip())

toDelete = []
for title in alertTimeMarkers.keys():
    for (datemarker,val) in alertTimeMarkers[title].items():
        date = dateFromMarker(datemarker)
        if (datetime.date.today() - date).days > 30:
            toDelete.append((title, datemarker))
        else:
            val, tweet = val
            alertTimeMarkers[title][datemarker] = PreviousReport(Decimal('{:.1f}'.format(val)), tweet)

for title, datemarker in toDelete:
    del alertTimeMarkers[title][datemarker]
del toDelete

for i in range(len(alerts)):
    alert = alerts[i]
    alert.datemarker = alertTimeMarkers.get(alert.title, None)
    if alert.datemarker == None:
        alert.datemarker = {}

    alertMessages = alert(city)

    if alertMessages == None:
        alertMessages = []

    for email in alertMessages:
        files = []
        if city == 'ottawa' and email.date != None:
            lineFname, bottom10Fname, top10Fname = dayplot.createPlots(
                city='ottawa',
                field=email.field,
                name=email.field.name,
                plotDate=email.date,
                plotZeros=False,
                verbose=False)
            fname = lineFname
            pngname = fname.replace('.svg', '.png').replace('/svg/','/')
            print(fname)
            assert os.system('rsvg-convert -o %s --background-color=white %s' % (pngname, fname)) == 0
            files.append(pngname)

            sendMail.sendMailConsole("thats.unpossible@gmail.com", alert.address,
                                     subject = alert.title,
                                     text = email.message,
                                     files = files)
        #twitterSend.api.PostMedia(alert.title, files[0])
    #if alert.title not in alertTimeMarkers:
    #    alertTimeMarkers[alert.title] = {}
    alertTimeMarkers[alert.title] = alert.datemarker

for title in alertTimeMarkers.keys():
    for (datemarker,val) in alertTimeMarkers[title].items():
        print((title, datemarker, val))
        alertTimeMarkers[title][datemarker] = PreviousReport(value=float(val[0]), tweet=val[1])
open(historyFname, 'w').write(PrettyPrinter().pformat(alertTimeMarkers))
