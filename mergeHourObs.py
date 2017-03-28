#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import datetime
import pprint

obs={}
for fname in ('log3.txt', 'log2.txt'):
    for line in open(fname):
        l = line.strip()
        if len(l) == 0:
            continue
        t, o = l.strip().split(' ', 1)
        t = datetime.datetime.strptime(t, '%Y/%m/%d@%H:%M')
        obs[t] = o

byYear = {i:0 for i in range(1953,2018)}
for t in obs.keys():
    byYear[t.year] += 1

pprint.PrettyPrinter().pprint(byYear)
