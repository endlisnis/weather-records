#!/usr/bin/python3
import hourly
d = hourly.load('ottawa')

run = []
count = 0
for i in reversed(sorted(d.keys())):
    w = d[i].WEATHER
    h = d[i].REL_HUM
    #print(w)
    if ( i.month == 7
         and (w == 'Cloudy' 
              or ( ( i.hour < 6 or i.hour > 21 ) and w in ('Clear','Mostly Cloudy','Smoke','Mainly Clear','Haze','Partly Cloudy') ))
         and len(h) > 0 and int(h) < 65 ):
        ts = i
        run.append(ts)
        if len(run) >= 12:
            print(len(run), ts)
    else:
        run = []
    count += 1
print(count)
