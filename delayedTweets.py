#!/usr/bin/python3

import bisect
import datetime as dt
import fcntl
import os
import pytz
import stations
import time
import twitterSend
import yaml

from namedtuplewithdefaults import namedtuple_with_defaults, dictFromArgs

TweetData = namedtuple_with_defaults(
    "TweetData",
    [ 'account', 'time', 'content', 'media', 'urgent' ],
    default_values=dictFromArgs(
        account=None,
        time=None,
        content=None,
        media=None,
        urgent=False))

def writeList(nextList, dest):
    dest.truncate(0)
    dest.seek(0, os.SEEK_SET)
    dest.write(yaml.dump([list(a) for a in nextList], default_flow_style=False))

def readList():
    file = open("scheduledTweets.yaml", 'r+')
    fcntl.flock(file, fcntl.LOCK_EX)
    currentList = yaml.load(file.read())
    currentList = list(map(lambda t: TweetData(*t), currentList))
    return currentList, file

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError

def addToListForCity(city, tweet, media=None, urgent=False):
    if urgent is True:
        insertUrgent(city, tweet, media)
    else:
        addToEndOfListForCity(city, tweet, media)

def insertUrgent(city, tweet, media=None):
    currentList, fd = readList()
    sortedList = list(sorted(currentList))
    v = TweetData(city, dt.datetime.now().strftime("%Y-%m-%d@%H:%M:%S"),
                  tweet, media, urgent=True)
    insertionIndex = bisect.bisect_left(sortedList, v)
    sortedList.insert(insertionIndex, v)
    last = v
    for i in range(insertionIndex + 1, len(sortedList)):
        c = sortedList[i]
        if c.account != city:
            break
        lasttime = dt.datetime.strptime(last.time, "%Y-%m-%d@%H:%M:%S")
        ctime = dt.datetime.strptime(c.time, "%Y-%m-%d@%H:%M:%S")
        if not c.urgent and ctime - lasttime < dt.timedelta(hours=1):
            newtime = (lasttime+dt.timedelta(hours=1)).strftime("%Y-%m-%d@%H:%M:%S")
            c = c._replace(time = newtime)
            sortedList[i] = c
        last = c
    # Replace the existing list in-place with the new list
    writeList(sortedList, fd)
    fd.close()

def addToEndOfListForCity(city, tweet, media=None):
    #import pudb; pu.db
    currentList, fd = readList()
    now = pytz.utc.localize(dt.datetime.utcnow())
    localnow = now.astimezone(stations.city[city].timezone)
    if localnow.hour < 8:
        localnow = localnow.replace(hour=8, minute=0, second=0)
    if ( localnow.weekday() in (5,6) # Saturday or Sunday
         and localnow.hour < 10
    ):
        localnow = localnow.replace(hour=10, minute=0, second=0)
    now = localnow.replace(tzinfo=None)
    print(now)
    newest = None
    for c in currentList:
        if city != c.account:
            continue
        datetimestamp = dt.datetime.strptime(c.time, "%Y-%m-%d@%H:%M:%S")
        if newest is None or datetimestamp > newest:
            newest = datetimestamp
    if newest is None:
        nextSlot = now
    else:
        newest = stations.city["ottawa"].timezone.localize(newest)
        newest = newest.astimezone(stations.city[city].timezone)
        newest = newest.replace(tzinfo=None)
        nextSlot = newest + dt.timedelta(hours=1)
    nextSlotWithTz = stations.city[city].timezone.localize(nextSlot)
    ottawaNextSlot = nextSlotWithTz.astimezone(stations.city['ottawa'].timezone)
    ottawaNextSlotStr = ottawaNextSlot.strftime("%Y-%m-%d@%H:%M:%S")
    currentList.append((city, ottawaNextSlotStr, tweet, media))
    writeList(currentList, fd)
    fd.close()

def main():
    while True:
        currentList, fd = readList()
        if len(currentList) == 0:
            break
        oldest = None
        nextList = currentList.copy()
        now = dt.datetime.now()

        for c in currentList:
            datetimestamp = dt.datetime.strptime(c.time, "%Y-%m-%d@%H:%M:%S")
            if datetimestamp <= now:
                print("{}/ {}/ {}/ {}".format(now, datetimestamp, c.account, c.content))
                if c.media is None:
                    twitterSend.tweet(c.account, c.content)
                else:
                    twitterSend.tweetMedia(c.account, c.content, c.media)
                nextList.remove(c)
                writeList(nextList, fd)
                continue
            if ( oldest is None
                 or datetimestamp < dt.datetime.strptime(oldest[1], "%Y-%m-%d@%H:%M:%S")
            ):
                oldest = c
        fd.close()
        if oldest is not None:
            delay = (dt.datetime.strptime(oldest[1], "%Y-%m-%d@%H:%M:%S") - now).seconds + 1
            print("Sleeping until {} ({} seconds)\r".format(oldest.time, delay))
            time.sleep(min(delay, 60))

if __name__ == '__main__':
    main()
