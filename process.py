#!/usr/bin/python3
# -*- coding: utf-8 -*-
import stations


for city, info in stations.city.items():
    print("./hourlyConvert.py {city}".format(**locals()))
