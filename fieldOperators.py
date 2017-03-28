# -*- coding: utf-8 -*-
import dailyRecords

def GreaterThan(lhs, rhs):
    if lhs is not None:
        result = (lhs > rhs)
        if result:
            return lhs
        return False
    return None

class OpWithFlag():
    def __init__(self, field, compare):
        self.field = field
        self.compare = compare
    def __call__(self, data, recentValues=None):
        value = data[self.field.index]
        flag = data[self.field.index+1]
        if flag == 'M':
            return None, ''
        if value is None:
            return None, '' #value = 0
        return self.op(value, recentValues), flag
    @property
    def units(self):
        return self.field.units
    @property
    def englishName(self):
        return self.field.englishName
    @property
    def minValue(self):
        return self.field.minValue
    @property
    def name(self):
        return self.field.name+'op'

class SpecialNone():
    def __lt__(self, other):
        return False
    def __le__(self, other):
        return (other is None)
    def __gt__(self, other):
        return False
    def __ge__(self, other):
        return (other is None)
    def __eq__(self, other):
        return (other is None)
    def __ne__(self, other):
        return False
    def __str__(self):
        return "SpecialNone()"
    def __repr__(self):
        return "SpecialNone()"


class Value():
    def __init__(self, field):
        self.field = field
    def __call__(self, data, date):
        value = data[self.field.index]
        flag = data[self.field.index+1]
        if flag == 'M':
            return SpecialNone()
        if value is None:
            return SpecialNone()
        return value
    def getFlag(self, data):
        return data[self.field.index+1]
    def getName(self):
        return self.field.name

class ValueNoFlag():
    def __init__(self, field):
        self.field = field
    def __call__(self, data, date):
        value = self.field(data)
        if value is None:
            return SpecialNone()
        return value
    def getFlag(self, data):
        return None
    def getName(self):
        return self.field.name


class ValueNearRecordMin():
    def __init__(self, field):
        self.field = field
    def __call__(self, data, date):
        value = data[self.field.index]
        flag = data[self.field.index+1]
        if flag == 'M':
            return SpecialNone()
        if value is None:
            return SpecialNone()
        maxMin = dailyRecords.cachedDailyMaxMin('ottawa', date, self.field)
        return value - maxMin.min.value
    def getFlag(self, data):
        return data[self.field.index+1]
    def getName(self):
        return self.field.name

class ValueEmptyZero():
    def __init__(self, field):
        self.field = field
    def __call__(self, data, date):
        value = data[self.field.index]
        flag = data[self.field.index+1]
        if flag == 'M':
            return None
        if value is None:
            return 0
        return value
    def getFlag(self, data):
        return data[self.field.index+1]
    def getName(self):
        return self.field.name

class ValueDiff():
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2
    def __call__(self, data, date):
        value1 = data[self.field1.index]
        flag1 = data[self.field1.index+1]
        value2 = data[self.field2.index]
        flag2 = data[self.field2.index+1]
        if flag1 == 'M' or flag2 == 'M':
            return None
        if value1 is None or value2 is None:
            return None
        diff = value1 - value2
        return diff
    def getFlag(self, data):
        return data[self.field1.index+1]+data[self.field2.index+1]
    def getName(self):
        return '%s-%s' % (self.field1.name, self.field2.name)

class FreezingDegreeDaysSnowDepth():
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2
    def __call__(self, data, date):
        maxV = data.MAX_TEMP
        maxFlag = data.MAX_TEMP_FLAG
        minV = data.MIN_TEMP
        minFlag = data.MIN_TEMP_FLAG
        snowV = data.SNOW_ON_GRND_CM
        snowFlag = data.SNOW_ON_GRND_FLAG

        if maxFlag == 'M' or minFlag == 'M' or snowFlag == 'M':
            return None
        if len(maxV) == 0 or len(minV) == 0 or len(snowV) == 0:
            return None
        fddsd = (min(0, -maxV) + min(0, -minV))*snowV
        return fddsd
    def getFlag(self, data):
        return data.MAX_TEMP_FLAG+data.MIN_TEMP_FLAG+data.SNOW_ON_GRND_FLAG
    def getName(self):
        return 'FreezingDegreeDaysSnowDepth'

class GreaterThanWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        result = (float(value) > self.compare)
        if result:
            return value
        return False

class GreaterThanWithFlagBoolean(OpWithFlag):
    def op(self, value, recentValues):
        return int(float(value) > self.compare)
    @property
    def units(self):
        return "days"
    @property
    def minValue(self):
        return 0

class AtMostWithFlagBoolean(OpWithFlag):
    def op(self, value, recentValues):
        return int(float(value) <= self.compare)
    @property
    def units(self):
        return "days"
    @property
    def minValue(self):
        return 0

class AtLeastWithFlagBoolean(OpWithFlag):
    def op(self, value, recentValues):
        return int(float(value) >= self.compare)
    @property
    def units(self):
        return "days"
    @property
    def minValue(self):
        return 0

class GreaterThanOrEqualToWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        result = (float(value) >= self.compare)
        if result:
            return value
        return False

class LessThanWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        result = (float(value) < self.compare)
        if result:
            return value
        #print value
        return False

class LessThanOrEqualToWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        result = (float(value) <= self.compare)
        if result:
            return value
        return False

class EqualToWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        return value == self.compare

class IncreasingWithFlag(OpWithFlag):
    def op(self, value, recentValues):
        if len(recentValues) == 0:
            return value
        result = (value > recentValues[-1])
        if result:
            return value
        return False

def GreaterThanOrEqual(lhs, rhs):
    if lhs != None and len(lhs):
        result = (lhs >= rhs)
        if result:
            return lhs
        return False
    return None

def LessThan(lhs, rhs):
    if lhs != None and len(lhs):
        #print( '"%s" < %d = %d' % (lhs, rhs, Fraction(lhs) < rhs))
        #return Fraction(lhs) < rhs
        if lhs < rhs:
            return lhs
        return False
    return None

def LessThanOrEqual(lhs, rhs):
    if lhs != None and len(lhs):
        #print '"%s" > %d' % (lhs, rhs)
        return lhs <= rhs
    return None

def TraceOrMore(val, flag):
    if flag=="T":
        return True
    if (val != None and len(val)):
        #print '"%s" > %d' % (lhs, rhs)
        return val > 0
    return None
