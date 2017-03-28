#!/usr/bin/python3
import argparse
import daily
from collections import namedtuple
import alertTweets
import stations

ValWithDate = namedtuple('ValWithDate', ( 'val', 'date' ) )

def main(city, year):
    data = daily.load(city)
    cold = ValWithDate(+999, None)
    heat = ValWithDate(-999, None)
    snow = ValWithDate(0, None)
    rain = ValWithDate(0, None)
    wind = ValWithDate(0, None)

    for day, weather in data.items():
        if day.year != year:
            continue
        #import pudb; pu.db
        if ( weather.MAX_TEMP is not None
             and weather.MAX_TEMP > heat.val
        ):
            heat = ValWithDate(weather.MAX_TEMP, day)
        if ( weather.MIN_TEMP is not None
             and weather.MIN_TEMP < cold.val
        ):
            cold = ValWithDate(weather.MIN_TEMP, day)
        if ( weather.TOTAL_SNOW_CM is not None
             and weather.TOTAL_SNOW_CM > snow.val
        ):
            snow = ValWithDate(weather.TOTAL_SNOW_CM, day)
        if ( weather.TOTAL_RAIN_MM is not None
             and weather.TOTAL_RAIN_MM > rain.val
        ):
            rain = ValWithDate(weather.TOTAL_RAIN_MM, day)
        if ( weather.SPD_OF_MAX_GUST_KPH is not None
             and weather.SPD_OF_MAX_GUST_KPH > wind.val
        ):
            wind = ValWithDate(weather.SPD_OF_MAX_GUST_KPH, day)

    cityName = stations.city[city].name
    tweet = '#{cityName} 2016 extremes:'.format(**locals())
    for name,u in ( ('heat','℃'),
                    ('cold','℃'),
                    ('snow','cm'),
                    ('rain','mm'),
                    ('wind','km/h') ):
        if locals()[name].date is None:
            continue
        tweet += ('\n{}: {}{} ({})'
                  .format(name,
                          locals()[name].val,
                          u,
                          locals()[name].date.strftime('%b %d')))
    alertTweets.maybeTweetWithSuffix(city, tweet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate monthly tweets.')
    parser.add_argument('--city', default='ottawa')
    parser.add_argument('--year', type=int, required=True)
    args = parser.parse_args()
    main(args.city, args.year)
