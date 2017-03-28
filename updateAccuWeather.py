#!/usr/bin/python3
# -*- coding: utf-8 -*-import stations
import datetime
import random
import stations
import os

now = datetime.date.today()
curMonth = datetime.date(now.year, now.month, 1)
nextMonth = datetime.date(now.year+curMonth.month//12, (now.month%12)+1, 1)

for city, info in stations.city.items():
    if info.accuweatherStationId != None:
        try:
            os.mkdir('{city}/accuweather'.format(**locals()))
        except FileExistsError:
            pass

        cityName = city
        if info.accuweatherCityName != None:
            cityName = info.accuweatherCityName

        for fn, m in (('thisMonth', curMonth), ('nextMonth', nextMonth)):
            monthName = m.strftime('%B').lower()
            monthStr = m.strftime('%m/1/%Y').lower()
            timeout = random.randint(8,12)
            print('while true; do wget -nv -T {timeout} -O {city}/accuweather/{fn}.html "http://www.accuweather.com/en/ca/{cityName}/k1s/{monthName}-weather/{info.accuweatherStationId}?monyr={monthStr}&view=table" && break; done'.format(**locals()))
