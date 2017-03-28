#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import print_function
from io import TextIOWrapper

import bz2
#import io

print(TextIOWrapper(bz2.BZ2File('h.bz2','r')).read())
