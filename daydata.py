#/bin/python3
# -*- coding: utf-8 -*-

from namedtuplewithdefaults import namedtuple_with_defaults
from score import selectBestWithFlag

def dictFromArgs(**kwargs):
    return kwargs

def _noneOrInt(val):
    if val is None:
        return None
    return int(val)

def _noneOrInt10(val):
    if val is None:
        return None
    return int(val*10)


DayDataBase = namedtuple_with_defaults(
    'DayData',
    ('MAX_TEMP', 'MAX_TEMP_FLAG',
     'MIN_TEMP', 'MIN_TEMP_FLAG',
     'TOTAL_RAIN_MM', 'TOTAL_RAIN_FLAG',
     'TOTAL_SNOW_CM', 'TOTAL_SNOW_FLAG',
     'TOTAL_PRECIP_MM', 'TOTAL_PRECIP_FLAG',
     'SNOW_ON_GRND_CM', 'SNOW_ON_GRND_FLAG',
     'DIR_OF_MAX_GUST_10S_DEG', 'DIR_OF_MAX_GUST_FLAG',
     'SPD_OF_MAX_GUST_KPH', 'SPD_OF_MAX_GUST_FLAG',
     'MAX_HUMIDEX', 'MAX_HUMIDEX_FLAG',
     'MIN_WINDCHILL', 'MIN_WINDCHILL_FLAG',
     'AVG_WINDCHILL', 'AVG_WINDCHILL_FLAG',
     'AVG_WIND', 'AVG_WIND_FLAG',
     'MEAN_TEMP', 'MEAN_TEMP_FLAG',
     'MIN_HUMIDITY', 'MIN_HUMIDITY_FLAG',
     'MEAN_HUMIDITY', 'MEAN_HUMIDITY_FLAG',
     'AVG_DEWPOINT', 'AVG_DEWPOINT_FLAG',
    ),
    default_values=dictFromArgs(
        MAX_TEMP=None, MAX_TEMP_FLAG='M',
        MIN_TEMP=None, MIN_TEMP_FLAG='M',
        TOTAL_RAIN_MM=None, TOTAL_RAIN_FLAG='M',
        TOTAL_SNOW_CM=None, TOTAL_SNOW_FLAG='M',
        TOTAL_PRECIP_MM=None, TOTAL_PRECIP_FLAG='M',
        SNOW_ON_GRND_CM=None, SNOW_ON_GRND_FLAG='M',
        DIR_OF_MAX_GUST_10S_DEG=None, DIR_OF_MAX_GUST_FLAG='M',
        SPD_OF_MAX_GUST_KPH=None, SPD_OF_MAX_GUST_FLAG='M',
        MAX_HUMIDEX=None, MAX_HUMIDEX_FLAG='M',
        MIN_WINDCHILL=None, MIN_WINDCHILL_FLAG='M',
        AVG_WINDCHILL=None, AVG_WINDCHILL_FLAG='M',
        AVG_WIND=None, AVG_WIND_FLAG='M',
        MEAN_TEMP=None, MEAN_TEMP_FLAG='M',
        MIN_HUMIDITY=None, MIN_HUMIDITY_FLAG='M',
        MEAN_HUMIDITY=None, MEAN_HUMIDITY_FLAG='M',
        AVG_DEWPOINT=None, AVG_DEWPOINT_FLAG='M' )
)

_compileCache = {}

class DayData(DayDataBase):
    def eval(self, evalStr, extraValues=None):
        global _compileCache
        if evalStr in _compileCache:
            compiled = _compileCache[evalStr]
        else:
            compiled = compile(evalStr, '.', 'eval')
            _compileCache[evalStr] = compiled
        expressionValues = {
            'max': self.MAX_TEMP,
            'maxFlag': self.MAX_TEMP_FLAG,
            'min': self.MIN_TEMP,
            'minFlag': self.MIN_TEMP_FLAG,
            'rain': self.TOTAL_RAIN_MM,
            'precip': self.TOTAL_PRECIP_MM,
            'snow': self.TOTAL_SNOW_CM,
            'snowDepth': self.SNOW_ON_GRND_CM,
            'maxWindGust': self.SPD_OF_MAX_GUST_KPH,
            'maxHumidex': self.MAX_HUMIDEX,
            'minWindchill': self.MIN_WINDCHILL,
            'avgWindchill': self.AVG_WINDCHILL,
            'avgWind': self.AVG_WIND,
            'meanTemp': self.MEAN_TEMP,
            'meanTempFlag': self.MEAN_TEMP_FLAG,
            'minHumidity': self.MIN_HUMIDITY,
            'meanHumidity': self.MEAN_HUMIDITY,
            'avgDewpoint': self.AVG_DEWPOINT,
        }
        if extraValues is not None:
            expressionValues.update(extraValues)
        try:
            ret = eval(compiled, expressionValues)
        except TypeError:
            return None
        return ret
    def merge(self, other):
        mergedValues = {}
        for fieldIndex, fieldName in enumerate(self._fields):
            if fieldName.endswith('_FLAG'):
                continue
            val, flag = selectBestWithFlag(
                self[fieldIndex], self[fieldIndex+1],
                other[fieldIndex], other[fieldIndex+1])
            mergedValues[fieldName] = val
            mergedValues[self._fields[fieldIndex+1]] = flag
        return DayData(**mergedValues)
    def dumpCsv(self):
        return (
            _noneOrInt10(self.MAX_TEMP), self.MAX_TEMP_FLAG,
            _noneOrInt10(self.MIN_TEMP), self.MIN_TEMP_FLAG,
            _noneOrInt10(self.TOTAL_RAIN_MM), self.TOTAL_RAIN_FLAG,
            _noneOrInt10(self.TOTAL_SNOW_CM), self.TOTAL_SNOW_FLAG,
            _noneOrInt10(self.TOTAL_PRECIP_MM), self.TOTAL_PRECIP_FLAG,
            self.SNOW_ON_GRND_CM, self.SNOW_ON_GRND_FLAG,
            self.DIR_OF_MAX_GUST_10S_DEG, self.DIR_OF_MAX_GUST_FLAG,
            self.SPD_OF_MAX_GUST_KPH, self.SPD_OF_MAX_GUST_FLAG,
            _noneOrInt10(self.MAX_HUMIDEX), self.MAX_HUMIDEX_FLAG,
            _noneOrInt10(self.MIN_WINDCHILL), self.MIN_WINDCHILL_FLAG,
            _noneOrInt10(self.AVG_WINDCHILL), self.AVG_WINDCHILL_FLAG,
            _noneOrInt(self.AVG_WIND), self.AVG_WIND_FLAG,
            _noneOrInt10(self.MEAN_TEMP), self.MEAN_TEMP_FLAG,
            self.MIN_HUMIDITY, self.MIN_HUMIDITY_FLAG,
            self.MEAN_HUMIDITY, self.MEAN_HUMIDITY_FLAG,
            _noneOrInt10(self.AVG_DEWPOINT), self.AVG_DEWPOINT_FLAG )

