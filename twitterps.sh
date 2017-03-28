#!/bin/bash -ex
for i in "$@";
do
    gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r375 -sOutputFile=$i.png $i
    convert -resize 1024x1024 -rotate 90 $i.png $i.small.png
    rm $i.png
done
