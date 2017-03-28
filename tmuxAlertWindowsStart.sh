#!/bin/bash
#unset TMUX
if [ -n "$TMUX" ]; then
    ./tmuxAlertWindows.sh $1
else
    tmux new-session "./tmuxAlertWindows.sh $1"
fi
