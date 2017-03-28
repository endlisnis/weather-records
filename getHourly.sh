#for year in 1953 1954 1955 1956 1957 1958 1959 1960 1961 1962 1963 1964 1965 1966 1967 1968 1969 1970 1971 1972 1973 1974 1975 1976 1977 1978 1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008; do
for year in 2010; do
#    for month in 1 2 3 4 5 6 7 8 9 10 11 12; do
    for month in $(( $(date '+%-m') - 1 )) $(date '+%-m'); do
	(rm ottawa/data/$year-$month.csv*;
	wget -qO ottawa/data/$year-$month.csv 'http://www.climate.weatheroffice.ec.gc.ca/climateData/bulkdata_e.html?timeframe=1&StationID=4337&Year='$year'&Month='$month'&format=csv&type=hly';
        bzip2 ottawa/data/$year-$month.csv; )&
    done
    wait
done
