i=0
for city in $(./liststations.py); do
    if [ $i = 0 ]; then
        tmux new-session -d "echo $city; ./alerts.py $city"
    else
        tmux split-window "echo $city; ./alerts.py $city"
    fi
    tmux select-layout tiled
    let i=i+1
done
tmux select-layout tiled
tmux attach
