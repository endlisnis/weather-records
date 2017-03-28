limit="${1:-4}"
i=0
cities=$(./liststations.py)
cityCount=$( echo $cities | wc -w )
for city in $(./liststations.py); do
    #tmux list-panes
    echo $i of $cityCount
    while [ $(tmux list-panes | wc -l) -gt $limit ]; do
        sleep 1
    done
    tmux split-window -d "echo $city; ./alerts.py $city || read -p \"command failed: \""
    tmux select-layout tiled
    let i=i+1
done
#tmux attach
