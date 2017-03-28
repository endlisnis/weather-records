#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json, sys, datetime
#import pprint
import pytz
from pytz import timezone
import stations

allObs = ('temperature',
          'relative_humidity',
          'dew_point',
          'wind_speed',
          'wind_gust_speed',
          'pressure_sea',
          'visibility')

def javascriptDate(year,month,day,hour,minute,second):
    return datetime.datetime(year,month+1,day,hour,minute,second)

def main(city, fname, verbose=False):
    data = {}
    try:
        stuff=open(fname).read()
    except FileNotFoundError:
        return data
    #prefix="google.visualization.Query.setResponse({status:'ok', table: "
    #suffix="});\n1\n"
    stuff = stuff.replace(');\n','')
    stuff = stuff.replace('google.visualization.Query.setResponse(','')
    stuff = stuff.replace('new Date','Date')
    stuff = stuff.replace(', ', ',\n')
    stuff = eval(stuff, {'status':'status', 'Date':javascriptDate, 'null':None, 'table':'table', 'false': False})

    inrows = stuff['table']['rows']
    outrows = []
    for row in inrows:
        values = row['c']
        datestamp = values[0]['v']
        value = values[1]['v']
        outrows.append((datestamp, value))

    for rowIndex, row in enumerate(outrows):
        datestamp, value = row
        dst = True
        if rowIndex == 0:
            if datestamp != outrows[1][0]:
                dst = False
        elif datestamp == outrows[rowIndex-1][0]:
            dst = False
        localtime = stations.city[city].timezone.localize(datestamp, is_dst=dst)
        utctime = localtime.astimezone(pytz.utc)
        if verbose:
            print(utctime.astimezone(stations.city[city].timezone), value)
        #data[datestamp] = value #local time
        data[utctime] = value

    return data

if __name__=='__main__':
    for a in sys.argv[1:]:
        main('ottawa', a, verbose=True)
    exit(0)
