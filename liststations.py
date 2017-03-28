#!/usr/bin/python3
# -*- coding: utf-8 -*-
import stations

def getMetarSnowCities():
    matchingCities = []
    for city, info in stations.city.items():
        if getattr(info, 'airportCode') is not None:
            matchingCities.append(city)
    return matchingCities

if __name__ == '__main__':
    import sys
    matchingCities = stations.city.keys()
    if len(sys.argv) > 1 and sys.argv[1] == 'airportCode':
        matchingCities = getMetarSnowCities()
    print(" ".join(sorted(matchingCities)))
