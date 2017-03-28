DATETIME:=$(shell date '+%Y.%m.%d.%H')

TIMEOUT=$(shell python -c "import random; print random.randint(8,12)")
WGET=while true; do wget $(if ${DEBUG},-nv,-q) -T ${TIMEOUT} -O ${1} ${2} && break; done

#YEARS:=$(shell python -c "print ' '.join(str(a) for a in range(${MINYEAR}, ${MAXYEAR}+1))")

.SECONDARY:
.DELETE_ON_ERROR:

.PHONY: all FORCE monthly

all:

include ${city}/years.mk

all: ${city}/data/all.fcsv.bz2 ${city}/svg/.debug ${city}/svg/histogram/.debug
#all: ${city}/CumulativeSnowfall.ps ${city}/DailyRainfall.ps ${city}/DailySnowfall.ps ${city}/SnowOnTheGround.ps ${city}/WeatherNetwork/${DATETIME}.html #${city}/forecast.ps

${city}/WeatherNetwork:
	mkdir -p $@

${city}/WeatherNetwork/%.html: | ${city}/WeatherNetwork
	$(call WGET, $@, 'http://www.theweathernetwork.com/fourteenday/caon0512/table')

${city}/data ${city}/svg/.debug ${city}/svg/histogram/.debug:
	mkdir -p $@

${city}/data/%.dailyextra-csv.bz2: city:=${city}
${city}/data/%.dailyextra-csv.bz2: ./convertHourlyToDaily.py hourly.py daily.py weather.mk | ${city}/data ${city}/environmentCanada.xml
	./convertHourlyToDaily.py ${city} $*

${city}/data/all.fcsv.bz2: city:=${city}
${city}/data/all.fcsv.bz2: $(foreach year,${MONTH_YEARS},${city}/data/${year}.dailyextra-csv.bz2) \
                           daily.py\
                           ${city}/data/yesterdayForecast.db.touch \
                           ${city}/data/metar.db.touch \
                           | ${city}/data
	python3 ./dailyConvert.py ${city}

%.mcsv.touch:
	./importOneMonth.py --year ${YEAR} --month ${MONTH} --city ${city}
	@touch $@

${city}/data/yesterdayForecast.db.touch: ${city}/environmentCanada.html parseHtmlForecast.py
	./parseHtmlForecast.py ${city} $<
	@touch $@

${city}/data/metar.db.touch:

${city}/data/weatherstats.db.touch: ${city}/data/temperature-24hrs.0.json ${city}/data/relative_humidity-24hrs.0.json ${city}/data/dew_point-24hrs.0.json ${city}/data/wind_speed-24hrs.0.json ${city}/data/wind_gust_speed-24hrs.0.json ${city}/data/pressure_sea-24hrs.0.json ${city}/data/visibility-24hrs.0.json
	./recentWeather.py --city ${city}
	@touch $@

#Provide default rules for these files in case they don't exist for a given city
${city}/data/temperature-24hrs.0.json ${city}/data/relative_humidity-24hrs.0.json ${city}/data/dew_point-24hrs.0.json ${city}/data/wind_speed-24hrs.0.json ${city}/data/wind_gust_speed-24hrs.0.json ${city}/data/pressure_sea-24hrs.0.json ${city}/data/visibility-24hrs.0.json:

${city}/%.ps: city:=${city}
${city}/%.ps: snow.py forecast.py ${city}/data/all.fcsv daily.py | ${city}/svg/.debug ${city}/svg/histogram/.debug
	python ./snow.py ${city} $* 2013

#${city}/forecast.ps: temperature.py  forecast.py ${city}/data/all.fcsv ${city}/data/forecast.html
#	python ./temperature.py ${city} 21

%.png: %.ps makefile
	gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r219.6 -sOutputFile=$<.png $<
	convert -resize 25% -rotate 90 $<.png $@
	rm $<.png
