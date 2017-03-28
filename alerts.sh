#!/bin/bash
set -e
nice ./update.sh
nice ./tmuxAlertWindowsStart.sh $1
nice ./gensvg.py | nice parallel --bar --eta -j10 --progress --halt 1
./delayedTweets.py
