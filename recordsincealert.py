from alert import *
from previousReport import PreviousReport
from alertTweets import shouldTweetSuffix
from monthName import monthName

import daily
import delayedTweets
import sendMail
import sinceWhen
import metarSnowChart
import recordSinceChart

def findHourFlag(flags):
    hour = findStartsWith(flags.split('+'), ('H', 'S'))
    if hour is None or len(hour) > 1:
        return hour
    return None

def dayStr(city, date):
    if date == today(city):
        return "today"
    if date == today(city)-datetime.timedelta(days=1):
        return "yesterday"
    return dayOfWeek(date)


def yearsDiff(new, old):
    yearDiff = new.year - old.year
    oldDateThisYear = datetime.date(new.year, old.month, old.day)
    if oldDateThisYear <= new:
        return yearDiff + (new-oldDateThisYear).days / 1000
    oldDateLastYear = datetime.date(new.year-1, old.month, old.day)
    return yearDiff - 1 + (new-oldDateLastYear).days / 1000

#yearsDiff(datetime.date.today(), datetime.date(2016,10,21))

class RecordSinceAlert(Alert):
    def __init__(
        self,
        title, address, field,
        skipMinRecords=False,
        skipMaxRecords=False,
        skipMinEstimated=False,
        skipMaxEstimated=False,
        skipIncomplete=False,
        skipMinIncomplete=False,
        skipMaxIncomplete=False,
        skipBelowZero=False,
        limitToThisMonth=False,
        skipFilter=None
    ):
        Alert.__init__(
            self,
            title, address, field,
            skipMinRecords=skipMinRecords,
            skipMaxRecords=skipMaxRecords,
            skipMinEstimated=skipMinEstimated,
            skipMaxEstimated=skipMaxEstimated,
            skipIncomplete=skipIncomplete,
            skipMinIncomplete=skipMinIncomplete,
            skipMaxIncomplete=skipMaxIncomplete,
            skipBelowZero=skipBelowZero,
            skipFilter=skipFilter)
        self.limitToThisMonth=limitToThisMonth
    def maybeTweetRecordSince(
            self, city,
            v, recordValue, alreadyReportedRecord,
            hour, sampleDay, datemarker, maxRecord):

        #if sampleDay.day == 3 and self.field.name == 'TOTAL_SNOW_CM':
        #    import pudb; pu.db
        if ( maxRecord is False
             and self.field in (daily.MAX_HUMIDEX,
                                daily.TOTAL_RAIN_MM,
                                daily.SNOW_ON_GRND_CM,
                                daily.SPD_OF_MAX_GUST_KPH,
             ) ):
            return
        if ( maxRecord is True and self.field in (daily.MIN_WINDCHILL, ) ):
            return

        media=None
        limit=90 #days
        if self.field in (daily.MAX_TEMP, daily.MIN_TEMP,
                          daily.MAX_HUMIDEX, daily.MIN_WINDCHILL,
                          daily.AVG_WINDCHILL, daily.MEAN_TEMP,
                          daily.AVG_DEWPOINT):
            limit=400 #days
        if self.limitToThisMonth:
            limit=365*4+32 #days
        #print (sampleDay, float(v), self.field.name, repr(recordValue))
        if recordValue != None:
            ageOfRecord = (today(city) - recordValue[1]).days
        if recordValue == None or ageOfRecord > limit:
            alreadyReportedRecordTweet = None
            if alreadyReportedRecord != None:
                alreadyReportedRecordTweet = alreadyReportedRecord.tweet
                #print("\n--------------------------------------------------------------------------------\nCorrecting a previous record of {:.1f}".format(alreadyReportedRecord.value))
                #print("OldTweet: ", alreadyReportedRecord.tweet)
            dayString = 'today is'
            possessiveDayString = 'Today\'s'
            if sampleDay == today(city)-datetime.timedelta(days=1):
                dayString = 'yesterday was'
                possessiveDayString = 'Yesterday\'s'
            elif sampleDay != today(city):
                dayString = '{} was'.format(dayOfWeek(sampleDay))
                possessiveDayString = '{}\'s'.format(dayOfWeek(sampleDay))
            sinceWhat = sinceWhen.sinceWhen(
                city, self.field.index,
                recordDate = recordValue[1] if recordValue is not None else None)

            if self.field == daily.MAX_TEMP:
                recordDescription = 'warmest'
                if v > 24:
                    recordDescription = 'hottest'
                if maxRecord is False:
                    recordDescription = 'coldest'
                    tweet = ( 'With a high of just {value:.1f}{deg}, {day} {cityName}'
                              ' {record} {filter}day {since}.' )
                else:
                    tweet = ( 'With a high of {value:.1f}{deg}, {day} {cityName}'
                              ' {record} {filter}day {since}.' )
                    if hour != None:
                        tweet = ( 'With a {hour} temp of {value:.1f}{deg}, {day}'
                                  ' {cityName} {record} {filter}day {since}.' )
            elif self.field == daily.MIN_TEMP:
                recordDescription = 'warmest'
                if v > 24:
                    recordDescription = 'hottest'
                tweet = ( 'With a low of {value:.1f}{deg}, {day} {cityName} {record}'
                          ' {filter}day {since}.' )
                if maxRecord is False:
                    tweet = ( '{possessiveDayString} temp of {value:.1f}{deg} is the'
                              ' coldest {simpleCityName} has been {since}.' )
                    if self.limitToThisMonth:
                        tweet = ( '{possessiveDayString} temp of {value:.1f}{deg} is'
                                  ' the coldest {simpleCityName} has been during'
                                  ' {filter}{since}.' )
                    recordDescription = 'coldest'
                    if hour != None:
                        recordDescription = None
                        tweet = ( '{possessiveDayString} {hour} temp of {value:.1f}{deg}'
                                  ' was {cityName} coldest {since}.' )
                        if self.limitToThisMonth:
                            tweet = ( '{possessiveDayString} {hour} temp of'
                                      ' {value:.1f}{deg} was {cityName} coldest'
                                      ' {filter}{since}.' )
            elif self.field == daily.MAX_HUMIDEX:
                recordDescription = 'muggiest'
                tweet = 'With a humidex of {value:.1f}, {day} {cityName} {record} {filter}day {since}.'
                if hour != None:
                    tweet = 'With a {hour} humidex of {value:.1f}, {day} {cityName} {record} {filter}day {since}.'
            elif self.field == daily.MIN_WINDCHILL:
                assert(hour is not None)
                recordDescription = 'windchilliest'
                #tweet = 'With a windchill of {value:.1f}, {day} {cityName} {record} {filter}day {since}.'
                #if hour != None:
                tweet = 'With a {hour} windchill of {value:.1f}, {day} {cityName} {record} {filter}day {since}.'
            elif self.field == daily.TOTAL_RAIN_MM:
                recordDescription = 'wettest'
                tweet = 'With {value:.1f}mm of rain, {day} {cityName} {record} {filter}day {since}.'
            elif self.field == daily.TOTAL_SNOW_CM:
                recordDescription = 'snowiest'
                tweet = ( 'With {value:.1f}cm of snow, {day} {cityName}'
                          ' {record} {filter}day {since}.' )
                if hour != None:
                    tweet = ( 'With a {hour} snow total of {value:.0f}cm, {day} {cityName}'
                              ' {record} {filter}day {since}.' )
                    media = metarSnowChart.main(
                        city, sampleDay, recently=True, thisDayInHistory=False,
                        thisMonthInHistory=False,
                        days=1, field=daily.TOTAL_SNOW_CM)

            elif self.field == daily.SNOW_ON_GRND_CM:
                recordDescription = 'deepest'
                tweet = ( 'With {value}cm of snow-on-the-ground, {day} {cityName}'
                          ' {record} {filter}day {since}.' )
                media = recordSinceChart.main(
                    city, sampleDay,
                    recently=True, thisDayInHistory=False,
                    field=daily.SNOW_ON_GRND_CM)
            elif self.field == daily.SPD_OF_MAX_GUST_KPH:
                recordDescription = 'windiest'
                tweet = ( 'With a wind gust of {value:.1f}km/h, {day} {cityName}'
                          ' {record} {filter}day {since}.' )
            elif self.field == daily.AVG_WIND:
                recordDescription = 'windiest'
                if maxRecord is False:
                    recordDescription = 'calmest'
                tweet = 'With an avg wind of {value:.0f}km/h, {day} {cityName} {record} {filter}day {since}.'
            elif self.field == daily.MIN_HUMIDITY:
                assert(hour is not None)
                recordDescription = 'moistest'
                if maxRecord is False:
                    recordDescription = 'driest'
                    if hour != None:
                        tweet = 'With a {hour} humidity of {value:.0f}%, {day} {cityName} {record} {filter}day {since}.'
                else:
                    tweet = 'With a min humidity of {value:.0f}%, {day} {cityName} {record} {filter}day {since}.'
            elif self.field == daily.MEAN_HUMIDITY:
                recordDescription = 'moistest'
                if maxRecord is False:
                    recordDescription = 'driest'
                tweet = 'With a humidity of {value:.1f}%, {day} {cityName} {record} {filter}day {since}.'
            hourText = clock12(city, hour)
            tweet = tweet.format(value=v,
                                 deg=chr(0x2103),
                                 hour=hourText,
                                 day=dayString,
                                 possessiveDayString=possessiveDayString,
                                 cityName='#'+possessive(stations.city[city].name),
                                 simpleCityName='#'+stations.city[city].name,
                                 record=recordDescription,
                                 since=sinceWhat,
                                 filter=['',monthName(sampleDay.month, long=True)+' '][self.limitToThisMonth])
            (use, tweet) = shouldTweetSuffix(
                city, tweet,
                oldText=alreadyReportedRecordTweet)
            if use is True:
                delayedTweets.addToEndOfListForCity(city, tweet, media)
                if city == 'ottawa':
                    sendMail.sendMailConsole("thats.unpossible@gmail.com",
                                             self.address,
                                             subject = self.title,
                                             text = tweet,
                                             auto = True)
            self.datemarker[datemarker] = PreviousReport(v, tweet)

    def call(self, city, sampleDay):
        datemarker = dateMarkerFromDate(sampleDay)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)
        try:
            dayValues = daily.dataByCity[city][sampleDay]
        except KeyError:
            return
        v = dayValues[self.field.index]
        if v is None:
            return
        flag = dayValues[self.field.index+1]
        if self.skipIncomplete and 'I' in flag:
            return
        if self.skipMinEstimated and self.skipMaxEstimated and 'E' in flag:
            return

        if alreadyReportedRecord != None:
            if v == alreadyReportedRecord.value:
                return

        maxV = None
        minV = None

        for recordDay in daily.dayRange(sampleDay-datetime.timedelta(days=1),
                                        min(daily.dataByCity[city].keys())-datetime.timedelta(days=1),
                                        -1):
            if self.limitToThisMonth is True and recordDay.month != sampleDay.month:
                # This is not the month we were instructed to look at, so just skip it
                continue
            try:
                rv = daily.dataByCity[city][recordDay][self.field.index]
            except KeyError:
                continue
            if rv is None:
                continue

            if maxV == None and rv >= v:
                maxV = (rv, recordDay)
                if minV is not None:
                    break
            if minV == None and rv <= v:
                minV = (rv, recordDay)
                if maxV is not None:
                    break

        if not (self.skipMaxRecords
                or (self.skipMaxEstimated and 'H' in flag)
                or (self.skipMaxIncomplete and 'I' in flag)
        ):
            hour = findHourFlag(flag)
            self.maybeTweetRecordSince(city, v, maxV, alreadyReportedRecord,
                                       hour, sampleDay, datemarker, maxRecord=True)
        if not (self.skipMinRecords
                or (self.skipMinEstimated and 'H' in flag)
                or (self.skipMinIncomplete and 'I' in flag)
        ):
            hour = findHourFlag(flag)
            self.maybeTweetRecordSince(city, v, minV, alreadyReportedRecord,
                                       hour, sampleDay, datemarker, maxRecord=False)


class RecordSinceAlertMultiDay(Alert):
    def __init__(
            self,
            title, address, field,
            dayCount,
            skipMinRecords=False,
            skipMaxRecords=False,
            skipMinEstimated=False,
            skipMaxEstimated=False,
            skipIncomplete=False,
            skipBelowZero=False,
            skipFilter=None
    ):
        Alert.__init__(
            self,
            title, address, field,
            skipMinRecords, skipMaxRecords,
            skipMinEstimated, skipMaxEstimated,
            skipIncomplete,
            skipBelowZero,
            skipFilter)
        self.dayCount=dayCount
    def maybeTweetRecordSince(
            self, city,
            v, recordValue, alreadyReportedRecord,
            dayCount, sampleDay, datemarker):

        limit=365 #days
        #print (sampleDay, float(v), self.field.name, repr(recordValue))
        if recordValue != None:
            ageOfRecord = (today(city) - recordValue[1]).days
        if recordValue == None or ageOfRecord > limit:
            alreadyReportedRecordTweet = None
            if alreadyReportedRecord != None:
                alreadyReportedRecordTweet = alreadyReportedRecord.tweet
                #print("\n--------------------------------------------------------------------------------\nCorrecting a previous record of {:.1f}".format(alreadyReportedRecord.value))
                #print("OldTweet: ", alreadyReportedRecord.tweet)
            if dayCount == 1:
                dayString = '{} was'.format(
                    dayStr(city, sampleDay))
            else:
                dayString = '{}-{} were'.format(
                    dayStr(city, sampleDay-datetime.timedelta(days=dayCount-1)),
                    dayStr(city, sampleDay))
            sinceWhat = sinceWhen.sinceWhen(
                city, self.field.index,
                recordDate = recordValue[1] if recordValue is not None else None)

            if self.field == daily.MAX_TEMP:
                recordDescription = 'warmest'
                if v > 24:
                    recordDescription = 'hottest'
                if maxRecord is False:
                    recordDescription = 'coldest'
                    tweet = 'With a high of just {value:.1f}{deg}, {day} {cityName} {record} day {since}.'
                else:
                    tweet = 'With a high of {value:.1f}{deg}, {day} {cityName} {record} day {since}.'
                    if hour != None:
                        tweet = 'With a {hour} temp of {value:.1f}{deg}, {day} {cityName} {record} day {since}.'
            elif self.field == daily.MIN_TEMP:
                recordDescription = 'warmest'
                if v > 24:
                    recordDescription = 'hottest'
                tweet = 'With a low of {value:.1f}{deg}, {day} {cityName} {record} day {since}.'
                if maxRecord is False:
                    recordDescription = 'coldest'
                    if hour != None:
                        tweet = 'With a {hour} temp of {value:.1f}{deg}, {day} {cityName} {record} day {since}.'
            elif self.field == daily.MAX_HUMIDEX:
                recordDescription = 'muggiest'
                tweet = 'With a humidex of {value:.1f}, {day} {cityName} {record} day {since}.'
                if hour != None:
                    tweet = 'With a {hour} humidex of {value:.1f}, {day} {cityName} {record} day {since}.'
            elif self.field == daily.MIN_WINDCHILL:
                assert(hour is not None)
                recordDescription = 'windchilliest'
                #tweet = 'With a windchill of {value:.1f}, {day} {cityName} {record} day {since}.'
                #if hour != None:
                tweet = 'With a {hour} windchill of {value:.1f}, {day} {cityName} {record} day {since}.'
            elif self.field == daily.TOTAL_RAIN_MM:
                recordDescription = 'wettest'
                tweet = 'With {dayCount}-day rainfall of {value:.1f}mm, {day} {cityName} {record} {dayCount} days {since}.'
            elif self.field == daily.TOTAL_SNOW_CM:
                recordDescription = 'snowiest'
                tweet = 'With {dayCount}-day snowfall of {value:.1f}cm, {day} {cityName} {record} {dayCount} days {since}.'
            elif self.field == daily.SNOW_ON_GRND_CM:
                recordDescription = 'snowiest'
                tweet = 'With {value:.1f}cm of snow-on-the-ground, {day} {cityName} {record} day {since}.'
            elif self.field == daily.SPD_OF_MAX_GUST_KPH:
                recordDescription = 'windiest'
                tweet = 'With a wind gust of {value:.1f}km/h, {day} {cityName} {record} day {since}.'
            elif self.field == daily.AVG_WIND:
                recordDescription = 'windiest'
                tweet = 'With a {dayCount}-day wind of {value:.1f}km/h, {day} {cityName} {record} {dayCount} days {since}.'
            elif self.field == daily.MIN_HUMIDITY:
                assert(hour is not None)
                recordDescription = 'moistest'
                if maxRecord is False:
                    recordDescription = 'driest'
                    if hour != None:
                        tweet = 'With a {hour} humidity of {value:.0f}%, {day} {cityName} {record} day {since}.'
                else:
                    tweet = 'With a min humidity of {value:.0f}%, {day} {cityName} {record} day {since}.'
            elif self.field == daily.MEAN_HUMIDITY:
                recordDescription = 'moistest'
                #if maxRecord is False:
                #    recordDescription = 'driest'
                tweet = 'With a {dayCount}-day humidity of {value:.1f}%, {day} {cityName} {record} {dayCount} days {since}.'
            tweet = tweet.format(value=float(v),
                                 deg=chr(0x2103),
                                 day=dayString,
                                 cityName='#'+possessive(stations.city[city].name),
                                 record=recordDescription,
                                 since=sinceWhat,
                                 dayCount=dayCount)
            (use, tweet) = shouldTweetSuffix(
                city, tweet,
                oldText=alreadyReportedRecordTweet)
            if use is True:
                delayedTweets.addToEndOfListForCity(city, tweet)
                if city == 'ottawa':
                    sendMail.sendMailConsole("thats.unpossible@gmail.com",
                                             self.address,
                                             subject = self.title,
                                             text = tweet,
                                             auto = True)
            self.datemarker[datemarker] = PreviousReport(round(float(v),1), tweet)

    def call(self, city, sampleDay):
        yesterday=sampleDay-datetime.timedelta(days=1)
        datemarker = dateMarkerFromDate(sampleDay)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)
        v = [None]*self.dayCount
        for i in range(self.dayCount):
            v[i] = self.calcForDays(city, sampleDay, days=i+1, history=False)
            if ( i > 1
                 and v[i] is not None
                 and self.calcForDays(city, yesterday, days=i, history=False) >= v[i]
            ):
                print("Skipping {sampleDay} because the previous day's record was worse."
                      .format(**locals()))
                v[i] = None
        if v.count(None) == len(v):
            # We have no observations to go by
            return

        maxV = [None]*self.dayCount
        minV = None

        for recordDay in daily.dayRange(yesterday,
                                        min(daily.dataByCity[city].keys())-datetime.timedelta(days=1),
                                        -1):
            for i in range(self.dayCount):
                if maxV[i] is None and v[i] is not None:
                    val = self.calcForDays(city, recordDay, days=i+1, history=True)
                    if val is None:
                        continue
                    if val >= v[i]:
                        recordValue = val
                        maxV[i] = (recordValue, recordDay)
                        break
            if maxV.count(None) == 0:
                break

        oldestDate = None
        for i in range(len(maxV)):
            if v[i] is None:
                continue
            if maxV[i] is None:
                oldestIndex = i
                dayCount = i + 1
                break
            if oldestDate is None or maxV[i][1] < oldestDate:
                oldestDate = maxV[i][1]
                oldestIndex = i
                dayCount = i + 1
        if dayCount == 1:
            return #There are other tests to catch 1-day records
        if alreadyReportedRecord is not None:
            alreadyReportedRecord = PreviousReport(value=alreadyReportedRecord[0],
                                                   tweet=alreadyReportedRecord[1])
            if str(round(float(v[oldestIndex]),1)) == str(float(alreadyReportedRecord.value)):
                return

        self.maybeTweetRecordSince(city, v[oldestIndex], maxV[oldestIndex],
                                   alreadyReportedRecord,
                                   dayCount, sampleDay, datemarker)


class RecordSinceAlertSum(RecordSinceAlertMultiDay):
    def calcForDays(self, city, day, days, history):
        if day == datetime.date(2008,12,25) and history is True and days==2:
            #import pudb; pu.db
            pass
        values = []
        for i in range(days):
            specificSampleDay = day-datetime.timedelta(days=i)
            try:
                v = daily.dataByCity[city][specificSampleDay][self.field.index]
                flag = daily.dataByCity[city][specificSampleDay][self.field.index+1]
            except KeyError:
                v = None
            if self.skipIncomplete and 'I' in flag:
                v = None
            if self.skipMinEstimated and self.skipMaxEstimated and 'E' in flag:
                v = None
            values.append(v)
            if values[-1] is None:
                if history is False:
                    return None
                values[-1] = 0

        if len(values) == 0:
            return None
        if history is False and min(values) == 0:
            return None
        if values[0] == 0:
            # Never advertise a sequence of days that didn't END with the event
            # you are looking for
            return None
        sumOfValues = sum(values)
        return sumOfValues


class RecordSinceAlertAvg(RecordSinceAlertMultiDay):
    def calcForDays(self, city, day, days, history):
        v = []
        for i in range(days):
            specificSampleDay = day-datetime.timedelta(days=i)
            try:
                fieldIndex = self.field.index
                v.append(daily.dataByCity[city][specificSampleDay][fieldIndex])
            except KeyError:
                return None
            if v[-1] is None:
                return None
            flag = daily.dataByCity[city][specificSampleDay][self.field.index+1]
            if self.skipIncomplete and 'I' in flag:
                return None
            if self.skipMinEstimated and self.skipMaxEstimated and 'E' in flag:
                return None

        if len(v) == 0:
            return None
        v = sum(v)/len(v)
        return v
