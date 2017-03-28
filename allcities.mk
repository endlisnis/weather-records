define INCLUDECITY

city:=$(1)
include weather.mk

endef

cities?=$(shell ./liststations.py)

$(foreach city,${cities},$(eval $(call INCLUDECITY,${city})))
