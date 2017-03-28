import atexit
import glob
import os
import stations
from pprint import PrettyPrinter

class NotInCache(BaseException):
    pass

cache = {}
fileCache = {}

for cityName in stations.city:
    cache[cityName] = {}
    for fname in glob.glob('{city}/data/cache/*.py'.format(city=cityName)):
        year = int(fname.split('/')[-1].split('.')[0])
        #print(year, fname)
        cacheData = open(fname).read()
        fileCache[fname] = cacheData
        #print(repr(cacheData))
        cache[cityName][year] = eval(cacheData)

def cacheThis(city, year, name, val):
    if year not in cache[city]:
        cache[city][year] = {}
    cache[city][year][name] = val

def readCache(city, year, name):
    try:
        return cache[city][year][name]
    except KeyError:
        print("Cache miss: {city} {year} {name}".format(**locals()))
        raise NotInCache()

@atexit.register
def goodbye():
    for cityName in cache:
        for year in cache[cityName]:
            fname = '{city}/data/cache/{year}.py'.format(city=cityName, year=year)
            fdata = PrettyPrinter().pformat(cache[cityName][year])
            if fdata == fileCache.get(fname, None):
                # Nothing has changed, no need to update file
                continue

            try:
                os.mkdir('{city}/data/cache'.format(city=cityName))
            except OSError as err:
                if err.errno != 17:
                    raise
            fh = open(fname+'.tmp', 'w')
            fh.write(PrettyPrinter().pformat(cache[cityName][year]))
            fh.close()
            os.rename(fname+'.tmp', fname)
    print("You are now leaving the Python sector.")

