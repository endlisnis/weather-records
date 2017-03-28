#!/usr/bin/python3
# -*- coding: utf-8 -*-
from reversedict import reverseDict

def distanceFromThisYear(year, retValByYear, retYearByVal):
    sortedVals = sorted(retYearByVal.keys())
    thisYear = max(retValByYear.keys())
    indexOfThisYear = sortedVals.index(retValByYear[thisYear])
    indexOfYear = sortedVals.index(retValByYear[year])
    minI = min(indexOfYear, indexOfThisYear)
    maxI = max(indexOfYear, indexOfThisYear)
    distance = 0
    for i in range(minI+1, maxI):
        distance += len(retYearByVal[sortedVals[i]])
    return distance

def makeFit(inValByYear, maxSize, verbose=False):
    retValByYear = {}
    #Python2: for (year, value) in inValByYear.iteritems():
    for (year, value) in inValByYear.items():
        if value != None:
            retValByYear[year] = value

    retYearByVal = reverseDict(retValByYear)

    # Remove the oldest year that is not the max or min value.
    while len(retValByYear) > maxSize:
        years = sorted(retValByYear.keys())
        firstBoringYearIndex = 0
        while ( firstBoringYearIndex < len(years)
                and ( ( retValByYear[years[firstBoringYearIndex]]
                        in ( min(retValByYear.values()), max(retValByYear.values()) ) )
                      or ( distanceFromThisYear(years[firstBoringYearIndex], retValByYear, retYearByVal) < 5 ) )
            ):
            firstBoringYearIndex += 1

        firstBoringYear = 9999
        if firstBoringYearIndex < len(years):
            firstBoringYear = years[firstBoringYearIndex]
        if firstBoringYear > max(retValByYear.keys()) - 30:
            if verbose:
                print("Ran out of years to throw out.")
            return retValByYear

        if verbose:
            print("Throwing out %d so the rest will fit" % firstBoringYear)
        del retValByYear[firstBoringYear]
    return retValByYear
