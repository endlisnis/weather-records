#!/usr/bin/python3
import daily, sys

city = sys.argv[1]
data = daily.load0(city)
daily.quickSave(city)
