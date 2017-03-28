# -*- coding: utf-8 -*-
from __future__ import print_function
import types

class ExtraData:
    __slots__ = ()
    def __init__(self):
        self.maxHmdxByDate = {}
        self.minWindchillByDate = {}
        self.avgWindchillByDate = {}
        self.avgWindByDate = {}
        self.minTempByDate = {}
        self.maxTempByDate = {}
        self.avgDewpointByDate = {}


class ValWithFlag:
    def __init__(self, val, flag):
        self._val = val
        self.flag = flag
        assert type(val) != types.StringType
    #def __ne__(self, other):
    #    if type(other) == type(self):
    #        return self.val.__ne__(other.val)
    #    return self.val.__ne__(other)
    def __cmp__(self, other):
        if type(other) == type(self):
            if self._val < other._val:
                return -1
            if self._val == other._val:
                return 0
            return 1
        if self._val < other:
            return -1
        if self._val == other:
            return 0
        return 1

    def getVal(self):
        return self._val

    def setVal(self, newVal):
        assert type(newVal) != types.StringType
        self._val = newVal

    val = property(getVal, setVal)

    def __repr__(self):
        return 'ValWithFlag(val=%s (%s), flag=%s)' % (repr(self._val), type(self._val), repr(self.flag))
