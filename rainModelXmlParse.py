#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml import etree
import bz2

root = etree.parse(bz2.open('2016081600_GEPS-NAEFS-RAW_OTTAWA_INTL_ON_CA_APCP-SFC_000-384.xml.bz2', 'rt'))

models = []
for model in root.xpath('/naefs_spena_forecast/forecast[@forecast_hour="36"]')[0].getchildren():
    models.append(float(model.text))

models.sort()
print(models, models[len(models)//2])
