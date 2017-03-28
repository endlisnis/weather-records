find */svg/histogram -ctime +30 -print0 | xargs -0 rm -v
find * -iname '*.png' -ctime +365 -print0 | xargs -0 rm -v
