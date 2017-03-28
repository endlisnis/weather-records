#!/bin/bash -ex
for i in "$@";
do
    #gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r261.6 -sOutputFile=$i.png $i
    #gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 -sOutputFile=$i.png $i #825
    #gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r349 -sOutputFile=$i.png $i
    gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r745 -sOutputFile=$i.png $i
    convert -resize 2048x2048 -rotate 90 $i.png $i.small.png
    rm $i.png
done
