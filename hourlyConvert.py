#!/usr/bin/python3
import hourly
import sys

city = 'ottawa'
city = sys.argv[1]
data = hourly.loadEnvCan(city)
#for key in data:
#    print(key)
hourly.save(data, city)
