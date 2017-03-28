#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import datetime as dt

from collections import namedtuple

WeatherStatsRow = namedtuple(
    'WeatherStatsRow',
    'date_time_local,date,barometer_value,barometer_change,barometer_tendency,wind_dir,wind_bearing,wind_speed,wind_gust,relative_humidity,dew_point,temperature,windchill,humidex,visibility,notify,en_conditions,fr_conditions,en_station,fr_station,iata_name'.split(','))

def parse(city):
    fname = '{city}/weatherStatsHourly.csv'.format(**locals())
    ret = {}
    for linenumber, row in enumerate(csv.reader(open(fname))):
        if linenumber == 0 or len(row) == 0:
            continue
        r = WeatherStatsRow(*row)
        time = dt.datetime.utcfromtimestamp(int(r.date))
        time = time.replace(tzinfo=dt.timezone.utc)
        #print(time, r.en_conditions)
        ret[time] = r.en_conditions
    return ret

if __name__ == '__main__':
    parse('ottawa')
