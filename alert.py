import daily
import datetime
import holidays
import stations
from collections import namedtuple
from monthName import *



def dayDescription(city, dateStamp, static=False):
    #import pudb; pu.db
    province = stations.city[city].label[:2].upper()
    localHolidays = holidays.Canada(
        state=province,
        years=[dateStamp.year, dateStamp.year-1],
        observed=False)
    for year in [dateStamp.year, dateStamp.year-1]:
        localHolidays.append(
            { datetime.date(year, 11, 11): 'Remembrance Day',
              datetime.date(year, 12, 24): 'Christmas Eve',
              datetime.date(year, 12, 31): 'New Year\'s Eve',
              datetime.date(year, 2, 14): 'Valentine\'s Day',
            }
        )
    holidayName = localHolidays.get(dateStamp,'')
    plainDate = '{} {}'.format(monthName(dateStamp.month), nth(dateStamp.day))
    if holidayName == '':
        return plainDate

    if static is True:
        prevYearDate = datetime.date(dateStamp.year-1, dateStamp.month, dateStamp.day)
        prevYearHolidayName = localHolidays.get(prevYearDate,'')
        if holidayName != prevYearHolidayName:
            return plainDate

    return holidayName

def today(city):
    return daily.timeByCity[city].date()

def dayOfWeek(day):
    return day.strftime('%A')

def dateMarkerFromDate(dateValue):
    return dateValue.year*10000+dateValue.month*100+dateValue.day

def dateFromMarker(dateMarker):
    return datetime.date(dateMarker // 10000, (dateMarker % 10000) // 100, dateMarker % 100)

def findStartsWith(iterable, prefixlist):
    for i in iterable:
        for p in prefixlist:
            if i.startswith(p):
                return i

def clock12(city, hour24):
    if hour24 is None:
        return None
    lookup = {
        None: None,
        0: 'midnight',
        1: '1am',
        2: '2am',
        3: '3am',
        4: '4am',
        5: '5am',
        6: '6am',
        7: '7am',
        8: '8am',
        9: '9am',
        10: '10am',
        11: '11am',
        12: 'noon',
        13: '1pm',
        14: '2pm',
        15: '3pm',
        16: '4pm',
        17: '5pm',
        18: '6pm',
        19: '7pm',
        20: '8pm',
        21: '9pm',
        22: '10pm',
        23: '11pm' }
    if city == 'stjohns':
        lookup = {
            None: None,
            0: '12:30am',
            1: '1:30am',
            2: '2:30am',
            3: '3:30am',
            4: '4:30am',
            5: '5:30am',
            6: '6:30am',
            7: '7:30am',
            8: '8:30am',
            9: '9:30am',
            10: '10:30am',
            11: '11:30am',
            12: '12:30pm',
            13: '1:30pm',
            14: '2:30pm',
            15: '3:30pm',
            16: '4:30pm',
            17: '5:30pm',
            18: '6:30pm',
            19: '7:30pm',
            20: '8:30pm',
            21: '9:30pm',
            22: '10:30pm',
            23: '11:30pm'}
    prefix = ''
    if hour24[0] == 'S':
        prefix = '~'
    return prefix + lookup[int(hour24[1:])]

def possessive(noun):
    if noun.endswith("'s"):
        return noun
    return noun+"'s"

def nth(count):
    if count % 100 in (11,12,13):
        return '{}th'.format(count)
    if count % 10 == 1:
        return '{}st'.format(count)
    if count % 10 == 2:
        return '{}nd'.format(count)
    if count % 10 == 3:
        return '{}rd'.format(count)
    return '{}th'.format(count)

Email = namedtuple('Email', 'field date message')

class Alert():
    def __init__(self, title, address, field,
                 skipMinRecords=False, skipMaxRecords=False,
                 skipMinEstimated=False, skipMaxEstimated=False,
                 skipIncomplete=False,
                 skipMinIncomplete=False, skipMaxIncomplete=False,
                 skipBelowZero=False, skipFilter=None):
        self.title = title
        self.address = address
        self.field = field
        self.datemarker = {}
        self.skipMinRecords = skipMinRecords
        self.skipMaxRecords = skipMaxRecords
        self.skipMinEstimated = skipMinEstimated
        self.skipMaxEstimated = skipMaxEstimated
        self.skipIncomplete = skipIncomplete
        self.skipMinIncomplete = skipMinIncomplete
        self.skipMaxIncomplete = skipMaxIncomplete
        self.skipBelowZero = skipBelowZero
        self.verbose = False
        self.skipFilter = skipFilter

    def dayRange(self, city):
        startDate = today(city)-datetime.timedelta(days=6)
        return daily.dayRange(startDate, today(city)+datetime.timedelta(1))

    def __call__(self, city):
        if self.field.name in stations.city[city].skipDailyFields:
            # This city doesn't keep track of this information in a useful way.
            return
        ret = []
        for sampleDay in self.dayRange(city):
            if self.skipFilter != None:
                try:
                    dayData = daily.dataByCity[city][sampleDay]
                except KeyError:
                    # We probably don't have data for that day for some reason, skip
                    continue
                if self.skipFilter(dayData):
                    continue
            result = self.call(city, sampleDay)
            if result != None:
                ret.append(result)
        return ret
