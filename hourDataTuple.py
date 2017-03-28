#/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple, OrderedDict
from score import selectBestWithFlag, selectBest
from namedtuplewithdefaults import namedtuple_with_defaults, dictFromArgs

import decimal
import math

D = decimal.Decimal

HourDataTuple = namedtuple_with_defaults(
    'HourData',
    ('TEMP', 'TEMP_FLAG', 'DEW_POINT_TEMP',
     'DEW_POINT_TEMP_FLAG', 'REL_HUM', 'REL_HUM_FLAG',
     'WIND_DIR', 'WIND_DIR_FLAG',
     'WIND_SPD', 'WIND_SPD_FLAG',
     'VISIBILITY', 'VISIBILITY_FLAG', 'STN_PRESS',
     'STN_PRESS_FLAG', 'WEATHER'),
    default_values=dictFromArgs(
        TEMP=None,
        TEMP_FLAG='M',
        DEW_POINT_TEMP=None,
        DEW_POINT_TEMP_FLAG='M',
        REL_HUM=None,
        REL_HUM_FLAG='M',
        WIND_DIR=None,
        WIND_DIR_FLAG='M',
        WIND_SPD=None,
        WIND_SPD_FLAG='M',
        VISIBILITY=None,
        VISIBILITY_FLAG='M',
        STN_PRESS=None,
        STN_PRESS_FLAG='M',
        WEATHER=None)
)

sqlTypes = HourDataTuple(
    TEMP='integer',
    TEMP_FLAG='text',
    DEW_POINT_TEMP='integer',
    DEW_POINT_TEMP_FLAG='text',
    REL_HUM='integer',
    REL_HUM_FLAG='text',
    WIND_DIR='integer',
    WIND_DIR_FLAG='text',
    WIND_SPD='integer',
    WIND_SPD_FLAG='text',
    VISIBILITY='integer',
    VISIBILITY_FLAG='text',
    STN_PRESS='integer',
    STN_PRESS_FLAG='text',
    WEATHER='text')


#HourDataTuple.__new__.__defaults__ = (None,) * len(HourDataTuple._fields)

def humidex(temperature, dewPoint):
    dewpointK = float(dewPoint) + 273.16
    e = 6.11*math.exp(5417.7530*( (1/273.16) - (1/dewpointK) ) )
    h = (0.5555)*(e - 10.0)
    hv = temperature+D(h).quantize(D('.1'), decimal.ROUND_HALF_UP)
    if hv > 23:
        return hv
    return temperature

def windchill(temp, wind):
    if temp < 10:
        return min(temp, 13.12 + .6215*temp - 11.37*wind**.16 + 0.3965*temp*wind**.16)
    return temp

def _strToFloat(strVal):
    if len(strVal) == 0:
        return None
    return float(strVal)

def _noneOrInt10(val):
    if val is None:
        return None
    return int(val*10)

def _noneOrInt100(val):
    if val is None:
        return None
    return int(val*100)

_compileCache = {}

class HourData(HourDataTuple):
    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        # The only reason why this function is here at all is because
        # _asdict is broken in Python3 when inheriting from a
        # namedtuple https://bugs.python.org/issue24931.
        return OrderedDict(zip(self._fields, self))
    @property
    def humidex(self):
        if ( self.DEW_POINT_TEMP is not  None
             and self.TEMP is not None
        ):
            #
            #print repr(self.TEMP), repr(self.DEW_POINT_TEMP)
            return humidex(self.TEMP, self.DEW_POINT_TEMP)
        return None

    @property
    def windchill(self):
        if self.TEMP is None:
            return None
        if self.WIND_SPD is None:
            return self.TEMP
        temp = float(self.TEMP)
        wind = self.WIND_SPD
        if temp >= 10:
            return None
        wc = D( 13.12
               + .6215*temp
               - 11.37*wind**.16
               + 0.3965*temp*wind**.16)
        wc = wc.quantize(D('.1'), decimal.ROUND_HALF_UP)
        return min(self.TEMP, wc)

    def eval(self, evalStr, extraValues=None):
        global _compileCache
        if evalStr in _compileCache:
            compiled = _compileCache[evalStr]
        else:
            compiled = compile(evalStr, '.', 'eval')
            _compileCache[evalStr] = compiled
        expressionValues = {
            'temp': self.TEMP,
            'dewpoint': self.DEW_POINT_TEMP,
            'humidity': self.REL_HUM,
            'wind': self.WIND_SPD,
            'visibility': self.VISIBILITY,
            'pressure': self.STN_PRESS,
            'weather': self.WEATHER,
            'humidex': self.humidex,
            'windchill': self.windchill,
        }
        if extraValues is not None:
            expressionValues.update(extraValues)
        try:
            ret = eval(compiled, expressionValues)
        except TypeError:
            return None
        return ret
    def dumpAsSql(self):
        TEMP=_noneOrInt10(self.TEMP)
        DEW_POINT_TEMP=_noneOrInt10(self.DEW_POINT_TEMP)
        VISIBILITY=_noneOrInt10(self.VISIBILITY)
        STN_PRESS=_noneOrInt100(self.STN_PRESS)
        return ( TEMP, self.TEMP_FLAG,
                 DEW_POINT_TEMP, self.DEW_POINT_TEMP_FLAG,
                 self.REL_HUM, self.REL_HUM_FLAG,
                 self.WIND_DIR, self.WIND_DIR_FLAG,
                 self.WIND_SPD, self.WIND_SPD_FLAG,
                 VISIBILITY, self.VISIBILITY_FLAG,
                 STN_PRESS, self.STN_PRESS_FLAG,
                 self.WEATHER )
    def merge(self, other):
        mergedValues = {}
        for fieldIndex, fieldName in enumerate(self._fields):
            if fieldName.endswith('_FLAG'):
                continue
            if fieldName == 'WEATHER':
                val = selectBest(
                    self[fieldIndex], other[fieldIndex])
            else:
                val, flag = selectBestWithFlag(
                    self[fieldIndex], self[fieldIndex+1],
                    other[fieldIndex], other[fieldIndex+1])
            mergedValues[fieldName] = val
            if fieldName != 'WEATHER':
                mergedValues[self._fields[fieldIndex+1]] = flag
        return HourData(**mergedValues)
