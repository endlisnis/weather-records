#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import stations, sys

city = sys.argv[1]

print 'TIMEOUT=$(shell python -c "import random; print random.randint(8,12)")'
print 'WGET=wget -nv -T ${TIMEOUT}'

print 'all:'
print

for stationId, yearRange in stations.dayStations[city].iteritems():
    print '#', stationId, range(yearRange[0], yearRange[1]+1)
    print '%d:' % (stationId)
    print '\tmkdir $@'
    print 
    print '%d/data/%%.csv: | %d' % (stationId, stationId)
    print "\t${WGET} -O $@ 'http://climate.weather.gc.ca/climateData/bulkdata_e.html?timeframe=2&stationID=%d&Year='$*'&Month=1&Day=1&format=csv'" % stationId
    print 
    print '%d/data/%%.mcsv: | %d' % (stationId, stationId)
    print "\t${WGET} -O $@ 'http://climate.weather.gc.ca/climateData/bulkdata_e.html?timeframe=1&stationID=%d&Year='${YEAR}'&Month='${MONTH}'&Day=1&format=csv'" % stationId
    print 

for stationId, yearRange in stations.dayStations[city].iteritems():
    for year in range(yearRange[0], yearRange[1]+1):
        print 'all: %d/data/%d.csv' % (stationId, year)

for stationId, yearRange in stations.hourStations.iteritems():
    for year in range(yearRange[0], yearRange[1]+1):
        for month in range(12):
            fname = '%d/data/%d-%02d.mcsv' % (stationId, year, month+1)
            print 'all: %s' % fname
            print '%s: YEAR=%d' % (fname, year)
            print '%s: MONTH=%02d' % (fname, month+1)
            
