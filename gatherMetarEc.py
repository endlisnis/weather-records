#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import metarParse
import requests
import sqlite3
import stations
import pathlib
import termcolor
import re

parser = argparse.ArgumentParser(
    description='Parse, save and load metar data.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--days', default=1, type=int)
args = parser.parse_args()

session = requests.Session()
city = args.city
airportCode = stations.city[city].airportCode
rawKeys = metarParse.loadRawKeys(city)

utcnow = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
today = utcnow.date()

metarData = metarParse.load(city,
                       sinceWhen=int((utcnow - datetime.timedelta(days=args.days))
                                     .timestamp()),
                       rawKeys=True)
dbname = city+"/data/metar.db"
conn = sqlite3.connect(dbname)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS metar (date int PRIMARY KEY, metar text)')
conn.commit()

def showAndSave(utctimestamp, metarStr, existingMetarStr=None):
    metarHighlighted = metarStr
    if re.search('/S[0-9O][0-9]/', metarStr) != None:
        metarHighlighted = re.sub(
            '/S[0-9O][0-9]/',
            termcolor.colored(re.search('/S[0-9O][0-9]/', metarStr).group(), 'red'),
            metarStr)

    print(datetime.datetime.fromtimestamp(utctimestamp, datetime.timezone.utc),
          metarHighlighted, existingMetarStr)
    sqlRow =  '{utctimestamp},"{metarStr}"'.format(**locals())
    sqlCmd = 'REPLACE INTO metar VALUES ({})'.format(sqlRow)
    try:
        c.execute(sqlCmd)
    except sqlite3.OperationalError:
        print(sqlCmd)
        raise
    conn.commit()
    pathlib.Path(dbname+'.touch').touch()
#conn.close()


for i in range(150):
    d = today-datetime.timedelta(days=i)
    for h in range(23, -1, -1):
        #print('echo -n {d.year:02}{d.month:02}{d.day:02};'
        #      .format(**locals())
        #)
        hdate = ( datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc)
                  + datetime.timedelta(hours=h) )
        htimestamp = int(hdate.timestamp())
        if ( hdate > utcnow
             or (htimestamp in rawKeys
                 and utcnow - hdate > datetime.timedelta(days=args.days))
        ):
            continue

        path=( 'http://dd.weather.gc.ca/bulletins/alphanumeric/'
               '{d.year:02}{d.month:02}{d.day:02}'
               '/SA/C{airportCode}/{h:02}'
               .format(**locals())
        )

        response = session.get(path)
        if response.status_code == 404: # File not found
            print("Skipping missing hour {path}".format(**locals()))
            continue
        if response.status_code != 200:
            print(path)
            assert(False)
        html = response.text
        entries = filter(lambda t: '/unknown' in t, html.split('\n'))
        for line in entries:
            fname = line.split('"')[5]
            #print(htimestamp, fname)
            response = session.get(path + '/' + fname)
            assert(response.status_code == 200)
            text = response.text.strip().replace('\n', ' ')
            metarStr = text[text.find('METAR ')+6:]
            if htimestamp in metarData:
                existingMetar = metarData[htimestamp]
                best = metarParse.best(metarStr, existingMetar)
                if best == metarStr and metarStr != existingMetar:
                    showAndSave(htimestamp, metarStr, existingMetar)
                    metarData[htimestamp] = metarStr
            else:
                showAndSave(htimestamp, metarStr)
                metarData[htimestamp] = metarStr

        #print('for t in $(wget -O - -q '
        #      '{path}'
        #      ' | grep /unknown'
        #      ' | cut -d\\" -f 6 ); do echo -n {htimestamp} " "; echo $( wget -O - {path}/$t 2>1/dev/null ) | sed "s/^.*METAR //"; done'
        #      .format(**locals())
        #)
