#!/usr/bin/python3

import datetime
import twitterSend

def sPeriod(date):
    minutes = date.hour * 60 + date.minute
    sp = (minutes - 1) // (6*60)
    if sp < 1:
        return (date-datetime.timedelta(days=1)).date(), sp+3
    return date.date(), sp-1

#for i in range(0,24): i,sPeriod(datetime.datetime(2017,1,1,i,0))

def main(city):
    if city != 'ottawa':
        return {}
    api = twitterSend.getApi('rolf')
    statuses = api.statuses.user_timeline(screen_name='CYOW_wx', count=200)
    snowPerSP = {}
    for status in reversed(statuses):
        tokens = status['text'].split()
        snow = None
        for tok in tokens:
            if tok.startswith('/S'):
                snow = int(tok[2:4],10)
        if snow is None:
            continue
        utcTimeStr = tokens[1]
        utcDay = int(utcTimeStr[0:2],10)
        utcHour = int(utcTimeStr[2:4],10)
        utcMin = int(utcTimeStr[4:6],10)
        utcNow = datetime.datetime.utcnow()
        #import pudb; pu.db
        if utcDay <= utcNow.day:
            metarDatestamp = datetime.datetime(
                utcNow.year, utcNow.month, utcDay, utcHour, utcMin,
                tzinfo=datetime.timezone.utc)
        else:
            metarDatestamp = datetime.datetime(
                utcNow.year if utcNow.month > 1 else utcNow.year-1,
                utcNow.month-1 if utcNow.month > 1 else 12,
                utcDay, utcHour, utcMin,
                tzinfo=datetime.timezone.utc)
        spDay, sp = sPeriod(metarDatestamp)
        print('utc={}, day={}, senoptic period={}, snow={}cm'
              .format(utcTimeStr, spDay, sp, snow))
        snowPerSP[spDay, sp] = snow

    snowPerDay = {}
    for spDay, sp in snowPerSP:
        snowPerDay[spDay] = snowPerDay.get(spDay,0) + snowPerSP[spDay, sp]
    return snowPerDay

if __name__=='__main__':
    for day, val in sorted(main('ottawa').items()):
        print(day, val)
