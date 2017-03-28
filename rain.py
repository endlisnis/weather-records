#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys, re


rangeRe = re.compile('.*\\b([0-9]+)-([0-9]+) mm\\b.*')
lessThanRe = re.compile('.*\\bless than ([0-9]+) mm\\b.*')
closeToRe = re.compile('.*\\bclose to ([0-9]+) mm\\b.*')
plusRe = re.compile('.*>([0-9]+)\\+<.*> mm\\b.*')

inside = False

for line in file(sys.argv[1]):
    if '24-Hr Rain' in line:
        inside = True
        continue
    if '</tr>' in line:
        inside = False
        continue

    if inside:
        tokens = line.strip().split()
        if tokens[-1] == '</td>':
            rain = None
            rangeMatch = rangeRe.match(line)
            lessThanMatch = lessThanRe.match(line)
            closeToMatch = closeToRe.match(line)
            plusMatch = plusRe.match(line)

            if tokens[0] == '-':
                rain = (0,0)
            elif rangeMatch != None:
                rain = map( int, rangeMatch.groups() )
            elif closeToMatch != None:
                rain = int(closeToMatch.groups()[0])
                rain = (rain,rain)
            elif lessThanMatch != None:
                rain = int(lessThanMatch.groups()[0])
                rain = (0, rain)
            elif plusMatch != None:
                rain = int(plusMatch.groups()[0])
                rain = (rain, rain)
            print rain
