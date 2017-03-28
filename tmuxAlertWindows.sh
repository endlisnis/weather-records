#!/bin/bash
limit="${1:-2}"
#let limit=limit+1 #To allow the tweeting window
i=0
cities=$(./liststations.py)
cityCount=$( echo $cities | wc -w )
#tmux new-window "./delayedTweets.py || read -p \"delayedTweets.py failed: \""
for city in $(./liststations.py); do
    echo $i of $cityCount
    let loopCount=0
    #while [ $(tmux list-windows | wc -l) -gt $limit -a $loopCount -le 12 ]; do
    sleep 1
    while [ $(top -n1 | grep '^Tasks:' | awk '{print $4}') -gt 2 ]; do
        sleep 2
        let loopCount=loopCount+1
    done
    if tmux list-windows | head -1 | grep '(active)$'; then
        tmux new-window -n $city "echo $city; ./alerts.py $city || read -p \"alerts.py failed: \"; ./hourAlerts.py --city=$city || read -p \"hourAlerts.py failed: \""
    else
        tmux new-window -d -n $city "echo $city; ./alerts.py $city || read -p \"alerts.py failed: \"; ./hourAlerts.py --city=$city || read -p \"hourAlerts.py failed: \""
    fi
    let i=i+1
done
while ! ./activeWindowCount.py;
do
    sleep 1
done
