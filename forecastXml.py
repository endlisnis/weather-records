#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import xml.etree.ElementTree as ET
import stations
import pytz

def getCurrentConditionsFromXmlFile(xmlFileName):
    tree = ET.parse(xmlFileName)
    root = tree.getroot()
    for child in root:
        if child.tag == '{http://www.w3.org/2005/Atom}entry':
            #for grandChild in child:
            #    print grandChild.tag, grandChild.attrib
            cat = child.find('{http://www.w3.org/2005/Atom}category')
            #print cat
            if cat.attrib['term'] == "Current Conditions":
                #for grandChild in child:
                #    print grandChild.tag, grandChild.attrib
                return child.find('{http://www.w3.org/2005/Atom}summary').text

isDst = {
    'EDT': True,
    'EST': False,
    'ADT': True,
    'AST': False,
    'PDT': True,
    'PST': False,
    'MDT': True,
    'MST': False,
    'NDT': True,
    'NST': False,
    'CDT': True,
    'CST': False,
}

def getCurrentConditionsFromXml(city, xmlFileName):
    text = getCurrentConditionsFromXmlFile(xmlFileName)
    result = {}
    if text == None:
        # There are no current conditions
        return result
    lines = text.split('\n')
    for line in lines:
        l = line.strip()
        if l.startswith('<b>Observed at:</b>'):
            timestamp = l.split()[-8:-1]
            timezonestr = timestamp[2]
            timestamp = timestamp[:2] + timestamp[3:] # Strip out the time zone
            dst = isDst[timezonestr]
            timestamp = datetime.datetime.strptime(
                ' '.join(timestamp), '%I:%M %p %A %d %B %Y')
            timestamp = stations.city[city].timezone.localize(timestamp, is_dst=dst)
            timestamp = timestamp.astimezone(pytz.utc)
            #print timestamp
            result['timestamp'] = timestamp
        else:
            l = l.replace('<b>', '').replace('<br/>', '').replace('&deg;C','').strip()
            if len(l) > 0:
                tokens = l.split(':</b> ')
                if len(tokens) == 1:
                    tokens = l.split(':</b>')
                result.update( (tokens,) )
    return result


if __name__ == '__main__':
    import sys, glob
    city = sys.argv[1]
    print(getCurrentConditionsFromXml(city, city+'/environmentCanada.xml'))
