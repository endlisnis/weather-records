#!/usr/bin/python
from __future__ import print_function
import weather, time
a = time.time(); weather.hourly.load("ottawa"); print time.time() - a
raw_input()
