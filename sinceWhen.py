from alert import *

import daily

def yearsDiff(new, old):
    yearDiff = new.year - old.year
    try:
        oldDateThisYear = datetime.date(new.year, old.month, old.day)
    except ValueError:
        if old.month == 2 and old.day == 29:
            oldDateThisYear = datetime.date(new.year, old.month, old.day-1)
        else:
            raise
    if oldDateThisYear <= new:
        return yearDiff + (new-oldDateThisYear).days / 1000
    try:
        oldDateLastYear = datetime.date(new.year-1, old.month, old.day)
    except ValueError:
        if old.month == 2 and old.day == 29:
            # Feb 29th. Can't just subtract one year.
            oldDateLastYear = datetime.date(new.year-1, old.month, old.day-1)
        else:
            raise
    return yearDiff - 1 + (new-oldDateLastYear).days / 1000

def sinceWhen(city, valueIndex, recordDate):
    cityData = daily.load(city)
    if recordDate is None:
        firstDateWithObservation = cityData.firstDateWithValue(valueIndex)
        sinceWhat = ( 'since records began in {begin}'
                      .format(begin=firstDateWithObservation.year) )
        return sinceWhat
    sinceWhat = 'since {}, {}'.format(dayDescription(city, recordDate), recordDate.year)
    ageYears = yearsDiff(today(city), recordDate)
    if ageYears < 1:
        sinceWhat =  'since {}'.format(dayDescription(city, recordDate))
    if ageYears > 2:
        sinceWhat = ( "in more than {} years, since {}, {}"
                      .format(int(ageYears),
                              dayDescription(city, recordDate),
                              recordDate.year) )
        if ageYears - int(ageYears) > 0.330:
            sinceWhat = ( "in almost {} years, since {}, {}"
                          .format(int(ageYears+1),
                                  dayDescription(city, recordDate),
                                  recordDate.year) )
    return sinceWhat
