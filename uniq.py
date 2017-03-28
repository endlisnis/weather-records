#!/usr/bin/python
from __future__ import print_function

import sys

keys = set()

for line in sys.stdin.read().split('\n'):
    tokens = line.strip().split('\t')
    #print tokens
    if len(tokens)<=1 or tokens[1] in keys:
        continue
    keys.add(tokens[1])
    print line
