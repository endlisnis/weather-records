from alert import *
import dailyRecords
import forecast
import daily
import dayplot
import os
import delayedTweets
import htmlday
from decimal import Decimal
from monthName import monthName
from alertTweets import *
from previousReport import PreviousReport

def dayOfWeek(day):
    return day.strftime('%A')

def tweetText(city, day, field, value, prevRecordValue, prevRecordYear, recordIsMax):
    dayString = 'today could be'
    if day == today(city) + datetime.timedelta(1):
        dayString = 'tomorrow could be'
    elif day != today(city):
        dayString = '{} could be'.format(dayOfWeek(day))

    sinceWhat = ( 'records began in {begin}'
                  .format(
                      begin=daily.dataByCity[city].firstDateWithValue(
                          field.index,
                          monthMask=day.month, dayMask=day.day).year) )
    if prevRecordValue != None:
        sinceWhat = '{prevRecordYear}'.format(prevRecordYear=prevRecordYear)

    if field.name == "MAX_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
            if value > 24:
                recordDescription = 'hottest'
        tweet = ( 'With a forecast high of {value}℃, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MEAN_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
            if value > 24:
                recordDescription = 'hottest'
        tweet = ( u'With a mean of {value}℃, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MIN_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
        tweet = ( 'With a forecast low of {value}℃, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "TOTAL_SNOW_CM":
        recordDescription = 'snowiest'
        tweet = ( 'With {value}cm of snow, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "TOTAL_RAIN_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value}mm of rain, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "TOTAL_PRECIP_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value}mm of precipitation, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "SNOW_ON_GRND_CM":
        value = int(value)
        recordDescription = 'shallowest'
        tweet = ( 'With only {value}cm of snow cover, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
        if recordIsMax:
            recordDescription = 'deepest'
            tweet = ( 'With {value}cm of snow cover, {day} {cityName} {record} {dateDescription}'
                      ' since {since}.' )
    elif field.name == "SPD_OF_MAX_GUST_KPH":
        recordDescription = 'windiest'
        tweet = ( 'With a max gust of {value}km/h, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MAX_HUMIDEX":
        recordDescription = 'muggiest'
        tweet = ( 'With a humidex of {value}, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MIN_WINDCHILL":
        recordDescription = 'windchilliest'
        tweet = ( 'With a windchill of {value}, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "AVG_WINDCHILL":
        recordDescription = 'windchilliest'
        tweet = ( 'With an avg windchill of {value}, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "AVG_WIND":
        recordDescription = 'calmest'
        if recordIsMax:
            recordDescription = 'windiest'
        tweet = ( 'With an avg wind of {value}km/h, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MEAN_HUMIDITY":
        recordDescription = 'driest'
        if recordIsMax:
            recordDescription = 'moistest'
        tweet = ( 'With a mean humidity of {value}%, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )
    elif field.name == "MIN_HUMIDITY":
        recordDescription = 'driest'
        tweet = ( 'With a min humidity of {value}%, {day} {cityName} {record} {dateDescription}'
                  ' since {since}.' )


    tweet = tweet.format( value=value,
                          day=dayString,
                          cityName='#'+possessive(stations.city[city].name),
                          record=recordDescription,
                          dateDescription=dayDescription(city, day, static=True),
                          since=sinceWhat)
    return tweet

def maybePostTweet(city, day, field, value,
                   prevRecordValue, prevRecordYear, recordIsMax):
    tweet = tweetText(city, day, field, value,
                      prevRecordValue, prevRecordYear, recordIsMax)
    (post, tweet) = shouldTweetSuffix(city, tweet, accountHint='')
    if post is True:
        lineFname, bottom10Fname, top10Fname = dayplot.createPlots(
            city=city,
            field=field,
            name=field.name,
            plotDate=day,
            plotZeros=(field.minValue != 0),
            verbose=False)
        svgs = [lineFname, bottom10Fname]
        if recordIsMax:
            svgs = [lineFname, top10Fname]
        pngs = []
        for svg in svgs:
            pngname = svg.replace('.svg', '.png').replace('/svg/','/')
            print(svg, pngname)
            assert os.system('rsvg-convert -o %s --background-color=white %s' % (pngname, svg)) == 0
            pngs.append(pngname)
        delayedTweets.addToEndOfListForCity(city, tweet, pngs)
    return tweet

class DailyForecastAlert(Alert):
    def dayRange(self, city):
        startDate = today(city)
        return daily.dayRange(startDate, today(city)+datetime.timedelta(2))

    def call(self, city, sampleDay):
        allcast = forecast.getForecastDataEnvCan(city)
        try:
            cast = allcast[sampleDay]
        except KeyError:
            return

        if cast[self.field.index] is None:
            # No forecast is available for this field for this day, skip
            return

        try:
            #print(city, sampleDay, cast)
            dInfo = dailyRecords.getInfo(city, sampleDay, self.field,
                                         recentValOverride=cast)
        except KeyError:
            return


        msg = ''
        msgPrefix = ''
        datemarker = dateMarkerFromDate(sampleDay)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)
        if alreadyReportedRecord != None:
            updatedAlert = 'This alert corrects the last alert which reported a value of %.1f%s.<br>\n' % (alreadyReportedRecord.value, self.field.htmlunits)
            msgPrefix = updatedAlert + '\n' + alreadyReportedRecord.tweet

        #print('cast={} recent={} max={} day={} since={}'.format(str(cast), float(dInfo.recent), float(dInfo.max.value), sampleDay.year, dInfo.maxSince.year))
        if ( dInfo.recent != None
             and (alreadyReportedRecord == None
                  or alreadyReportedRecord.value != dInfo.recent)
        ):
            if ( ( dInfo.recent > dInfo.max.value
                   or ( sampleDay.year - dInfo.maxSince.year) > 55 )
                 and self.skipMaxRecords == False
                 and not (self.skipMaxEstimated and dInfo.recentEstimated)
            ):
                print(msgPrefix)
                tweet = maybePostTweet(city, sampleDay, self.field, dInfo.recent,
                                       dInfo.maxSince.value, dInfo.maxSince.year,
                                       recordIsMax=True)
                msg += tweet + '<br>'
                if dInfo.maxSince.value == None:
                    compareDay = datetime.date(
                        dInfo.max.year, sampleDay.month, sampleDay.day)
                else:
                    compareDay = datetime.date(
                        dInfo.maxSince.year, sampleDay.month, sampleDay.day)

                self.datemarker[datemarker] = PreviousReport(dInfo.recent, tweet)
            elif ( ( dInfo.recent < dInfo.min.value
                     or ( sampleDay.year - dInfo.minSince.year) > 55 )
                   and self.skipMinRecords == False
                   and not (self.skipMinEstimated and dInfo.recentEstimated) ):

                print(msgPrefix)
                tweet = maybePostTweet(city, sampleDay, self.field, dInfo.recent,
                                       dInfo.minSince.value, dInfo.minSince.year, False)
                msg += tweet + '<br>'
                if dInfo.minSince.value == None:
                    compareDay = datetime.date(dInfo.min.year, sampleDay.month, sampleDay.day)
                else:
                    compareDay = datetime.date(dInfo.minSince.year, sampleDay.month, sampleDay.day)
                self.datemarker[datemarker] = PreviousReport(dInfo.recent, tweet)
            if len(msg) > 0:
                return Email(field=self.field, date=sampleDay, message=msgPrefix+msg)

class DailyForecastAlertMaxMin(Alert):
    def dayRange(self, city):
        startDate = today(city)
        return daily.dayRange(startDate, today(city)+datetime.timedelta(8))

    def call(self, city, sampleDay):
        allcast = forecast.getForecastDataEnvCan(city)
        try:
            cast = allcast[sampleDay]
        except KeyError:
            return

        if len(cast[self.field.index]) == 0:
            # No forecast is available for this field for this day, skip
            return

        nextDay = sampleDay+datetime.timedelta(1)
        try:
            cast2 = allcast[sampleDay+datetime.timedelta(1)]
        except KeyError:
            return
        #print(cast.MIN_TEMP, cast2.MIN_TEMP, str(min(int(cast.MIN_TEMP),int(cast2.MIN_TEMP))))
        cast = cast._replace(MIN_TEMP=str(min(int(cast.MIN_TEMP),int(cast2.MIN_TEMP))))

        try:
            #print(city, sampleDay, cast)
            dInfo = dailyRecords.getInfo(city, sampleDay, self.field,
                                         recentValOverride=cast)
        except KeyError:
            return


        msg = ''
        msgPrefix = ''
        datemarker = dateMarkerFromDate(sampleDay)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)
        if alreadyReportedRecord != None:
            print(repr(alreadyReportedRecord))
            updatedAlert = 'This alert corrects the last alert which reported a value of %.1f%s.<br>\n' % (alreadyReportedRecord.value, self.field.htmlunits)
            msgPrefix = updatedAlert + '\n' + alreadyReportedRecord.tweet

        #print('cast={} recent={} max={} day={} since={}'.format(str(cast), float(dInfo.recent), float(dInfo.max.value), sampleDay.year, dInfo.maxSince.year))
        if ( dInfo.recent != None
             and (alreadyReportedRecord == None
                  or alreadyReportedRecord.value != dInfo.recent)
        ):
            if ( ( dInfo.recent > dInfo.max.value
                   or ( sampleDay.year - dInfo.maxSince.year) > 55 )
                 and self.skipMaxRecords == False
                 and not (self.skipMaxEstimated and dInfo.recentEstimated)
            ):
                print(msgPrefix)
                tweet = maybePostTweet(city, sampleDay, self.field, dInfo.recent,
                                       dInfo.maxSince.value, dInfo.maxSince.year,
                                       recordIsMax=True)
                msg += tweet + '<br>'
                if dInfo.maxSince.value == None:
                    compareDay = datetime.date(
                        dInfo.max.year, sampleDay.month, sampleDay.day)
                else:
                    compareDay = datetime.date(
                        dInfo.maxSince.year, sampleDay.month, sampleDay.day)

                self.datemarker[datemarker] = PreviousReport(dInfo.recent, tweet)
            if len(msg) > 0:
                return Email(field=self.field, date=sampleDay, message=msgPrefix+msg)
