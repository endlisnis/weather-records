#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
import stations

windows = subprocess.check_output(
    ['tmux', 'list-windows', '-F', '#{window_name}']).strip().decode().split()

count = 0
for key in stations.city.keys():
    if key in windows:
        print(key)
        count += 1
exit(count)
#print(windows)
