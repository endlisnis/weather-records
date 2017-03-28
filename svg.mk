city?=ottawa
SVG:=$(wildcard */svg/*.svg */svg/histogram/*.svg)
PNG:=$(patsubst ${city}/svg/%.svg,${city}/%.png,${SVG})

.PHONY: all

all: ${PNG}

${city}/histogram:
	mkdir -p $@

${city}/%.png: ${city}/svg/%.svg | ${city}/histogram
	rsvg-convert -o "$@" --background-color=white "$<"
	rm "$<"

