#!/usr/bin/python3
# -*- coding: utf-8 -*-
import collections
import pytz
from datetime import timedelta
from pytz import timezone
import os

class CityInfo():
    def __init__(
            self,
            dayStations,
            hourStations,
            label,
            name,
            hourlyDataTimeOffset,
            timezone,
            #*,
            skipOb=None,
            skipDailyFields=None,
            weatherStatsSite=None,
            stationName=None,
            airportCode=None,
            skipMetar=False,
    ):
        self.dayStations = dayStations
        self.hourStations = hourStations
        self.label = label
        self.name = name
        self.airportCode = airportCode
        self.skipMetar = skipMetar

        if skipOb == None:
            skipOb = []
        self.skipOb=skipOb

        if skipDailyFields == None:
            skipDailyFields = []
        self.skipDailyFields=skipDailyFields
        self.weatherStatsSite = weatherStatsSite
        self.stationName = stationName
        self.hourlyDataTimeOffset = hourlyDataTimeOffset
        self.timezone = timezone

def weatherStatsSite(cityName):
    if city[cityName].weatherStatsSite != None:
        return city[cityName].weatherStatsSite
    return cityName


city = {
    'barrie': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 42183, (2003,2017) ), # Barrie-Oro
            (  4408, (1968,2003) ), # Barrie WPCC
        ] ),
        hourStations = collections.OrderedDict( [
            ( 42183, (2003,2017) ),
        ] ),
        label = 'on-151',
        name = 'Barrie',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        skipDailyFields=['TOTAL_RAIN_MM', 'TOTAL_SNOW_CM'],
        skipOb = ['visibility'],
        stationName="Lake Simcoe Regional Airport",
    ),
    'calgary': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50430, (2012,2017) ),
            (  2205, (1881,2012) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50430, (2012,2017) ),
            (  2205, (1953,2012) ),
        ] ),
        label = 'ab-52',
        name = 'Calgary',
        hourlyDataTimeOffset=timedelta(hours=7),
        timezone=timezone('America/Edmonton'),
        stationName="Calgary Int'l Airport",
        airportCode='YYC',
    ),

    'charlottetown': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50621, (2012,2017) ),
            (  6526, (1943,2012) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50621, (2012,2017) ),
            (  6526, (1953,2012) ),
        ] ),
        label = 'pe-5',
        name = 'Charlottetown',
        hourlyDataTimeOffset=timedelta(hours=4),
        timezone=timezone('America/Moncton'),
        stationName="Charlottetown Airport",
        airportCode='YYG',
    ),

    'edmonton-airport': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50149, (2012,2017) ),
            (  1865, (1959,2012) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50149, (2012,2017) ),
            (  1865, (1961,2012) ),
        ] ),
        label = 'ab-71',
        name = 'Edmonton-Airport',
        weatherStatsSite='edmontonairport',
        hourlyDataTimeOffset=timedelta(hours=7),
        timezone=timezone('America/Edmonton'),
        stationName="Edmonton Int'l Airport",
        airportCode='YEG',
    ),

    'edmonton': CityInfo(
        dayStations = collections.OrderedDict( [
             ( 27214, (1996,2017) ),
            (  1867, (1937,1996) ),
    #        (  1863, (1880,1943) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 27214, (1999,2017) ),
            (  1867, (1953,1999) ),
        ] ),
        label = 'ab-50',
        name = 'Edmonton-Blatchford',
        weatherStatsSite='edmonton',
        skipOb = ['visibility'],
        skipDailyFields=['TOTAL_RAIN_MM', 'TOTAL_SNOW_CM'],
        hourlyDataTimeOffset=timedelta(hours=7),
        timezone=timezone('America/Edmonton'),
        stationName="Edmonton Blatchford",
        airportCode='XEC',
        skipMetar=True,
    ),

    'fredericton': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 48568, (2010,2017) ),
            (  6157, (1951,2010) ),
            (  6159, (1971,1951) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 48568, (2010,2017) ),
            (  6157, (1953,2010) ),
        ] ),
        label = 'nb-29',
        name = 'Fredericton',
        skipDailyFields=['TOTAL_RAIN_MM', 'TOTAL_SNOW_CM'],
        hourlyDataTimeOffset=timedelta(hours=4),
        timezone=timezone('America/Moncton'),
        stationName="Fredericton Int'l Airport",
        airportCode='YFC',
    ),

#    'gagetown': CityInfo(
#        dayStations=None,
#        hourStations=None,
#        label=None,
#        hourlyDataTimeOffset=None,
#        name = 'CFB Gagetown',
#        timezone=timezone('America/Moncton'),
#        stationName="CFB Gagetown",
#        airportCode='YCX',
#    ),

    'halifax': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50620, (2012,2017) ),
            (  6358, (1953,2012) ),
            (  6357, (1933,1953) ),
            (  6355, (1871,1933) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50620, (2012,2017) ),
            (  6358, (1961,2012) ),
        ] ),
        label = 'ns-19',
        name = 'Halifax',
        hourlyDataTimeOffset=timedelta(hours=4),
        timezone=timezone('America/Halifax'),
        weatherStatsSite='halifaxairport',
        stationName="Halifax Stanfield Int'l Airport",
        airportCode='YHZ',
    ),

    'hamilton': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 49908, (2011,2017) ),
            (  4932, (1959,2011) ),
            (  4612, (1931,1953) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 49908, (2011,2017) ),
            (  4932, (1970,2011) ),
        ] ),
        label = 'on-77',
        name = 'Hamilton',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Hamilton Munro Int'l Airport",
        airportCode='YHM',
    ),

    'kingston': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 47267, (2008,2017) ),
            (  4295, (1930,1996) ),
            (  4301, (1872,1930) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 47267, (2008,2017) ),
            (  4295, (1967,2008) ),
        ] ),
        label = 'on-69',
        name = 'Kingston',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        skipDailyFields=['TOTAL_RAIN_MM', 'TOTAL_SNOW_CM'],
        stationName="Kingston Airport",
        airportCode='YGK',
    ),

    'london': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50093, (2012,2017) ),
            ( 10999, (2002,2012) ),
            (  4789, (1940,2002) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50093, (2012,2017) ),
            ( 10999, (2002,2012) ),
            (  4789, (1953,2002) ),
        ] ),
        label = 'on-137',
        name = 'London',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        skipDailyFields=['MIN_WINDCHILL',
                         'TOTAL_RAIN_MM',
                         'TOTAL_SNOW_CM',
                         'AVG_WIND',
                         'SPD_OF_MAX_GUST_KPH'],
        stationName="London Int'l Airport",
        airportCode='YXU',
    ),

    'montreal': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 51157, (2013,2017) ),
            (  5415, (1941,2013) ),
            (  5420, (1871,1940) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 51157, (2013,2017) ),
            (  5415, (1953,2013) ),
        ] ),
        label = 'qc-147',
        name = 'Montréal',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Montréal-Trudeau Int'l Airport",
        airportCode='YUL',
    ),

    'ottawa': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 49568, (2011,2017) ),
            (  4337, (1938,2011) ),
            #(  4333, (1889,2014) ),
            (  4333, (1889,1938) ),
            (  4327, (1872,1935) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 49568, (2011,2017) ),
            (  4337, (1953,2011) ),
        ] ),
        label = 'on-118',
        name = 'Ottawa',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Ottawa Macdonald-Cartier Int'l Airport",
        airportCode='YOW',
    ),

    'quebec': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 26892, (1992,2017) ),
            (  5251, (1943,2017) ),
            (  5249, (1872,1943) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 26892, (2005,2017) ),
            (  5251, (1953,2013) ),
        ] ),
        label = 'qc-133',
        name = 'Québec City',
        skipDailyFields=['TOTAL_RAIN_MM',
                         'TOTAL_SNOW_CM',
                         'SPD_OF_MAX_GUST_KPH',
                         'SNOW_ON_GRND_CM'],
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Quebec Lesage Int'l Airport",
        airportCode='YQB',
    ),

    'regina': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 28011, (1999,2017) ),
            (  3002, (1883,1999) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 28011, (1999,2017) ),
            (  3002, (1953,1999) ),
        ] ),
        label = 'sk-32',
        name = "Regina",
        skipDailyFields=['MEAN_HUMIDITY', 'MIN_HUMIDITY'],
        hourlyDataTimeOffset=timedelta(hours=6),
        timezone=timezone('America/Regina'),
        stationName="Regina Int'l Airport",
        airportCode='YQR',
    ),

    'stjohn': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50310, (2012,2017) ),
            (  6250, (1946,2012) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50310, (2012,2017) ),
            (  6250, (1953,2012) ),
        ] ),
        label = 'nb-23',
        name = "StJohn",
        hourlyDataTimeOffset=timedelta(hours=4),
        timezone=timezone('America/Moncton'),
        stationName="Saint John Airport",
        airportCode='YSJ',
    ),

    'stjohns': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 50089, (2012,2017) ),
            (  6720, (1942,2017) ),
            (  6718, (1874,1956) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 50089, (2012,2017) ),
            (  6720, (1959,2013) ),
        ] ),
        label = 'nl-24',
        name = "StJohns",
        hourlyDataTimeOffset=timedelta(hours=3, minutes=30),
        timezone=timezone('America/St_Johns'),
        stationName="St. John's Int'l Airport",
        airportCode='YYT',
    ),

    'toronto': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 51459, (2013,2017) ),
            (  5097, (1937,2013) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 51459, (2013,2017) ),
            (  5097, (1953,2013) ),
        ] ),
        label = 'on-143',
        name = 'Toronto',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Toronto Pearson Int'l Airport",
        airportCode='YYZ',
    ),

    'thunderBay': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 30682, (2003,2017) ),
            (  4055, (1941,2004) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 30682, (2000,2017) ),
            (  4055, (1953,2013) ),
        ] ),
        label = 'on-100',
        name = 'Thunder Bay',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        stationName="Thunder Bay Airport",
        airportCode='YQT',
    ),

    'vancouver': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 51442, (2013,2017) ),
            (  889,  (1937,2013) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 51442, (2013,2017) ),
            (   889, (1953,2013) ),
        ] ),
        label = 'bc-74',
        name = 'Vancouver',
        hourlyDataTimeOffset=timedelta(hours=8),
        timezone=timezone('America/Vancouver'),
        stationName="Vancouver Int'l Airport",
        airportCode='YVR',
    ),

    'vernon': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 46987, (2005,2017) ),
            (  6837, (1991,2005) ),
            (  1068, (1900,1997) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 46987, (2007,2017) ),
            (  6837, (1994,2008) ),
            (  1065, (1989,1995) ),
            #(  1065, (1971,1979) ),
        ] ),
        label = 'bc-27',
        name = 'Vernon',
        hourlyDataTimeOffset=timedelta(hours=8),
        timezone=timezone('America/Vancouver'),
        skipOb = ['visibility'],
        stationName="Vernon",
        airportCode='WJV',
        skipMetar=True,
    ),

    'victoria': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 51337, (2013,2017) ),
            (   118, (1940,2013) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 51337, (2013,2017) ),
            (   118, (1953,2013) ),
        ] ),
        label = 'bc-85',
        name = 'Victoria',
        hourlyDataTimeOffset=timedelta(hours=8),
        timezone=timezone('America/Vancouver'),
        stationName="Victoria Int'l Airport",
        airportCode='YYJ',
    ),

    'waterloo': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 48569, (2010,2017) ),
            ( 32008, (2002,2011) ),
            (  4832, (1970,2003) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 48569, (2010,2017) ),
            ( 32008, (2002,2010) ),
            (  4832, (1966,2002) ),
        ] ),
        label = 'on-82',
        name = 'Waterloo',
        hourlyDataTimeOffset=timedelta(hours=5),
        timezone=timezone('America/Toronto'),
        skipDailyFields=[],
        weatherStatsSite='kitchenerwaterloo',
        stationName="Region of Waterloo Int'l Airport",
        airportCode='YKF',
    ),

    'whitehorse': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 48168, (2009,2017) ),
            (  1617, (1942,2009) ),
            (  1616, (1900,1942) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 48168, (2009,2017) ),
            (  1617, (1953,2015) ),
        ] ),
        label = 'yt-16',
        name = 'Whitehorse',
        skipDailyFields=['MIN_WINDCHILL',
                         'TOTAL_RAIN_MM',
                         'TOTAL_SNOW_CM',
                         'AVG_WIND',
                         'SPD_OF_MAX_GUST_KPH'],
        hourlyDataTimeOffset=timedelta(hours=7),
        timezone=timezone('America/Edmonton'),
        stationName="Whitehorse Airport",
        airportCode='YXY',
    ),

    'winnipeg': CityInfo(
        dayStations = collections.OrderedDict( [
            ( 27174, (2008,2017) ),
            (  3698, (1938,2008) ),
            (  3703, (1872,1938) ),
        ] ),
        hourStations = collections.OrderedDict( [
            ( 27174, (2013,2017) ),
            ( 51097, (2013,2013) ),
            (  3698, (1953,2013) ),
        ] ),
        label = 'mb-38',
        name = 'Winnipeg',
        skipDailyFields=['TOTAL_RAIN_MM', 'TOTAL_SNOW_CM'],
        hourlyDataTimeOffset=timedelta(hours=6),
        timezone=timezone('America/Winnipeg'),
        stationName="Winnipeg Richardson Int'l Airport",
        airportCode='YWG',
    ),

}

if 'METAR' in os.environ:
    city.update({
        'gagetown': CityInfo(
            dayStations=None,
            hourStations=None,
            label=None,
            hourlyDataTimeOffset=None,
            name = 'CFB Gagetown',
            timezone=timezone('America/Moncton'),
            stationName="CFB Gagetown",
            airportCode='YCX',
        ),
        'gatineau': CityInfo(
            dayStations=None,
            hourStations=None,
            label=None,
            hourlyDataTimeOffset=None,
            name = 'Gatineau',
            timezone=timezone('America/Toronto'),
            airportCode='YND',
        ),
        'moncton': CityInfo(
            dayStations=None,
            hourStations=None,
            label=None,
            hourlyDataTimeOffset=None,
            name = 'Moncton',
            timezone=timezone('America/Moncton'),
            airportCode='YQM',
        )
    })
    for cityName, apc in {
            'Sault Ste. Marie': 'CYAM',
            'Geraldton': 'CYGQ',
            'Buttonville': 'CYKZ',
            'Chapleau': 'CYLD',
            'Pickle Lake': 'CYPL',
            'Windsor': 'CYQG',
            'Kenora': 'CYQK',
            'Red Lake': 'CYRL',
            'Sudbury': 'CYSB',
            'St. Catharines/Niagara': 'CYSN',
            'Marathon': 'CYSP',
            'Trenton': 'CYTR',
            'Timmins': 'CYTS',
            'Wiarton': 'CYVV',
            'Sioux Lookout': 'CYXL',
            'Wawa': 'CYXZ',
            'Kapuskasing': 'CYYU',
            }.items():
        city[cityName] = CityInfo(
            dayStations=None,
            hourStations=None,
            label=None,
            hourlyDataTimeOffset=None,
            name=cityName,
            timezone=timezone('America/Toronto'),
            airportCode=apc)


del city['london']
#city = {'ottawa': city['ottawa']}
