#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import daily, datetime

defaultFields = ( daily.MAX_TEMP,
                  daily.MAX_HUMIDEX,
                  daily.MIN_TEMP,
                  daily.MIN_WINDCHILL,
                  daily.AVG_WINDCHILL,
                  daily.TOTAL_RAIN_MM,
                  daily.TOTAL_SNOW_CM,
                  daily.TOTAL_PRECIP_MM,
                  daily.SNOW_ON_GRND_CM,
                  daily.AVG_WIND,
                  daily.SPD_OF_MAX_GUST_KPH )

def htmlTable(data, dates, fields = defaultFields):
    #print "htmlTable(%s, %s):" % (repr(dates), repr(fields))
    ret = "<table border=1>\n"

    ret += "<tr><td></td>"
    for date in dates:
        ret += "<th>%s</th>" % date
    ret += "</tr>\n"

    for field in fields:
        ret += "<tr>"
        ret += "<th>%s</th>" % field.englishName
        for date in dates:
            ret += "<td align=right>"
            v = data[date][field.index]
            if v is not None:
                ret += "%.1f%s" % (float(data[date][field.index]), field.htmlunits)
            else:
                ret += "n/a"
            ret += "</td>"
        ret += "</tr>\n"

    ret += "</table>\n"
    return ret

if __name__ == "__main__":
    print("<html><body>\n")
    dates = ( datetime.date(2013,7,19),
              datetime.date(1977,7,19) )

    data = daily.load('ottawa')

    print(htmlTable(data, dates))
    print("</body></html>\n")
