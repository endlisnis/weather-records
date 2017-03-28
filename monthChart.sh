./monthChart.py
for i in Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec; do
    mkdir ottawa/$i
    mv -v ottawa/$i*.png ottawa/$i
done
