set -e
for city in $(./liststations.py); do
    echo $city
    ./monthTweets.py --city $city --avgTemp --force
done
