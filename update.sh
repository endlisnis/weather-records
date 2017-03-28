#!/bin/bash
set -e
rm -f */data/*-24hrs*.json
./update.py | nice parallel -uj20 --halt 1
#./process.py | nice parallel -uj2 --halt 1
nice make -Rrj4 all
