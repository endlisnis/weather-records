#!/usr/bin/python3
# -*- coding: utf-8 -*-

def reverseDict(db):
    ret = {}
    #Python2: for (key, value) in db.iteritems():
    for (key, value) in db.items():
        if value not in ret:
            ret[value] = [key]
        else:
            ret[value].append(key)
    return ret

def topNKeys(db, count):
    ret = {}
    for i in sorted(db.keys())[-count:]:
        ret[i] = db[i]
    return ret

def topNValuesLists(db, count, bottomN=False):
    ret = {}
    if bottomN:
        keyList = sorted(db.keys())
    else:
        keyList = reversed(sorted(db.keys()))
    for i in keyList:
        if sum(len(a) for a in ret.values()) < count:
            ret[i] = db[i]
            continue
        break
    return ret

def inListOfLists(db, val):
    for a in db:
        if val in a:
            return True
    return False
