#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys, datetime, os, random

now = datetime.datetime.now().date()
yesterday = now - datetime.timedelta(1)

fpath = sys.argv[1]
fname = fpath.split('/')[-1]
ftime = os.stat(fpath).st_mtime

(year, month) = fname.split('.')[0].split('-')
year = int(year)
month = int(month)

if year == yesterday.year and month == yesterday.month:
    sys.exit(0)

age = (now.year - year)*12 + (now.month - month)

if age < 0:
    sys.exit(1)

rage = random.randint(0, age)
if rage != 0:
    sys.exit(1)

sys.exit(0)
