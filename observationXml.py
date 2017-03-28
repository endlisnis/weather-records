#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime, glob
import xml.etree.ElementTree as ET
import stations

ns = {'om': "http://www.opengis.net/om/1.0"}

def getConditionsFromObservation(observation):
    conditions = {}
    results = list(observation.iter('{http://www.opengis.net/om/1.0}result'))[0]
    for element in results.iter('{http://dms.ec.gc.ca/schema/point-observation/2.0}element'):
        #print(element.tag, element.attrib)
        conditions[element.attrib['name']] = element.attrib['value']
    return conditions


def getCurrentConditionsFromXmlFile(xmlFileName, city):
    tree = ET.parse(xmlFileName)
    root = tree.getroot()
    for observation in root.iter('{http://www.opengis.net/om/1.0}Observation'):
        for ident in observation.iter('{http://dms.ec.gc.ca/schema/point-observation/2.0}identification-elements'):
            identification = {}
            for child in ident:
                identification[child.attrib['name']] = child.attrib['value']
            if identification.get('station_name', None) == stations.city[city].station:
                timestamp = datetime.datetime.strptime(identification['observation_date_local_time'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                ret = getConditionsFromObservation(observation)
                ret['timestamp'] = timestamp
                return ret


if __name__ == '__main__':
    import sys
    print(getCurrentConditionsFromXmlFile(sys.argv[1]))
