#!/usr/bin/python3
# -*- coding: utf-8 -*-
from alert import *
import dailyRecords
from monthName import monthName
from alertTweets import *
import dayplot
import os
import delayedTweets
import htmlday
import stations
import metarSnowChart
import recordSinceChart
import datetime as dt

def dayOfWeek(day):
    return day.strftime('%A')


def tweetText(city, day, field, value, hour, prevRecordValue, prevRecordYear, recordIsMax):
    if day == today(city):
        dayString = 'today is'
    elif day == today(city)-datetime.timedelta(days=1):
        dayString = 'yesterday was'
    elif day >= today(city)-datetime.timedelta(days=6):
        dayString = '{} was'.format(dayOfWeek(day))
    else:
        dayString = '{} {} was'.format(day.strftime('%B'), nth(day.day) )


    sinceWhat = ( 'records began in {begin}'
                  .format(
                      begin=daily.dataByCity[city].firstDateWithValue(
                          field.index,
                          monthMask=day.month, dayMask=day.day).year) )
    if prevRecordValue != None:
        sinceWhat = '{prevRecordYear}'.format(prevRecordYear=prevRecordYear)

    media = None

    if field.name == "MAX_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
            if value > 24:
                recordDescription = 'hottest'
        tweet = ( 'With a high of {value:.1f}{deg}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} temp of {value:.1f}{deg}, {relativeDay} {cityName}'
                      ' {record} {day} since {since}.' )
            media = metarSnowChart.main(
                city, day, recently=False, thisDayInHistory=True, thisMonthInHistory=False,
                days=1, field=field, checkMax=recordIsMax)
    elif field.name == "MEAN_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
            if value > 24:
                recordDescription = 'hottest'
        tweet = ( 'With a mean of {value:.1f}{deg}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MIN_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
        tweet = ( 'With a low of {value:.1f}{deg}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} temp of {value:.1f}{deg}, {relativeDay} {cityName} {record} {day}'
                      ' since {since}.' )
            media = metarSnowChart.main(
                city, day, recently=False, thisDayInHistory=True,
                thisMonthInHistory=False, days=1,
                field=field, checkMax=recordIsMax)
    elif field.name == "TOTAL_SNOW_CM":
        recordDescription = 'snowiest'
        tweet = ( 'With {value:.1f}cm of snow, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} snow total of {value:.0f}cm, {relativeDay} {cityName}'
                      ' {record} {day} since {since}.' )
            media = metarSnowChart.main(
                city, day, recently=False, thisDayInHistory=True, thisMonthInHistory=False,
                days=1, field=field)
    elif field.name == "TOTAL_RAIN_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value:.1f}mm of rain, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "TOTAL_PRECIP_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value:.1f}mm of precipitation, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "SNOW_ON_GRND_CM":
        value = int(value)
        recordDescription = 'shallowest'
        tweet = ( 'With only {value}cm of snow cover, {relativeDay} {cityName} {record}'
                  ' {day} since {since}.' )
        if recordIsMax:
            recordDescription = 'deepest'
            tweet = ( 'With {value}cm of snow cover, {relativeDay} {cityName} {record}'
                      ' {day} since {since}.' )
            media = recordSinceChart.main(city, day,
                                          recently=False, thisDayInHistory=True,
                                          field=daily.SNOW_ON_GRND_CM)
    elif field.name == "SPD_OF_MAX_GUST_KPH":
        recordDescription = 'windiest'
        tweet = ( 'With a max gust of {value}km/h, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MAX_HUMIDEX":
        recordDescription = 'muggiest'
        tweet = ( 'With a humidex of {value:.1f}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} humidex of {value:.1f}, {relativeDay} {cityName}'
                      ' {record} {day} since {since}.' )
    elif field.name == "MIN_WINDCHILL":
        recordDescription = 'windchilliest'
        tweet = ( 'With a windchill of {value:.1f}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} windchill of {value:.1f}, {relativeDay} {cityName} {record}'
                      ' {day} since {since}.' )
            media = metarSnowChart.main(
                city, day, recently=False, thisDayInHistory=True, thisMonthInHistory=False,
                days=1, field=field, checkMax=recordIsMax)
    elif field.name == "AVG_WINDCHILL":
        recordDescription = 'windchilliest'
        tweet = ( 'With an avg windchill of {value:.1f}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "AVG_WIND":
        recordDescription = 'calmest'
        if recordIsMax:
            recordDescription = 'windiest'
        tweet = ( 'With an avg wind of {value:.0f}km/h, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MEAN_HUMIDITY":
        recordDescription = 'driest'
        if recordIsMax:
            recordDescription = 'moistest'
        tweet = ( u'With a mean humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MIN_HUMIDITY":
        recordDescription = 'driest'
        tweet = ( 'With a min humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                      ' since {since}.' )

    hourText = clock12(city, hour)
    tweet = tweet.format(
        value=value,
        deg=chr(0x2103),
        relativeDay=dayString,
        cityName='#'+possessive(stations.city[city].name),
        record=recordDescription,
        day=dayDescription(city, day),
        since=sinceWhat,
        hour=hourText)
    return tweet, media


def maybePostTweet(city, day, field, value, hour,
                   prevRecordValue, prevRecordYear,
                   oldTweet,
                   recordIsMax):
    tweet, media = tweetText(city, day, field, value, hour,
                      prevRecordValue, prevRecordYear, recordIsMax)
    (post, tweet) = shouldTweetSuffix(city, tweet, oldText=oldTweet)
    if post is True:
        if media is None:
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
                assert os.system('rsvg-convert -o %s --background-color=white %s'
                                 % (pngname, svg)) == 0
                pngs.append(pngname)
            media = pngs
        delayedTweets.addToListForCity(city, tweet, media, urgent=(hour is not None))
    return tweet

def tweetCloseText(
        city, day, field, value, hour, prevRecordValue, recordIsMax):
    if day == today(city):
        dayString = 'today is'
    elif day == today(city)-datetime.timedelta(days=1):
        dayString = 'yesterday was'
    elif day >= today(city)-datetime.timedelta(days=6):
        dayString = '{} was'.format(dayOfWeek(day))
    else:
        dayString = '{} {} was'.format(day.strftime('%B'), nth(day.day) )


    if field.name == "MAX_TEMP":
        if recordIsMax:
            tweet = ( 'Near record warmth. A high of {value:.1f}{deg} brought {cityName}'
                      ' within {diff}{deg} of the highest ever recorded on {day}.' )
            if hour != None:
                tweet = ( 'Near record warmth. The {hour} temp of {value:.1f}{deg} brought'
                          ' {cityName} within {diff}{deg} of the highest ever'
                          ' recorded on {day}.' )
        else:
            tweet = ( 'Near record cold. A high of {value:.1f}{deg} brought {cityName}'
                      ' within {diff}{deg} of the lowest high ever recorded on {day}.' )
            if hour != None:
                tweet = ( 'Near record cold. The {hour} temp of {value:.1f}{deg} brought'
                          ' {cityName} within {diff}{deg} of the lowest high ever'
                          ' recorded on {day}.' )
    elif field.name == "MEAN_TEMP":
        recordDescription = 'coldest'
        if recordIsMax:
            recordDescription = 'warmest'
            if value > 24:
                recordDescription = 'hottest'
        tweet = ( 'With a mean of {value:.1f}{deg}, {relativeDay} {cityName} {record}'
                  ' {day} since {since}.' )
    elif field.name == "MIN_TEMP":
        tweet = ( 'Near record cold. A low of {value:.1f}{deg} brought {cityName}'
                  ' within {diff}{deg} of the lowest ever recorded on {day}.' )
        if hour != None:
            tweet = ( 'Near record cold. A {hour} temp of {value:.1f}{deg} brought'
                      ' {cityName} within {diff}{deg} of the lowest ever'
                      ' recorded on {day}.' )
        if recordIsMax:
            tweet = ( 'Near record warmth. A low of {value:.1f}{deg} brought {cityName}'
                      ' within {diff}{deg} of the highest low ever recorded on {day}.' )
    elif field.name == "TOTAL_SNOW_CM":
        recordDescription = 'snowiest'
        tweet = ( 'With {value:.1f}cm of snow, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "TOTAL_RAIN_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value:.1f}mm of rain, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "TOTAL_PRECIP_MM":
        recordDescription = 'wettest'
        tweet = ( 'With {value:.1f}mm of precipitation, {relativeDay} {cityName}'
                  ' {record} {day} since {since}.' )
    elif field.name == "SNOW_ON_GRND_CM":
        value = int(value)
        recordDescription = 'shallowest'
        tweet = ( 'With only {value}cm of snow cover, {relativeDay} {cityName}'
                  ' {record} {day} since {since}.' )
        if recordIsMax:
            recordDescription = 'deepest'
            tweet = ( 'Near record snow depth. {value}cm of snow on the ground brought'
                      ' {cityName} within {diff}cm of the deepest snow ever recorded on'
                      ' {day}.')
    elif field.name == "SPD_OF_MAX_GUST_KPH":
        recordDescription = 'windiest'
        tweet = ( 'With a max gust of {value}km/h, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MAX_HUMIDEX":
        recordDescription = 'muggiest'
        tweet = ( 'With a humidex of {value:.1f}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} humidex of {value:.1f}, {relativeDay} {cityName}'
                      ' {record} {day} since {since}.' )
    elif field.name == "MIN_WINDCHILL":
        tweet = ( 'Near record windchill. A windchill of {value:.1f} brought {cityName}'
                  ' within {diff} of the lowest ever recorded on {day}.' )
        if hour != None:
            tweet = ( 'Near record windchill. {hour} windchill of {value:.1f} brought'
                      ' {cityName} within {diff} of the lowest ever'
                      ' recorded on {day}.' )
    elif field.name == "AVG_WINDCHILL":
        recordDescription = 'windchilliest'
        tweet = ( 'With an avg windchill of {value:.1f}, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "AVG_WIND":
        recordDescription = 'calmest'
        if recordIsMax:
            recordDescription = 'windiest'
        tweet = ( 'With an avg wind of {value:.0f}km/h, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MEAN_HUMIDITY":
        recordDescription = 'driest'
        if recordIsMax:
            recordDescription = 'moistest'
        tweet = ( u'With a mean humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
    elif field.name == "MIN_HUMIDITY":
        recordDescription = 'driest'
        tweet = ( 'With a min humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                  ' since {since}.' )
        if hour != None:
            tweet = ( 'With a {hour} humidity of {value:.1f}%, {relativeDay} {cityName} {record} {day}'
                      ' since {since}.' )

    hourText = clock12(city, hour)
    diff = abs(prevRecordValue - value)
    try:
        tweet = tweet.format(
            value=value,
            deg=chr(0x2103),
            relativeDay=dayString,
            cityName='#'+stations.city[city].name,
            pCityName='#'+possessive(stations.city[city].name),
            day=dayDescription(city, day),
            hour=hourText,
            diff=diff)
    except KeyError:
        import pudb; pu.db
    return tweet


def maybePostCloseTweet(
        city, day, field, value, hour,
        prevRecordValue,
        oldTweet,
        recordIsMax):
    tweet = tweetCloseText(city, day, field, value, hour,
                           prevRecordValue, recordIsMax)
    (post, tweet) = shouldTweetSuffix(city, tweet, oldText=oldTweet)
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
            assert os.system('rsvg-convert -o %s --background-color=white %s'
                             % (pngname, svg)) == 0
            pngs.append(pngname)
        delayedTweets.addToListForCity(city, tweet, pngs, urgent=(hour is not None))
    return tweet

def calcCloseToRecordMax(field, recordVal, curVal):
    diff = abs(recordVal - curVal)
    if field is daily.SNOW_ON_GRND_CM:
        return recordVal > 0 and curVal > 0 and diff > 0 and diff < 10 and diff > curVal/2
    if field in (daily.MAX_TEMP, daily.MIN_TEMP, daily.MIN_WINDCHILL):
        return diff > 0 and diff < 1
    return False


class DailyRecordAlert(Alert):
    def call(self, city, sampleDay):
        try:
            dInfo = dailyRecords.getInfo(city, sampleDay, self.field)
        except KeyError:
            return

        msg = ''
        updatedAlert = ''
        datemarker = dateMarkerFromDate(sampleDay)
        alreadyReportedRecord = self.datemarker.get(datemarker,None)
        alreadyReportedRecordTweet = None
        if alreadyReportedRecord != None:
            updatedAlert = 'This alert corrects the last alert which reported a value of %.1f%s.<br>\n' % (alreadyReportedRecord.value, self.field.htmlunits)
            alreadyReportedRecordTweet = alreadyReportedRecord.tweet

        if ( dInfo.recent != None
             and ( alreadyReportedRecord == None
                   or alreadyReportedRecord.value != dInfo.recent )
             and not (self.skipIncomplete and dInfo.incomplete)
             and not (self.skipBelowZero and dInfo.recent < 0)
        ):
            tweet = None
            #if self.field is daily.MIN_TEMP and sampleDay == dt.date(2017,3,5):
            #    import pudb; pu.db
            closeToMax = calcCloseToRecordMax(self.field, dInfo.max.value, dInfo.recent)
            closeToMin = calcCloseToRecordMax(self.field, dInfo.min.value, dInfo.recent)
            recordMax = ( dInfo.recent > dInfo.max.value
                          or ( sampleDay.year - dInfo.maxSince.year) > 55 )
            tryMax = ( self.skipMaxRecords == False
                       and not (self.skipMaxEstimated and dInfo.recentEstimated )
                       and not (self.skipMaxIncomplete and dInfo.incomplete) )

            recordMin = ( dInfo.recent < dInfo.min.value
                          or ( sampleDay.year - dInfo.minSince.year) > 55 )
            tryMin = ( self.skipMinRecords == False
                       and not (self.skipMinEstimated and dInfo.recentEstimated)
                       and not (self.skipMinIncomplete and dInfo.incomplete) )
            if tryMax and recordMax:
                print(updatedAlert, end=' ')
                tweet = maybePostTweet(city,
                                       sampleDay, self.field, dInfo.recent,
                                       dInfo.recentEstimatedHour,
                                       dInfo.maxSince.value, dInfo.maxSince.year,
                                       oldTweet=alreadyReportedRecordTweet,
                                       recordIsMax=True)
                msg += tweet + '<br>'
                if dInfo.maxSince.value == None:
                    compareDay = datetime.date(dInfo.max.year,
                                               sampleDay.month, sampleDay.day)
                else:
                    compareDay = datetime.date(dInfo.maxSince.year,
                                               sampleDay.month, sampleDay.day)
                    msg += htmlday.htmlTable( daily.load(city), (sampleDay, compareDay) )
            elif tryMax and closeToMax:
                tweet = maybePostCloseTweet(
                    city,
                    sampleDay, self.field, dInfo.recent,
                    dInfo.recentEstimatedHour,
                    dInfo.max.value,
                    oldTweet=alreadyReportedRecordTweet,
                    recordIsMax=True)
            elif tryMin and recordMin:
                print(updatedAlert, end=' ')
                #import pudb; pu.db
                tweet = maybePostTweet(city,
                                       sampleDay, self.field, dInfo.recent,
                                       dInfo.recentEstimatedHour,
                                       dInfo.minSince.value, dInfo.minSince.year,
                                       oldTweet=alreadyReportedRecordTweet,
                                       recordIsMax=False)
                msg += tweet + '<br>'
                if dInfo.minSince.value == None:
                    compareDay = datetime.date(dInfo.min.year,
                                               sampleDay.month, sampleDay.day)
                else:
                    compareDay = datetime.date(dInfo.minSince.year,
                                               sampleDay.month, sampleDay.day)
                    print((dInfo.minSince.value, compareDay, sampleDay))
                    msg += htmlday.htmlTable( daily.load(city), (sampleDay, compareDay) )
            elif tryMin and closeToMin:
                tweet = maybePostCloseTweet(
                    city,
                    sampleDay, self.field, dInfo.recent,
                    dInfo.recentEstimatedHour,
                    dInfo.min.value,
                    oldTweet=alreadyReportedRecordTweet,
                    recordIsMax=False)
            if tweet is not None:
                self.datemarker[datemarker] = (dInfo.recent, tweet)
            if len(msg) > 0:
                return Email(field=self.field, date=sampleDay, message=msg)


if __name__ == '__main__':
    print(dayDescription('ottawa', datetime.date(2016,11,11)))
    print(dayDescription('ottawa', datetime.date(2016,11,10)))
    print(dayDescription('ottawa', datetime.date(2016,12,25)))
    print(dayDescription('ottawa', datetime.date(2016,12,26)))
