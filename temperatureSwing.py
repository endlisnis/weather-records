#!/usr/bin/python3
import daily, time
import argparse

parser = argparse.ArgumentParser(description='Calculate monthly average and charts.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--span')
args = parser.parse_args()

data = daily.load(args.city)
span=int(args.span)

days=[]
maxSwing=0

for date in reversed(sorted(data.keys())):
    values = data[date]
    if len(values.MAX_TEMP) > 0 and len(values.MIN_TEMP) > 0:
        val = float(values.MIN_TEMP)
        days.append(val)
        val = float(values.MAX_TEMP)
        days.append(val)
        while len(days) > span*2:
            days.pop(0)
    swing = max(days) - min(days)
    if swing > maxSwing:
        maxSwing = swing
        print(date, swing, days)
