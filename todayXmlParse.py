#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml import etree
import argparse
import decimal
import gzip
import stations
D = decimal.Decimal

def getMinMax(city):
    root = etree.parse(gzip.open('{city}/data/today.xml.gzip'.format(**locals()), 'rt'))

    ns = {
        'om': 'http://www.opengis.net/om/1.0',
        'po': 'http://dms.ec.gc.ca/schema/point-observation/2.1',
    }

    stationId = stations.city[city].stationName

    maxTemp = root.xpath('/om:ObservationCollection/om:member/om:Observation/om:metadata'
                         '/po:set/po:identification-elements'
                         '/po:element[@value="{stationId}"]'
                         '/../../../../om:result/po:elements'
                         '/po:element[@name="air_temperature_today_high"]/@value'
                         .format(**locals()),
                         namespaces=ns)[0]

    minTemp = root.xpath('/om:ObservationCollection/om:member/om:Observation/om:metadata'
                         '/po:set/po:identification-elements'
                         '/po:element[@value="{stationId}"]'
                         '/../../../../om:result/po:elements'
                         '/po:element[@name="air_temperature_today_low"]/@value'
                         .format(**locals()),
                         namespaces=ns)[0]
    maxGust = root.xpath('/om:ObservationCollection/om:member/om:Observation/om:metadata'
                         '/po:set/po:identification-elements'
                         '/po:element[@value="{stationId}"]'
                         '/../../../../om:result/po:elements'
                         '/po:element[@name="wind_gust_speed"]/@value'
                         .format(**locals()),
                         namespaces=ns)[0]

    if len(maxGust) == 0:
        maxGust = None
    else:
        maxGust = int(maxGust)

    return D(minTemp), D(maxTemp), maxGust

def main():
    parser = argparse.ArgumentParser(description='Determine today\'s high and low.')
    parser.add_argument('--city', default='ottawa')
    args = parser.parse_args()

    minTemp, maxTemp, maxGust = getMinMax(args.city)

    print(maxTemp, minTemp, maxGust)

if __name__=='__main__':
    main()
