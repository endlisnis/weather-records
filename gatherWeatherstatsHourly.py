#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import sys
import datetime as dt
import sqlite3
import parseWeatherstatsHourly
import stations
import time

session = requests.Session()

existingResults = set()

class Db():
    def __init__(self):
        dbname = "ottawa/data/weatherstatshistory.db"
        self.conn = sqlite3.connect(dbname)
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS observations'
                  ' (date int PRIMARY KEY, json text)')
        self.conn.commit()
    def execAndCommit(self, *args):
        result = self.conn.cursor().execute(*args)
        self.conn.commit()
        return result
    def execute(self, *args):
        result = self.conn.cursor().execute(*args)
        return result

def getOneUrl(timestamp):
    url = 'http://ottawa.weatherstats.ca/data.json'
    if timestamp is not None:
        url += ( '?date={timestamp.year}-{timestamp.month:02}-{timestamp.day:02};'
                 'time={timestamp.hour:02}:{timestamp.minute:02}'.format(**locals()) )
    while True:
        print(url)
        f = session.get(url)
        if f.status_code == 502: #Bad Gateway, try again
            print("Bad Gateway")
            time.sleep(1)
            continue
        d = f.text
        break
    return d

def getOneDb(timestamp, db):
    r = db.execute('SELECT json from observations where date < ?',
                   [ int(timestamp.timestamp()) ]
    )
    return tuple(r)[0][0]

def getOne(requestTimestamp, db):
    json = getOneUrl(requestTimestamp)
    time, observation = parseWeatherstatsHourly.parse(json)
    if time is not None and int(time.timestamp()) not in existingResults:
        sqlCmd = 'REPLACE INTO observations VALUES (?,?)'
        try:
            db.execAndCommit(sqlCmd, (int(time.timestamp()), json))
        except sqlite3.OperationalError:
            print(sqlCmd, (int(time.timestamp()), json))
            raise
    return time, observation


def main():
    mytimezone = stations.city['ottawa'].timezone
    db = Db()

    for row in db.execute('SELECT date from observations'):
        existingResults.add(row[0])
    oldestExistingResult = min(existingResults)


    #time, observation = getOne(None, db)
    #print(time, observation)
    time = dt.datetime.fromtimestamp(oldestExistingResult, dt.timezone.utc)
    while time != None:
        prevTime = time
        time, observation = getOne(time.astimezone(mytimezone), db)
        print(time, observation)
        if time is None or time == prevTime:
            time = prevTime - dt.timedelta(minutes=1)
    exit(0)

    while threading.active_count() > 1:
        try:
            tsv, d = results.get(timeout=1)
        except queue.Empty:
            print(threading.enumerate())
            continue
        sqlCmd = 'REPLACE INTO observations VALUES (?,?)'
        try:
            c.execute(sqlCmd, (tsv, d))
            conn.commit()
        except sqlite3.OperationalError:
            print(sqlCmd, (tsv, d))
            raise
    conn.close()

main()
