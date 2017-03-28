MAKECMDGOALS?=all
.PHONY: ${MAKECMDGOALS}

cities?=$(shell ./liststations.py)

${cities}:
	mkdir -p $@

.PHONY: $(foreach city,${cities},${city}.target)

$(foreach city,${cities},${city}.target): ${cities}
	./genMakefile.py $(basename $@) > $(basename $@)/years.mk

all: $(foreach city,${cities},${city}.target) | ${cities}
	${MAKE} -f allcities.mk all
