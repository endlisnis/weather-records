.PHONY: all

all:
	./gensvg.py > svg3.mk
	make -j10 -fsvg3.mk
