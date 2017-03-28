# -*- coding: utf-8 -*-
from __future__ import print_function
import twitterSend

api = twitterSend.getApi('ottawa')

allTweets=[]
max_id = None
while True:
    print 'Reading...',
    #tweets = api.GetHomeTimeline(count=200, trim_user=True, exclude_replies=False, max_id=max_id)
    tweets = api.GetUserTimeline(count=200, trim_user=True, exclude_replies=True, max_id=max_id)
    print 'got {} tweets'.format(len(tweets))
    if len(tweets) == 0:
        break
    allTweets += tweets
    max_id = tweets[-1].GetId()-1

for tweet in allTweets:
    print api.GetRetweeters(tweet.GetId())
