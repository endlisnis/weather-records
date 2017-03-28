#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import snow, daily, datetime

snow.createPlot('ottawa',
                running=True,
                field=daily.TOTAL_SNOW_CM,
                otheryears = [2012],
                name = "SpringSnow",
                dataStartDay = datetime.date(2014, 3, 22),
                plotStartDay = datetime.date(2014, 3, 22),
                plotEndDay = datetime.date(2014, 6, 1))
